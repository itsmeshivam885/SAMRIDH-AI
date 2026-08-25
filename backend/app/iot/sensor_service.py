from typing import Dict, Any, List
from app.models.sensor import SoilReading


def compute_soil_stress_metrics(
    moisture: float,
    temperature: float,
    nitrogen: float = 45.0,
    phosphorus: float = 22.0,
    potassium: float = 180.0,
    ph: float = 7.2,
    ec: float = 0.8,
) -> Dict[str, Any]:
    """
    Calculate water stress index (0.0 to 1.0) and agronomic status
    based on field sensor telemetry.
    """
    # Water Stress Calculation (Optimal range: 45% - 70%)
    if moisture < 20.0:
        water_stress_index = 0.95
        status = "CRITICAL_DROUGHT_DEFICIT"
    elif moisture < 35.0:
        water_stress_index = 0.65
        status = "MODERATE_WATER_DEFICIT"
    elif moisture > 85.0:
        water_stress_index = 0.85
        status = "WATERLOGGED_ROOT_HYPOXIA"
    elif moisture > 75.0:
        water_stress_index = 0.35
        status = "SATURATED_MOISTURE"
    else:
        water_stress_index = 0.05
        status = "OPTIMAL_MOISTURE"

    # Nutrient flag
    nutrient_stress = False
    if (nitrogen and nitrogen < 25.0) or (phosphorus and phosphorus < 12.0) or (potassium and potassium < 100.0):
        nutrient_stress = True

    return {
        "water_stress_index": round(water_stress_index, 2),
        "nutrient_stress_flag": nutrient_stress,
        "status_label": status,
    }
