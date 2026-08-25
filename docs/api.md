# SAMRIDH-AI REST API Specification

All SAMRIDH-AI APIs are versioned under `/api/v1/` and return consistent JSON envelopes.

## 1. Response Envelopes

### Success Envelope
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": null
}
```

### Error Envelope
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "OUT_OF_GEOFENCE",
    "message": "Evidence image coordinates lie outside the registered farm polygon."
  },
  "meta": { "path": "/api/v1/damage/report" }
}
```

---

## 2. Core Endpoint Summary

| Domain | Method | Path | Description |
|---|---|---|---|
| **Auth** | `POST` | `/api/v1/auth/login` | JWT login with username/phone & password |
| **Auth** | `POST` | `/api/v1/auth/otp/request` | Request mobile OTP |
| **Auth** | `POST` | `/api/v1/auth/otp/verify` | Verify OTP & receive token |
| **Farms** | `GET` | `/api/v1/farms` | List user's farms |
| **Farms** | `POST` | `/api/v1/farms` | Register new farm with GeoJSON polygon |
| **Farms** | `GET` | `/api/v1/farms/gis/all` | Get all state farms for GIS maps |
| **IoT** | `GET` | `/api/v1/soil/farm/{id}/summary` | Get latest soil stress indicators |
| **IoT** | `GET` | `/api/v1/soil/farm/{id}/history` | 7-day soil moisture & temp series |
| **Weather** | `GET` | `/api/v1/weather/farm/{id}/current` | Current weather & 5-day forecast |
| **Satellite** | `GET` | `/api/v1/satellite/farm/{id}/ndvi` | Sentinel-2 NDVI time-series & anomaly |
| **AI** | `POST` | `/api/v1/ai/crop-scan` | Computer vision disease scan |
| **AI** | `POST` | `/api/v1/ai/crop-doctor` | Grounded agronomic conversational assistant |
| **Damage** | `POST` | `/api/v1/damage/report` | Initiate calamity damage report |
| **Evidence** | `POST` | `/api/v1/damage/{id}/evidence` | Upload ground photo with auto-quality & fraud gate |
| **Claims** | `GET` | `/api/v1/claims` | List user or district claims |
| **Claims** | `POST` | `/api/v1/claims/from-report/{id}` | Formulate PMFBY claim dossier |
| **Officer** | `POST` | `/api/v1/officer/claims/{id}/review` | Officer review & approval |
| **Admin** | `GET` | `/api/v1/admin/stats` | National command center metrics |
