import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from app.integrations.weather.base import BaseWeatherProvider


class MockWeatherProvider(BaseWeatherProvider):
    """
    Simulated IMD weather feed providing realistic forecasts, precipitation, and heat alerts.
    """

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        return {
            "source": "IMD Regional Weather Radar (Bhopal Station)",
            "temperature_celsius": 31.5,
            "relative_humidity_percent": 78.0,
            "rainfall_mm": 42.5,
            "wind_speed_kmh": 22.0,
            "precipitation_probability": 85.0,
            "weather_condition": "Heavy Thunderstorm / Rain Showers",
            "heat_stress_index": 0.1,
            "flood_risk_level": "HIGH",
            "hail_risk_level": "MEDIUM",
            "drought_risk_level": "LOW",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "is_mock_demo": True,
        }

    def get_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict[str, Any]]:
        forecasts = []
        now = datetime.now(timezone.utc)
        conditions = [
            ("Moderate Rain", 28.0, 80.0, 18.0),
            ("Heavy Rain & Squall", 26.5, 92.0, 65.0),
            ("Scattered Showers", 29.0, 75.0, 12.0),
            ("Partly Cloudy", 31.0, 65.0, 2.0),
            ("Clear Sunny", 33.5, 55.0, 0.0),
        ]
        for i in range(days):
            day_time = now + timedelta(days=i + 1)
            cond, temp, hum, rain = conditions[i % len(conditions)]
            forecasts.append({
                "date": day_time.strftime("%Y-%m-%d"),
                "day_name": day_time.strftime("%A"),
                "condition": cond,
                "temp_max_celsius": temp + 2.0,
                "temp_min_celsius": temp - 5.0,
                "humidity_percent": hum,
                "expected_rainfall_mm": rain,
                "rain_probability": min(95.0, rain * 1.5 + 20.0),
            })
        return forecasts


weather_provider = MockWeatherProvider()
