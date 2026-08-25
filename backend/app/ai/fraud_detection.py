from typing import Dict, Any, List, Optional
from app.utils.hashing import hamming_distance
from app.core.config import settings


class FraudDetectionAIService:
    """
    Multi-Signal Fraud & Evidence Consistency Engine.
    Fuses Geofence, Perceptual Hashing, Baseline Landmark Comparison, and Temporal Metadata.
    """

    def evaluate_evidence_integrity(
        self,
        geofence_result: Dict[str, Any],
        evidence_phash: str,
        existing_evidence_phashes: List[Dict[str, str]], # [{"id": "...", "phash": "..."}]
        baseline_match_score: float = 0.88,
        time_difference_hours: float = 2.0,
    ) -> Dict[str, Any]:
        flag_reasons = []
        fraud_risk_score = 0.0

        # Signal 1: Geofence Validation
        is_inside = geofence_result.get("is_inside", True)
        distance = geofence_result.get("distance_to_boundary_meters", 0.0)
        geofence_status = geofence_result.get("geofence_status", "INSIDE")

        if not is_inside:
            if geofence_status == "OUTSIDE":
                fraud_risk_score += 0.45
                flag_reasons.append(f"Photo captured {distance:.1f}m OUTSIDE registered farm boundary.")
            elif geofence_status == "BORDERLINE":
                fraud_risk_score += 0.15
                flag_reasons.append(f"Photo captured near polygon border ({distance:.1f}m).")

        # Signal 2: Duplicate / Recycled Image Check via pHash Hamming Distance
        duplicate_flag = False
        min_distance = 64
        matched_id = None

        if evidence_phash:
            for item in existing_evidence_phashes:
                curr_phash = item.get("phash")
                if curr_phash:
                    dist = hamming_distance(evidence_phash, curr_phash)
                    if dist < min_distance:
                        min_distance = dist
                        matched_id = item.get("id")
                    if dist <= settings.PHASH_HAMMING_DISTANCE_THRESHOLD:
                        duplicate_flag = True

        if duplicate_flag:
            fraud_risk_score += 0.50
            flag_reasons.append(f"Duplicate/recycled image detected (Hamming distance {min_distance} <= threshold {settings.PHASH_HAMMING_DISTANCE_THRESHOLD}).")

        # Signal 3: Baseline Consistency Check
        if baseline_match_score < settings.SIFT_FEATURE_MATCH_THRESHOLD:
            fraud_risk_score += 0.25
            flag_reasons.append(f"Low visual landmark correlation with sowing baseline ({baseline_match_score:.2f} < {settings.SIFT_FEATURE_MATCH_THRESHOLD}).")

        # Normalize score
        fraud_risk_score = min(1.0, max(0.0, fraud_risk_score))

        if fraud_risk_score >= 0.60:
            overall_risk = "HIGH"
            requires_audit = True
        elif fraud_risk_score >= 0.25:
            overall_risk = "MEDIUM"
            requires_audit = True
        else:
            overall_risk = "LOW"
            requires_audit = False

        return {
            "is_inside_geofence": is_inside,
            "distance_to_boundary_meters": distance,
            "geofence_status": geofence_status,
            "duplicate_image_flag": duplicate_flag,
            "min_phash_hamming_distance": float(min_distance),
            "matched_duplicate_evidence_id": matched_id,
            "baseline_match_score": round(baseline_match_score, 3),
            "landmarks_aligned": baseline_match_score >= settings.SIFT_FEATURE_MATCH_THRESHOLD,
            "overall_fraud_risk": overall_risk,
            "fraud_risk_score": round(fraud_risk_score, 2),
            "flag_reasons": flag_reasons,
            "requires_manual_audit": requires_audit,
        }


fraud_detection_ai = FraudDetectionAIService()
