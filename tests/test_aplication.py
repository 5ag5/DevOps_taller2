import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "STATIC_TOKEN": "test-token",
        }
    )

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.drop_all()


def auth_headers():
    return {"Authorization": "Bearer test-token"}


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_blacklist_endpoint_requires_authorization(client):
    response = client.get("/blacklists/user@example.com")

    assert response.status_code == 401
    assert response.get_json()["msg"] == "Token de autorización no proporcionado"

def test_can_add_and_check_blacklisted_email(client):
    payload = {
        "email": "user@example.com",
        "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "blocked_reason": "Prueba unitaria",
    }

    create_response = client.post(
        "/blacklists", json=payload, headers=auth_headers()
    )
    check_response = client.get(
        "/blacklists/user@example.com", headers=auth_headers()
    )

    assert create_response.status_code == 201
    assert create_response.get_json()["blacklist"]["email"] == "user@example.com"
    assert check_response.status_code == 200
    assert check_response.get_json() == {
        "email": "user@example.com",
        "is_blacklisted": True,
        "blocked_reason": "Prueba unitaria",
    }
