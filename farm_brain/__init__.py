import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import current_user
from sqlalchemy import text

from .config import Config
from .extensions import csrf, db, login_manager
from .models import MemberProfile, User
from .routes import auth_bp, main_bp
from .features import features_bp
from .messaging import messaging_bp, media_bp
from .aquaponics import aqua_bp
from .models import UserRole


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if (not app.config.get("SECRET_KEY") or app.config.get("SECRET_KEY") == "replace-with-a-long-random-secret") and os.getenv("APP_ENV", "development").lower() == "production":
        raise RuntimeError("Set SECRET_KEY in the production environment before starting FARM BRAIN.")
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY") or "local-development-only-change-me"

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(features_bp)
    app.register_blueprint(messaging_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(aqua_bp)

    @app.context_processor
    def inject_globals():
        return {"current_user": current_user}

    @app.get("/healthz")
    def healthz():
        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ok", "service": "farm-brain"}, 200
        except Exception:
            db.session.rollback()
            return {"status": "database_unavailable", "service": "farm-brain"}, 503

    @app.get("/manifest.webmanifest")
    def pwa_manifest():
        return app.send_static_file("manifest.webmanifest")

    @app.get("/service-worker.js")
    def service_worker():
        response = app.send_static_file("service-worker.js")
        response.headers["Service-Worker-Allowed"] = "/"
        response.headers["Cache-Control"] = "no-cache"
        return response

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        return response

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", title="Page not found", message="That page does not exist."), 404

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("error.html", title="Access not allowed", message="You do not have permission to perform this action."), 403

    @app.errorhandler(400)
    def bad_request(_error):
        return render_template("error.html", title="Request could not be completed", message="Please review the form and try again."), 400

    @app.errorhandler(413)
    def too_large(_error):
        return render_template("error.html", title="File too large", message="The request is larger than this demo allows."), 413

    with app.app_context():
        db.create_all()
        # Only the deployment owner's configured email receives admin access.
        # Never accept an admin role from a public registration form.
        # Backfill public profiles for accounts created by an earlier FARM BOOK/FARM BRAIN build.
        from .features import make_handle
        existing_users = (User.query.outerjoin(MemberProfile)
                          .filter(MemberProfile.id.is_(None)).all())
        for member in existing_users:
            if member.member_profile is None:
                is_farmer = "Farmer / Grower" in (member.capability_names or [])
                db.session.add(MemberProfile(
                    user_id=member.id,
                    handle=make_handle(member.name, member.id),
                    plan_code="FARMER_BASIC_FREE" if is_farmer else "COMMUNITY_FREE",
                ))
        admin_email = app.config.get("ADMIN_EMAIL", "").strip().lower()
        if admin_email:
            owner = User.query.filter_by(email=admin_email).first()
            if owner and not any(grant.role == "admin" for grant in owner.role_grants):
                db.session.add(UserRole(user_id=owner.id, role="admin"))
        db.session.commit()

    return app
