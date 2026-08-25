# SAMRIDH-AI GIS & Spatial Engine

## 1. PostGIS Data Architecture
Farm boundaries are represented as WGS84 GeoJSON Polygons (`SRID: 4326`) and PostGIS Geometry objects.

### Core Geometry Operations
- **Geofence Point-in-Polygon**: Uses Shapely & PostGIS `ST_Contains` and `ST_Distance` to determine whether field photos originate within the farm parcel.
- **Geodesic Surface Area**: Converts degree coordinates using local UTM approximation to calculate area in hectares ($1 \text{ ha} = 10,000 \text{ m}^2$).
- **Perimeter Length**: Calculates boundary fence perimeter in meters.

---

## 2. Multi-Layer Map Integration
The platform renders layered Leaflet / MapLibre layers:
1. **Registered Farm Parcels Layer**: Green polygons showing surveyed agricultural land.
2. **IoT Sensor Node Markers**: Real-time status pins showing battery and soil moisture.
3. **Disaster Hazard Heatmap**: Red-alert zones indicating severe precipitation or hailstorm footprints.
4. **Claim Density Layer**: Aggregated claim volume by district and tehsil.
