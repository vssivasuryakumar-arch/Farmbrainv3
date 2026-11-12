"""Create clearly labelled example listings for a local development database only."""
import os
from farm_brain import create_app
from farm_brain.extensions import db
from farm_brain.models import CapabilityAssignment, Listing, MemberProfile, User

if os.getenv("APP_ENV", "development").lower() == "production":
    raise SystemExit("Refusing to seed demo accounts in production. Use the live registration flow instead.")

app = create_app()

with app.app_context():
    demo_email = "demo@farmbrain.local"
    user = User.query.filter_by(email=demo_email).first()
    if not user:
        user = User(name="FARM BRAIN Demo Member", email=demo_email, city="Madurai", state="Tamil Nadu", country="IN")
        user.set_password("demo-password-change-me")
        user.capabilities.append(CapabilityAssignment(capability="Farmer / Grower"))
        user.capabilities.append(CapabilityAssignment(capability="Buyer"))
        db.session.add(user)
        db.session.flush()
        from farm_brain.features import make_handle
        db.session.add(MemberProfile(user_id=user.id, handle=make_handle(user.name, user.id), plan_code="FARMER_BASIC_FREE"))

    if Listing.query.count() == 0:
        db.session.add_all([
            Listing(owner_id=user.id, division="Agri Products", category="Vegetables", record_type="offer",
                    action="sell", title="DEMO — Fresh vegetables from Madurai", description="Illustrative demo listing only. This is not a real offer, stock confirmation or customer record.",
                    quantity=250, unit="kg", price=24, currency="INR", city="Madurai", state="Tamil Nadu", country="IN"),
            Listing(owner_id=user.id, division="Agri Products", category="Millets", record_type="requirement",
                    action="buy", title="DEMO — Buyer requirement for millets", description="Illustrative demo requirement only. Use this record to test search and enquiries.",
                    quantity=1000, unit="kg", currency="INR", city="Madurai", state="Tamil Nadu", country="IN"),
            Listing(owner_id=user.id, division="Agri Business", category="Transport", record_type="requirement",
                    action="buy", transport_kind="load_request", title="DEMO — Load request: farm produce movement", description="Illustrative load request. Route, vehicle class, schedule and pricing need to be agreed separately.",
                    city="Madurai", state="Tamil Nadu", country="IN"),
            Listing(owner_id=user.id, division="Agri Business", category="Transport", record_type="offer",
                    action="availability", transport_kind="vehicle_availability", title="DEMO — Vehicle availability: 5 tonne truck", description="Illustrative vehicle availability. This is not a confirmed freight booking.",
                    city="Madurai", state="Tamil Nadu", country="IN"),
        ])
    db.session.commit()
    print("Demo seed complete. Sign in with demo@farmbrain.local / demo-password-change-me.")
    print("Change or remove the demo password before any shared deployment.")
