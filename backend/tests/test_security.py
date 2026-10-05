from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_user(role):
    username = f"security_{role.lower()}_{uuid4().hex[:8]}"
    password = "SecurityTest123"

    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": password,
            "role": role
        }
    )

    assert response.status_code == 200

    return username, password


def login(username, password):
    response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_header(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def test_audit_requires_authentication():
    response = client.get(
        "/api/audit/"
    )

    assert response.status_code in [401, 403]


def test_invalid_token_rejected():
    response = client.get(
        "/api/audit/",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_analyst_cannot_create_case():
    username, password = create_user("Analyst")
    token = login(username, password)

    response = client.post(
        "/api/cases/",
        headers=auth_header(token),
        json={
            "case_name": "Unauthorized Case",
            "description": "RBAC test",
            "investigator": username,
            "status": "Open",
            "priority": "Medium"
        }
    )

    assert response.status_code == 403


def test_investigator_cannot_view_audit_logs():
    username, password = create_user("Investigator")
    token = login(username, password)

    response = client.get(
        "/api/audit/",
        headers=auth_header(token)
    )

    assert response.status_code == 403


def test_analyst_cannot_generate_report():
    username, password = create_user("Analyst")
    token = login(username, password)

    response = client.post(
        "/api/reports/1/generate",
        headers=auth_header(token)
    )

    assert response.status_code == 403


def test_analyst_cannot_upload_evidence():
    username, password = create_user("Analyst")
    token = login(username, password)

    response = client.post(
        "/api/evidence/upload",
        headers=auth_header(token),
        data={
            "case_id": "1",
            "uploaded_by": username,
            "description": "RBAC test"
        },
        files={
            "file": (
                "test.txt",
                b"security test",
                "text/plain"
            )
        }
    )

    assert response.status_code == 403


def test_investigator_can_view_cases():
    username, password = create_user("Investigator")
    token = login(username, password)

    response = client.get(
        "/api/cases/",
        headers=auth_header(token)
    )

    assert response.status_code == 200


def test_analyst_can_view_cases():
    username, password = create_user("Analyst")
    token = login(username, password)

    response = client.get(
        "/api/cases/",
        headers=auth_header(token)
    )

    assert response.status_code == 200