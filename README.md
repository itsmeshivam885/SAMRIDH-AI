# SAMRIDH-AI (समृद्धि AI)
### *Predict. Prevent. Protect. Prove.*
**Smart Agricultural Management for Risk Identification, Damage Assessment, and Harvest**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![PostGIS](https://img.shields.io/badge/PostGIS-Spatial_AI-336791.svg?logo=postgresql&logoColor=white)](https://postgis.net)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.4-38B2AC.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌾 Overview

**SAMRIDH-AI** is an end-to-end multimodal agricultural intelligence and PMFBY (Pradhan Mantri Fasal Bima Yojana) crop-insurance decision-support ecosystem. It unifies **IoT soil telemetry, on-device/edge computer vision, multispectral satellite NDVI, meteorological risk modeling, PostGIS geofencing, and multi-signal fraud verification** into a continuous Digital Farm Health Ledger.

```
                   ┌──────────────────────────────────────────────────────────┐
                   │             DIGITAL FARM HEALTH LEDGER                   │
                   │  Sowing ──> Growth ──> Stress ──> Disaster ──> Recovery │
                   └──────────────────────────────────────────────────────────┘
                                ▲                                  ▲
                                │                                  │
               ┌────────────────┴──────────────┐   ┌──────────────┴──────────────┐
               │    CYCLE A: PREVENTIVE LOOP   │   │  CYCLE B: COMPENSATIVE LOOP │
               ├───────────────────────────────┤   ├─────────────────────────────┤
               │ • Farm Geo-boundary Mapping   │   │ • Multi-trigger SOS/Disaster│
               │ • Baseline Landmark Capture   │   │ • Edge Image Quality Gate   │
               │ • IoT Soil Moisture/NPK/pH    │   │ • GPS Geofence Verification │
               │ • AI Crop Disease / Pest Scan │   │ • pHash Duplicate Detection │
               │ • Sentinel-2 NDVI Time-Series │   │ • SIFT Baseline Comparison  │
               │ • Proactive Agronomic Advisor │   │ • AI Damage Segmentation    │
               │ • Weather Risk Forecasting    │   │ • PMFBY Officer Review Hub  │
               └───────────────────────────────┘   └─────────────────────────────┘
```

> **Legal & Ethical Boundary**: SAMRIDH-AI provides **AI-assisted decision support**. AI loss estimates and confidence scores assist field officers and scheme authorities — they never override or replace official government/insurer survey protocols.

---

## 🏛️ System Architecture

SAMRIDH-AI is organized as a unified monorepo:

- **`apps/web`**: Public portal with product architecture, interactive intelligence previews, PMFBY guide, impact analytics, and portal routing.
- **`apps/farmer-mobile`**: Farmer-first mobile & web interface featuring bilingual (English/Hindi) support, Farm Health scores, IoT Soil dashboard, AI Crop Doctor, 1-click damage reporting, and live claim tracker.
- **`apps/officer-portal`**: Claim verification workstation with triage filters, GPS polygon visualizer, Before/After image slider, AI damage mask overlays, multi-source evidence score, and one-click disposition.
- **`apps/admin-portal`**: National & District GIS Command Center with multi-layer maps, active disaster feeds, fraud alerts, sensor telemetry monitors, and model registry.
- **`backend/`**: High-performance FastAPI application layer powered by SQLAlchemy, PostGIS spatial indexing, JWT + RBAC, OpenCV image pipeline, and mockable integration adapters.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (Optional for containerized run)

### 1. Backend Setup & Run

```bash
# Navigate to backend
cd backend

# Create & activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database seeder (generates demo data & sqlite database)
python ../scripts/seed.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at: **http://127.0.0.1:8000/docs**

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

---

## 🔑 Default Demo Personas

| Role | Username / Mobile | Password / OTP | Purpose |
|------|-------------------|----------------|---------|
| **Farmer** | `9876543210` / `ramesh` | `DemoPass123!` / `123456` | Ramesh Kumar (Sehore, MP - Soybean 2.5ha) |
| **Field Officer** | `officer_sharma` | `DemoPass123!` | District Agriculture Officer review console |
| **Admin** | `admin_samridh` | `DemoPass123!` | National agricultural GIS command center |

---

## 🧪 Automated Testing

Execute the comprehensive test suite verifying spatial geofencing, IoT ingest, pHash fraud checks, blur quality gate, and end-to-end claim workflows:

```bash
pytest backend/tests/ -v
```

---

## 📜 Team & Heritage
- **Team**: TwinBit (Smart India Hackathon)
- **Lead & Architect**: Shivam (VIT Bhopal University)
- **Tagline**: *Predict. Prevent. Protect. Prove.*
