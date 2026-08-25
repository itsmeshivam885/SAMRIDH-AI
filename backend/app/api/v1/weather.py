from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.weather import WeatherRiskAnalysis, WeatherRecordRead, WeatherAlertRead
from app.schemas.common import APIResponse
from app.integrations.weather.mock import weather_provider
from app.models.farm import Farm
from datetime import datetime, timezone

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])


@router.get("/farm/{farm_id}/current", response_model=APIResponse[dict])
def get_farm_weather(farm_id: str, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    lat = farm.center_latitude if farm else 23.2
    lon = farm.center_longitude if farm else 77.08
    
    curr = weather_provider.get_current_weather(lat, lon)
    forecast = weather_provider.get_forecast(lat, lon, days=5)

    return APIResponse(
        success=True,
        data={
            "current": curr,
            "forecast": forecast,
            "overall_meteorological_risk": curr.get("flood_risk_level", "HIGH"),
        }
    )
