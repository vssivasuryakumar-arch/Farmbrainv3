from datetime import datetime, timezone
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40), default="")
    city = db.Column(db.String(100), default="")
    state = db.Column(db.String(100), default="")
    country = db.Column(db.String(2), default="IN", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    capabilities = db.relationship("CapabilityAssignment", backref="user", cascade="all, delete-orphan")
    role_grants = db.relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    member_profile = db.relationship("MemberProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    @property
    def is_admin(self):
        return any(grant.role == "admin" for grant in self.role_grants)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def capability_names(self):
        return [item.capability for item in self.capabilities]


class CapabilityAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    capability = db.Column(db.String(80), nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "capability", name="uq_user_capability"),)


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    division = db.Column(db.String(40), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    record_type = db.Column(db.String(20), nullable=False, index=True)  # offer or requirement
    action = db.Column(db.String(40), nullable=False, default="sell")
    transport_kind = db.Column(db.String(30), nullable=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Numeric(14, 3), nullable=True)
    unit = db.Column(db.String(30), default="")
    price = db.Column(db.Numeric(14, 2), nullable=True)
    currency = db.Column(db.String(3), default="INR", nullable=False)
    city = db.Column(db.String(100), default="")
    state = db.Column(db.String(100), default="")
    country = db.Column(db.String(2), default="IN", nullable=False)
    status = db.Column(db.String(20), default="active", nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    owner = db.relationship("User", backref=db.backref("listings", lazy=True))
    enquiries = db.relationship("Enquiry", backref="listing", cascade="all, delete-orphan")

    @property
    def is_discovery_only(self):
        return self.division == "Agri Business" and self.category == "Banks & Investors"

    @property
    def safety_note(self):
        if self.is_discovery_only:
            return "Discovery and enquiry only. FARM BRAIN does not arrange finance or provide investment advice."
        if self.category == "Veterinarian":
            return "A directory/enquiry listing only. This is not diagnosis, emergency care or credential verification."
        if self.category == "Transport":
            return "Transport discovery and enquiry only. No freight booking or delivery confirmation is provided here."
        return "Contact the listing owner to clarify product details, terms and availability."


class Enquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(24), default="new", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    sender = db.relationship("User", foreign_keys=[sender_id])
    quotations = db.relationship("Quotation", backref="enquiry", cascade="all, delete-orphan")


class Quotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.Integer, db.ForeignKey("enquiry.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=True)
    currency = db.Column(db.String(3), nullable=False, default="INR")
    terms = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="sent")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    sender = db.relationship("User", foreign_keys=[sender_id])


class SavedListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "listing_id", name="uq_saved_listing"),)


class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    author = db.relationship("User", backref=db.backref("community_posts", lazy=True))


class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(80), default="")
    quantity = db.Column(db.Numeric(14, 3), nullable=False, default=Decimal("0"))
    unit = db.Column(db.String(30), nullable=False)
    reorder_level = db.Column(db.Numeric(14, 3), nullable=False, default=Decimal("0"))
    notes = db.Column(db.String(500), default="")
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class StockMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("inventory_item.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    delta = db.Column(db.Numeric(14, 3), nullable=False)
    note = db.Column(db.String(250), default="")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

# ---------------------------------------------------------------------------
# FARM BRAIN v2 operational modules. These are new tables so the original MVP
# tables remain backward compatible while users can gradually migrate.
# ---------------------------------------------------------------------------

class MemberProfile(db.Model):
    __tablename__ = "member_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    handle = db.Column(db.String(60), nullable=False, unique=True, index=True)
    bio = db.Column(db.String(1200), default="", nullable=False)
    avatar_url = db.Column(db.String(500), default="", nullable=False)
    cover_url = db.Column(db.String(500), default="", nullable=False)
    farm_name = db.Column(db.String(140), default="", nullable=False)
    farm_type = db.Column(db.String(100), default="", nullable=False)
    farm_area = db.Column(db.Numeric(12, 3), nullable=True)
    farm_area_unit = db.Column(db.String(30), default="acre", nullable=False)
    primary_crops = db.Column(db.String(500), default="", nullable=False)
    farming_methods = db.Column(db.String(500), default="", nullable=False)
    soil_type = db.Column(db.String(100), default="", nullable=False)
    irrigation = db.Column(db.String(100), default="", nullable=False)
    website = db.Column(db.String(300), default="", nullable=False)
    plan_code = db.Column(db.String(40), default="FARMER_BASIC_FREE", nullable=False)
    visibility = db.Column(db.String(20), default="public", nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    user = db.relationship("User", back_populates="member_profile")


class BusinessProfile(db.Model):
    __tablename__ = "business_profile"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    name = db.Column(db.String(160), nullable=False)
    business_type = db.Column(db.String(100), default="", nullable=False)
    description = db.Column(db.String(2000), default="", nullable=False)
    website = db.Column(db.String(300), default="", nullable=False)
    public_phone = db.Column(db.String(40), default="", nullable=False)
    city = db.Column(db.String(100), default="", nullable=False)
    state = db.Column(db.String(100), default="", nullable=False)
    country = db.Column(db.String(2), default="IN", nullable=False)
    verification_status = db.Column(db.String(24), default="not_submitted", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class UserRole(db.Model):
    __tablename__ = "user_role"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    role = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    user = db.relationship("User", back_populates="role_grants")
    __table_args__ = (db.UniqueConstraint("user_id", "role", name="uq_user_role"),)


class ProfileFollow(db.Model):
    __tablename__ = "profile_follow"
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (db.UniqueConstraint("follower_id", "followed_id", name="uq_profile_follow"),
                      db.CheckConstraint("follower_id != followed_id", name="ck_profile_follow_not_self"))


class PostLike(db.Model):
    __tablename__ = "post_like"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("community_post.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (db.UniqueConstraint("post_id", "user_id", name="uq_post_like"),)


class PostComment(db.Model):
    __tablename__ = "post_comment"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("community_post.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    body = db.Column(db.String(1200), nullable=False)
    status = db.Column(db.String(20), default="active", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    author = db.relationship("User")


class ContentReport(db.Model):
    __tablename__ = "content_report"
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = db.Column(db.String(24), nullable=False, index=True)  # listing, post, comment, profile
    target_id = db.Column(db.Integer, nullable=False, index=True)
    reason = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(1200), default="", nullable=False)
    status = db.Column(db.String(20), default="open", nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    reporter = db.relationship("User", foreign_keys=[reporter_id])
    reviewer = db.relationship("User", foreign_keys=[reviewer_id])


class AdminAudit(db.Model):
    __tablename__ = "admin_audit"
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    action = db.Column(db.String(80), nullable=False)
    target_type = db.Column(db.String(24), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(1200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    actor = db.relationship("User")


class TransportDetail(db.Model):
    __tablename__ = "transport_detail"
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    kind = db.Column(db.String(30), nullable=False)  # load_request / vehicle_availability
    origin = db.Column(db.String(160), default="", nullable=False)
    destination = db.Column(db.String(160), default="", nullable=False)
    cargo_type = db.Column(db.String(120), default="", nullable=False)
    weight = db.Column(db.Numeric(14, 3), nullable=True)
    weight_unit = db.Column(db.String(30), default="tonne", nullable=False)
    vehicle_type = db.Column(db.String(100), default="", nullable=False)
    vehicle_capacity = db.Column(db.Numeric(14, 3), nullable=True)
    available_from = db.Column(db.Date, nullable=True)
    pricing_basis = db.Column(db.String(100), default="To be discussed", nullable=False)
    listing = db.relationship("Listing", backref=db.backref("transport_detail", uselist=False, cascade="all, delete-orphan"))


class CropCycle(db.Model):
    __tablename__ = "crop_cycle"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    crop = db.Column(db.String(100), nullable=False)
    variety = db.Column(db.String(100), default="", nullable=False)
    season = db.Column(db.String(80), default="", nullable=False)
    area = db.Column(db.Numeric(12, 3), nullable=True)
    area_unit = db.Column(db.String(30), default="acre", nullable=False)
    planted_on = db.Column(db.Date, nullable=True)
    expected_harvest = db.Column(db.Date, nullable=True)
    notes = db.Column(db.String(1200), default="", nullable=False)
    status = db.Column(db.String(24), default="planned", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)


class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    message = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(500), default="", nullable=False)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

# ---------------------------------------------------------------------------
# Prototype v3: email verification, media sharing, direct messages and
# Magppliv smart aquaponics management. New tables preserve earlier data.
# ---------------------------------------------------------------------------

class PendingRegistration(db.Model):
    __tablename__ = "pending_registration"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40), default="", nullable=False)
    city = db.Column(db.String(100), default="", nullable=False)
    state = db.Column(db.String(100), default="", nullable=False)
    country = db.Column(db.String(2), default="IN", nullable=False)
    capabilities_json = db.Column(db.Text, nullable=False)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    last_sent_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class PasswordResetOTP(db.Model):
    __tablename__ = "password_reset_otp"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    verified_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    user = db.relationship("User")


class PostAttachment(db.Model):
    __tablename__ = "post_attachment"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("community_post.id", ondelete="CASCADE"), nullable=False, index=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    storage_name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    post = db.relationship("CommunityPost", backref=db.backref("attachments", cascade="all, delete-orphan"))
    uploader = db.relationship("User")


class ListingAttachment(db.Model):
    __tablename__ = "listing_attachment"
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id", ondelete="CASCADE"), nullable=False, index=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    storage_name = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    listing = db.relationship("Listing", backref=db.backref("attachments", cascade="all, delete-orphan"))
    uploader = db.relationship("User")


class DirectMessage(db.Model):
    __tablename__ = "direct_message"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    body = db.Column(db.String(3000), default="", nullable=False)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])
    attachments = db.relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")
    __table_args__ = (db.CheckConstraint("sender_id != recipient_id", name="ck_message_not_self"),)


class MessageAttachment(db.Model):
    __tablename__ = "message_attachment"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("direct_message.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    message = db.relationship("DirectMessage", back_populates="attachments")


class AquaponicsFarm(db.Model):
    __tablename__ = "aquaponics_farm"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    country = db.Column(db.String(2), nullable=False)
    mode = db.Column(db.String(24), nullable=False)  # india_rnd / uae_pilot
    currency = db.Column(db.String(3), nullable=False)  # INR / AED
    partner_name = db.Column(db.String(160), default="", nullable=False)
    location = db.Column(db.String(200), default="", nullable=False)
    status = db.Column(db.String(32), default="planning", nullable=False)
    notes = db.Column(db.String(2000), default="", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    owner = db.relationship("User")
    members = db.relationship("AquaponicsMembership", back_populates="farm", cascade="all, delete-orphan")
    systems = db.relationship("AquaponicsSystem", back_populates="farm", cascade="all, delete-orphan")


class AquaponicsMembership(db.Model):
    __tablename__ = "aquaponics_membership"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("aquaponics_farm.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    role = db.Column(db.String(40), nullable=False, default="operator")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    farm = db.relationship("AquaponicsFarm", back_populates="members")
    user = db.relationship("User")
    __table_args__ = (db.UniqueConstraint("farm_id", "user_id", name="uq_aqua_farm_user"),)


class AquaponicsSystem(db.Model):
    __tablename__ = "aquaponics_system"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("aquaponics_farm.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    configuration_json = db.Column(db.Text, default="{}", nullable=False)
    # Thresholds are opt-in farm-specific configuration. Null means not set.
    ph_min = db.Column(db.Float, nullable=True)
    ph_max = db.Column(db.Float, nullable=True)
    temperature_min_c = db.Column(db.Float, nullable=True)
    temperature_max_c = db.Column(db.Float, nullable=True)
    dissolved_oxygen_min_mg_l = db.Column(db.Float, nullable=True)
    ammonia_max_mg_l = db.Column(db.Float, nullable=True)
    nitrite_max_mg_l = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    farm = db.relationship("AquaponicsFarm", back_populates="systems")
    tanks = db.relationship("AquaponicsTank", back_populates="system", cascade="all, delete-orphan")


class AquaponicsTank(db.Model):
    __tablename__ = "aquaponics_tank"
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey("aquaponics_system.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(100), default="", nullable=False)
    stocked_count = db.Column(db.Integer, nullable=False, default=0)
    current_count = db.Column(db.Integer, nullable=False, default=0)
    average_weight_g = db.Column(db.Float, nullable=True)
    volume_litres = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(1000), default="", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    system = db.relationship("AquaponicsSystem", back_populates="tanks")

    @property
    def estimated_biomass_kg(self):
        if self.average_weight_g is None:
            return None
        return round(self.current_count * self.average_weight_g / 1000.0, 3)


class AquaponicsWaterReading(db.Model):
    __tablename__ = "aquaponics_water_reading"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("aquaponics_farm.id", ondelete="CASCADE"), nullable=False, index=True)
    system_id = db.Column(db.Integer, db.ForeignKey("aquaponics_system.id", ondelete="CASCADE"), nullable=False, index=True)
    tank_id = db.Column(db.Integer, db.ForeignKey("aquaponics_tank.id", ondelete="SET NULL"), nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    source = db.Column(db.String(16), nullable=False, default="manual")  # manual only in Phase 1
    temperature_c = db.Column(db.Float, nullable=True)
    ph = db.Column(db.Float, nullable=True)
    dissolved_oxygen_mg_l = db.Column(db.Float, nullable=True)
    ammonia_mg_l = db.Column(db.Float, nullable=True)
    nitrite_mg_l = db.Column(db.Float, nullable=True)
    nitrate_mg_l = db.Column(db.Float, nullable=True)
    ec_ms_cm = db.Column(db.Float, nullable=True)
    water_level_percent = db.Column(db.Float, nullable=True)
    flow_l_min = db.Column(db.Float, nullable=True)
    alkalinity_mg_l = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(1200), default="", nullable=False)
    recorded_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    recorded_user = db.relationship("User")
    tank = db.relationship("AquaponicsTank")


class AquaponicsFishLog(db.Model):
    __tablename__ = "aquaponics_fish_log"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("aquaponics_farm.id", ondelete="CASCADE"), nullable=False, index=True)
    tank_id = db.Column(db.Integer, db.ForeignKey("aquaponics_tank.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    log_type = db.Column(db.String(24), nullable=False)  # feed / mortality / sample / harvest
    quantity_kg = db.Column(db.Float, nullable=True)
    fish_count = db.Column(db.Integer, nullable=True)
    average_weight_g = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(1200), default="", nullable=False)
    logged_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    tank = db.relationship("AquaponicsTank")
    user = db.relationship("User")


class AquaponicsCrop(db.Model):
    __tablename__ = "aquaponics_crop"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("aquaponics_farm.id", ondelete="CASCADE"), nullable=False, index=True)
    system_id = db.Column(db.Integer, db.ForeignKey("aquaponics_system.id", ondelete="CASCADE"), nullable=False, index=True)
    crop = db.Column(db.String(100), nullable=False)
    variety = db.Column(db.String(100), default="", nullable=False)
    growing_method = db.Column(db.String(40), nullable=False, default="DWC")
    plant_count = db.Column(db.Integer, nullable=False, default=0)
    planted_on = db.Column(db.Date, nullable=True)
    expected_harvest = db.Column(db.Date, nullable=True)
    actual_harvest_kg = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(24), default="growing", nullable=False)
    notes = db.Column(db.String(1200), default="", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class AquaponicsExperiment(db.Model):
    __tablename__ = "aquaponics_experiment"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("aquaponics_farm.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    objective = db.Column(db.String(2000), nullable=False)
    hypothesis = db.Column(db.String(1500), default="", nullable=False)
    test_group = db.Column(db.String(500), default="", nullable=False)
    control_group = db.Column(db.String(500), default="", nullable=False)
    status = db.Column(db.String(24), default="planned", nullable=False)
    observations = db.Column(db.Text, default="", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    creator = db.relationship("User")


class AquaponicsFinanceEntry(db.Model):
    __tablename__ = "aquaponics_finance_entry"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("aquaponics_farm.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    entry_type = db.Column(db.String(12), nullable=False)  # expense / revenue
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    description = db.Column(db.String(1200), default="", nullable=False)
    entry_date = db.Column(db.Date, nullable=False, default=lambda: utcnow().date())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    user = db.relationship("User")


class AquaponicsAlert(db.Model):
    __tablename__ = "aquaponics_alert"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("aquaponics_farm.id", ondelete="CASCADE"), nullable=False, index=True)
    reading_id = db.Column(db.Integer, db.ForeignKey("aquaponics_water_reading.id", ondelete="CASCADE"), nullable=False)
    metric = db.Column(db.String(60), nullable=False)
    severity = db.Column(db.String(16), nullable=False)
    measured_value = db.Column(db.Float, nullable=False)
    threshold_text = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    recommended_action = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    reading = db.relationship("AquaponicsWaterReading")
