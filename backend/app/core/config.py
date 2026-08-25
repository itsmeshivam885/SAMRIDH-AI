from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "SAMRIDH-AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DEMO_MODE: bool = True

    # JWT & Auth
    SECRET_KEY: str = "samridh_ai_super_secret_jwt_signing_key_for_sih_hackathon_demo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./samridh_ai.db"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "*",
    ]

    # Image Quality Gate Thresholds
    IMAGE_BLUR_THRESHOLD: float = 80.0
    IMAGE_MIN_LUMINANCE: float = 35.0
    IMAGE_MAX_LUMINANCE: float = 245.0
    IMAGE_MIN_WIDTH: int = 400
    IMAGE_MIN_HEIGHT: int = 400

    # Fraud Detection Thresholds
    PHASH_HAMMING_DISTANCE_THRESHOLD: int = 8  # Below this distance is flagged as duplicate
    SIFT_FEATURE_MATCH_THRESHOLD: float = 0.60
    GPS_MAX_ALLOWED_DISTANCE_METERS: float = 150.0  # Max tolerance for edge of farm polygon

    # Mock Integrations
    MOCK_PMFBY_PROVIDER: bool = True
    MOCK_WEATHER_PROVIDER: bool = True
    MOCK_SATELLITE_PROVIDER: bool = True
    MOCK_OTP_PROVIDER: bool = True
    MOCK_OTP_CODE: str = "123456"

    # Storage paths
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    MAX_UPLOAD_SIZE_MB: int = 25

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow",
    )


settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
