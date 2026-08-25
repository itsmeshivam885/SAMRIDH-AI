from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.officer import Officer, FieldVerification
from app.models.claim import Claim
from app.schemas.claim import ClaimRead, ClaimReviewAction
from app.schemas.officer import OfficerRead, FieldVerificationCreate, FieldVerificationRead
from app.schemas.common import APIResponse
from app.services.claim_service import claim_service

router = APIRouter(prefix="/officer", tags=["Field Officer Workbench"])


@router.get("/claims", response_model=APIResponse[List[ClaimRead]])
def get_officer_claim_queue(
    status: Optional[str] = None,
    current_user: User = Depends(require_roles(["officer", "admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    claims = claim_service.get_all_claims(db, status_filter=status)
    return APIResponse(success=True, data=claims)


@router.post("/claims/{claim_id}/review", response_model=APIResponse[ClaimRead])
def review_claim(
    claim_id: str,
    action: ClaimReviewAction,
    current_user: User = Depends(require_roles(["officer", "admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    officer = current_user.officer_profile
    if not officer:
        # Fallback for demo admin / officer
        officer = db.query(Officer).first()
        if not officer:
            officer = Officer(
                user_id=current_user.id,
                officer_badge_number="OFFICER-MP-001",
                assigned_state="Madhya Pradesh",
                assigned_district="Sehore",
            )
            db.add(officer)
            db.commit()

    updated = claim_service.review_claim_by_officer(db, claim_id, officer, action)
    return APIResponse(success=True, data=updated)
