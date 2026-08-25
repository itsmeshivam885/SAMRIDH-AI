import pytest
from app.gis.geofence import check_point_in_polygon
from app.gis.spatial import calculate_polygon_metrics

# Sample 2.5ha polygon in Sehore, MP
SAMPLE_POLYGON = {
    "type": "Polygon",
    "coordinates": [[
        [76.8810, 23.0175],
        [76.8835, 23.0175],
        [76.8835, 23.0195],
        [76.8810, 23.0195],
        [76.8810, 23.0175]
    ]]
}


def test_point_inside_farm_geofence():
    # Center of farm
    res = check_point_in_polygon(lat=23.0185, lon=76.8821, polygon_geojson=SAMPLE_POLYGON)
    assert res["is_inside"] is True
    assert res["geofence_status"] == "INSIDE"
    assert res["distance_to_boundary_meters"] == 0.0


def test_point_outside_farm_geofence():
    # 5 km away
    res = check_point_in_polygon(lat=23.0800, lon=76.9500, polygon_geojson=SAMPLE_POLYGON)
    assert res["is_inside"] is False
    assert res["geofence_status"] == "OUTSIDE"
    assert res["distance_to_boundary_meters"] > 1000.0


def test_polygon_area_and_perimeter_calculation():
    metrics = calculate_polygon_metrics(SAMPLE_POLYGON)
    assert metrics["area_hectares"] > 2.0
    assert metrics["area_hectares"] < 10.0
    assert metrics["perimeter_meters"] > 500.0
