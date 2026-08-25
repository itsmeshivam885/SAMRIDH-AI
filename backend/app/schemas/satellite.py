from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class NDVIRecordRead(BaseModel):
    id: str
    date: datetime
    ndvi_value: float
    historical_avg_ndvi: float
    status: str

    model_config = ConfigDict(from_attributes=True)


class SatelliteObservationRead(BaseModel):
    id: str
    farm_id: str
    satellite_source: str
    acquisition_date: datetime
    cloud_cover_percentage: float
    mean_ndvi: float
    min_ndvi: Optional[float] = None
    max_ndvi: Optional[float] = None
    mean_ndwi: Optional[float] = None
    vegetation_health_status: str
    anomaly_detected: bool
    change_rate_percent: float

    model_config = ConfigDict(from_attributes=True)


class NDVIAnomalyResponse(BaseModel):
    farm_id: str
    current_ndvi: float
    baseline_ndvi: float
    percentage_deviation: float
    anomaly_detected: bool
    status: str
    time_series: List[NDVIRecordRead] = []
