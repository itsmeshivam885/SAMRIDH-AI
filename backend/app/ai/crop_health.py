"""
Updated CropHealthAIService — now powered by CropVisionEngine (Gemini Vision API + spectral fallback)
Maintains backward-compatible API response shape for existing frontend consumers.
"""

import io
import time
from typing import Dict, Any
from PIL import Image
import numpy as np

from app.utils.image import analyze_image_quality
from app.ai.crop_vision_engine import crop_vision_engine


class CropHealthAIService:
    """
    Analyzes field crop imagery using real AI vision:
      1. Google Gemini 2.0 Flash multimodal vision (primary)
      2. RGB spectral vegetation indices (offline fallback)

    Returns PMFBY-compatible crop health assessment with:
      - Crop type identification
      - Disease / damage classification
      - Loss percentage estimation
      - Growth stage prediction
      - Treatment advisory (EN + HI)
    """

    def analyze_crop_image(self, image_bytes: bytes, crop_name: str = "Unknown") -> Dict[str, Any]:
        start_time = time.time()

        # 1. Run real quality gate (blur / luminance checks)
        quality = analyze_image_quality(image_bytes)

        # 2. Run real crop vision analysis
        vision_result = crop_vision_engine.analyze(image_bytes, crop_hint=crop_name)

        # 3. Build backward-compatible response
        loss_pct = float(vision_result.get("crop_loss_percentage", 0.0))
        canopy = float(vision_result.get("canopy_coverage_percent", 0.0))

        # Health score: 100 - loss%, clamped 0-100
        health_score = round(max(0.0, min(100.0, 100.0 - loss_pct)), 1)

        # Excess Green Index from spectral features
        spectral = vision_result.get("spectral_features", {})
        mean_exg = spectral.get("exg", 0.0)
        green_ratio = spectral.get("green_ratio", canopy / 100.0)

        duration_ms = (time.time() - start_time) * 1000

        return {
            # Model Identity
            "ai_model": vision_result.get("ai_model", "SAMRIDH-CropVision-v3"),
            "model_version": vision_result.get("model_version", "3.0.0"),

            # Crop Identification
            "crop_type": vision_result.get("crop_type", "Unknown"),
            "is_crop_image": vision_result.get("is_crop_image", True),

            # Disease / Damage Classification
            "detected_condition": vision_result.get("disease_name", "Unknown"),
            "category": vision_result.get("disease_category", "UNKNOWN"),
            "disease_severity": vision_result.get("disease_severity", "UNKNOWN"),
            "damage_cause": vision_result.get("damage_cause", "UNKNOWN"),

            # Health & Loss Metrics
            "crop_health_score": health_score,
            "crop_loss_percentage": round(loss_pct, 1),
            "confidence": round(float(vision_result.get("confidence", 0.85)), 2),
            "green_canopy_ratio": round(green_ratio * 100, 1),
            "canopy_coverage_percent": round(canopy, 1),
            "excess_green_index": round(float(mean_exg), 1),

            # Growth Stage
            "growth_stage": vision_result.get("growth_stage", "LATE_VEGETATIVE"),
            "growth_stage_details": vision_result.get("growth_stage_details", {}),

            # PMFBY Insurance Eligibility
            "pmfby_insurable": vision_result.get("pmfby_insurable", loss_pct > 15.0),
            "pmfby_loss_threshold_met": vision_result.get("pmfby_loss_threshold_met", loss_pct >= 33.0),
            "estimated_claim_multiplier": vision_result.get("estimated_claim_multiplier", 0.0),

            # Treatment & Urgency
            "treatment_advisory_en": vision_result.get("treatment_advisory_en", ""),
            "treatment_advisory_hi": vision_result.get("treatment_advisory_hi", ""),
            "urgency": vision_result.get("urgency", "MEDIUM"),

            # Visual Observations (from Gemini)
            "visual_observations": vision_result.get("visual_observations", []),

            # Spectral Indices
            "spectral_features": spectral,

            # Quality Gate & Metadata
            "quality_gate": quality,
            "processing_time_ms": round(duration_ms, 1),
            "warnings": [] if quality.get("passed_quality_gate", True) else [quality.get("validation_remarks", "")],
            "analysis_source": vision_result.get("source", "spectral_fallback"),
            "research_references": vision_result.get("research_references", []),
        }


crop_health_ai = CropHealthAIService()
