from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SoilReadingCreate(BaseModel):
    sensor_id: str
    soil_moisture_percent: float
    soil_temperature_celsius: float
    nitrogen_mg_kg: Optional[float] = None
    phosphorus_mg_kg: Optional[float] = None
    potassium_mg_kg: Optional[float] = None
    ph_level: Optional[float] = None
    electrical_conductivity_us_cm: Optional[float] = None


class SoilReadingRead(BaseModel):
    id: str
    sensor_id: str
    timestamp: datetime
    soil_moisture_percent: float
    soil_temperature_celsius: float
    nitrogen_mg_kg: Optional[float] = None
    phosphorus_mg_kg: Optional[float] = None
    potassium_mg_kg: Optional[float] = None
    ph_level: Optional[float] = None
    electrical_conductivity_us_cm: Optional[float] = None
    water_stress_index: float
    nutrient_stress_flag: bool
    status_label: str

    model_config = ConfigDict(from_attributes=True)


class SoilSensorRead(BaseModel):
    id: str
    farm_id: str
    device_id: str
    model_type: str
    latitude: float
    longitude: float
    depth_cm: float
    battery_level_percent: float
    is_active: bool
    latest_reading: Optional[SoilReadingRead] = None

    model_config = ConfigDict(from_attributes=True)


class SoilStressSummary(BaseModel):
    farm_id: str
    sensor_count: int
    avg_soil_moisture_percent: float
    avg_soil_temperature_celsius: float
    avg_ph: float
    moisture_status: str
    water_stress_score: float
    recommendation: str
