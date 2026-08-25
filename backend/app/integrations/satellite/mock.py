from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from app.integrations.satellite.base import BaseSatelliteProvider


class MockSatelliteProvider(BaseSatelliteProvider):
    """
    Mock Sentinel-2 MSI / ISRO Bhuvan satellite provider for demo execution.
    """

    def get_latest_observation(self, farm_id: str, lat: float, lon: float) -> Dict[str, Any]:
        return {
            "farm_id": farm_id,
            "satellite_source": "Sentinel-2 L2A (10m Multispectral)",
            "acquisition_date": datetime.now(timezone.utc).isoformat(),
            "cloud_cover_percentage": 3.2,
            "mean_ndvi": 0.42,
            "min_ndvi": 0.21,
            "max_ndvi": 0.68,
            "mean_ndwi": 0.18,
            "vegetation_health_status": "SIGNIFICANT_VEGETATION_DROP",
            "anomaly_detected": True,
            "change_rate_percent": -34.8,
            "resolution_meters": 10.0,
            "is_mock_demo": True,
        }

    def get_historical_ndvi_series(self, farm_id: str, weeks: int = 8) -> List[Dict[str, Any]]:
        # Sowing healthy growth -> sudden drop in recent week reflecting calamity
        now = datetime.now(timezone.utc)
        trajectory = [0.28, 0.42, 0.58, 0.72, 0.76, 0.74, 0.42, 0.38]
        expected_avg = [0.30, 0.45, 0.60, 0.70, 0.75, 0.78, 0.79, 0.80]
        
        series = []
        for i in range(min(weeks, len(trajectory))):
            pt_date = now - timedelta(weeks=weeks - 1 - i)
            val = trajectory[i]
            exp = expected_avg[i]
            diff = val - exp
            status = "ANOMALY_DROP" if diff < -0.20 else "NORMAL"
            series.append({
                "date": pt_date.strftime("%Y-%m-%d"),
                "ndvi_value": val,
                "historical_avg_ndvi": exp,
                "status": status,
            })
        return series


satellite_provider = MockSatelliteProvider()
