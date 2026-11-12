"""Social profiles, transport finder, crop records and moderation controls."""
from datetime import date
from decimal import Decimal, InvalidOperation
import re
from urllib.parse import urlparse, urlsplit

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .extensions import db
from .models import (
    AdminAudit, BusinessProfile, CommunityPost, ContentReport, CropCycle,
    MemberProfile, Notification, PostComment, PostLike, ProfileFollow,
    TransportDetail, UserRole, utcnow,
)

features_bp = Blueprint("features", __name__)


def make_handle(name: str, user_id: int) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", (name or "farmer").lower()).strip("-")[:42] or "farmer"
    return f"{base}-{user_id}"


def get_or_create_profile(user):
    profile = MemberProfile.query.filter_by(user_id=user.id).first()
    if profile:
        return profile
    farmer = "Farmer / Grower" in (user.capability_names or [])
    profile = MemberProfile(
        user_id=user.id,
        handle=make_handle(user.name, user.id),
        plan_code="FARMER_BASIC_FREE" if farmer else "COMMUNITY_FREE",
    )
    db.session.add(profile)
    db.session.flush()
    return profile



def safe_referrer(default_endpoint="main.home"):
    """Use only a same-origin referrer; never redirect a user off-site."""
    candidate = request.referrer or ""
    if candidate.startswith("/") and not candidate.startswith("//") and "\\" not in candidate:
        return candidate
    try:
        parsed = urlsplit(candidate)
        host = urlsplit(request.host_url)
        if parsed.scheme == host.scheme and parsed.netloc == host.netloc and parsed.path.startswith("/"):
            return parsed.path + (("?" + parsed.query) if parsed.query else "") + (("#" + parsed.fragment) if parsed.fragment else "")
    except ValueError:
        pass
    return url_for(default_endpoint)


def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)


def safe_http_url(value: str) -> str:
    value = (value or "").strip()[:500]
    if not value:
        return ""
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""


@features_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = get_or_create_profile(current_user)
    if request.method == "POST":
        profile.bio = request.form.get("bio", "").strip()[:1200]
        profile.avatar_url = safe_http_url(request.form.get("avatar_url")) or profile.avatar_url
        profile.cover_url = safe_http_url(request.form.get("cover_url")) or profile.cover_url
        avatar = request.files.get("avatar_file")
        cover = request.files.get("cover_file")
        if avatar and avatar.filename:
            try:
                from .uploads import save_image
                stored, _name, _size, _mime = save_image(avatar, "profiles")
                profile.avatar_url = stored if stored.startswith("https://") else url_for("media.public_media", storage_name=stored)
            except ValueError as exc:
                flash(str(exc), "error")
                return render_template("profile_edit.html", profile=profile), 400
        if cover and cover.filename:
            try:
                from .uploads import save_image
                stored, _name, _size, _mime = save_image(cover, "profiles")
                profile.cover_url = stored if stored.startswith("https://") else url_for("media.public_media", storage_name=stored)
            except ValueError as exc:
                flash(str(exc), "error")
                return render_template("profile_edit.html", profile=profile), 400
        profile.farm_name = request.form.get("farm_name", "").strip()[:140]
        profile.farm_type = request.form.get("farm_type", "").strip()[:100]
        profile.primary_crops = request.form.get("primary_crops", "").strip()[:500]
        profile.farming_methods = request.form.get("farming_methods", "").strip()[:500]
        profile.soil_type = request.form.get("soil_type", "").strip()[:100]
        profile.irrigation = request.form.get("irrigation", "").strip()[:100]
        profile.website = safe_http_url(request.form.get("website"))
        try:
            area_text = request.form.get("farm_area", "").strip()
            profile.farm_area = Decimal(area_text) if area_text else None
            if profile.farm_area is not None and (not profile.farm_area.is_finite() or profile.farm_area < 0):
                raise ValueError
        except (TypeError, ValueError, InvalidOperation):
            flash("Farm area must be a non-negative number.", "error")
            return render_template("profile_edit.html", profile=profile), 400
        profile.farm_area_unit = request.form.get("farm_area_unit", "acre").strip()[:30] or "acre"
        db.session.commit()
        flash("Your FARM BRAIN profile has been updated.", "success")
        return redirect(url_for("features.profile", handle=profile.handle))
    return render_template("profile_edit.html", profile=profile)


@features_bp.get("/profile/<handle>")
def profile(handle):
    profile = MemberProfile.query.filter_by(handle=handle.lower()).first_or_404()
    user = profile.user
    if profile.visibility != "public" and not (current_user.is_authenticated and (current_user.id == user.id or current_user.is_admin)):
        abort(404)
    posts = CommunityPost.query.filter_by(user_id=user.id).order_by(CommunityPost.created_at.desc()).limit(30).all()
    followers = ProfileFollow.query.filter_by(followed_id=user.id).count()
    following = ProfileFollow.query.filter_by(follower_id=user.id).count()
    is_following = False
    if current_user.is_authenticated and current_user.id != user.id:
        is_following = ProfileFollow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first() is not None
    business = BusinessProfile.query.filter_by(owner_id=user.id).order_by(BusinessProfile.created_at.desc()).first()
    likes = {post.id: PostLike.query.filter_by(post_id=post.id).count() for post in posts}
    comments = {post.id: PostComment.query.filter_by(post_id=post.id, status="active").count() for post in posts}
    return render_template("profile.html", profile=profile, member=user, posts=posts,
                           followers=followers, following=following, is_following=is_following,
                           business=business, likes=likes, comments=comments)


@features_bp.post("/profile/<handle>/follow")
@login_required
def follow_profile(handle):
    profile = MemberProfile.query.filter_by(handle=handle.lower()).first_or_404()
    if profile.user_id == current_user.id:
        abort(400)
    existing = ProfileFollow.query.filter_by(follower_id=current_user.id, followed_id=profile.user_id).first()
    if existing:
        db.session.delete(existing)
        flash("You unfollowed this member.", "info")
    else:
        db.session.add(ProfileFollow(follower_id=current_user.id, followed_id=profile.user_id))
        db.session.add(Notification(user_id=profile.user_id,
                                   message=f"{current_user.name} started following your profile.",
                                   url=url_for("features.profile", handle=get_or_create_profile(current_user).handle)))
        flash("You are now following this member.", "success")
    db.session.commit()
    return redirect(url_for("features.profile", handle=handle))


@features_bp.post("/posts/<int:post_id>/like")
@login_required
def like_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    existing = PostLike.query.filter_by(post_id=post.id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(PostLike(post_id=post.id, user_id=current_user.id))
    db.session.commit()
    return redirect(safe_referrer("main.community"))


@features_bp.post("/posts/<int:post_id>/comment")
@login_required
def comment_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    body = request.form.get("body", "").strip()
    if len(body) < 2 or len(body) > 1200:
        flash("Comments must be between 2 and 1,200 characters.", "error")
    else:
        db.session.add(PostComment(post_id=post.id, user_id=current_user.id, body=body))
        db.session.add(Notification(user_id=post.user_id,
                                    message=f"{current_user.name} commented on your FARM BRAIN post.",
                                    url=url_for("main.community")))
        db.session.commit()
        flash("Comment added.", "success")
    return redirect(safe_referrer("main.community"))


@features_bp.post("/report")
@login_required
def report_content():
    target_type = request.form.get("target_type", "").strip()
    target_id = request.form.get("target_id", type=int)
    reason = request.form.get("reason", "other").strip()[:80]
    details = request.form.get("details", "").strip()[:1200]
    if target_type not in {"listing", "post", "comment", "profile"} or not target_id or target_id < 1:
        abort(400)
    if target_type == "listing":
        from .models import Listing
        target_exists = db.session.get(Listing, target_id) is not None
    elif target_type == "post":
        target_exists = db.session.get(CommunityPost, target_id) is not None
    elif target_type == "comment":
        target_exists = db.session.get(PostComment, target_id) is not None
    else:
        from .models import User
        target_exists = db.session.get(User, target_id) is not None
    if not target_exists:
        abort(404)
    db.session.add(ContentReport(reporter_id=current_user.id, target_type=target_type,
                                 target_id=target_id, reason=reason, details=details))
    db.session.commit()
    flash("Report submitted for moderator review.", "success")
    return redirect(safe_referrer("main.home"))


@features_bp.get("/admin/moderation")
@login_required
def moderation():
    require_admin()
    reports = ContentReport.query.order_by(ContentReport.created_at.desc()).limit(200).all()
    audits = AdminAudit.query.order_by(AdminAudit.created_at.desc()).limit(100).all()
    return render_template("moderation.html", reports=reports, audits=audits)


@features_bp.post("/admin/moderation/<int:report_id>/<action>")
@login_required
def moderation_action(report_id, action):
    require_admin()
    report = ContentReport.query.get_or_404(report_id)
    if action not in {"resolve", "dismiss", "hide"}:
        abort(400)
    reason = request.form.get("reason", "").strip()[:1200]
    if len(reason) < 5:
        flash("Enter a moderation reason (at least 5 characters).", "error")
        return redirect(url_for("features.moderation"))
    report.status = "resolved" if action in {"resolve", "hide"} else "dismissed"
    report.reviewed_at = utcnow()
    report.reviewer_id = current_user.id
    if action == "hide":
        if report.target_type == "listing":
            from .models import Listing
            item = db.session.get(Listing, report.target_id)
            if item:
                item.status = "removed"
        elif report.target_type == "post":
            item = db.session.get(CommunityPost, report.target_id)
            if item:
                PostLike.query.filter_by(post_id=item.id).delete(synchronize_session=False)
                PostComment.query.filter_by(post_id=item.id).delete(synchronize_session=False)
                db.session.delete(item)
        elif report.target_type == "comment":
            item = db.session.get(PostComment, report.target_id)
            if item:
                item.status = "removed"
        elif report.target_type == "profile":
            item = MemberProfile.query.filter_by(user_id=report.target_id).first()
            if item:
                item.visibility = "hidden"
    db.session.add(AdminAudit(actor_id=current_user.id, action=f"report_{action}",
                              target_type=report.target_type, target_id=report.target_id,
                              reason=reason))
    db.session.commit()
    flash("Moderation decision saved and recorded in the audit log.", "success")
    return redirect(url_for("features.moderation"))


@features_bp.route("/business/profile", methods=["GET", "POST"])
@login_required
def business_profile_edit():
    business = BusinessProfile.query.filter_by(owner_id=current_user.id).first()
    if request.method == "POST":
        if not business:
            business = BusinessProfile(owner_id=current_user.id, name="")
            db.session.add(business)
        business.name = request.form.get("name", "").strip()[:160]
        business.business_type = request.form.get("business_type", "").strip()[:100]
        business.description = request.form.get("description", "").strip()[:2000]
        business.website = safe_http_url(request.form.get("website"))
        business.public_phone = request.form.get("public_phone", "").strip()[:40]
        business.city = request.form.get("city", "").strip()[:100]
        business.state = request.form.get("state", "").strip()[:100]
        business.country = request.form.get("country", current_user.country).strip().upper()[:2]
        if len(business.name) < 2 or business.country not in {"IN", "AE", "US", "GB"}:
            flash("Enter a business name and a supported country.", "error")
            return render_template("business_edit.html", business=business), 400
        business.verification_status = "not_submitted"
        db.session.commit()
        flash("Business profile saved. It is not verified until our review process is completed.", "success")
        return redirect(url_for("features.business_profile_edit"))
    return render_template("business_edit.html", business=business)


@features_bp.route("/transport")
def transport():
    from .models import Listing
    kind = request.args.get("kind", "")
    query = Listing.query.filter_by(division="Agri Business", category="Transport", status="active")
    if kind in {"load_request", "vehicle_availability"}:
        query = query.filter(Listing.transport_kind == kind)
    listings = query.order_by(Listing.created_at.desc()).limit(100).all()
    return render_template("transport.html", listings=listings, kind=kind)


@features_bp.route("/farm-records", methods=["GET", "POST"])
@login_required
def farm_records():
    if request.method == "POST":
        crop = request.form.get("crop", "").strip()[:100]
        variety = request.form.get("variety", "").strip()[:100]
        season = request.form.get("season", "").strip()[:80]
        area_unit = request.form.get("area_unit", "acre").strip()[:30]
        notes = request.form.get("notes", "").strip()[:1200]
        try:
            area_text = request.form.get("area", "").strip()
            area = Decimal(area_text) if area_text else None
            if area is not None and (not area.is_finite() or area <= 0):
                raise ValueError
            planted_on = date.fromisoformat(request.form["planted_on"]) if request.form.get("planted_on") else None
            expected_harvest = date.fromisoformat(request.form["expected_harvest"]) if request.form.get("expected_harvest") else None
            if planted_on and expected_harvest and expected_harvest < planted_on:
                raise ValueError
        except (ValueError, KeyError, InvalidOperation):
            flash("Check area and dates. Harvest date must not be earlier than planting date.", "error")
            return redirect(url_for("features.farm_records"))
        if len(crop) < 2:
            flash("Enter a crop name.", "error")
            return redirect(url_for("features.farm_records"))
        db.session.add(CropCycle(user_id=current_user.id, crop=crop, variety=variety,
                                 season=season, area=area, area_unit=area_unit,
                                 planted_on=planted_on, expected_harvest=expected_harvest,
                                 notes=notes))
        db.session.commit()
        flash("Farm crop record saved. This is a record book, not an agronomy recommendation.", "success")
        return redirect(url_for("features.farm_records"))
    cycles = CropCycle.query.filter_by(user_id=current_user.id).order_by(CropCycle.created_at.desc()).all()
    return render_template("farm_records.html", cycles=cycles)


@features_bp.post("/farm-records/<int:cycle_id>/status")
@login_required
def update_crop_status(cycle_id):
    cycle = CropCycle.query.get_or_404(cycle_id)
    if cycle.user_id != current_user.id:
        abort(403)
    status = request.form.get("status", "")
    if status not in {"planned", "growing", "harvested", "cancelled"}:
        abort(400)
    cycle.status = status
    db.session.commit()
    return redirect(url_for("features.farm_records"))


@features_bp.get("/farm-intelligence")
def farm_intelligence():
    mandi_configured = bool(current_app.config.get("OGD_API_KEY") and current_app.config.get("OGD_MANDI_RESOURCE_ID"))
    soil_configured = bool(current_app.config.get("SOIL_HEALTH_API_TOKEN"))
    mandi_result = None
    state = request.args.get("state", "").strip()[:80]
    commodity = request.args.get("commodity", "").strip()[:100]
    if request.args.get("search") == "1":
        from .data_integrations import get_ogd_mandi_prices
        mandi_result = get_ogd_mandi_prices(
            current_app.config.get("OGD_API_KEY", ""),
            current_app.config.get("OGD_MANDI_RESOURCE_ID", ""),
            current_app.config.get("OGD_API_BASE_URL", "https://data.gov.in/api/datastore/resource.json"),
            state=state, commodity=commodity, limit=50,
        )
    return render_template("farm_intelligence.html", mandi_configured=mandi_configured,
                           soil_configured=soil_configured, mandi_result=mandi_result,
                           state=state, commodity=commodity)


@features_bp.get("/notifications")
@login_required
def notifications():
    items = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(100).all()
    for item in items:
        if item.read_at is None:
            item.read_at = utcnow()
    db.session.commit()
    return render_template("notifications.html", items=items)


@features_bp.get("/api/v1/system/modules")
def modules_api():
    return jsonify({
        "brand": "FARM BRAIN",
        "country_default": "IN",
        "farmer_basic_plan": "free",
        "modules": [
            {"code": "profiles", "status": "available"},
            {"code": "community", "status": "available"},
            {"code": "marketplace", "status": "available"},
            {"code": "requirements_and_enquiries", "status": "available"},
            {"code": "transport_discovery", "status": "available"},
            {"code": "inventory_register", "status": "available"},
            {"code": "crop_records", "status": "available"},
            {"code": "moderation", "status": "available_configured_admin_only"},
            {"code": "government_mandi_data", "status": "configured" if current_app.config.get("OGD_API_KEY") and current_app.config.get("OGD_MANDI_RESOURCE_ID") else "not_configured"},
            {"code": "soil_health_card_api", "status": "credential_and_authorisation_required"},
            {"code": "imd_agromet", "status": "official_bulletins_linked_api_access_not_verified"},
        ],
    })


@features_bp.get("/api/v1/markets/mandi")
def mandi_api():
    from .data_integrations import get_ogd_mandi_prices
    result = get_ogd_mandi_prices(
        current_app.config.get("OGD_API_KEY", ""),
        current_app.config.get("OGD_MANDI_RESOURCE_ID", ""),
        current_app.config.get("OGD_API_BASE_URL", "https://data.gov.in/api/datastore/resource.json"),
        state=request.args.get("state", ""), commodity=request.args.get("commodity", ""),
        limit=request.args.get("limit", 25, type=int),
    )
    code = 200 if result.get("available") else 503
    return jsonify(result), code


@features_bp.get("/api/v1/transport")
def transport_api():
    from .models import Listing
    rows = Listing.query.filter_by(division="Agri Business", category="Transport", status="active").order_by(Listing.created_at.desc()).limit(100).all()
    return jsonify({"items": [{
        "id": row.id, "title": row.title, "kind": row.transport_detail.kind if row.transport_detail else row.transport_kind,
        "origin": row.transport_detail.origin if row.transport_detail else row.city,
        "destination": row.transport_detail.destination if row.transport_detail else "",
        "cargo_type": row.transport_detail.cargo_type if row.transport_detail else "",
        "vehicle_type": row.transport_detail.vehicle_type if row.transport_detail else "",
        "city": row.city, "state": row.state, "country": row.country,
        "detail_url": url_for("main.listing_detail", listing_id=row.id),
    } for row in rows]})


@features_bp.get("/photos")
def photos_gallery():
    """Public photo feed sourced from community post attachments."""
    from .models import PostAttachment
    photos = PostAttachment.query.join(CommunityPost).filter(CommunityPost.user_id == PostAttachment.uploader_id).order_by(PostAttachment.created_at.desc()).limit(100).all()
    return render_template("photos.html", photos=photos)
