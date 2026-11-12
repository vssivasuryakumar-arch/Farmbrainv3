import pytest

from farm_brain import create_app
from farm_brain.extensions import db


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "UPLOAD_FOLDER": "/tmp/farmbrain-test-uploads",
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, name, email, capability="Farmer / Grower"):
    response = client.post("/register", data={
        "name": name,
        "email": email,
        "password": "a-safe-test-password",
        "country": "IN",
        "capabilities": [capability],
    }, follow_redirects=False)
    code = client.application.extensions["otp_test_codes"][email]
    return client.post("/verify-email", data={"code": code}, follow_redirects=True)
