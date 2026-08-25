from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.claim import Claim
from app.schemas.claim import ClaimRead, ClaimReviewAction, SettlementStatusUpdate
from app.schemas.common import APIResponse
from app.services.claim_service import claim_service

router = APIRouter(prefix="/claims", tags=["PMFBY Claims & Settlement"])


@router.get("", response_model=APIResponse[List[ClaimRead]])
def list_claims(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # If farmer, only return farmer's claims
    if current_user.role == "farmer" and current_user.farmer_profile:
        claims = db.query(Claim).filter(Claim.farmer_id == current_user.farmer_profile.id).order_by(Claim.created_at.desc()).all()
    else:
        claims = claim_service.get_all_claims(db, status_filter=status)
    return APIResponse(success=True, data=claims)


@router.post("/from-report/{damage_report_id}", response_model=APIResponse[ClaimRead])
def create_claim_from_report(
    damage_report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    claim = claim_service.create_claim_from_damage_report(db, damage_report_id)
    return APIResponse(success=True, data=claim)


@router.get("/{claim_id}", response_model=APIResponse[ClaimRead])
def get_claim_details(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found"})
    return APIResponse(success=True, data=claim)
