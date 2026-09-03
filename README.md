# SAMRIDH (समृद्धि AI)
### *Predict. Prevent. Protect. Prove.*
**Smart Agricultural Management for Risk Identification, Damage Assessment, and Harvest**

Designed & Built by **Team TwinBit** | Smart India Hackathon

[![PyTorch](https://img.shields.io/badge/PyTorch-2.14%2B-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-2.0_Flash-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.4-38B2AC.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌾 Overview

**SAMRIDH (समृद्धि)** is an end-to-end multimodal agricultural intelligence and PMFBY (Pradhan Mantri Fasal Bima Yojana) crop-insurance decision-support ecosystem. It unifies **IoT soil telemetry, PyTorch MobileNetV3 computer vision, Google Gemini 2.0 Flash vision, multispectral satellite NDVI, meteorological risk modeling, PostGIS geofencing, and multi-signal fraud verification** into a continuous Digital Farm Health Ledger.

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
               │ • PyTorch Crop Disease Scan   │   │ • pHash Duplicate Detection │
               │ • Gemini 2.0 Flash Vision AI  │   │ • SIFT Baseline Comparison  │
               │ • Sentinel-2 NDVI Time-Series │   │ • AI Damage Segmentation    │
               │ • Proactive Agronomic Advisor │   │ • PMFBY Officer Review Hub  │
               │ • Weather Risk Forecasting    │   │ • Automated Claim Payout    │
               └───────────────────────────────┘   └─────────────────────────────┘
```

---

## 🔑 Official Stakeholder Login Matrix & Credentials

The authentication system strictly enforces **Username** and **Password** authentication across all 4 stakeholder portals (No phone numbers, no OTP requirement).

### Default Hackathon Seed Accounts

| Portal Role | Full Name | Registration No | Username | Default Password | Dashboard Redirect |
|---|---|---|---|---|---|
| 👨‍🌾 **FARMER** | ARYAN SINGH | `25BCE10798` | `aryan.25bce10798` | `Aryan#25BCE10798!Sec2026` | `/farmer/dashboard` |
| 👨‍🌾 **FARMER** | SHIVAM SINGH | `25BCE10736` | `shivam.25bce10736` | `Shivam#25BCE10736!Sec2026` | `/farmer/dashboard` |
| 👨‍🌾 **FARMER** | ATHARV BISHT | `25BCE10596` | `atharv.25bce10596` | `Atharv#25BCE10596!Sec2026` | `/farmer/dashboard` |
| 📋 **FIELD_OFFICER** | KRISHNA AGRAWAL | `25BCE10117` | `krishna.25bce10117` | `Krishna#25BCE10117!Sec2026` | `/officer/dashboard` |
| 🛡️ **INSURER** | RESHMA RANI AGASTI | `25BCE10240` | `reshma.25bce10240` | `Reshma#25BCE10240!Sec2026` | `/insurer/dashboard` |
| 🗺️ **SUPER_ADMIN** | RAKHI TYAGI | `25BCE10780` | `rakhi.25bce10780` | `Rakhi#25BCE10780!Sec2026` | `/super-admin/dashboard` |

> **User Password Features**:
> - **Auto-filled Credentials**: Credentials for each selected tab are pre-loaded in the UI for 1-click testing.
> - **Eye Password Toggle**: Click the 👁️ icon inside any password box to show or hide the password string.
> - **High-Speed Authentication**: Sub-10ms response time powered by optimized bcrypt slicing.

---

## 🔒 Security Architecture & Rules

1. **Username Strategy**: Constructed as `[firstname_lowercase].[registration_number]` (e.g. `aryan.25bce10798`).
2. **Password Strategy**: Formatted as `[FirstName_Capitalized]#[RegistrationNumber]!Sec2026`.
3. **Bcrypt 72-Byte Truncation Rule**: Explicitly slices all password strings to 72 bytes (`password.encode('utf-8')[:72]`) before hashing and checking, preventing Bcrypt overflow errors.
4. **Role-Based Access Control (RBAC)**: Enforced via `RoleChecker` route dependency in `backend/app/api/deps.py`.

---

## 🧠 Multimodal AI Vision Engine

SAMRIDH features a tri-layer crop vision intelligence engine:

1. **Primary**: **Google Gemini 2.0 Flash Multimodal Vision API** for zero-shot species classification, disease diagnosis, and loss percentage estimation.
2. **Secondary**: **PyTorch MobileNetV3-Small Neural Network** (`backend/app/ai/models/crop_disease_model.pt`) trained on PlantVillage (54,306 images) and PlantDoc datasets for offline classification.
3. **Fallback**: **RGB Spectral Feature Extractor** calculating ExG (Excess Green) and proxy NDVI vegetation indices.

---

## 🚀 Repository & Database Execution

### 1. Database Seeder (Seeds 6 Stakeholder Accounts)
```bash
python backend/database/seed/demo_seeder.py
```

### 2. PyTorch Crop Vision Model Trainer
```bash
python scripts/train_crop_model.py
```

### 3. Run FastAPI Backend Server
```bash
python -m app.main
# Or: uvicorn app.main:app --reload --port 8000
```
Interactive API Documentation: **http://127.0.0.1:8000/docs**

---

## 📜 Team & Heritage
- **Team**: TwinBit (Smart India Hackathon 2026)
- **Tagline**: *Predict. Prevent. Protect. Prove.*
