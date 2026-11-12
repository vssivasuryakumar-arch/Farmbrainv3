from decimal import Decimal

from farm_brain.extensions import db
from farm_brain.models import (
    CommunityPost, ContentReport, CropCycle, Listing, MemberProfile,
    Notification, PostComment, PostLike, ProfileFollow, TransportDetail,
    User, UserRole,
)
from .conftest import register


def test_farmer_gets_free_public_profile(client, app):
    response = register(client, "Malar Farm", "malar@example.com")
    assert response.status_code == 200
    with app.app_context():
        profile = MemberProfile.query.one()
        assert profile.plan_code == "FARMER_BASIC_FREE"
        handle = profile.handle
    response = client.get(f"/profile/{handle}")
    assert response.status_code == 200
    assert b"Malar Farm" in response.data
    assert b"Free" in response.data


def test_profile_edit_and_farm_crop_records(client, app):
    register(client, "Field Notes", "field@example.com")
    response = client.post("/profile/edit", data={
        "bio": "Growing vegetables and millets.",
        "farm_name": "Field Notes Farm",
        "farm_area": "2.5",
        "farm_area_unit": "acre",
        "primary_crops": "Tomato, millet",
        "avatar_url": "javascript:alert(1)",
        "website": "https://example.com",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        profile = MemberProfile.query.one()
        assert profile.farm_area == Decimal("2.500")
        assert profile.avatar_url == ""
        assert profile.website == "https://example.com"
    response = client.post("/farm-records", data={
        "crop": "Tomato", "variety": "Hybrid", "season": "Rabi",
        "area": "1.25", "area_unit": "acre", "planted_on": "2026-10-01",
        "expected_harvest": "2027-01-15", "notes": "Drip irrigation block A",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        cycle = CropCycle.query.one()
        assert cycle.area == Decimal("1.250")
        assert cycle.status == "planned"


def test_community_social_like_comment_and_follow(client, app):
    register(client, "Grower One", "grower1@example.com")
    client.post("/community", data={"body": "Our first banana harvest is ready for this season."})
    with app.app_context():
        post = CommunityPost.query.one()
        post_id = post.id
        post_owner = User.query.get(post.user_id)
        owner_handle = post_owner.member_profile.handle
    client.post("/logout")
    register(client, "Grower Two", "grower2@example.com")
    assert client.post(f"/posts/{post_id}/like", follow_redirects=True).status_code == 200
    assert client.post(f"/posts/{post_id}/comment", data={"body": "Congratulations on the harvest!"}, follow_redirects=True).status_code == 200
    assert client.post(f"/profile/{owner_handle}/follow", follow_redirects=True).status_code == 200
    with app.app_context():
        assert PostLike.query.filter_by(post_id=post_id).count() == 1
        assert PostComment.query.filter_by(post_id=post_id, status="active").count() == 1
        assert ProfileFollow.query.count() == 1
        assert Notification.query.count() >= 2


def test_transport_load_and_vehicle_records_stay_distinct(client, app):
    register(client, "Transport Member", "transport@example.com", "Transporter / Vehicle Owner")
    response = client.post("/listing/new", data={
        "division": "Agri Business", "category": "Transport", "record_type": "offer",
        "action": "sell", "transport_kind": "load_request", "title": "Tomato load to Chennai",
        "description": "Need a clean vehicle for 5 tonnes of fresh tomato.",
        "origin": "Madurai", "destination": "Chennai", "cargo_type": "Tomato",
        "weight": "5", "weight_unit": "tonne", "city": "Madurai", "state": "Tamil Nadu", "country": "IN",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        load = Listing.query.one()
        assert load.record_type == "requirement"
        assert load.transport_kind == "load_request"
        assert load.transport_detail.kind == "load_request"
        assert load.transport_detail.weight == Decimal("5.000")
    response = client.post("/listing/new", data={
        "division": "Agri Business", "category": "Transport", "record_type": "requirement",
        "action": "buy", "transport_kind": "vehicle_availability", "title": "14 ft truck available",
        "description": "14 ft truck available for agricultural transport routes.",
        "origin": "Dindigul", "vehicle_type": "14 ft truck", "vehicle_capacity": "7.5",
        "city": "Dindigul", "state": "Tamil Nadu", "country": "IN",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        vehicle = Listing.query.filter_by(title="14 ft truck available").one()
        assert vehicle.record_type == "offer"
        assert vehicle.transport_kind == "vehicle_availability"
    assert client.get("/transport?kind=load_request").status_code == 200
    assert client.get("/transport?kind=vehicle_availability").status_code == 200
    assert client.get("/api/v1/transport").json["items"]


def test_admin_moderation_requires_role_and_writes_audit(client, app):
    register(client, "Reporter", "reporter@example.com")
    client.post("/community", data={"body": "An unsafe or misleading claim to be reviewed."})
    with app.app_context():
        post = CommunityPost.query.one()
        post_id = post.id
        owner = User.query.filter_by(email="reporter@example.com").one()
        report = ContentReport(reporter_id=owner.id, target_type="post", target_id=post_id, reason="misleading", details="Needs moderator review")
        db.session.add(report)
        db.session.commit()
        report_id = report.id
    assert client.get("/admin/moderation").status_code == 403
    with app.app_context():
        owner = User.query.filter_by(email="reporter@example.com").one()
        db.session.add(UserRole(user_id=owner.id, role="admin"))
        db.session.commit()
    assert client.post(f"/admin/moderation/{report_id}/hide", data={"reason": "Clearly misleading content."}, follow_redirects=True).status_code == 200
    with app.app_context():
        assert ContentReport.query.one().status == "resolved"
        assert CommunityPost.query.count() == 0
        assert db.session.query(UserRole).count() == 1


def test_official_data_sources_are_explicit_and_unconfigured_mandi_is_not_fake_live(client):
    assert client.get("/farm-intelligence").status_code == 200
    response = client.get("/api/v1/markets/mandi")
    assert response.status_code == 503
    assert response.json["status"] == "not_configured"


def test_health_and_installable_web_manifest(client):
    assert client.get("/healthz").json["status"] == "ok"
    manifest = client.get("/manifest.webmanifest")
    assert manifest.status_code == 200
    assert b"FARM BRAIN" in manifest.data


def test_social_actions_ignore_external_referrer(client, app):
    register(client, "Safe Redirect Farmer", "safe-redirect@example.com")
    client.post("/community", data={"body": "Testing same-origin redirects for FARM BRAIN."})
    with app.app_context():
        post_id = CommunityPost.query.one().id
    response = client.post(
        f"/posts/{post_id}/like", data={},
        headers={"Referer": "https://malicious.example/phishing"},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/community")


def test_inventory_records_movements_and_blocks_negative_stock(client, app):
    register(client, "Inventory Farmer", "inventory@example.com")
    response = client.post("/inventory", data={
        "name": "Tomato seed trays", "sku": "TRAY-01", "unit": "piece",
        "quantity": "10", "reorder_level": "2", "notes": "Nursery stock",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        from farm_brain.models import InventoryItem, StockMovement
        item_id = InventoryItem.query.one().id
    client.post(f"/inventory/{item_id}/adjust", data={"delta": "-3", "note": "Used in nursery"})
    client.post(f"/inventory/{item_id}/adjust", data={"delta": "-100", "note": "Invalid withdrawal"})
    with app.app_context():
        from farm_brain.models import InventoryItem, StockMovement
        item = db.session.get(InventoryItem, item_id)
        assert item.quantity == Decimal("7.000")
        assert StockMovement.query.filter_by(item_id=item_id).count() == 2


def test_official_mandi_connector_parses_configured_provider_response(monkeypatch):
    import json
    from farm_brain.data_integrations import get_ogd_mandi_prices

    seen = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _size):
            return json.dumps({"records": [{"commodity": "Tomato", "modal_price": "1200"}]}).encode()

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("farm_brain.data_integrations.urlopen", fake_urlopen)
    result = get_ogd_mandi_prices(
        "test-key", "resource-123", "https://data.gov.in/api/datastore/resource.json",
        state="Tamil Nadu", commodity="Tomato", limit=10,
    )
    assert result["available"] is True
    assert result["records"][0]["commodity"] == "Tomato"
    assert "filters%5Bstate%5D=Tamil+Nadu" in seen["url"]
    assert seen["timeout"] == 12
