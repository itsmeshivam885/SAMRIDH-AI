from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.damage import DamageReport
from app.schemas.damage import DamageReportCreate, DamageReportRead, DamageEvidenceRead
from app.schemas.common import APIResponse
from app.services.claim_service import claim_service
from app.services.evidence_service import evidence_service

router = APIRouter(prefix="/damage", tags=["Damage Reporting & Loss Assessment"])


@router.post("/report", response_model=APIResponse[DamageReportRead])
def create_damage_report(
    payload: DamageReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farmer_id = current_user.farmer_profile.id if current_user.farmer_profile else "demo-farmer-id"
    report = claim_service.create_damage_report(db, farmer_id, payload)
    return APIResponse(success=True, data=report)


@router.post("/{damage_report_id}/evidence", response_model=APIResponse[DamageEvidenceRead])
async def upload_damage_evidence(
    damage_report_id: str,
    gps_latitude: float = Form(...),
    gps_longitude: float = Form(...),
    device_model: str = Form("Android Mobile (Demo)"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    evidence = await evidence_service.process_and_store_evidence(
        db=db,
        damage_report_id=damage_report_id,
        file=file,
        gps_latitude=gps_latitude,
        gps_longitude=gps_longitude,
        device_model=device_model,
    )
    return APIResponse(success=True, data=evidence)


@router.get("/report/{damage_report_id}", response_model=APIResponse[DamageReportRead])
def get_damage_report(damage_report_id: str, db: Session = Depends(get_db)):
    report = db.query(DamageReport).filter(DamageReport.id == damage_report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Damage report not found"})
    return APIResponse(success=True, data=report)
