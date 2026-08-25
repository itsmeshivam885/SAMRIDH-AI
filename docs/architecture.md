# SAMRIDH-AI Architecture Documentation
### Smart Agricultural Management for Risk Identification, Damage Assessment, and Harvest

## 1. High-Level Architecture
SAMRIDH-AI is organized as a six-tier architecture:

```
[ Tier 1: Client Surfaces ]
├── Farmer Mobile / Responsive Web App (Bilingual Hindi/English)
├── Field Officer Claim Review Workstation
├── State & National Agricultural Command Center (GIS)
└── Public Information & PMFBY Decision Support Portal

[ Tier 2: API Gateway & Security ]
├── FastAPI HTTP / WebSocket Gateway
├── JWT Authentication & Role-Based Access Control (RBAC)
└── Standardized JSON Response / Error Envelope Handler

[ Tier 3: Domain Services ]
├── Farm & Land Boundary Service (PostGIS / Shapely)
├── IoT Sensor Telemetry Service (MQTT & HTTP Ingestion)
├── PMFBY Claims & Settlement State Machine
└── Notification & Proactive Advisory Engine

[ Tier 4: AI & Multimodal Fusion Engines ]
├── Crop Health & Disease Vision Engine (YOLOv11 / EfficientNet)
├── AI Damage Semantic Segmentation (SAM / SegFormer)
├── Multi-Signal Fraud Radar (Geofence + pHash + SIFT + Metadata)
└── Multimodal Confidence & Loss Fuser (Vision + Satellite + Weather)

[ Tier 5: External Integration Adapters ]
├── PMFBY & PFMS Payment Gateway Adapter (Mockable)
├── IMD Regional Meteorological Radar Adapter (Mockable)
└── Sentinel-2 & ISRO Bhuvan Multispectral NDVI Adapter (Mockable)

[ Tier 6: Persistence & Storage ]
├── PostgreSQL 16 + PostGIS 3.4 (Spatial indexing, UUIDs)
└── S3 / MinIO Object Storage (Cryptographic hashes, photos, masks)
```

---

## 2. The Digital Farm Health Ledger
The central conceptual innovation of SAMRIDH-AI is the **Digital Farm Health Ledger**. Rather than evaluating a crop loss based solely on a single photo taken after a calamity, every registered farm maintains a continuous historical ledger:

1. **Sowing Baseline**: High-resolution landmark photos capturing farm geometry, soil type, and early canopy appearance.
2. **Weekly Telemetry**: Continuous root-zone soil moisture, temperature, pH, NPK, and Sentinel-2 NDVI vegetative vigor.
3. **Disaster Anomaly**: Sudden drops in NDVI or abnormal sensor spikes cross-correlated with IMD weather alerts.
4. **Damage Capture**: Ground evidence verified against the sowing baseline, geofenced inside the registered polygon, and evaluated for duplicate perceptual hashes.
5. **Recovery / Settlement**: Officer-sanctioned DBT payout tracking.
