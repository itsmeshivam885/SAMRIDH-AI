import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import engine, Base
import app.models # Registers all SQLAlchemy models
from app.api.v1.router import api_router

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SAMRIDH-AI API Gateway",
    description="Smart Agricultural Management for Risk Identification, Damage Assessment, and Harvest (PMFBY Decision Support)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for evidence & masks
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Standardized JSON Error Envelopes
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code", "HTTP_ERROR")
        message = detail.get("message", str(detail))
    else:
        code = "HTTP_ERROR"
        message = str(detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
            "meta": {"path": request.url.path},
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload or query parameters",
                "details": exc.errors(),
            },
            "meta": {"path": request.url.path},
        },
    )


# Root Health Check
@app.get("/", tags=["Health & Status"])
def health_check():
    return {
        "status": "healthy",
        "service": "SAMRIDH-AI Core Gateway",
        "tagline": "Predict. Prevent. Protect. Prove.",
        "version": settings.VERSION,
        "demo_mode": settings.DEMO_MODE,
        "docs": "/docs",
    }


# Mount versioned API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup():
    """Ensure tables exist on boot"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[!] Startup DB creation warning: {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"[*] Starting SAMRIDH-AI server on port {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
