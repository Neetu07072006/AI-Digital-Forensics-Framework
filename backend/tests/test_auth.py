from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    username = "test_investigator_123"

    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "TestPassword123",
            "role": "Investigator"
        }
    )

    assert response.status_code in [200, 400]

def test_login_invalid_user():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent_user",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401

def test_protected_audit_endpoint_without_token():
    response = client.get("/api/audit/")

    assert response.status_code in [401, 403]