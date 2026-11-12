from farm_brain.extensions import db
from farm_brain.models import Enquiry, Listing, Quotation, User

from .conftest import register


def test_home_and_market_render(client):
    assert client.get("/").status_code == 200
    assert client.get("/market").status_code == 200
    assert client.get("/api/v1/listings").json["items"] == []


def test_user_can_register_with_multiple_capabilities(client, app):
    response = client.post("/register", data={
        "name": "Test Member", "email": "member@example.com",
        "password": "a-safe-test-password", "country": "IN",
        "capabilities": ["Farmer / Grower", "Buyer"],
    }, follow_redirects=False)
    assert response.status_code == 302
    with app.app_context():
        assert User.query.filter_by(email="member@example.com").first() is None
    code = app.extensions["otp_test_codes"]["member@example.com"]
    response = client.post("/verify-email", data={"code": code}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your email is verified" in response.data
    with app.app_context():
        user = User.query.filter_by(email="member@example.com").one()
        assert set(user.capability_names) == {"Farmer / Grower", "Buyer"}
        assert user.check_password("a-safe-test-password")


def test_listing_enquiry_and_quote_lifecycle(client, app):
    register(client, "Seller", "seller@example.com", "Seller / Supplier")
    response = client.post("/listing/new", data={
        "division": "Agri Products", "category": "Vegetables",
        "record_type": "offer", "action": "sell", "title": "Fresh tomatoes",
        "description": "Fresh tomatoes available from this week's harvest.",
        "quantity": "100", "unit": "kg", "price": "28", "currency": "INR",
        "city": "Madurai", "state": "Tamil Nadu", "country": "IN",
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        listing_id = Listing.query.filter_by(title="Fresh tomatoes").one().id

    client.post("/logout", follow_redirects=True)
    register(client, "Buyer", "buyer@example.com", "Buyer")
    response = client.post(f"/listing/{listing_id}/enquire", data={
        "message": "I would like to know the available quantity and harvest date."
    }, follow_redirects=True)
    assert b"Your enquiry was sent" in response.data

    with app.app_context():
        enquiry_id = Enquiry.query.one().id

    client.post("/logout", follow_redirects=True)
    client.post("/login", data={"email": "seller@example.com", "password": "a-safe-test-password"})
    response = client.post(f"/enquiry/{enquiry_id}/quote", data={
        "amount": "2500", "currency": "INR", "terms": "Indicative price subject to final quality and collection date."
    }, follow_redirects=True)
    assert b"Indicative quotation sent" in response.data

    with app.app_context():
        quote_id = Quotation.query.one().id

    client.post("/logout", follow_redirects=True)
    client.post("/login", data={"email": "buyer@example.com", "password": "a-safe-test-password"})
    response = client.post(f"/quotation/{quote_id}/accept-for-discussion", follow_redirects=True)
    assert b"accepted for further discussion only" in response.data
    with app.app_context():
        quote = db.session.get(Quotation, quote_id)
        assert quote.status == "accepted_for_discussion"


def test_user_cannot_enquire_on_own_listing(client, app):
    register(client, "Owner", "owner@example.com")
    client.post("/listing/new", data={
        "division": "Agri Products", "category": "Seeds", "record_type": "offer",
        "action": "sell", "title": "Certified seed listing", "description": "Seed details for demonstration purposes."
    })
    with app.app_context():
        listing_id = Listing.query.one().id
    response = client.post(f"/listing/{listing_id}/enquire", data={
        "message": "I am trying to enquire about my own listing."
    }, follow_redirects=True)
    assert b"You cannot send an enquiry to your own listing" in response.data
    with app.app_context():
        assert Enquiry.query.count() == 0


def test_non_owner_cannot_reply_to_an_enquiry(client, app):
    register(client, "Seller", "owner2@example.com", "Seller / Supplier")
    client.post("/listing/new", data={
        "division": "Agri Products", "category": "Vegetables", "record_type": "offer",
        "action": "sell", "title": "Onion offer", "description": "Fresh onions available for enquiry."
    })
    with app.app_context():
        listing_id = Listing.query.one().id
    client.post("/logout")
    register(client, "Buyer", "buyer2@example.com", "Buyer")
    client.post(f"/listing/{listing_id}/enquire", data={"message": "Please share details about the onion lot."})
    client.post("/logout")
    register(client, "Other", "other@example.com")
    with app.app_context():
        enquiry_id = Enquiry.query.one().id
    response = client.post(f"/enquiry/{enquiry_id}/quote", data={
        "terms": "I am not the listing owner, so this must be blocked."
    })
    assert response.status_code == 403


def test_email_verification_is_required_and_wrong_code_is_rejected(client, app):
    response = client.post("/register", data={
        "name": "OTP Test", "email": "otp@example.com",
        "password": "a-safe-test-password", "country": "IN",
        "capabilities": ["Farmer / Grower"],
    })
    assert response.status_code == 302
    response = client.post("/verify-email", data={"code": "123456"})
    assert response.status_code == 400
    with app.app_context():
        assert User.query.filter_by(email="otp@example.com").first() is None
    code = app.extensions["otp_test_codes"]["otp@example.com"]
    assert client.post("/verify-email", data={"code": code}, follow_redirects=True).status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="otp@example.com").count() == 1
