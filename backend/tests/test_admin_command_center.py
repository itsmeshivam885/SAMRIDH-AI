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


def test_admin_district_intelligence():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "rakhi.25bce10780", "password": "Rakhi#25BCE10780!Sec2026"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. District Summaries GET /districts
    dist_resp = client.get("/api/v1/admin/districts", headers=headers)
    assert dist_resp.status_code == 200
    dist_list = dist_resp.json()["data"]
    assert isinstance(dist_list, list)
    assert len(dist_list) > 0
    first_district = dist_list[0]["district"]

    # 2. District Drill-Down GET /districts/{district_name}
    detail_resp = client.get(f"/api/v1/admin/districts/{first_district}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()["data"]
    assert detail["district"].lower() == first_district.lower()
    assert "total_farmers" in detail
    assert "total_farms" in detail
    assert "claim_status_breakdown" in detail

    # 3. Unknown District 404
    unknown_resp = client.get("/api/v1/admin/districts/NonExistentDistrict99", headers=headers)
    assert unknown_resp.status_code == 404


def test_admin_eight_modules():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "rakhi.25bce10780", "password": "Rakhi#25BCE10780!Sec2026"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Module 3: Season & Notifications
    season_resp = client.get("/api/v1/admin/season-notifications", headers=headers)
    assert season_resp.status_code == 200
    assert len(season_resp.json()["data"]) > 0

    # Module 4: CCE & Yield Monitoring
    cce_resp = client.get("/api/v1/admin/cce-monitoring", headers=headers)
    assert cce_resp.status_code == 200
    assert len(cce_resp.json()["data"]) > 0

    # Module 7: SLA & Grievance Monitoring
    sla_resp = client.get("/api/v1/admin/sla-monitoring", headers=headers)
    assert sla_resp.status_code == 200
    assert len(sla_resp.json()["data"]) > 0

    # Module 8: Financial Reconciliation
    fin_resp = client.get("/api/v1/admin/financial-reconciliation", headers=headers)
    assert fin_resp.status_code == 200
    assert len(fin_resp.json()["data"]) > 0


