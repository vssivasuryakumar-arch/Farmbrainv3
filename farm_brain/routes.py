from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta, timezone
import json
import secrets
from functools import wraps

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import (
    CapabilityAssignment, CommunityPost, Enquiry, InventoryItem, Listing,
    Quotation, SavedListing, StockMovement, User, UserRole, MemberProfile, TransportDetail,
    PostLike, PostComment, utcnow, PendingRegistration, PasswordResetOTP, ListingAttachment,
)
from .taxonomy import CATEGORIES, CAPABILITIES, CURRENCIES, DIVISIONS, RECORD_TYPES, TRANSPORT_KINDS


auth_bp = Blueprint("auth", __name__)
main_bp = Blueprint("main", __name__)


def form_decimal(value, label, optional=True):
    value = (value or "").strip()
    if not value:
        if optional:
            return None
        raise ValueError(f"Please enter {label.lower()}.")
    try:
        number = Decimal(value)
        if not number.is_finite() or number < 0:
            raise ValueError
        return number
    except (InvalidOperation, ValueError):
        raise ValueError(f"Please enter a valid non-negative {label.lower()}.")


def is_listing_owner(listing):
    return current_user.is_authenticated and listing.owner_id == current_user.id


def safe_next(default_endpoint="main.dashboard"):
    # Redirect only to a local path. External redirect values are ignored.
    target = request.form.get("next", "")
    if target.startswith("/") and not target.startswith("//"):
        return target
    return url_for(default_endpoint)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Create a pending account and require an email OTP before activation."""
    import re
    from werkzeug.security import generate_password_hash
    from .mailer import send_email

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        country = request.form.get("country", "IN").strip().upper()
        capabilities = list(dict.fromkeys(request.form.getlist("capabilities")))
        errors = []
        if not name or len(name) > 100:
            errors.append("Enter your name (up to 100 characters).")
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(email) > 255:
            errors.append("Enter a valid email address.")
        if len(password) < 10:
            errors.append("Use a password with at least 10 characters.")
        if len(phone) > 40 or len(city) > 100 or len(state) > 100:
            errors.append("Phone, city or state is longer than the supported limit.")
        if country not in {"IN", "AE", "US", "GB"}:
            errors.append("Choose a supported country option.")
        if not capabilities or any(c not in CAPABILITIES for c in capabilities):
            errors.append("Select at least one capability.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with that email already exists.")
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("auth/register.html", capabilities=CAPABILITIES, form=request.form), 400

        pending = PendingRegistration.query.filter_by(email=email).first()
        if pending:
            expires = pending.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) <= expires:
                session["pending_registration_email"] = email
                flash("A registration verification is already in progress for this email. Enter the code you received or use the resend option after the cooldown.", "info")
                return redirect(url_for("auth.verify_email"))
            db.session.delete(pending)
            db.session.flush()
        code = f"{secrets.randbelow(1_000_000):06d}"
        pending = PendingRegistration(
            name=name, email=email, password_hash=generate_password_hash(password),
            phone=phone, city=city, state=state, country=country,
            capabilities_json=json.dumps(capabilities),
            otp_hash=generate_password_hash(code),
            expires_at=utcnow() + timedelta(minutes=current_app.config.get("OTP_TTL_MINUTES", 10)),
            attempts=0, last_sent_at=utcnow(),
        )
        db.session.add(pending)
        try:
            send_email(
                email,
                "Your FARM BRAIN verification code",
                f"Your FARM BRAIN email verification code is {code}. It expires in {current_app.config.get('OTP_TTL_MINUTES', 10)} minutes. If you did not request this, ignore this email.",
                f"<p>Your FARM BRAIN verification code is:</p><h1 style='letter-spacing:6px'>{code}</h1><p>It expires in {current_app.config.get('OTP_TTL_MINUTES', 10)} minutes.</p><p>If you did not request this, ignore this email.</p>",
            )
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            current_app.logger.exception("FARM BRAIN OTP delivery failed")
            flash("We could not send the verification email. Please check the mail settings or try again later.", "error")
            return render_template("auth/register.html", capabilities=CAPABILITIES, form=request.form), 503
        session["pending_registration_email"] = email
        if current_app.testing:
            current_app.extensions.setdefault("otp_test_codes", {})[email] = code
        elif current_app.config.get("OTP_DEV_MODE") and current_app.config.get("APP_ENV") != "production":
            flash(f"Local development OTP: {code}. Configure SMTP to test actual email delivery.", "info")
        flash("We sent a six-digit verification code to your email address.", "success")
        return redirect(url_for("auth.verify_email"))
    return render_template("auth/register.html", capabilities=CAPABILITIES, form=request.form)


@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    from .features import make_handle
    from .models import MemberProfile
    from werkzeug.security import check_password_hash

    email = session.get("pending_registration_email", "")
    pending = PendingRegistration.query.filter_by(email=email).first() if email else None
    if not pending:
        flash("Your registration session expired. Please start again.", "error")
        return redirect(url_for("auth.register"))
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        expires = pending.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            db.session.delete(pending)
            db.session.commit()
            session.pop("pending_registration_email", None)
            flash("That code expired. Please register again to receive a new code.", "error")
            return redirect(url_for("auth.register"))
        if pending.attempts >= current_app.config.get("OTP_MAX_ATTEMPTS", 5):
            db.session.delete(pending)
            db.session.commit()
            session.pop("pending_registration_email", None)
            flash("Too many incorrect attempts. Please register again.", "error")
            return redirect(url_for("auth.register"))
        pending.attempts += 1
        if len(code) != 6 or not code.isdigit() or not check_password_hash(pending.otp_hash, code):
            db.session.commit()
            flash("The verification code is incorrect.", "error")
            return render_template("auth/verify_email.html", email=email), 400
        user = User(
            name=pending.name, email=pending.email, password_hash=pending.password_hash,
            phone=pending.phone, city=pending.city, state=pending.state, country=pending.country,
        )
        for capability in json.loads(pending.capabilities_json):
            user.capabilities.append(CapabilityAssignment(capability=capability))
        db.session.add(user)
        db.session.flush()
        farmer = "Farmer / Grower" in json.loads(pending.capabilities_json)
        db.session.add(MemberProfile(
            user_id=user.id, handle=make_handle(user.name, user.id),
            plan_code="FARMER_BASIC_FREE" if farmer else "COMMUNITY_FREE",
        ))
        if user.email == current_app.config.get("ADMIN_EMAIL", "").strip().lower() and user.email:
            db.session.add(UserRole(user_id=user.id, role="admin"))
        db.session.delete(pending)
        db.session.commit()
        session.pop("pending_registration_email", None)
        login_user(user)
        flash("Your email is verified and your FARM BRAIN account is ready.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("auth/verify_email.html", email=email)


@auth_bp.post("/verify-email/resend")
def resend_email_otp():
    from datetime import datetime, timezone
    from werkzeug.security import generate_password_hash
    from .mailer import send_email
    email = session.get("pending_registration_email", "")
    pending = PendingRegistration.query.filter_by(email=email).first() if email else None
    if not pending:
        flash("Your registration session expired. Please start again.", "error")
        return redirect(url_for("auth.register"))
    last_sent = pending.last_sent_at
    if last_sent.tzinfo is None:
        last_sent = last_sent.replace(tzinfo=timezone.utc)
    seconds = (datetime.now(timezone.utc) - last_sent).total_seconds()
    if seconds < current_app.config.get("OTP_RESEND_SECONDS", 60):
        flash("Please wait before requesting another code.", "error")
        return redirect(url_for("auth.verify_email"))
    code = f"{secrets.randbelow(1_000_000):06d}"
    pending.otp_hash = generate_password_hash(code)
    pending.expires_at = utcnow() + timedelta(minutes=current_app.config.get("OTP_TTL_MINUTES", 10))
    pending.attempts = 0
    pending.last_sent_at = utcnow()
    try:
        send_email(email, "Your new FARM BRAIN verification code", f"Your new code is {code}. It expires in 10 minutes.")
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("We could not send a new code. Please try again later.", "error")
        return redirect(url_for("auth.verify_email"))
    if current_app.testing:
        current_app.extensions.setdefault("otp_test_codes", {})[email] = code
    elif current_app.config.get("OTP_DEV_MODE") and current_app.config.get("APP_ENV") != "production":
        flash(f"Local development OTP: {code}.", "info")
    flash("A new verification code has been sent.", "success")
    return redirect(url_for("auth.verify_email"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    from werkzeug.security import generate_password_hash
    from .mailer import send_email
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        session.pop("password_reset_user_id", None)
        # Always use the same success message so account existence is not disclosed.
        if user:
            latest = PasswordResetOTP.query.filter_by(user_id=user.id, verified_at=None).order_by(PasswordResetOTP.created_at.desc()).first()
            recently_sent = False
            if latest:
                created = latest.created_at
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                recently_sent = (datetime.now(timezone.utc) - created).total_seconds() < current_app.config.get("OTP_RESEND_SECONDS", 60)
            if recently_sent:
                # Keep the same outward response for known and unknown addresses.
                session["password_reset_user_id"] = user.id
            else:
                code = f"{secrets.randbelow(1_000_000):06d}"
                PasswordResetOTP.query.filter_by(user_id=user.id, verified_at=None).delete(synchronize_session=False)
                reset = PasswordResetOTP(
                    user_id=user.id, otp_hash=generate_password_hash(code),
                    expires_at=utcnow() + timedelta(minutes=10), attempts=0,
                )
                db.session.add(reset)
                try:
                    send_email(user.email, "FARM BRAIN password reset code", f"Your password reset code is {code}. It expires in 10 minutes.")
                    db.session.commit()
                    session["password_reset_user_id"] = user.id
                    if current_app.testing:
                        current_app.extensions.setdefault("otp_test_codes", {})[email] = code
                    elif current_app.config.get("OTP_DEV_MODE") and current_app.config.get("APP_ENV") != "production":
                        flash(f"Local development reset code: {code}.", "info")
                except Exception:
                    db.session.rollback()
                    current_app.logger.exception("Password reset email failed")
        flash("If that email is registered, a reset code has been sent. Wait before requesting another code.", "success")
        return redirect(url_for("auth.reset_password"))
    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    from werkzeug.security import check_password_hash
    user_id = session.get("password_reset_user_id")
    reset = PasswordResetOTP.query.filter_by(user_id=user_id, verified_at=None).order_by(PasswordResetOTP.created_at.desc()).first() if user_id else None
    if request.method == "POST":
        if not reset:
            flash("Start the password reset process again.", "error")
            return redirect(url_for("auth.forgot_password"))
        code = request.form.get("code", "").strip()
        password = request.form.get("password", "")
        expires = reset.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires or reset.attempts >= 5:
            db.session.delete(reset)
            db.session.commit()
            session.pop("password_reset_user_id", None)
            flash("The reset code expired or exceeded its attempt limit.", "error")
            return redirect(url_for("auth.forgot_password"))
        reset.attempts += 1
        if not code.isdigit() or len(code) != 6 or not check_password_hash(reset.otp_hash, code) or len(password) < 10:
            db.session.commit()
            flash("Check the six-digit code and use a password of at least 10 characters.", "error")
            return render_template("auth/reset_password.html"), 400
        user = db.session.get(User, user_id)
        if not user:
            abort(404)
        user.set_password(password)
        reset.verified_at = utcnow()
        db.session.commit()
        session.pop("password_reset_user_id", None)
        flash("Your password has been updated. Please sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=False)
            flash("Welcome back.", "success")
            return redirect(safe_next())
        flash("Email or password was not recognised.", "error")
    return render_template("auth/login.html")


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have signed out.", "info")
    return redirect(url_for("main.home"))


@main_bp.route("/")
def home():
    latest = Listing.query.filter_by(status="active").order_by(Listing.created_at.desc()).limit(6).all()
    counts = {division: Listing.query.filter_by(division=division, status="active").count() for division in DIVISIONS}
    return render_template("home.html", latest=latest, counts=counts, categories=CATEGORIES)


@main_bp.route("/market")
def market():
    query = Listing.query.filter_by(status="active")
    search = request.args.get("q", "").strip()[:100]
    division = request.args.get("division", "")
    category = request.args.get("category", "")
    record_type = request.args.get("type", "")
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Listing.title.ilike(like), Listing.description.ilike(like), Listing.city.ilike(like)))
    if division in DIVISIONS:
        query = query.filter_by(division=division)
    else:
        division = ""
    if category and (not division or category in CATEGORIES[division]):
        query = query.filter_by(category=category)
    else:
        category = ""
    if record_type in RECORD_TYPES:
        query = query.filter_by(record_type=record_type)
    else:
        record_type = ""
    listings = query.order_by(Listing.created_at.desc()).limit(100).all()
    categories = CATEGORIES.get(division, [])
    return render_template(
        "market.html", listings=listings, search=search, division=division,
        category=category, record_type=record_type, divisions=DIVISIONS,
        categories=categories, categories_map=CATEGORIES, record_types=RECORD_TYPES,
    )


@main_bp.route("/listing/new", methods=["GET", "POST"])
@login_required
def new_listing():
    form = request.form if request.method == "POST" else {}
    if request.method == "POST":
        division = request.form.get("division", "")
        category = request.form.get("category", "")
        record_type = request.form.get("record_type", "")
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        action = request.form.get("action", "").strip()
        transport_kind = request.form.get("transport_kind", "").strip() or None
        currency = request.form.get("currency", "INR").strip().upper()
        unit = request.form.get("unit", "").strip()[:30]
        city = request.form.get("city", "").strip()[:100]
        state = request.form.get("state", "").strip()[:100]
        country = request.form.get("country", current_user.country).strip().upper()

        errors = []
        quantity = price = None
        if division not in CATEGORIES:
            errors.append("Select a valid division.")
        elif category not in CATEGORIES[division]:
            errors.append("Select a category belonging to the chosen division.")
        if record_type not in RECORD_TYPES:
            errors.append("Choose offer/supply or requirement/demand.")
        if not title or len(title) > 140:
            errors.append("Enter a title (up to 140 characters).")
        if len(description) < 10 or len(description) > 5000:
            errors.append("Description must be between 10 and 5,000 characters.")
        if not action or action not in {"sell", "buy", "rent", "lease", "service", "job", "internship", "discovery", "availability"}:
            errors.append("Choose a valid action.")
        if currency not in CURRENCIES:
            errors.append("Choose a supported currency.")
        if country not in {"IN", "AE", "US", "GB"}:
            errors.append("Choose a supported country.")
        if division == "Agri Business" and category == "Transport":
            if transport_kind not in TRANSPORT_KINDS:
                errors.append("Choose whether this is a load request or vehicle availability.")
            else:
                # Preserve the transport distinction in both the UI and stored record.
                record_type = "requirement" if transport_kind == "load_request" else "offer"
                action = "buy" if transport_kind == "load_request" else "availability"
        else:
            transport_kind = None
        try:
            quantity = form_decimal(request.form.get("quantity"), "quantity", optional=True)
            price = form_decimal(request.form.get("price"), "price", optional=True)
        except ValueError as exc:
            errors.append(str(exc))
        if quantity is not None and quantity <= 0:
            errors.append("Quantity must be greater than zero when supplied.")
        if quantity is not None and not unit:
            errors.append("Choose a unit when you enter a quantity.")
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "listing_form.html", divisions=DIVISIONS, categories=CATEGORIES,
                currencies=CURRENCIES, transport_kinds=TRANSPORT_KINDS, form=form,
            ), 400

        # Finance and investor categories are discovery only, not brokerage or investment advice.
        if division == "Agri Business" and category == "Banks & Investors":
            action = "discovery"
        listing = Listing(
            owner_id=current_user.id, division=division, category=category,
            record_type=record_type, action=action, transport_kind=transport_kind,
            title=title, description=description, quantity=quantity, unit=unit,
            price=price, currency=currency, city=city, state=state, country=country,
        )
        db.session.add(listing)
        db.session.flush()
        photos = [item for item in request.files.getlist("photos") if item and item.filename]
        if len(photos) > 2:
            db.session.rollback()
            flash("Attach up to two listing photos (6 MB maximum each).", "error")
            return render_template(
                "listing_form.html", divisions=DIVISIONS, categories=CATEGORIES,
                currencies=CURRENCIES, transport_kinds=TRANSPORT_KINDS, form=form,
            ), 400
        if photos:
            try:
                from .uploads import save_image
                for photo in photos:
                    storage_name, original_name, size_bytes, mime_type = save_image(photo, "listings")
                    db.session.add(ListingAttachment(
                        listing_id=listing.id, uploader_id=current_user.id,
                        storage_name=storage_name, original_name=original_name,
                        mime_type=mime_type, size_bytes=size_bytes,
                    ))
            except ValueError as exc:
                db.session.rollback()
                flash(str(exc), "error")
                return render_template(
                    "listing_form.html", divisions=DIVISIONS, categories=CATEGORIES,
                    currencies=CURRENCIES, transport_kinds=TRANSPORT_KINDS, form=form,
                ), 400
        if division == "Agri Business" and category == "Transport" and transport_kind:
            origin = request.form.get("origin", "").strip()[:160]
            destination = request.form.get("destination", "").strip()[:160]
            cargo_type = request.form.get("cargo_type", "").strip()[:120]
            vehicle_type = request.form.get("vehicle_type", "").strip()[:100]
            weight_unit = request.form.get("weight_unit", "tonne").strip()[:30]
            pricing_basis = request.form.get("pricing_basis", "To be discussed").strip()[:100]
            weight_text = request.form.get("weight", "").strip()
            capacity_text = request.form.get("vehicle_capacity", "").strip()
            available_text = request.form.get("available_from", "").strip()
            try:
                weight = Decimal(weight_text) if weight_text else None
                vehicle_capacity = Decimal(capacity_text) if capacity_text else None
                from datetime import date
                available_from = date.fromisoformat(available_text) if available_text else None
                if (weight is not None and (not weight.is_finite() or weight <= 0)) or (vehicle_capacity is not None and (not vehicle_capacity.is_finite() or vehicle_capacity <= 0)):
                    raise ValueError
                if transport_kind == "load_request" and (not origin or not destination or not cargo_type):
                    raise ValueError
                if transport_kind == "vehicle_availability" and (not origin or not vehicle_type):
                    raise ValueError
            except (ValueError, InvalidOperation):
                db.session.rollback()
                flash("Complete valid transport details: origin, destination and cargo for a load; operating area and vehicle type for vehicle availability.", "error")
                return render_template(
                    "listing_form.html", divisions=DIVISIONS, categories=CATEGORIES,
                    currencies=CURRENCIES, transport_kinds=TRANSPORT_KINDS, form=form,
                ), 400
            db.session.add(TransportDetail(
                listing_id=listing.id, kind=transport_kind, origin=origin,
                destination=destination, cargo_type=cargo_type, weight=weight,
                weight_unit=weight_unit, vehicle_type=vehicle_type,
                vehicle_capacity=vehicle_capacity, available_from=available_from,
                pricing_basis=pricing_basis,
            ))
        db.session.commit()
        flash("Your listing is now visible in the marketplace. An enquiry is not a confirmed sale or booking.", "success")
        return redirect(url_for("main.listing_detail", listing_id=listing.id))

    return render_template(
        "listing_form.html", divisions=DIVISIONS, categories=CATEGORIES,
        currencies=CURRENCIES, transport_kinds=TRANSPORT_KINDS, form=form,
    )


@main_bp.route("/listing/<int:listing_id>", methods=["GET"])
def listing_detail(listing_id):
    listing = db.get_or_404(Listing, listing_id)
    if listing.status != "active" and not is_listing_owner(listing):
        abort(404)
    if listing.owner.member_profile is None:
        from .features import get_or_create_profile
        get_or_create_profile(listing.owner)
        db.session.commit()
    saved = False
    if current_user.is_authenticated:
        saved = SavedListing.query.filter_by(user_id=current_user.id, listing_id=listing.id).first() is not None
    return render_template("listing_detail.html", listing=listing, saved=saved)


@main_bp.post("/listing/<int:listing_id>/save")
@login_required
def save_listing(listing_id):
    listing = db.get_or_404(Listing, listing_id)
    existing = SavedListing.query.filter_by(user_id=current_user.id, listing_id=listing.id).first()
    if existing:
        db.session.delete(existing)
        flash("Listing removed from your saved items.", "info")
    elif listing.owner_id != current_user.id:
        db.session.add(SavedListing(user_id=current_user.id, listing_id=listing.id))
        flash("Listing saved to your dashboard.", "success")
    db.session.commit()
    return redirect(url_for("main.listing_detail", listing_id=listing.id))


@main_bp.post("/listing/<int:listing_id>/enquire")
@login_required
def enquire(listing_id):
    listing = db.get_or_404(Listing, listing_id)
    message = request.form.get("message", "").strip()
    if listing.status != "active":
        abort(400)
    if listing.owner_id == current_user.id:
        flash("You cannot send an enquiry to your own listing.", "error")
    elif len(message) < 10 or len(message) > 2000:
        flash("Write an enquiry between 10 and 2,000 characters.", "error")
    else:
        db.session.add(Enquiry(listing_id=listing.id, sender_id=current_user.id, message=message))
        db.session.commit()
        flash("Your enquiry was sent. This is a conversation lead, not a confirmed order.", "success")
    return redirect(url_for("main.listing_detail", listing_id=listing.id))


@main_bp.post("/enquiry/<int:enquiry_id>/quote")
@login_required
def send_quote(enquiry_id):
    enquiry = db.get_or_404(Enquiry, enquiry_id)
    if not is_listing_owner(enquiry.listing):
        abort(403)
    if enquiry.listing.status != "active":
        abort(400)
    terms = request.form.get("terms", "").strip()
    currency = request.form.get("currency", "INR").strip().upper()
    try:
        amount = form_decimal(request.form.get("amount"), "amount", optional=True)
        error = None
    except ValueError as exc:
        amount, error = None, str(exc)
    if error or len(terms) < 5 or len(terms) > 2000 or currency not in CURRENCIES:
        flash(error or "Enter quotation terms (5–2,000 characters) and a supported currency.", "error")
        return redirect(url_for("main.dashboard"))
    db.session.add(Quotation(enquiry_id=enquiry.id, sender_id=current_user.id, amount=amount, currency=currency, terms=terms))
    enquiry.status = "responded"
    db.session.commit()
    flash("Indicative quotation sent. It does not confirm payment, supply, delivery or a completed trade.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.post("/quotation/<int:quotation_id>/<decision>")
@login_required
def decide_quote(quotation_id, decision):
    quote = db.get_or_404(Quotation, quotation_id)
    if quote.enquiry.sender_id != current_user.id:
        abort(403)
    if decision not in {"accept-for-discussion", "decline"} or quote.status != "sent":
        abort(400)
    quote.status = "accepted_for_discussion" if decision == "accept-for-discussion" else "declined"
    db.session.commit()
    flash(
        "Quotation accepted for further discussion only; no trade, payment or delivery is confirmed." if decision == "accept-for-discussion" else "Quotation declined.",
        "info",
    )
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    my_listings = Listing.query.filter_by(owner_id=current_user.id).order_by(Listing.created_at.desc()).all()
    received = Enquiry.query.join(Listing).filter(Listing.owner_id == current_user.id).order_by(Enquiry.created_at.desc()).all()
    sent = Enquiry.query.filter_by(sender_id=current_user.id).order_by(Enquiry.created_at.desc()).all()
    saved = SavedListing.query.filter_by(user_id=current_user.id).all()
    saved_listings = [db.session.get(Listing, item.listing_id) for item in saved]
    inventory = InventoryItem.query.filter_by(user_id=current_user.id).order_by(InventoryItem.name.asc()).all()
    return render_template(
        "dashboard.html", my_listings=my_listings, received=received, sent=sent,
        saved_listings=[item for item in saved_listings if item], inventory=inventory,
    )


@main_bp.route("/community", methods=["GET", "POST"])
def community():
    if request.method == "POST":
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        body = request.form.get("body", "").strip()
        photo = request.files.get("photo")
        if len(body) > 3000 or (len(body) < 3 and (not photo or not photo.filename)):
            flash("Write a short post or attach a photo. Text must be up to 3,000 characters.", "error")
            return redirect(url_for("main.community"))
        post = CommunityPost(user_id=current_user.id, body=body or "Shared a farm photo.")
        db.session.add(post)
        db.session.flush()
        if photo and photo.filename:
            try:
                from .uploads import save_image
                from .models import PostAttachment
                storage_name, original_name, size_bytes, mime_type = save_image(photo, "community")
                db.session.add(PostAttachment(post_id=post.id, uploader_id=current_user.id,
                                              storage_name=storage_name, original_name=original_name,
                                              mime_type=mime_type, size_bytes=size_bytes))
            except ValueError as exc:
                db.session.rollback()
                flash(str(exc), "error")
                return redirect(url_for("main.community"))
        db.session.commit()
        flash("Your community post has been published.", "success")
        return redirect(url_for("main.community"))
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).limit(100).all()
    from .features import get_or_create_profile
    for post in posts:
        if post.author.member_profile is None:
            get_or_create_profile(post.author)
    post_likes = {post.id: PostLike.query.filter_by(post_id=post.id).count() for post in posts}
    post_comments = {post.id: PostComment.query.filter_by(post_id=post.id, status="active").order_by(PostComment.created_at.asc()).limit(3).all() for post in posts}
    liked_ids = set()
    if current_user.is_authenticated and posts:
        liked_ids = {row.post_id for row in PostLike.query.filter(PostLike.user_id == current_user.id, PostLike.post_id.in_([post.id for post in posts])).all()}
    post_comment_counts = {post.id: PostComment.query.filter_by(post_id=post.id, status="active").count() for post in posts}
    return render_template("community.html", posts=posts, post_likes=post_likes,
                           post_comments=post_comments, post_comment_counts=post_comment_counts,
                           liked_ids=liked_ids)


@main_bp.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        sku = request.form.get("sku", "").strip()[:80]
        unit = request.form.get("unit", "").strip()[:30]
        notes = request.form.get("notes", "").strip()[:500]
        try:
            quantity = form_decimal(request.form.get("quantity"), "quantity", optional=False)
            reorder = form_decimal(request.form.get("reorder_level", "0"), "reorder level", optional=False)
        except ValueError as exc:
            quantity, reorder = None, None
            flash(str(exc), "error")
        if quantity is not None:
            if not name or len(name) > 120 or not unit:
                flash("Enter an item name and unit.", "error")
            else:
                item = InventoryItem(user_id=current_user.id, name=name, sku=sku, unit=unit,
                                     quantity=quantity, reorder_level=reorder, notes=notes)
                db.session.add(item)
                db.session.flush()
                db.session.add(StockMovement(item_id=item.id, user_id=current_user.id, delta=quantity, note="Initial stock"))
                db.session.commit()
                flash("Inventory item saved. Use this as a basic stock register, not a full ERP.", "success")
                return redirect(url_for("main.inventory"))
    items = InventoryItem.query.filter_by(user_id=current_user.id).order_by(InventoryItem.name.asc()).all()
    return render_template("inventory.html", items=items)


@main_bp.post("/inventory/<int:item_id>/adjust")
@login_required
def adjust_inventory(item_id):
    item = db.get_or_404(InventoryItem, item_id)
    if item.user_id != current_user.id:
        abort(403)
    try:
        delta = Decimal(request.form.get("delta", ""))
        if not delta.is_finite() or delta == 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        flash("Enter a non-zero stock adjustment.", "error")
        return redirect(url_for("main.inventory"))
    new_quantity = Decimal(item.quantity) + delta
    if new_quantity < 0:
        flash("Stock cannot become negative.", "error")
        return redirect(url_for("main.inventory"))
    item.quantity = new_quantity
    db.session.add(StockMovement(item_id=item.id, user_id=current_user.id, delta=delta,
                                 note=request.form.get("note", "Manual adjustment")[:250]))
    db.session.commit()
    flash("Stock movement recorded.", "success")
    return redirect(url_for("main.inventory"))


BOARDS = {
    "transport": ("Transport exchange", "Separate load requests from vehicle availability.", "Agri Business", "Transport"),
    "careers": ("Careers and skilled work", "Discover roles and connect workers with employers.", "Farm Aid", "Farm Labour"),
    "machinery": ("Machinery and equipment", "Discover equipment offered for sale, rent or lease.", "Agri Business", "Machineries"),
    "capital": ("Finance discovery", "Find agriculture finance contacts and project discovery posts.", "Agri Business", "Banks & Investors"),
    "learning": ("Learning and internships", "Discover practical learning and internship opportunities.", "Farm Aid", "Learning & Internship"),
}


@main_bp.route("/board/<board>")
def board(board):
    config = BOARDS.get(board)
    if not config:
        abort(404)
    title, description, division, category = config
    listings = Listing.query.filter_by(division=division, category=category, status="active").order_by(Listing.created_at.desc()).limit(100).all()
    return render_template("board.html", title=title, description=description, division=division,
                           category=category, listings=listings, board=board)


@main_bp.get("/api/v1/listings")
def api_listings():
    """Small read-only API starting point for a future React/mobile client."""
    query = Listing.query.filter_by(status="active")
    division = request.args.get("division", "")
    if division in DIVISIONS:
        query = query.filter_by(division=division)
    rows = query.order_by(Listing.created_at.desc()).limit(50).all()
    return jsonify({
        "items": [{
            "id": row.id, "title": row.title, "division": row.division,
            "category": row.category, "record_type": row.record_type,
            "action": row.action, "city": row.city, "state": row.state,
            "country": row.country, "currency": row.currency,
            "price": str(row.price) if row.price is not None else None,
            "status": row.status,
        } for row in rows],
        "limit": 50,
    })
