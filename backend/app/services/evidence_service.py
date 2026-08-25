import os
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from app.models.damage import DamageReport, DamageAssessment
from app.models.evidence import DamageEvidence, EvidenceValidation
from app.models.fraud import FraudCheck
from app.models.farm import Farm
from app.models.baseline import BaselineRecord, BaselineImage
from app.utils.hashing import compute_sha256, compute_phash
from app.utils.image import analyze_image_quality, compare_image_features
from app.gis.geofence import check_point_in_polygon
from app.ai.damage_segmentation import damage_segmentation_ai
from app.ai.fraud_detection import fraud_detection_ai
from app.core.config import settings


class EvidenceService:
    async def process_and_store_evidence(
        self,
        db: Session,
        damage_report_id: str,
        file: UploadFile,
        gps_latitude: float,
        gps_longitude: float,
        device_model: str = "Android Mobile (Demo)",
    ) -> DamageEvidence:
        damage_report = db.query(DamageReport).filter(DamageReport.id == damage_report_id).first()
        if not damage_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DAMAGE_REPORT_NOT_FOUND", "message": "Damage report not found"},
            )

        farm = db.query(Farm).filter(Farm.id == damage_report.farm_id).first()
        contents = await file.read()
        file_size = len(contents)

        # 1. Edge Image Quality Gate
        quality_result = analyze_image_quality(contents)

        # 2. Cryptographic & Perceptual Hashing
        sha256_hash = compute_sha256(contents)
        phash_val = compute_phash(contents)

        # Save file to disk
        file_ext = os.path.splitext(file.filename)[1] or ".jpg"
        unique_filename = f"evidence_{uuid.uuid4().hex[:12]}{file_ext}"
        saved_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        with open(saved_path, "wb") as f:
            f.write(contents)

        # Create DamageEvidence entity
        evidence = DamageEvidence(
            damage_report_id=damage_report.id,
            file_path=saved_path,
            file_name=file.filename,
            mime_type=file.content_type or "image/jpeg",
            file_size_bytes=float(file_size),
            file_sha256=sha256_hash,
            phash=phash_val,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            device_model=device_model,
        )
        db.add(evidence)
        db.flush()

        # Create EvidenceValidation entity
        validation = EvidenceValidation(
            evidence_id=evidence.id,
            blur_score=quality_result["blur_score"],
            is_blurry=quality_result["is_blurry"],
            mean_luminance=quality_result["mean_luminance"],
            is_exposure_acceptable=quality_result["is_exposure_acceptable"],
            resolution_width=quality_result["resolution_width"],
            resolution_height=quality_result["resolution_height"],
            passed_quality_gate=quality_result["passed_quality_gate"],
            validation_remarks=quality_result["validation_remarks"],
        )
        db.add(validation)

        # 3. Fraud Verification Signals
        # 3a. Geofence test
        boundary_geojson = farm.boundary.geojson if farm and farm.boundary else None
        if boundary_geojson:
            geofence_res = check_point_in_polygon(gps_latitude, gps_longitude, boundary_geojson)
        else:
            geofence_res = {"is_inside": True, "distance_to_boundary_meters": 0.0, "geofence_status": "INSIDE"}

        # 3b. Duplicate perceptual hash check against existing evidence
        all_other_evidence = db.query(DamageEvidence).filter(DamageEvidence.id != evidence.id).all()
        existing_hashes = [{"id": e.id, "phash": e.phash} for e in all_other_evidence if e.phash]

        # 3c. Baseline feature match
        baseline_score = 0.88 # standard match in demo

        fraud_eval = fraud_detection_ai.evaluate_evidence_integrity(
            geofence_result=geofence_res,
            evidence_phash=phash_val,
            existing_evidence_phashes=existing_hashes,
            baseline_match_score=baseline_score,
        )

        fraud_check = FraudCheck(
            evidence_id=evidence.id,
            is_inside_geofence=fraud_eval["is_inside_geofence"],
            distance_to_boundary_meters=fraud_eval["distance_to_boundary_meters"],
            geofence_status=fraud_eval["geofence_status"],
            duplicate_image_flag=fraud_eval["duplicate_image_flag"],
            min_phash_hamming_distance=fraud_eval["min_phash_hamming_distance"],
            matched_duplicate_evidence_id=fraud_eval["matched_duplicate_evidence_id"],
            baseline_match_score=fraud_eval["baseline_match_score"],
            landmarks_aligned=fraud_eval["landmarks_aligned"],
            overall_fraud_risk=fraud_eval["overall_fraud_risk"],
            fraud_risk_score=fraud_eval["fraud_risk_score"],
            flag_reasons=fraud_eval["flag_reasons"],
            requires_manual_audit=fraud_eval["requires_manual_audit"],
        )
        db.add(fraud_check)

        # 4. Trigger AI Damage Segmentation
        seg_result = damage_segmentation_ai.segment_damage_evidence(
            image_bytes=contents,
            loss_category=damage_report.loss_category,
            farmer_claimed_percentage=damage_report.farmer_reported_loss_percentage,
        )

        assessment = DamageAssessment(
            damage_report_id=damage_report.id,
            ai_model_name=seg_result["ai_model_name"],
            ai_model_version=seg_result["ai_model_version"],
            total_analyzed_area_px=seg_result["total_analyzed_area_px"],
            healthy_canopy_area_px=seg_result["healthy_canopy_area_px"],
            damaged_area_px=seg_result["damaged_area_px"],
            damage_percentage=seg_result["damage_percentage"],
            primary_damage_type=seg_result["primary_damage_type"],
            confidence_score=seg_result["confidence_score"],
            segment_breakdown=seg_result["segment_breakdown"],
            segmentation_mask_url=seg_result["segmentation_mask_url"],
            processing_time_ms=seg_result["processing_time_ms"],
            warnings=seg_result["warnings"],
        )
        db.add(assessment)

        damage_report.status = "AI_ASSESSED"
        db.commit()
        db.refresh(evidence)
        return evidence


evidence_service = EvidenceService()
