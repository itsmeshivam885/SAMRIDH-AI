import os
import sys
from datetime import datetime, date, timedelta, timezone

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)

from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, Role
from app.models.farmer import Farmer
from app.models.farm import Farm, FarmBoundary
from app.models.crop import CropSeason, FarmCrop
from app.models.baseline import BaselineRecord, BaselineImage
from app.models.sensor import SoilSensor, SoilReading
from app.models.weather import WeatherRecord, WeatherAlert
from app.models.satellite import SatelliteObservation, NDVIRecord
from app.models.disaster import DisasterEvent
from app.models.damage import DamageReport, DamageAssessment
from app.models.evidence import DamageEvidence, EvidenceValidation
from app.models.fraud import FraudCheck
from app.models.claim import Claim, ClaimEvent
from app.models.officer import Officer
from app.models.notification import Advisory, Notification
from app.models.audit import AIModelRegistry, SystemSetting
from app.iot.simulator import generate_simulated_readings


def seed_database():
    print("[*] Initializing SAMRIDH-AI database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing demo data
    print("[*] Resetting database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    now = datetime.now(timezone.utc)

    print("[*] Seeding Roles...")
    roles = {
        "farmer": Role(name="farmer", description="Farmer with farm management and claim filing access"),
        "officer": Role(name="officer", description="Field and Agriculture Officer for claim verification"),
        "admin": Role(name="admin", description="District/State Agronomy Administrator"),
        "super_admin": Role(name="super_admin", description="Super Admin with system & model registry access"),
    }
    for r in roles.values():
        db.add(r)
    db.flush()

    print("[*] Seeding Users...")
    pw_hash = get_password_hash("DemoPass123!")

    # 1. Farmer Ramesh Kumar
    farmer_user = User(
        username="ramesh",
        phone_number="9876543210",
        email="ramesh.farmer@samridh.ai",
        full_name="Ramesh Kumar",
        role="farmer",
        preferred_language="hi",
        hashed_password=pw_hash,
    )
    db.add(farmer_user)
    db.flush()

    farmer_profile = Farmer(
        user_id=farmer_user.id,
        farmer_id_code="FARMER-MP-2026-001",
        masked_aadhaar="XXXX-XXXX-8921",
        state="Madhya Pradesh",
        district="Sehore",
        tehsil="Ashta",
        village="Kothri",
        pincode="466116",
        pmfby_policy_number="PMFBY-2026-MP-984210",
        bank_account_masked="SBI-XXXX-4512",
        ifsc_code="SBIN0001234",
    )
    db.add(farmer_profile)
    db.flush()

    # 2. Officer Sharma
    officer_user = User(
        username="officer_sharma",
        phone_number="9876543211",
        email="sharma.officer@samridh.ai",
        full_name="V. K. Sharma",
        role="officer",
        preferred_language="en",
        hashed_password=pw_hash,
    )
    db.add(officer_user)
    db.flush()

    officer_profile = Officer(
        user_id=officer_user.id,
        officer_badge_number="OFFICER-MP-SEH-01",
        designation="District Agricultural Loss Assessor",
        assigned_state="Madhya Pradesh",
        assigned_district="Sehore",
        assigned_tehsil="Ashta",
    )
    db.add(officer_profile)

    # 3. Admin Verma
    admin_user = User(
        username="admin_samridh",
        phone_number="9876543212",
        email="verma.admin@samridh.ai",
        full_name="Rajesh Verma",
        role="admin",
        preferred_language="en",
        hashed_password=pw_hash,
    )
    db.add(admin_user)
    db.commit()

    print("[*] Seeding Farms and GIS Boundaries...")
    # Primary Demo Farm: Farm-001 (Soybean 2.5ha in Ashta, Sehore)
    farm1 = Farm(
        farmer_id=farmer_profile.id,
        farm_code="FARM-001",
        name="Kothri North Field - Ramesh Kumar",
        survey_number="KH-142/1",
        area_hectares=2.5,
        soil_type="Deep Black Cotton Soil (Vertisol)",
        irrigation_source="Borewell + Rainfed",
        center_latitude=23.0185,
        center_longitude=76.8821,
    )
    db.add(farm1)
    db.flush()

    # GeoJSON Polygon for Farm-001 (approx 2.5 ha boundary)
    farm1_polygon = {
        "type": "Polygon",
        "coordinates": [[
            [76.8810, 23.0175],
            [76.8835, 23.0175],
            [76.8835, 23.0195],
            [76.8810, 23.0195],
            [76.8810, 23.0175]
        ]]
    }
    boundary1 = FarmBoundary(
        farm_id=farm1.id,
        geojson=farm1_polygon,
        perimeter_meters=780.0,
        calculated_area_hectares=2.52,
        verified_by_officer=True,
    )
    db.add(boundary1)

    # Secondary Farms for GIS Map
    other_farms_data = [
        ("FARM-002", "Bhopal West Wheat Farm", 3.2, 23.2599, 77.4126, "Alluvial Soil", "Canal"),
        ("FARM-003", "Dewas Paddy Parcel", 1.8, 22.9676, 76.0534, "Medium Black Soil", "Borewell"),
        ("FARM-004", "Ujjain Mustard Field", 4.0, 23.1765, 75.7885, "Black Soil", "Rainfed"),
        ("FARM-005", "Hoshangabad Pulse Farm", 2.2, 22.7519, 77.7289, "Sandy Loam", "Tube Well"),
    ]
    for code, fname, ha, lat, lon, stype, irri in other_farms_data:
        f = Farm(
            farmer_id=farmer_profile.id,
            farm_code=code,
            name=fname,
            survey_number=f"KH-{code[-2:]}0/B",
            area_hectares=ha,
            soil_type=stype,
            irrigation_source=irri,
            center_latitude=lat,
            center_longitude=lon,
        )
        db.add(f)
        db.flush()
        poly = {
            "type": "Polygon",
            "coordinates": [[
                [lon - 0.001, lat - 0.001],
                [lon + 0.001, lat - 0.001],
                [lon + 0.001, lat + 0.001],
                [lon - 0.001, lat + 0.001],
                [lon - 0.001, lat - 0.001]
            ]]
        }
        b = FarmBoundary(farm_id=f.id, geojson=poly, perimeter_meters=600.0, calculated_area_hectares=ha, verified_by_officer=True)
        db.add(b)

    db.commit()

    print("[*] Seeding Crops and Crop Seasons...")
    season = CropSeason(
        name="Kharif 2026",
        season_type="Kharif",
        year=2026,
        start_date=date(2026, 6, 15),
        end_date=date(2026, 11, 15),
        is_current=True,
    )
    db.add(season)
    db.flush()

    crop1 = FarmCrop(
        farm_id=farm1.id,
        crop_name="Soybean",
        variety="JS-9560 (High Yield)",
        season="Kharif 2026",
        sowing_date=date(2026, 6, 22),
        expected_harvest_date=date(2026, 10, 10),
        current_growth_stage="Pod Filling / Pre-Harvest",
        notified_sum_insured_per_ha=48000.0,
    )
    db.add(crop1)
    db.commit()

    print("[*] Seeding Baseline Record...")
    base_rec = BaselineRecord(
        farm_id=farm1.id,
        crop_id=crop1.id,
        growth_stage="Germination / Early Vegetative",
        canopy_density_score=88.5,
        notes="Clean germination baseline. Boundary tree in North-East corner and borewell shed visible.",
        verified_by_officer=True,
    )
    db.add(base_rec)
    db.flush()

    base_img = BaselineImage(
        baseline_id=base_rec.id,
        file_path="/uploads/baseline_farm001_sowing.jpg",
        file_hash="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
        phash="a8f0e0c4b2d10077",
        gps_latitude=23.0184,
        gps_longitude=76.8820,
        view_angle="North-Facing Panoramic Landmark",
        landmarks_detected=["borewell_shed_east", "neem_tree_north", "drainage_trench"],
    )
    db.add(base_img)
    db.commit()

    print("[*] Seeding IoT Soil Sensors & Telemetry...")
    sensor1 = SoilSensor(
        farm_id=farm1.id,
        device_id="ESP32-SOIL-MP-SEH-001",
        model_type="TwinBit SoilNode Pro (NPK+EC+pH)",
        latitude=23.0185,
        longitude=76.8821,
        depth_cm=15.0,
        battery_level_percent=92.0,
    )
    db.add(sensor1)
    db.flush()

    # Generate 7 days of simulated readings
    readings = generate_simulated_readings(sensor_id=sensor1.id, days=7, simulate_flood=True)
    for r in readings:
        s_read = SoilReading(**r)
        db.add(s_read)
    db.commit()

    print("[*] Seeding Weather & Satellite Records...")
    w_rec = WeatherRecord(
        farm_id=farm1.id,
        temperature_celsius=31.2,
        relative_humidity_percent=82.0,
        rainfall_mm=64.5,
        wind_speed_kmh=28.0,
        precipitation_probability=90.0,
        weather_condition="Severe Inundation & Squall",
        flood_risk_level="HIGH",
        hail_risk_level="MEDIUM",
    )
    db.add(w_rec)

    w_alert = WeatherAlert(
        district="Sehore",
        state="Madhya Pradesh",
        alert_type="HEAVY_RAINFALL_AND_SQUALL",
        severity="ORANGE",
        headline="Orange Alert: Severe Inundation & Gusty Winds Expected in Sehore",
        description="Localized waterlogging and lodging risk for Kharif crops over next 48 hours.",
        valid_until=now + timedelta(days=2),
    )
    db.add(w_alert)

    sat_obs = SatelliteObservation(
        farm_id=farm1.id,
        mean_ndvi=0.41,
        min_ndvi=0.22,
        max_ndvi=0.65,
        vegetation_health_status="SUDDEN_DECLINE_ANOMALY",
        anomaly_detected=True,
        change_rate_percent=-32.5,
    )
    db.add(sat_obs)

    # NDVI Historical points
    trajectory = [0.32, 0.48, 0.62, 0.74, 0.78, 0.76, 0.41]
    for i, val in enumerate(trajectory):
        d = now - timedelta(weeks=len(trajectory) - 1 - i)
        n_rec = NDVIRecord(farm_id=farm1.id, date=d, ndvi_value=val, historical_avg_ndvi=0.75, status="ANOMALY" if val < 0.50 else "NORMAL")
        db.add(n_rec)
    db.commit()

    print("[*] Seeding Disaster Event & Claim Workflow (Cycle B)...")
    disaster = DisasterEvent(
        disaster_type="FLOOD_AND_LODGING",
        state="Madhya Pradesh",
        district="Sehore",
        tehsil="Ashta",
        severity="SEVERE",
        estimated_affected_area_ha=1450.0,
        official_notification_number="MP-DISASTER-REV-2026-081",
        description="Incessant precipitation leading to waterlogging and vegetative lodging in Ashta tehsil.",
    )
    db.add(disaster)
    db.flush()

    dmg_report = DamageReport(
        farm_id=farm1.id,
        disaster_event_id=disaster.id,
        report_code="DMG-2026-0001",
        loss_category="LODGING_AND_WATERLOGGING",
        farmer_reported_loss_percentage=75.0,
        description="Heavy squall and waterlogging flattened soybean crop across central 2 hectares.",
        status="CLAIM_CREATED",
    )
    db.add(dmg_report)
    db.flush()

    evidence = DamageEvidence(
        damage_report_id=dmg_report.id,
        file_path="/uploads/damage_lodging_farm001.jpg",
        file_name="damage_lodging_farm001.jpg",
        file_size_bytes=2458900.0,
        file_sha256="c7be1e92d0019283749817293810293847561029384756102938475610293847",
        phash="a8f0e0c4b2d10077",
        gps_latitude=23.0185,
        gps_longitude=76.8821,
    )
    db.add(evidence)
    db.flush()

    val = EvidenceValidation(
        evidence_id=evidence.id,
        blur_score=142.5,
        is_blurry=False,
        mean_luminance=112.0,
        is_exposure_acceptable=True,
        resolution_width=1920.0,
        resolution_height=1080.0,
        passed_quality_gate=True,
        validation_remarks="Quality Gate Passed: High sharpness, optimal exposure, and HD resolution.",
    )
    db.add(val)

    fraud = FraudCheck(
        evidence_id=evidence.id,
        is_inside_geofence=True,
        distance_to_boundary_meters=0.0,
        geofence_status="INSIDE",
        duplicate_image_flag=False,
        min_phash_hamming_distance=32.0,
        baseline_match_score=0.89,
        landmarks_aligned=True,
        overall_fraud_risk="LOW",
        fraud_risk_score=0.06,
        flag_reasons=[],
        requires_manual_audit=False,
    )
    db.add(fraud)

    assessment = DamageAssessment(
        damage_report_id=dmg_report.id,
        ai_model_name="SAMRIDH-SegFormer-Agri-v2",
        ai_model_version="2.1.0-demo",
        total_analyzed_area_px=2073600.0,
        healthy_canopy_area_px=642816.0,
        damaged_area_px=1430784.0,
        damage_percentage=69.0,
        primary_damage_type="LODGING_CANOPY_COLLAPSE",
        confidence_score=0.94,
        segment_breakdown={"severely_lodged": 51.5, "partially_bent": 17.5, "healthy_standing": 31.0},
        processing_time_ms=158.0,
        warnings=["DEMO / SIMULATED AI RESULT: Field officer verification recommended before PMFBY settlement."],
    )
    db.add(assessment)

    claim = Claim(
        claim_number="PMFBY-CLAIM-2026-MP-0001",
        damage_report_id=dmg_report.id,
        farm_id=farm1.id,
        farmer_id=farmer_profile.id,
        crop_season_name="Kharif 2026",
        ai_damage_percentage=69.0,
        ai_confidence_score=0.92,
        ai_fraud_risk="LOW",
        estimated_payout_amount=82800.0,  # 2.5ha * 48,000 * 69%
        status="OFFICER_REVIEW",
        assigned_officer_id=officer_profile.id,
        pmfby_application_id="PMFBY-APP-2026-MP-984210",
    )
    db.add(claim)
    db.flush()

    evt1 = ClaimEvent(
        claim_id=claim.id,
        event_type="CLAIM_INITIATED",
        actor_role="FARMER",
        actor_id=farmer_user.id,
        message="Claim intimation registered by Ramesh Kumar for severe crop lodging and waterlogging.",
    )
    evt2 = ClaimEvent(
        claim_id=claim.id,
        event_type="AI_MULTIMODAL_ASSESSMENT_COMPLETED",
        actor_role="SYSTEM",
        message="AI Multimodal Assessment: 69.0% loss estimated (Confidence: 92%). Estimated payout: ₹82,800.00.",
    )
    db.add(evt1)
    db.add(evt2)

    print("[*] Seeding AI Models & Proactive Advisories...")
    models = [
        AIModelRegistry(name="SAMRIDH-YOLOv11-CropDisease-Vision", task_type="CROP_DISEASE", version="1.4.2", accuracy_metric="mAP@0.5: 0.932"),
        AIModelRegistry(name="SAMRIDH-SegFormer-Agri-v2", task_type="DAMAGE_SEGMENTATION", version="2.1.0", accuracy_metric="mIoU: 0.884"),
        AIModelRegistry(name="SAMRIDH-Sentinel2-NDVI-Temporal", task_type="SATELLITE_NDVI", version="1.2.0", accuracy_metric="Correlation: 0.91"),
        AIModelRegistry(name="SAMRIDH-MultiSignal-FraudRadar", task_type="FRAUD_DETECTION", version="3.0.1", accuracy_metric="ROC-AUC: 0.965"),
    ]
    for m in models:
        db.add(m)

    adv = Advisory(
        farm_id=farm1.id,
        category="DRAINAGE_AND_LODGING",
        priority="URGENT",
        title="Immediate Water Drainage & Post-Lodging Care",
        title_hi="तत्काल जल निकासी एवं फसल झुकाव प्रबंधन",
        message="Heavy water accumulation detected in lower elevation parcel. Open field furrows immediately to drain standing water and apply 0.5% zinc spray once topsoil aerates.",
        message_hi="खेत के निचले हिस्से में पानी जमा है। नालियां खोलकर तुरंत पानी निकालें और मिट्टी सूखने पर 0.5% जिंक का छिड़काव करें।",
        reasoning={"soil_moisture": 84.5, "rainfall_mm": 64.5, "damage_pct": 69.0},
        action_items=["Open field drainage furrows", "Avoid heavy tractor movement on wet soil", "Monitor for secondary fungal infection"],
    )
    db.add(adv)

    db.commit()
    db.close()
    print("[+] Database successfully seeded with full SAMRIDH-AI demo ecosystem!")


if __name__ == "__main__":
    seed_database()
