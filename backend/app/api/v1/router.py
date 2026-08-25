from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.farms import router as farms_router
from app.api.v1.soil import router as soil_router
from app.api.v1.weather import router as weather_router
from app.api.v1.satellite import router as satellite_router
from app.api.v1.ai import router as ai_router
from app.api.v1.damage import router as damage_router
from app.api.v1.claims import router as claims_router
from app.api.v1.officer import router as officer_router
from app.api.v1.admin import router as admin_router
from app.api.v1.notifications import router as notifications_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(farms_router)
api_router.include_router(soil_router)
api_router.include_router(weather_router)
api_router.include_router(satellite_router)
api_router.include_router(ai_router)
api_router.include_router(damage_router)
api_router.include_router(claims_router)
api_router.include_router(officer_router)
api_router.include_router(admin_router)
api_router.include_router(notifications_router)
