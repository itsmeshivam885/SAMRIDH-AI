import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SAMRIDH-AI Core Gateway"
    assert data["tagline"] == "Predict. Prevent. Protect. Prove."


def test_farmer_login():
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_phone": "ramesh", "password": "DemoPass123!"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert "access_token" in res["data"]
    assert res["data"]["role"] == "farmer"
    assert res["data"]["full_name"] == "Ramesh Kumar"


def test_officer_login():
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_phone": "officer_sharma", "password": "DemoPass123!"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["role"] == "officer"


def test_otp_flow():
    # Request OTP
    req_resp = client.post("/api/v1/auth/otp/request", json={"phone_number": "9876543210"})
    assert req_resp.status_code == 200
    assert req_resp.json()["data"]["otp_sent"] is True

    # Verify OTP
    ver_resp = client.post("/api/v1/auth/otp/verify", json={"phone_number": "9876543210", "otp_code": "123456"})
    assert ver_resp.status_code == 200
    assert ver_resp.json()["data"]["role"] == "farmer"
