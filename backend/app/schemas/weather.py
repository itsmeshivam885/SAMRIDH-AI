from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class WeatherRecordRead(BaseModel):
    id: str
    recorded_at: datetime
    source: str
    temperature_celsius: float
    relative_humidity_percent: float
    rainfall_mm: float
    wind_speed_kmh: float
    precipitation_probability: float
    weather_condition: str
    heat_stress_index: float
    flood_risk_level: str
    hail_risk_level: str
    drought_risk_level: str

    model_config = ConfigDict(from_attributes=True)


class WeatherAlertRead(BaseModel):
    id: str
    district: str
    state: str
    alert_type: str
    severity: str
    headline: str
    description: str
    valid_from: datetime
    valid_until: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class WeatherRiskAnalysis(BaseModel):
    farm_id: str
    current_weather: WeatherRecordRead
    active_alerts: List[WeatherAlertRead] = []
    overall_meteorological_risk: str
    forecast_summary: str
