import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.audit import CropScan
from app.schemas.common import APIResponse
from app.schemas.admin import AICropDoctorQuery, AICropDoctorResponse
from app.ai.crop_health import crop_health_ai
from app.ai.advisory import advisory_ai

router = APIRouter(prefix="/ai", tags=["AI Engines & Crop Doctor"])


@router.post("/crop-scan", response_model=APIResponse[dict])
async def perform_crop_scan(
    farm_id: str = Form("farm_001"),
    crop_name: str = Form("Soybean"),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await image.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty image file provided")

    # Run AI Analysis on real uploaded image bytes
    res = crop_health_ai.analyze_crop_image(contents, crop_name=crop_name)

    # Save real uploaded image to disk for display
    file_id = str(uuid.uuid4())[:8]
    clean_filename = f"scan_{file_id}_{image.filename}".replace(" ", "_")
    filepath = os.path.join(settings.UPLOAD_DIR, clean_filename)
    try:
        with open(filepath, "wb") as f:
            f.write(contents)
        res["image_url"] = f"http://127.0.0.1:8000/uploads/{clean_filename}"
    except Exception:
        res["image_url"] = ""

    # Store crop scan record in database
    try:
        scan = CropScan(
            farm_id=farm_id,
            image_url=res.get("image_url", ""),
            health_score=res["crop_health_score"],
            detected_condition=res["detected_condition"],
            condition_category=res["category"],
            confidence=res["confidence"],
            advisory_recommendation=res["treatment_advisory_en"],
            advisory_recommendation_hi=res["treatment_advisory_hi"],
        )
        db.add(scan)
        db.commit()
    except Exception:
        db.rollback()

    return APIResponse(success=True, data=res)


@router.post("/crop-doctor", response_model=APIResponse[AICropDoctorResponse])
def chat_with_crop_doctor(query: AICropDoctorQuery, db: Session = Depends(get_db)):
    farm_context = {
        "farm_id": query.farm_id or "farm_001",
        "crop_name": "Soybean",
        "soil_moisture": 52.4,
        "health_score": 87.0,
    }
    resp = advisory_ai.answer_crop_doctor_query(query.question, farm_context)
    return APIResponse(success=True, data=AICropDoctorResponse(**resp))
