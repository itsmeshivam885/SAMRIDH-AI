from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.satellite import NDVIAnomalyResponse, NDVIRecordRead
from app.schemas.common import APIResponse
from app.integrations.satellite.mock import satellite_provider
from app.models.farm import Farm

router = APIRouter(prefix="/satellite", tags=["Satellite Intelligence & NDVI"])


@router.get("/farm/{farm_id}/ndvi", response_model=APIResponse[dict])
def get_farm_satellite_ndvi(farm_id: str, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    lat = farm.center_latitude if farm else 23.2
    lon = farm.center_longitude if farm else 77.08

    obs = satellite_provider.get_latest_observation(farm_id, lat, lon)
    series = satellite_provider.get_historical_ndvi_series(farm_id, weeks=8)

    return APIResponse(
        success=True,
        data={
            "observation": obs,
            "ndvi_time_series": series,
            "canopy_trend": "DECLINE_DETECTED" if obs.get("anomaly_detected") else "HEALTHY",
        }
    )
