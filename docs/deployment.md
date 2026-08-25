# SAMRIDH-AI Deployment & Operations Guide

## 1. Quick Local Development

```powershell
# 1. Navigate to backend
cd backend

# 2. Seed database
python ../scripts/seed.py

# 3. Start development server
uvicorn app.main:app --reload --port 8000
```
- Open Swagger API: `http://127.0.0.1:8000/docs`
- Open Web Portal: Open `apps/web/index.html` in your browser.

---

## 2. Docker Compose Production Deployment

```bash
docker-compose up --build -d
```

### Services Started:
- **`samridh-postgis`**: PostgreSQL 16 with PostGIS 3.4 on port `5432`
- **`samridh-backend`**: FastAPI application server on port `8000`
- **`samridh-mqtt`**: Eclipse Mosquitto IoT broker on port `1883`

---

## 3. Environment Configuration

Copy `.env.example` to `.env` and set:
- `DEMO_MODE=true` (for simulated AI inference and mock PMFBY/IMD feeds)
- `SECRET_KEY` (secure JWT signature secret)
- `DATABASE_URL` (`sqlite:///./samridh_ai.db` or `postgresql://postgres:pass@localhost:5432/samridh_ai`)
