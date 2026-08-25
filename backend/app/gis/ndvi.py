from typing import Dict, Any, List
from datetime import datetime, timedelta


def analyze_ndvi_trend(current_ndvi: float, historical_baseline_ndvi: float) -> Dict[str, Any]:
    """
    Analyze satellite NDVI drop against seasonal expected baseline.
    Detects sudden severe drops indicative of flood submersion, lodging, or pest damage.
    """
    delta = current_ndvi - historical_baseline_ndvi
    percentage_change = (delta / (historical_baseline_ndvi + 1e-6)) * 100.0

    if current_ndvi >= 0.65:
        status = "EXCELLENT_CANOPY_VIGOR"
        anomaly = False
    elif current_ndvi >= 0.45:
        status = "MODERATE_VEGETATION"
        anomaly = False
    elif percentage_change <= -25.0:
        status = "CRITICAL_VEGETATION_DROP_ANOMALY"
        anomaly = True
    elif current_ndvi < 0.30:
        status = "SEVERE_STRESS_OR_BARE_SOIL"
        anomaly = True
    else:
        status = "NORMAL_SEASONAL_VARIATION"
        anomaly = False

    return {
        "current_ndvi": round(current_ndvi, 3),
        "baseline_ndvi": round(historical_baseline_ndvi, 3),
        "percentage_change": round(percentage_change, 2),
        "anomaly_detected": anomaly,
        "status": status,
        "satellite_evidence_confidence": "HIGH" if abs(percentage_change) > 20 else "MEDIUM",
    }
