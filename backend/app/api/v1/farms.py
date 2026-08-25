from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmRead, FarmGISSummary
from app.schemas.farmer import FarmerProfile
from app.schemas.common import APIResponse
from app.services.farm_service import farm_service

router = APIRouter(prefix="/farms", tags=["Farms & Land"])


@router.get("", response_model=APIResponse[List[FarmRead]])
def list_my_farms(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.farmer_profile:
        return APIResponse(success=True, data=[])
    farms = farm_service.get_farmer_farms(db, current_user.farmer_profile.id)
    return APIResponse(success=True, data=farms)


@router.post("", response_model=APIResponse[FarmRead])
def create_farm(payload: FarmCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.farmer_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"code": "NOT_A_FARMER", "message": "User must have farmer profile to add a farm"})
    farm = farm_service.create_farm(db, current_user.farmer_profile.id, payload)
    return APIResponse(success=True, data=farm)


@router.get("/{farm_id}", response_model=APIResponse[FarmRead])
def get_farm_details(farm_id: str, db: Session = Depends(get_db)):
    farm = farm_service.get_farm_by_id(db, farm_id)
    return APIResponse(success=True, data=farm)


@router.get("/gis/all", response_model=APIResponse[List[FarmGISSummary]])
def get_all_gis_farms(db: Session = Depends(get_db)):
    farms = farm_service.get_all_farms_for_gis(db)
    return APIResponse(success=True, data=farms)
