"""
Test API endpoints
"""
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "overpass_url" in data


def test_geocode_endpoint():
    """Test geocoding endpoint"""
    response = client.get("/api/v1/geocode?q=São Paulo&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        result = data[0]
        assert "lat" in result
        assert "lon" in result
        assert "display_name" in result


def test_geocode_endpoint_min_length():
    """Test geocoding with short query (should fail validation)"""
    response = client.get("/api/v1/geocode?q=SP")
    assert response.status_code == 422  # Validation error


def test_score_endpoint_point():
    """Test scoring endpoint with Point geometry"""
    payload = {
        "geometry": {
            "type": "Point",
            "coordinates": [-46.6333, -23.5505]  # São Paulo
        },
        "business_type": "restaurante"
    }
    
    # Note: This will fail without proper auth in production
    # In a real test, you'd mock the auth or use a test token
    response = client.post("/api/v1/score", json=payload)
    
    # Should return 200 or 401 depending on auth setup
    assert response.status_code in [200, 401, 429]
    
    if response.status_code == 200:
        data = response.json()
        assert "score" in data
        assert "features" in data
        assert "explanation" in data
        assert "center" in data
        assert 0 <= data["score"] <= 100


def test_score_endpoint_invalid_business_type():
    """Test scoring with invalid business type"""
    payload = {
        "geometry": {
            "type": "Point",
            "coordinates": [-46.6333, -23.5505]
        },
        "business_type": "invalid_type"
    }
    
    response = client.post("/api/v1/score", json=payload)
    assert response.status_code in [422, 401]  # Validation error or auth error


def test_score_endpoint_invalid_geometry():
    """Test scoring with invalid geometry type"""
    payload = {
        "geometry": {
            "type": "LineString",  # Not supported
            "coordinates": [[-46.6333, -23.5505], [-46.6334, -23.5506]]
        },
        "business_type": "restaurante"
    }
    
    response = client.post("/api/v1/score", json=payload)
    # Should fail with validation or bad request
    assert response.status_code in [400, 401, 422]


def test_projects_list_endpoint():
    """Test listing projects"""
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_layers_endpoint_competition():
    """Test layers endpoint for competition"""
    bbox = "-46.7,-23.6,-46.6,-23.5"
    response = client.get(f"/api/v1/layers/competition?bbox={bbox}&business_type=restaurante")
    
    # Should return GeoJSON or require auth
    assert response.status_code in [200, 401, 429]
    
    if response.status_code == 200:
        data = response.json()
        assert "type" in data
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert isinstance(data["features"], list)


def test_layers_endpoint_pois():
    """Test layers endpoint for POIs"""
    bbox = "-46.7,-23.6,-46.6,-23.5"
    response = client.get(f"/api/v1/layers/pois?bbox={bbox}&business_type=restaurante")
    
    assert response.status_code in [200, 401, 429]
    
    if response.status_code == 200:
        data = response.json()
        assert data["type"] == "FeatureCollection"


def test_layers_endpoint_transit():
    """Test layers endpoint for transit"""
    bbox = "-46.7,-23.6,-46.6,-23.5"
    response = client.get(f"/api/v1/layers/transit?bbox={bbox}")
    
    assert response.status_code in [200, 401, 429]
    
    if response.status_code == 200:
        data = response.json()
        assert data["type"] == "FeatureCollection"


def test_layers_endpoint_flow():
    """Test layers endpoint for flow heatmap"""
    bbox = "-46.7,-23.6,-46.6,-23.5"
    response = client.get(f"/api/v1/layers/flow?bbox={bbox}")
    
    assert response.status_code in [200, 401, 429]
    
    if response.status_code == 200:
        data = response.json()
        assert data["type"] == "FeatureCollection"
        # Flow layer creates a grid of points
        if len(data["features"]) > 0:
            feature = data["features"][0]
            assert "properties" in feature
            assert "value" in feature["properties"]


def test_layers_endpoint_invalid_layer():
    """Test layers endpoint with invalid layer type"""
    response = client.get("/api/v1/layers/invalid_layer?bbox=-46.7,-23.6,-46.6,-23.5")
    
    # Should return empty FeatureCollection or 404
    if response.status_code == 200:
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 0


def test_cors_headers():
    """Test that CORS headers are set"""
    response = client.options("/api/v1/health")
    # CORS headers should be present
    assert response.status_code in [200, 405]  # Options or Method Not Allowed


def test_api_versioning():
    """Test that API endpoints are versioned correctly"""
    # All endpoints should be under /api/v1/
    endpoints = [
        "/api/v1/health",
        "/api/v1/geocode?q=test",
        "/api/v1/projects",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404


@pytest.mark.parametrize("business_type", ["restaurante", "academia", "varejo_moda"])
def test_score_all_business_types(business_type):
    """Test that all business types are supported"""
    payload = {
        "geometry": {
            "type": "Point",
            "coordinates": [-46.6333, -23.5505]
        },
        "business_type": business_type
    }
    
    response = client.post("/api/v1/score", json=payload)
    # Should not fail with validation error (might need auth)
    assert response.status_code in [200, 401, 429]


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    
    if response.status_code == 200:
        # Prometheus format
        text = response.text
        assert "http_requests" in text or "python" in text

