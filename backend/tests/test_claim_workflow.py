import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from app.main import app

client = TestClient(app)


def test_full_claim_and_officer_review_workflow():
    # 1. Login as Farmer Ramesh
    login_resp = client.post("/api/v1/auth/login", json={"username_or_phone": "ramesh", "password": "DemoPass123!"})
    assert login_resp.status_code == 200
    farmer_token = login_resp.json()["data"]["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

    # 2. Get Farmer Farms
    farms_resp = client.get("/api/v1/farms", headers=farmer_headers)
    assert farms_resp.status_code == 200
    farms = farms_resp.json()["data"]
    assert len(farms) > 0
    farm_id = farms[0]["id"]

    # 3. Create Damage Report
    report_resp = client.post(
        "/api/v1/damage/report",
        json={
            "farm_id": farm_id,
            "loss_category": "FLOOD_AND_LODGING",
            "farmer_reported_loss_percentage": 70.0,
            "description": "Submersion damage due to heavy localized thunderstorm.",
        },
        headers=farmer_headers,
    )
    assert report_resp.status_code == 200
    report_id = report_resp.json()["data"]["id"]

    # 4. Upload Damage Photo Evidence
    img = Image.new("RGB", (800, 800), color=(100, 180, 80))
    draw = ImageDraw.Draw(img)
    for x in range(0, 800, 40):
        draw.line([(x, 0), (x, 800)], fill=(40, 90, 40), width=3)
    
    img_buf = io.BytesIO()
    img.save(img_buf, format="JPEG")
    img_bytes = img_buf.getvalue()

    evidence_resp = client.post(
        f"/api/v1/damage/{report_id}/evidence",
        data={
            "gps_latitude": 23.0185,
            "gps_longitude": 76.8821,
            "device_model": "Farmer Phone Test",
        },
        files={"file": ("damage_test.jpg", img_bytes, "image/jpeg")},
        headers=farmer_headers,
    )
    assert evidence_resp.status_code == 200
    evid_data = evidence_resp.json()["data"]
    assert evid_data["validation"]["passed_quality_gate"] is True
    assert evid_data["fraud_check"]["geofence_status"] == "INSIDE"

    # 5. Create Claim from Damage Report
    claim_resp = client.post(f"/api/v1/claims/from-report/{report_id}", headers=farmer_headers)
    assert claim_resp.status_code == 200
    claim = claim_resp.json()["data"]
    assert claim["status"] == "OFFICER_REVIEW"
    assert claim["ai_damage_percentage"] > 0
    assert claim["estimated_payout_amount"] > 0
    claim_id = claim["id"]

    # 6. Login as Officer Sharma
    off_login = client.post("/api/v1/auth/login", json={"username_or_phone": "officer_sharma", "password": "DemoPass123!"})
    officer_token = off_login.json()["data"]["access_token"]
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # 7. Officer Reviews and Approves Claim
    review_resp = client.post(
        f"/api/v1/officer/claims/{claim_id}/review",
        json={
            "decision": "APPROVED",
            "remarks": "Ground photos and Sentinel-2 NDVI drop correlate with localized inundation report. Recommended for DBT sanction.",
            "approved_loss_percentage": 68.0,
            "sanctioned_payout_amount": 81600.0,
        },
        headers=officer_headers,
    )
    assert review_resp.status_code == 200
    reviewed_claim = review_resp.json()["data"]
    assert reviewed_claim["status"] == "APPROVED"
    assert reviewed_claim["final_sanctioned_amount"] == 81600.0
    assert reviewed_claim["settlement_status"] == "PROCESSED_FOR_DBT"
