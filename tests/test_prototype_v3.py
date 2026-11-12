from io import BytesIO
from pathlib import Path

from PIL import Image

from farm_brain.extensions import db
from farm_brain.models import (
    AquaponicsAlert, AquaponicsFarm, AquaponicsFishLog, AquaponicsMembership,
    AquaponicsTank, AquaponicsWaterReading, DirectMessage, MessageAttachment,
    PostAttachment, User,
)
from .conftest import register


def png_bytes():
    image = Image.new("RGB", (32, 32), (30, 120, 60))
    stream = BytesIO()
    image.save(stream, format="PNG")
    stream.seek(0)
    return stream


def test_community_photo_upload_is_sanitised_and_visible(client, app):
    register(client, "Photo Farmer", "photo@example.com")
    response = client.post(
        "/community",
        data={"body": "Tomato crop update from our farm.", "photo": (png_bytes(), "harvest.png")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"published" in response.data
    with app.app_context():
        attachment = PostAttachment.query.one()
        assert attachment.mime_type == "image/jpeg"
        assert attachment.storage_name.startswith("public/community/")
        path = Path(app.config["UPLOAD_FOLDER"]) / attachment.storage_name
        assert path.exists()
        assert path.read_bytes().startswith(b"\xff\xd8")
        storage_name = attachment.storage_name
    assert client.get(f"/media/{storage_name}").status_code == 200
    assert client.get("/photos").status_code == 200


def test_message_pdf_attachment_is_private_to_conversation_participants(client, app):
    register(client, "Sender", "sender@example.com")
    client.post("/logout")
    register(client, "Receiver", "receiver@example.com")
    with app.app_context():
        sender = User.query.filter_by(email="sender@example.com").one()
        sender_id = sender.id
        receiver_id = User.query.filter_by(email="receiver@example.com").one().id
    client.post("/logout")
    client.post("/login", data={"email": "sender@example.com", "password": "a-safe-test-password"})
    pdf = BytesIO(b"%PDF-1.4\n% sample attachment\n%%EOF")
    response = client.post(
        f"/inbox/{receiver_id}",
        data={"body": "Please review the attached farm document.", "attachment": (pdf, "farm-record.pdf")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        message = DirectMessage.query.one()
        attachment = MessageAttachment.query.one()
        attachment_id = attachment.id
        assert message.sender_id == sender_id
        assert attachment.original_name == "farm-record.pdf"
    assert client.get(f"/private-media/{attachment_id}").status_code == 200
    client.post("/logout")
    register(client, "Third Party", "third@example.com")
    assert client.get(f"/private-media/{attachment_id}").status_code == 404


def test_aquaponics_india_rnd_manual_readings_and_threshold_alerts(client, app):
    register(client, "Magppliv Research", "magppliv@example.com")
    response = client.post("/aquaponics/", data={
        "name": "Magppliv India Prototype",
        "mode": "india_rnd", "country": "IN", "location": "Tamil Nadu",
        "partner_name": "University collaboration planning",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        farm = AquaponicsFarm.query.one()
        assert farm.currency == "INR"
        farm_id = farm.id
        system_id = farm.systems[0].id
    response = client.post(f"/aquaponics/farm/{farm_id}/system", data={
        "name": "Prototype loop A", "ph_min": "6.5", "ph_max": "7.5",
        "temperature_min_c": "20", "temperature_max_c": "30",
        "dissolved_oxygen_min_mg_l": "5", "ammonia_max_mg_l": "0.5",
        "nitrite_max_mg_l": "0.5",
    }, follow_redirects=True)
    assert response.status_code == 200
    response = client.post(f"/aquaponics/farm/{farm_id}/water", data={
        "system_id": str(system_id), "ph": "8.1", "temperature_c": "28",
        "dissolved_oxygen_mg_l": "6", "ammonia_mg_l": "0.2",
        "notes": "Manual test kit reading, demo test only",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        reading = AquaponicsWaterReading.query.one()
        assert reading.source == "manual"
        assert AquaponicsAlert.query.filter_by(metric="pH", status="open").count() == 1
    assert client.get(f"/aquaponics/farm/{farm_id}/water").status_code == 200
    assert client.get(f"/aquaponics/farm/{farm_id}/report.csv").status_code == 200


def test_aquaponics_uae_pilot_currency_is_aed_and_investor_is_read_only(client, app):
    register(client, "Magppliv UAE", "uaepilot@example.com")
    response = client.post("/aquaponics/", data={
        "name": "UAE Partner Farm Pilot", "mode": "uae_pilot", "country": "AE",
        "location": "UAE partner farm site", "partner_name": "Pilot partner (planning)",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        farm = AquaponicsFarm.query.one()
        assert farm.currency == "AED"
        farm_id = farm.id
    client.post("/logout")
    register(client, "Investor Viewer", "investor@example.com")
    with app.app_context():
        viewer = User.query.filter_by(email="investor@example.com").one()
        db.session.add(AquaponicsMembership(farm_id=farm_id, user_id=viewer.id, role="investor_readonly"))
        db.session.commit()
    assert client.get(f"/aquaponics/farm/{farm_id}").status_code == 200
    assert client.post(f"/aquaponics/farm/{farm_id}/system", data={"name": "Attempt edit"}).status_code == 403


def test_aquaponics_fish_management_updates_population_and_biomass(client, app):
    register(client, "Fish Operator", "fish@example.com")
    client.post("/aquaponics/", data={
        "name": "Fish Test Farm", "mode": "india_rnd", "country": "IN",
    })
    with app.app_context():
        farm = AquaponicsFarm.query.one()
        farm_id = farm.id
        system_id = farm.systems[0].id
    client.post(f"/aquaponics/farm/{farm_id}/fish", data={
        "action": "create_tank", "system_id": str(system_id), "name": "Tank 01",
        "species": "Tilapia (example)", "stocked_count": "100", "average_weight_g": "50",
        "volume_litres": "2000",
    })
    with app.app_context():
        tank = AquaponicsTank.query.one()
        tank_id = tank.id
    client.post(f"/aquaponics/farm/{farm_id}/fish", data={
        "action": "log", "tank_id": str(tank_id), "log_type": "mortality",
        "fish_count": "3", "notes": "Observed mortality, record only",
    })
    with app.app_context():
        tank = db.session.get(AquaponicsTank, tank_id)
        assert tank.current_count == 97
        assert AquaponicsFishLog.query.one().log_type == "mortality"
    assert client.get(f"/aquaponics/farm/{farm_id}/fish").status_code == 200


def test_marketplace_listing_accepts_public_photos(client, app):
    register(client, "Photo Seller", "listing-photo@example.com", "Seller / Supplier")
    response = client.post(
        "/listing/new",
        data={
            "division": "Agri Products", "category": "Vegetables",
            "record_type": "offer", "action": "sell",
            "title": "Fresh brinjal harvest", "description": "Fresh brinjal available from our farm this week.",
            "quantity": "50", "unit": "kg", "currency": "INR", "country": "IN",
            "photos": (png_bytes(), "brinjal.png"),
        },
        content_type="multipart/form-data", follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        from farm_brain.models import Listing, ListingAttachment
        listing = Listing.query.filter_by(title="Fresh brinjal harvest").one()
        attachment = ListingAttachment.query.one()
        listing_id = listing.id
        assert attachment.listing_id == listing.id
        assert attachment.mime_type == "image/jpeg"
    detail = client.get(f"/listing/{listing_id}")
    assert detail.status_code == 200
    assert b"brinjal" in detail.data.lower()


def test_password_reset_uses_email_otp_and_updates_password(client, app):
    register(client, "Password Member", "password-reset@example.com")
    client.post("/logout")
    response = client.post("/forgot-password", data={"email": "password-reset@example.com"}, follow_redirects=True)
    assert response.status_code == 200
    code = app.extensions["otp_test_codes"]["password-reset@example.com"]
    response = client.post("/reset-password", data={
        "code": code, "password": "a-new-safe-password"
    }, follow_redirects=True)
    assert response.status_code == 200
    response = client.post("/login", data={
        "email": "password-reset@example.com", "password": "a-new-safe-password"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back" in response.data
