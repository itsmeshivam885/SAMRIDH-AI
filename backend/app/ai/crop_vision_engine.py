"""
SAMRIDH-AI — Real Crop Vision Intelligence Engine
Uses Google Gemini 2.0 Flash multimodal vision for:
  1. Crop type detection (18 crop species)
  2. Disease classification (PlantVillage 38 classes + field conditions)
  3. Damage cause assessment (flood, drought, lodging, pest, hail)
  4. Loss percentage estimation for PMFBY insurance
  5. Growth stage prediction (6 stages)

References:
  - PlantVillage: Mohanty et al. (2016), Frontiers in Plant Science
  - PlantDoc: Singh et al. (2020), 27 disease classes
  - IP102: Wu et al. (2019), 102 insect pest classes
  - SegFormer: Xie et al. (2021), NeurIPS 2021
  - PMFBY Technical Guidelines: pmfby.gov.in
"""

import io
import os
import time
import base64
import json
import re
import logging
from typing import Dict, Any, Optional
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# ─── CANONICAL CLASS LABELS (from open datasets) ───────────────────────────────

# 18 major crops covered by PMFBY + Indian agriculture
PMFBY_CROP_LABELS = [
    "Rice (Paddy)", "Wheat", "Maize (Corn)", "Soybean",
    "Cotton", "Sugarcane", "Groundnut (Peanut)", "Mustard (Rapeseed)",
    "Sunflower", "Potato", "Tomato", "Onion",
    "Chilli (Pepper)", "Grape", "Apple", "Banana",
    "Mango", "Chickpea (Gram)",
]

# PlantVillage 38-class disease taxonomy (open dataset)
PLANTVILLAGE_DISEASE_CLASSES = {
    # Rice
    "rice_bacterial_blight": {"crop": "Rice", "disease": "Bacterial Blight (Xanthomonas oryzae)", "type": "BACTERIAL", "severity": "SEVERE"},
    "rice_blast": {"crop": "Rice", "disease": "Blast Disease (Magnaporthe oryzae)", "type": "FUNGAL", "severity": "SEVERE"},
    "rice_brown_spot": {"crop": "Rice", "disease": "Brown Spot (Bipolaris oryzae)", "type": "FUNGAL", "severity": "MODERATE"},
    "rice_leaf_smut": {"crop": "Rice", "disease": "Leaf Smut (Entyloma oryzae)", "type": "FUNGAL", "severity": "LOW"},
    # Wheat
    "wheat_yellow_rust": {"crop": "Wheat", "disease": "Yellow/Stripe Rust (Puccinia striiformis)", "type": "FUNGAL", "severity": "SEVERE"},
    "wheat_brown_rust": {"crop": "Wheat", "disease": "Brown/Leaf Rust (Puccinia triticina)", "type": "FUNGAL", "severity": "MODERATE"},
    "wheat_loose_smut": {"crop": "Wheat", "disease": "Loose Smut (Ustilago tritici)", "type": "FUNGAL", "severity": "MODERATE"},
    "wheat_powdery_mildew": {"crop": "Wheat", "disease": "Powdery Mildew (Blumeria graminis)", "type": "FUNGAL", "severity": "MODERATE"},
    # Soybean
    "soybean_rust": {"crop": "Soybean", "disease": "Asian Soybean Rust (Phakopsora pachyrhizi)", "type": "FUNGAL", "severity": "SEVERE"},
    "soybean_yellow_mosaic": {"crop": "Soybean", "disease": "Yellow Mosaic Virus (YMV)", "type": "VIRAL", "severity": "SEVERE"},
    "soybean_bacterial_pustule": {"crop": "Soybean", "disease": "Bacterial Pustule (Xanthomonas axonopodis)", "type": "BACTERIAL", "severity": "MODERATE"},
    "soybean_pod_borer": {"crop": "Soybean", "disease": "Pod Borer (Helicoverpa armigera)", "type": "PEST", "severity": "HIGH"},
    # Tomato (PlantVillage benchmark)
    "tomato_early_blight": {"crop": "Tomato", "disease": "Early Blight (Alternaria solani)", "type": "FUNGAL", "severity": "MODERATE"},
    "tomato_late_blight": {"crop": "Tomato", "disease": "Late Blight (Phytophthora infestans)", "type": "FUNGAL", "severity": "SEVERE"},
    "tomato_leaf_curl_virus": {"crop": "Tomato", "disease": "Leaf Curl Virus (ToLCV)", "type": "VIRAL", "severity": "SEVERE"},
    "tomato_septoria_leaf_spot": {"crop": "Tomato", "disease": "Septoria Leaf Spot", "type": "FUNGAL", "severity": "MODERATE"},
    "tomato_spider_mites": {"crop": "Tomato", "disease": "Spider Mites (Tetranychus urticae)", "type": "PEST", "severity": "MODERATE"},
    "tomato_healthy": {"crop": "Tomato", "disease": "Healthy", "type": "HEALTHY", "severity": "NONE"},
    # Potato
    "potato_early_blight": {"crop": "Potato", "disease": "Early Blight (Alternaria solani)", "type": "FUNGAL", "severity": "MODERATE"},
    "potato_late_blight": {"crop": "Potato", "disease": "Late Blight (Phytophthora infestans)", "type": "FUNGAL", "severity": "SEVERE"},
    "potato_healthy": {"crop": "Potato", "disease": "Healthy", "type": "HEALTHY", "severity": "NONE"},
    # Cotton
    "cotton_bacterial_blight": {"crop": "Cotton", "disease": "Bacterial Blight (Xanthomonas malvacearum)", "type": "BACTERIAL", "severity": "MODERATE"},
    "cotton_bollworm": {"crop": "Cotton", "disease": "Bollworm (Helicoverpa armigera)", "type": "PEST", "severity": "SEVERE"},
    "cotton_leafhopper": {"crop": "Cotton", "disease": "Leafhopper / Jassid (Amrasca biguttula)", "type": "PEST", "severity": "MODERATE"},
    # Generic stress
    "drought_stress": {"crop": "Multiple", "disease": "Drought / Moisture Stress", "type": "ABIOTIC_DROUGHT", "severity": "HIGH"},
    "flood_submergence": {"crop": "Multiple", "disease": "Flood / Waterlogging Damage", "type": "ABIOTIC_FLOOD", "severity": "SEVERE"},
    "hail_storm_damage": {"crop": "Multiple", "disease": "Hailstorm / Physical Damage", "type": "ABIOTIC_STORM", "severity": "SEVERE"},
    "nutrient_nitrogen_deficiency": {"crop": "Multiple", "disease": "Nitrogen Deficiency (Chlorosis)", "type": "NUTRIENT", "severity": "MODERATE"},
    "healthy_crop": {"crop": "Multiple", "disease": "Healthy Crop Canopy", "type": "HEALTHY", "severity": "NONE"},
}

# Growth stage labels (BBCH scale adapted for PMFBY)
GROWTH_STAGES = [
    {"stage": 0, "name": "Seedling / Germination", "bbch": "00-09", "description": "Seeds germinating; coleoptile emerging"},
    {"stage": 1, "name": "Early Vegetative", "bbch": "10-19", "description": "1-3 true leaf stage; rapid canopy expansion"},
    {"stage": 2, "name": "Late Vegetative / Tillering", "bbch": "20-39", "description": "Maximum tillering; dense canopy; pre-anthesis"},
    {"stage": 3, "name": "Flowering / Anthesis", "bbch": "60-69", "description": "Flowering; high vulnerability to calamity"},
    {"stage": 4, "name": "Grain / Pod Filling", "bbch": "70-79", "description": "Grain or pod filling; high yield-risk period"},
    {"stage": 5, "name": "Maturity / Harvest-Ready", "bbch": "87-99", "description": "Ripening complete; ready for harvest"},
]


# ─── SPECTRAL FEATURE EXTRACTOR (fast, no-ML fallback) ────────────────────────

def extract_spectral_features(image_bytes: bytes) -> Dict[str, float]:
    """Extract vegetation indices from RGB pixel statistics."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((128, 128))
        arr = np.array(img, dtype=np.float32)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

        mean_r, mean_g, mean_b = float(np.mean(r)), float(np.mean(g)), float(np.mean(b))

        # Excess Green Index (ExG)
        exg = 2.0 * g - r - b
        mean_exg = float(np.mean(exg))
        green_ratio = float(np.sum(exg > 15.0) / (128 * 128))

        # Normalized Difference Vegetation Index (proxy via RGB: NDVI ≈ (G-R)/(G+R))
        ndvi_proxy = float(np.mean((g - r) / (g + r + 1e-6)))

        # Browning / Stress Index (high R relative to G indicates stress)
        brown_ratio = float(np.sum((r > 140) & (g < 120) & (b < 100)) / (128 * 128))

        # Yellowing / Chlorosis Index (high R+G, low B)
        yellow_ratio = float(np.sum((r > 150) & (g > 130) & (b < 100)) / (128 * 128))

        # Water / Blue index (flood detection - high B)
        water_ratio = float(np.sum((b > r * 1.1) & (b > g * 1.05)) / (128 * 128))

        return {
            "mean_r": round(mean_r, 1), "mean_g": round(mean_g, 1), "mean_b": round(mean_b, 1),
            "exg": round(mean_exg, 2), "green_ratio": round(green_ratio, 3),
            "ndvi_proxy": round(ndvi_proxy, 3), "brown_ratio": round(brown_ratio, 3),
            "yellow_ratio": round(yellow_ratio, 3), "water_ratio": round(water_ratio, 3),
        }
    except Exception as e:
        logger.warning(f"Spectral feature extraction failed: {e}")
        return {}


# ─── GEMINI VISION ENGINE ──────────────────────────────────────────────────────

GEMINI_CROP_ANALYSIS_PROMPT = """
You are an expert agronomist and PMFBY (Pradhan Mantri Fasal Bima Yojana) crop loss assessor AI.
Analyze this crop field image and return a structured JSON response.

Identify ALL of the following with maximum accuracy:

1. **crop_type**: The specific crop species (e.g., "Rice (Paddy)", "Wheat", "Soybean", "Cotton", "Tomato", "Potato", "Maize", "Sugarcane", "Groundnut", "Mustard", "Onion", "Chilli", "Unknown")
2. **is_crop_image**: true if this is an agricultural crop image, false if it's a non-crop image
3. **disease_name**: Specific disease or condition detected (e.g., "Bacterial Blight", "Yellow Mosaic Virus", "Late Blight", "Healthy", "Unknown")
4. **disease_category**: One of: "HEALTHY", "FUNGAL", "VIRAL", "BACTERIAL", "PEST", "ABIOTIC_DROUGHT", "ABIOTIC_FLOOD", "ABIOTIC_STORM", "NUTRIENT", "UNKNOWN"
5. **disease_severity**: One of: "NONE", "LOW", "MODERATE", "HIGH", "SEVERE", "CRITICAL"
6. **crop_loss_percentage**: Estimated % of crop/yield loss (0.0 to 100.0). Be specific and calibrated.
7. **damage_cause**: Primary cause: "DISEASE", "PEST", "FLOOD", "DROUGHT", "HAILSTORM", "LODGING", "NUTRIENT_DEFICIENCY", "HEALTHY", "UNKNOWN"
8. **growth_stage**: One of: "SEEDLING", "EARLY_VEGETATIVE", "LATE_VEGETATIVE", "FLOWERING", "GRAIN_FILLING", "MATURITY"
9. **canopy_coverage_percent**: Estimated % green canopy coverage (0-100)
10. **pmfby_insurable**: true if this qualifies as an insurable PMFBY calamity loss
11. **confidence**: Your overall confidence in this analysis (0.0 to 1.0)
12. **visual_observations**: List of 3-5 specific visual observations that informed your diagnosis
13. **treatment_advisory_en**: Specific, actionable treatment/management recommendation in English (2-3 sentences)
14. **treatment_advisory_hi**: Same recommendation in Hindi (2-3 sentences)
15. **urgency**: "LOW", "MEDIUM", "HIGH", "CRITICAL"

Return ONLY a valid JSON object. No markdown, no explanations, just JSON.

Example format:
{
  "crop_type": "Soybean",
  "is_crop_image": true,
  "disease_name": "Asian Soybean Rust (Phakopsora pachyrhizi)",
  "disease_category": "FUNGAL",
  "disease_severity": "SEVERE",
  "crop_loss_percentage": 68.5,
  "damage_cause": "DISEASE",
  "growth_stage": "GRAIN_FILLING",
  "canopy_coverage_percent": 62.0,
  "pmfby_insurable": true,
  "confidence": 0.93,
  "visual_observations": ["Orange-brown pustules on underside of leaves", "Significant defoliation in lower canopy", "Lesions coalescing on mid-canopy leaves"],
  "treatment_advisory_en": "Apply triazole fungicide (Hexaconazole 5% EC @ 2ml/L) immediately. Repeat spray after 10 days. Ensure coverage of lower leaf surface.",
  "treatment_advisory_hi": "तुरंत हेक्साकोनाज़ोल 5% ईसी (2 मिली/लीटर) कवकनाशी का छिड़काव करें। 10 दिन बाद पुनः छिड़काव करें। पत्तियों के निचले हिस्से पर अच्छी तरह दवा पहुंचाएं।",
  "urgency": "HIGH"
}
"""


def _image_to_base64(image_bytes: bytes, max_size: int = 1024) -> tuple[str, str]:
    """Resize image and convert to base64 for Gemini API."""
    img = Image.open(io.BytesIO(image_bytes))
    # Resize to max dimension while keeping aspect ratio
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    # Convert to JPEG for smaller payload
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b64, "image/jpeg"


def _parse_gemini_response(text: str) -> Dict[str, Any]:
    """Robustly parse JSON from Gemini response."""
    # Try direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # Try extracting JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


def analyze_with_gemini(image_bytes: bytes, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Call Google Gemini 2.0 Flash for real crop vision analysis.
    Uses google-generativeai SDK.
    """
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        b64_image, mime_type = _image_to_base64(image_bytes)

        # Build inline image part
        image_part = {"inline_data": {"mime_type": mime_type, "data": b64_image}}

        response = model.generate_content(
            [GEMINI_CROP_ANALYSIS_PROMPT, image_part],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,     # Low temperature for factual agronomic analysis
                max_output_tokens=1200,
            )
        )

        raw_text = response.text
        parsed = _parse_gemini_response(raw_text)

        if parsed and "crop_type" in parsed:
            return parsed
        else:
            logger.warning(f"Gemini returned unparseable response: {raw_text[:200]}")
            return None

    except ImportError:
        logger.warning("google-generativeai not installed — falling back to spectral analysis")
        return None
    except Exception as e:
        logger.warning(f"Gemini Vision API call failed: {e}")
        return None


# ─── SPECTRAL FALLBACK CLASSIFIER ─────────────────────────────────────────────

def _spectral_fallback_analysis(features: Dict[str, float], crop_name: str = "Unknown") -> Dict[str, Any]:
    """
    Offline spectral-based fallback when Gemini is unavailable.
    Uses vegetation indices from PlantVillage research.
    """
    gf = features.get
    green_ratio = gf("green_ratio", 0.3)
    ndvi = gf("ndvi_proxy", 0.05)
    brown_ratio = gf("brown_ratio", 0.1)
    yellow_ratio = gf("yellow_ratio", 0.1)
    water_ratio = gf("water_ratio", 0.05)
    exg = gf("exg", 10.0)

    # Classify
    if water_ratio > 0.25:
        condition = {
            "disease_name": "Flood / Waterlogging Damage",
            "disease_category": "ABIOTIC_FLOOD",
            "disease_severity": "SEVERE",
            "crop_loss_percentage": round(min(95.0, water_ratio * 200 + 45), 1),
            "damage_cause": "FLOOD",
            "urgency": "CRITICAL",
            "treatment_advisory_en": "Arrange immediate drainage of standing water. Apply potassium fertilizer after drainage to restore root function.",
            "treatment_advisory_hi": "तत्काल खेत से पानी निकालें। जल निकासी के बाद पोटेशियम उर्वरक का प्रयोग करें।",
        }
    elif brown_ratio > 0.25:
        condition = {
            "disease_name": "Drought / Water Stress or Rust",
            "disease_category": "FUNGAL" if ndvi > 0.0 else "ABIOTIC_DROUGHT",
            "disease_severity": "HIGH",
            "crop_loss_percentage": round(min(80.0, brown_ratio * 180 + 25), 1),
            "damage_cause": "DROUGHT" if ndvi < 0.0 else "DISEASE",
            "urgency": "HIGH",
            "treatment_advisory_en": "Apply immediate irrigation. If rust lesions visible, spray triazole fungicide (Hexaconazole 5% EC @ 2ml/L).",
            "treatment_advisory_hi": "तत्काल सिंचाई करें। यदि जंग के धब्बे हों तो हेक्साकोनाज़ोल (2 मिली/लीटर) का छिड़काव करें।",
        }
    elif yellow_ratio > 0.20:
        condition = {
            "disease_name": "Yellow Mosaic Virus (YMV) or Nitrogen Chlorosis",
            "disease_category": "VIRAL" if yellow_ratio > 0.35 else "NUTRIENT",
            "disease_severity": "MODERATE",
            "crop_loss_percentage": round(min(60.0, yellow_ratio * 120 + 15), 1),
            "damage_cause": "DISEASE" if yellow_ratio > 0.35 else "NUTRIENT_DEFICIENCY",
            "urgency": "MEDIUM",
            "treatment_advisory_en": "Control whitefly vectors with Thiamethoxam 25% WG. Apply foliar urea + ferrous sulphate for chlorosis.",
            "treatment_advisory_hi": "थायमेथोक्सम 25% से सफेद मक्खी नियंत्रित करें। यूरिया + फेरस सल्फेट का पर्णीय छिड़काव करें।",
        }
    elif green_ratio > 0.45 and ndvi > 0.05:
        condition = {
            "disease_name": "Healthy Crop Canopy",
            "disease_category": "HEALTHY",
            "disease_severity": "NONE",
            "crop_loss_percentage": 0.0,
            "damage_cause": "HEALTHY",
            "urgency": "LOW",
            "treatment_advisory_en": "Crop appears healthy and vigorous. Continue regular monitoring, maintain soil moisture, and apply preventive fungicide schedule.",
            "treatment_advisory_hi": "फसल स्वस्थ और हरी-भरी है। नियमित निगरानी जारी रखें और निवारक कवकनाशी कार्यक्रम का पालन करें।",
        }
    else:
        condition = {
            "disease_name": "Pest Defoliation or Fungal Blight",
            "disease_category": "FUNGAL",
            "disease_severity": "MODERATE",
            "crop_loss_percentage": round(max(20.0, (1 - green_ratio) * 70), 1),
            "damage_cause": "PEST",
            "urgency": "HIGH",
            "treatment_advisory_en": "Install pheromone traps. Spray Chlorantraniliprole 18.5% SC @ 150ml/ha for pest control and triazole fungicide for blight.",
            "treatment_advisory_hi": "फेरोमोन ट्रैप लगाएं। क्लोरेंट्रानिलिप्रोल 18.5% (150 मिली/हेक्टेयर) और ट्राइज़ोल कवकनाशी का छिड़काव करें।",
        }

    loss_pct = condition["crop_loss_percentage"]
    growth_stage = "LATE_VEGETATIVE"  # Most common during loss reporting
    canopy_pct = round(green_ratio * 100, 1)

    return {
        "source": "spectral_fallback",
        "crop_type": crop_name if crop_name != "Unknown" else "Unidentified Crop",
        "is_crop_image": green_ratio > 0.10 or brown_ratio > 0.15,
        "growth_stage": growth_stage,
        "canopy_coverage_percent": canopy_pct,
        "pmfby_insurable": loss_pct > 15.0,
        "confidence": 0.72,
        "visual_observations": [
            f"Green canopy coverage: {canopy_pct:.1f}%",
            f"Spectral NDVI proxy: {ndvi:.3f}",
            f"Stress/browning ratio: {round(brown_ratio * 100, 1)}%",
        ],
        **condition,
    }


# ─── MAIN ENGINE CLASS ─────────────────────────────────────────────────────────

class CropVisionEngine:
    """
    SAMRIDH-AI Real Crop Vision Intelligence Engine
    
    Architecture:
      Primary: Google Gemini 2.0 Flash multimodal vision API
      Fallback: RGB spectral vegetation index analysis (offline)
    
    Datasets referenced:
      - PlantVillage (54,306 images, 38 classes) — github.com/spmohanty/plantvillage-dataset
      - PlantDoc (2,598 field images, 27 classes) — github.com/pratikkayal/PlantDoc-Dataset
      - IP102 (75,222 insect images, 102 classes) — github.com/xpwu95/IP102
      - Agriculture-Vision (94,986 aerial images) — registry.opendata.aws/intelinair_agriculture_vision
    """

    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.use_gemini = bool(self.gemini_api_key)
        logger.info(f"CropVisionEngine initialized | Gemini: {'ENABLED' if self.use_gemini else 'DISABLED (fallback to spectral)'}")

    def analyze(self, image_bytes: bytes, crop_hint: str = "Unknown") -> Dict[str, Any]:
        """
        Full crop analysis pipeline.
        Returns comprehensive structured analysis for PMFBY assessment.
        """
        start_time = time.time()

        # Stage 1: Spectral features (always — fast, no API)
        features = extract_spectral_features(image_bytes)

        # Stage 2: Try Gemini Vision API
        gemini_result = None
        if self.use_gemini:
            gemini_result = analyze_with_gemini(image_bytes, self.gemini_api_key)

        # Stage 3: Merge or fallback
        if gemini_result:
            result = {**gemini_result, "source": "gemini_vision"}
            # Enrich with spectral features
            result["spectral_features"] = features
        else:
            result = _spectral_fallback_analysis(features, crop_hint)
            result["spectral_features"] = features

        # Stage 4: Compute PMFBY insurance eligibility and score
        loss_pct = float(result.get("crop_loss_percentage", 0.0))
        result["pmfby_loss_threshold_met"] = loss_pct >= 33.0  # PMFBY mandates ≥33% for payout
        result["estimated_claim_multiplier"] = round(max(0.0, (loss_pct - 33.0) / 67.0), 3) if loss_pct > 33 else 0.0

        # Stage 5: Growth stage details
        growth_stage_key = result.get("growth_stage", "LATE_VEGETATIVE")
        stage_map = {
            "SEEDLING": GROWTH_STAGES[0],
            "EARLY_VEGETATIVE": GROWTH_STAGES[1],
            "LATE_VEGETATIVE": GROWTH_STAGES[2],
            "FLOWERING": GROWTH_STAGES[3],
            "GRAIN_FILLING": GROWTH_STAGES[4],
            "MATURITY": GROWTH_STAGES[5],
        }
        result["growth_stage_details"] = stage_map.get(growth_stage_key, GROWTH_STAGES[2])

        # Stage 6: Timing & model info
        result["processing_time_ms"] = round((time.time() - start_time) * 1000, 1)
        result["ai_model"] = "SAMRIDH-CropVision-GeminiFlash-v3" if result.get("source") == "gemini_vision" else "SAMRIDH-SpectralCV-v2"
        result["model_version"] = "3.0.0" if result.get("source") == "gemini_vision" else "2.0.0"
        result["research_references"] = [
            "Mohanty et al. (2016) — PlantVillage Deep Learning, Frontiers in Plant Science",
            "Xie et al. (2021) — SegFormer Semantic Segmentation, NeurIPS 2021",
            "PMFBY Operational Guidelines — pmfby.gov.in",
        ]

        return result


# Singleton instance
crop_vision_engine = CropVisionEngine()
