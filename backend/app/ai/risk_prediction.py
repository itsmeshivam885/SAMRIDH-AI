from typing import Dict, Any, List


class RiskPredictionAIService:
    """
    Multimodal Risk & Loss Confidence Cross-Validation Engine.
    Fuses ground vision, IoT telemetry, satellite NDVI anomalies, and meteorological alerts.
    """

    def compute_multimodal_claim_confidence(
        self,
        visual_damage_percentage: float,
        visual_confidence: float,
        satellite_anomaly: bool,
        satellite_drop_percentage: float,
        weather_hazard_level: str,
        fraud_risk_score: float,
    ) -> Dict[str, Any]:
        """
        Synthesize multi-source evidence score for officer decision support.
        """
        # Base confidence from computer vision
        fused_score = visual_confidence * 0.40

        # Satellite cross-validation (30% weight)
        if satellite_anomaly and satellite_drop_percentage <= -20.0:
            fused_score += 0.30
        elif satellite_drop_percentage < -10.0:
            fused_score += 0.20
        else:
            fused_score += 0.10

        # Weather correlation (20% weight)
        if weather_hazard_level in ["HIGH", "SEVERE", "EXTREME"]:
            fused_score += 0.20
        elif weather_hazard_level == "MEDIUM":
            fused_score += 0.15
        else:
            fused_score += 0.05

        # Penalize confidence by fraud risk score (10% weight)
        fused_score -= (fraud_risk_score * 0.25)
        fused_confidence = max(0.20, min(0.99, fused_score + 0.10))

        if fused_confidence >= 0.85 and fraud_risk_score < 0.20:
            evidence_grade = "STRONG_CONVERGENT_EVIDENCE"
            officer_recommendation = "AI RECOMMENDS: APPROVE_ASSESSMENT"
        elif fraud_risk_score >= 0.50:
            evidence_grade = "FRAUD_SUSPICION_ALERT"
            officer_recommendation = "AI RECOMMENDS: MANDATORY_PHYSICAL_VERIFICATION"
        elif fused_confidence < 0.60:
            evidence_grade = "INSUFFICIENT_CROSS_CORRELATION"
            officer_recommendation = "AI RECOMMENDS: REQUEST_ADDITIONAL_EVIDENCE"
        else:
            evidence_grade = "MODERATE_EVIDENCE"
            officer_recommendation = "AI RECOMMENDS: OFFICER_DISCRETIONARY_REVIEW"

        return {
            "fused_confidence_score": round(fused_confidence, 2),
            "evidence_grade": evidence_grade,
            "officer_recommendation": officer_recommendation,
            "stream_breakdown": {
                "ground_vision_confidence": round(visual_confidence, 2),
                "satellite_ndvi_drop_percent": round(satellite_drop_percentage, 1),
                "weather_event_confirmed": weather_hazard_level in ["MEDIUM", "HIGH", "SEVERE"],
                "fraud_penalty_deduction": round(fraud_risk_score * 0.25, 2),
            }
        }


risk_prediction_ai = RiskPredictionAIService()
