from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.sensor import SoilSensor, SoilReading
from app.models.farm import Farm
from app.schemas.soil import SoilSensorRead, SoilReadingCreate, SoilReadingRead, SoilStressSummary
from app.schemas.common import APIResponse
from app.iot.sensor_service import compute_soil_stress_metrics
from app.iot.simulator import generate_simulated_readings

router = APIRouter(prefix="/soil", tags=["IoT & Soil Monitoring"])


@router.get("/farm/{farm_id}/summary", response_model=APIResponse[SoilStressSummary])
def get_soil_summary(farm_id: str, db: Session = Depends(get_db)):
    sensors = db.query(SoilSensor).filter(SoilSensor.farm_id == farm_id, SoilSensor.is_active == True).all()
    if not sensors:
        # Default representative baseline
        return APIResponse(
            success=True,
            data=SoilStressSummary(
                farm_id=farm_id,
                sensor_count=1,
                avg_soil_moisture_percent=52.4,
                avg_soil_temperature_celsius=27.8,
                avg_ph=7.2,
                moisture_status="OPTIMAL",
                water_stress_score=0.05,
                recommendation="Soil root zone moisture is optimal for current crop growth stage.",
            )
        )

    # Get latest readings
    readings = []
    for s in sensors:
        latest = db.query(SoilReading).filter(SoilReading.sensor_id == s.id).order_by(SoilReading.timestamp.desc()).first()
        if latest:
            readings.append(latest)

    avg_moisture = sum(r.soil_moisture_percent for r in readings) / len(readings) if readings else 50.0
    avg_temp = sum(r.soil_temperature_celsius for r in readings) / len(readings) if readings else 26.0
    avg_ph = sum(r.ph_level or 7.0 for r in readings) / len(readings) if readings else 7.0

    stress = compute_soil_stress_metrics(avg_moisture, avg_temp)

    return APIResponse(
        success=True,
        data=SoilStressSummary(
            farm_id=farm_id,
            sensor_count=len(sensors),
            avg_soil_moisture_percent=round(avg_moisture, 1),
            avg_soil_temperature_celsius=round(avg_temp, 1),
            avg_ph=round(avg_ph, 2),
            moisture_status=stress["status_label"],
            water_stress_score=stress["water_stress_index"],
            recommendation=f"Soil status: {stress['status_label']}. Water stress index: {stress['water_stress_index']}.",
        )
    )


@router.get("/farm/{farm_id}/history", response_model=APIResponse[List[SoilReadingRead]])
def get_soil_history(farm_id: str, days: int = 7, db: Session = Depends(get_db)):
    sensor = db.query(SoilSensor).filter(SoilSensor.farm_id == farm_id).first()
    if not sensor:
        sim_readings = generate_simulated_readings(sensor_id="ESP32-DEMO", days=days)
        return APIResponse(success=True, data=sim_readings)

    readings = db.query(SoilReading).filter(SoilReading.sensor_id == sensor.id).order_by(SoilReading.timestamp.desc()).limit(days * 6).all()
    if not readings:
        sim_readings = generate_simulated_readings(sensor_id=sensor.id, days=days)
        return APIResponse(success=True, data=sim_readings)

    return APIResponse(success=True, data=readings)
