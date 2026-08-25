param (
    [switch]$ResetDB
)

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " SAMRIDH-AI: Predict. Prevent. Protect. Prove." -ForegroundColor Green
Write-Host " Smart Agricultural Decision-Support Ecosystem" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green

# 1. Seed database only if it doesn't exist or -ResetDB was requested
$dbPath = "backend\samridh_ai.db"
$rootDbPath = "samridh_ai.db"

if ($ResetDB -or (-not (Test-Path $dbPath) -and -not (Test-Path $rootDbPath))) {
    Write-Host "`n[*] Initializing & Seeding demo database..." -ForegroundColor Cyan
    python scripts/seed.py
} else {
    Write-Host "`n[✓] Database already initialized. Skipping seed for fast startup. (Use -ResetDB to re-seed)" -ForegroundColor Green
}

Write-Host "`n[*] Starting SAMRIDH-AI FastAPI Server (http://127.0.0.1:8000)..." -ForegroundColor Cyan
Write-Host "[*] Swagger Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "[*] Web Portal: Open apps\web\index.html in your browser`n" -ForegroundColor Yellow

Set-Location backend

# Run Uvicorn optimized to watch only app/ directory (avoids OneDrive sync loops)
uvicorn app.main:app --reload --reload-dir app --port 8000
