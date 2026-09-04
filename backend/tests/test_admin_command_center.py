import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_admin_login_and_stats():
    # Login as Super Admin Rakhi
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "rakhi.25bce10780", "password": "Rakhi#25BCE10780!Sec2026"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch stats
    stats_resp = client.get("/api/v1/admin/stats", headers=headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()["data"]
    assert "total_registered_farmers" in stats
    assert "total_monitored_hectares" in stats
    assert "district_wise_claim_density" in stats


def test_admin_global_search():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "rakhi.25bce10780", "password": "Rakhi#25BCE10780!Sec2026"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    search_resp = client.get("/api/v1/admin/search?q=shivam", headers=headers)
    assert search_resp.status_code == 200
    data = search_resp.json()["data"]
    assert isinstance(data, list)


def test_admin_fraud_radar():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "rakhi.25bce10780", "password": "Rakhi#25BCE10780!Sec2026"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    radar_resp = client.get("/api/v1/admin/fraud-radar", headers=headers)
    assert radar_resp.status_code == 200
    summary = radar_resp.json()["data"]
    assert "total_flagged_evidence" in summary
    assert "high_risk_count" in summary


def test_admin_prevent_self_deactivation():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "rakhi.25bce10780", "password": "Rakhi#25BCE10780!Sec2026"}
    )
    token_data = login_resp.json()
    token = token_data["access_token"]
    user_id = token_data["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt self-deactivation
    deact_resp = client.patch(
        f"/api/v1/admin/users/{user_id}/status",
        json={"is_active": False, "reason": "Self deactivation test"},
        headers=headers
    )
    assert deact_resp.status_code == 400
    assert "cannot deactivate their own" in deact_resp.json()["error"]["message"]


def test_admin_audit_logs_and_settings():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "rakhi.25bce10780", "password": "Rakhi#25BCE10780!Sec2026"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Read Audit logs
    logs_resp = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert logs_resp.status_code == 200
    assert isinstance(logs_resp.json()["data"], list)

    # Read Settings
    settings_resp = client.get("/api/v1/admin/settings", headers=headers)
    assert settings_resp.status_code == 200
    settings_list = settings_resp.json()["data"]
    assert len(settings_list) > 0

    # Update Setting
    put_resp = client.put(
        "/api/v1/admin/settings/PHASH_HAMMING_THRESHOLD",
        json={"value": "14", "reason": "Threshold tuning unit test"},
        headers=headers
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["data"]["value"] == "14"
