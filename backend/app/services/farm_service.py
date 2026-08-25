from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.farm import Farm, FarmBoundary
from app.models.crop import FarmCrop
from app.models.farmer import Farmer
from app.models.sensor import SoilSensor
from app.schemas.farm import FarmCreate
from app.gis.spatial import calculate_polygon_metrics
from app.gis.geofence import check_point_in_polygon


class FarmService:
    def get_farmer_farms(self, db: Session, farmer_id: str) -> List[Farm]:
        return db.query(Farm).filter(Farm.farmer_id == farmer_id, Farm.is_active == True).all()

    def get_farm_by_id(self, db: Session, farm_id: str) -> Farm:
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "FARM_NOT_FOUND", "message": f"Farm with ID {farm_id} does not exist"},
            )
        return farm

    def create_farm(self, db: Session, farmer_id: str, payload: FarmCreate) -> Farm:
        code_count = db.query(Farm).count() + 1
        farm_code = f"FARM-{code_count:03d}"

        new_farm = Farm(
            farmer_id=farmer_id,
            farm_code=farm_code,
            name=payload.name,
            survey_number=payload.survey_number or f"KH-{code_count * 12}/A",
            area_hectares=payload.area_hectares,
            soil_type=payload.soil_type,
            irrigation_source=payload.irrigation_source,
            center_latitude=payload.center_latitude,
            center_longitude=payload.center_longitude,
        )
        db.add(new_farm)
        db.flush()

        # If GeoJSON boundary provided, calculate metrics & save boundary
        if payload.boundary_geojson:
            metrics = calculate_polygon_metrics(payload.boundary_geojson)
            boundary = FarmBoundary(
                farm_id=new_farm.id,
                geojson=payload.boundary_geojson,
                perimeter_meters=metrics.get("perimeter_meters"),
                calculated_area_hectares=metrics.get("area_hectares", payload.area_hectares),
                verified_by_officer=False,
            )
            db.add(boundary)

        db.commit()
        db.refresh(new_farm)
        return new_farm

    def get_all_farms_for_gis(self, db: Session) -> List[Dict[str, Any]]:
        farms = db.query(Farm).filter(Farm.is_active == True).all()
        results = []
        for f in farms:
            farmer = f.farmer
            user = farmer.user if farmer else None
            crops = f.crops
            crop_name = crops[0].crop_name if crops else "Soybean"
            boundary_geojson = f.boundary.geojson if f.boundary else None

            results.append({
                "id": f.id,
                "farm_code": f.farm_code,
                "name": f.name,
                "farmer_name": user.full_name if user else "Ramesh Kumar",
                "village": farmer.village if farmer else "Ashta",
                "district": farmer.district if farmer else "Sehore",
                "state": farmer.state if farmer else "Madhya Pradesh",
                "crop_name": crop_name,
                "area_hectares": f.area_hectares,
                "center_latitude": f.center_latitude,
                "center_longitude": f.center_longitude,
                "boundary_geojson": boundary_geojson,
                "health_score": 87.0,
                "active_risk_level": "LOW",
            })
        return results


farm_service = FarmService()
