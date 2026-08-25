from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Advisory, Notification, Grievance
from app.schemas.advisory import AdvisoryRead
from app.schemas.common import APIResponse

router = APIRouter(prefix="/notifications", tags=["Advisories & Alerts"])


@router.get("/advisories", response_model=APIResponse[List[AdvisoryRead]])
def get_farmer_advisories(
    farm_id: str,
    db: Session = Depends(get_db),
):
    advisories = db.query(Advisory).filter(Advisory.farm_id == farm_id).order_by(Advisory.generated_at.desc()).all()
    if not advisories:
        # Generate on the fly if none stored yet
        from app.ai.advisory import advisory_ai
        adv_data = advisory_ai.generate_proactive_advisory(
            crop_name="Soybean",
            growth_stage="Flowering / Pod Formation",
            soil_moisture=52.4,
            water_stress_index=0.05,
            temperature=28.5,
            rainfall_expected_mm=2.0,
            ndvi_health="HEALTHY",
        )
        adv = Advisory(
            farm_id=farm_id,
            category=adv_data["category"],
            priority=adv_data["priority"],
            title=adv_data["title"],
            title_hi=adv_data["title_hi"],
            message=adv_data["message"],
            message_hi=adv_data["message_hi"],
            reasoning=adv_data["reasoning"],
            action_items=adv_data["action_items"],
        )
        db.add(adv)
        db.commit()
        db.refresh(adv)
        advisories = [adv]

    return APIResponse(success=True, data=advisories)
