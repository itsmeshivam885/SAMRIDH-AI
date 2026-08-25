import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from app.iot.sensor_service import compute_soil_stress_metrics


def generate_simulated_readings(
    sensor_id: str,
    days: int = 7,
    interval_hours: int = 4,
    base_moisture: float = 52.0,
    simulate_flood: bool = False,
    simulate_drought: bool = False,
) -> List[Dict[str, Any]]:
    """
    Generate synthetic historical IoT soil readings for realistic dashboard graphing.
    """
    readings = []
    now = datetime.now(timezone.utc)
    total_intervals = (days * 24) // interval_hours

    current_moisture = base_moisture
    for i in range(total_intervals, 0, -1):
        reading_time = now - timedelta(hours=i * interval_hours)
        
        # Diurnal temperature cycle (hotter at 14:00, cooler at 04:00)
        hour = reading_time.hour
        temp_cycle = 24.0 + 8.0 * (1.0 - abs(hour - 14) / 12.0)
        soil_temp = round(temp_cycle + random.uniform(-1.0, 1.0), 1)

        # Moisture dynamics
        if simulate_flood and i < total_intervals // 3:
            current_moisture = min(96.0, current_moisture + random.uniform(8.0, 15.0))
        elif simulate_drought and i < total_intervals // 2:
            current_moisture = max(14.0, current_moisture - random.uniform(0.5, 1.2))
        else:
            current_moisture = max(25.0, min(80.0, current_moisture + random.uniform(-1.5, 1.2)))

        metrics = compute_soil_stress_metrics(
            moisture=current_moisture,
            temperature=soil_temp,
            nitrogen=42.0 + random.uniform(-4.0, 4.0),
            phosphorus=21.0 + random.uniform(-2.0, 2.0),
            potassium=175.0 + random.uniform(-10.0, 10.0),
            ph=7.1 + random.uniform(-0.2, 0.2),
            ec=0.75 + random.uniform(-0.1, 0.1),
        )

        readings.append({
            "sensor_id": sensor_id,
            "timestamp": reading_time,
            "soil_moisture_percent": round(current_moisture, 1),
            "soil_temperature_celsius": soil_temp,
            "nitrogen_mg_kg": round(42.0 + random.uniform(-4.0, 4.0), 1),
            "phosphorus_mg_kg": round(21.0 + random.uniform(-2.0, 2.0), 1),
            "potassium_mg_kg": round(175.0 + random.uniform(-10.0, 10.0), 1),
            "ph_level": round(7.1 + random.uniform(-0.2, 0.2), 2),
            "electrical_conductivity_us_cm": round(0.75 + random.uniform(-0.1, 0.1), 2),
            "water_stress_index": metrics["water_stress_index"],
            "nutrient_stress_flag": metrics["nutrient_stress_flag"],
            "status_label": metrics["status_label"],
        })

    return readings
