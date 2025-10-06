from shapely.geometry import Point, Polygon
from app.core.features import (
    count_within_radius, nearest_distance_meters, kde_value, 
    entropy_mix, filter_by_tag, to_geodf, normalize
)
import geopandas as gpd
import math

def test_count_within_radius():
    """Test counting points within a radius"""
    pts = gpd.GeoDataFrame(geometry=[Point(0,0), Point(0.001, 0.001)], crs=4326)
    c = count_within_radius(pts, Point(0,0), 300)
    assert c >= 1
    
def test_count_within_radius_empty():
    """Test counting with empty GeoDataFrame"""
    empty = gpd.GeoDataFrame(geometry=[], crs=4326)
    c = count_within_radius(empty, Point(0,0), 500)
    assert c == 0

def test_nearest_distance_meters():
    """Test calculating nearest distance"""
    pts = gpd.GeoDataFrame(geometry=[Point(0.01, 0.01), Point(0.02, 0.02)], crs=4326)
    dist = nearest_distance_meters(pts, Point(0, 0))
    assert dist > 0
    assert dist < 5000  # Should be less than 5km

def test_nearest_distance_empty():
    """Test nearest distance with empty GeoDataFrame"""
    empty = gpd.GeoDataFrame(geometry=[], crs=4326)
    dist = nearest_distance_meters(empty, Point(0, 0))
    assert dist == float('inf')

def test_kde_value():
    """Test KDE (Kernel Density Estimation)"""
    gdf1 = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(0.001, 0.001)], crs=4326)
    gdf2 = gpd.GeoDataFrame(geometry=[Point(0.002, 0)], crs=4326)
    val = kde_value(Point(0, 0), [gdf1, gdf2], bandwidth_m=200)
    assert val > 0
    assert math.isfinite(val)

def test_kde_value_empty_sources():
    """Test KDE with empty sources"""
    empty = gpd.GeoDataFrame(geometry=[], crs=4326)
    val = kde_value(Point(0, 0), [empty], bandwidth_m=200)
    assert val == 0.0

def test_entropy_mix():
    """Test Shannon entropy for amenity mix"""
    # Balanced mix - high entropy
    balanced = {"offices": 10, "schools": 10, "parks": 10}
    ent_balanced = entropy_mix(balanced)
    assert 0.9 < ent_balanced <= 1.0
    
    # Unbalanced mix - lower entropy
    unbalanced = {"offices": 100, "schools": 1, "parks": 1}
    ent_unbalanced = entropy_mix(unbalanced)
    assert ent_unbalanced < ent_balanced
    
    # Single category - zero entropy
    single = {"offices": 100, "schools": 0, "parks": 0}
    ent_single = entropy_mix(single)
    assert ent_single == 0.0
    
    # Empty - zero entropy
    empty_dict = {"offices": 0, "schools": 0, "parks": 0}
    ent_empty = entropy_mix(empty_dict)
    assert ent_empty == 0.0

def test_filter_by_tag():
    """Test filtering GeoDataFrame by OSM tags"""
    data = [
        {"tags": {"office": "company"}},
        {"tags": {"amenity": "school"}},
        {"tags": {"office": "government"}},
        {"tags": {"leisure": "park"}}
    ]
    geoms = [Point(i, i) for i in range(4)]
    gdf = gpd.GeoDataFrame(data, geometry=geoms, crs=4326)
    
    # Filter by key only
    offices = filter_by_tag(gdf, 'office')
    assert len(offices) == 2
    
    # Filter by key and value
    schools = filter_by_tag(gdf, 'amenity', ['school'])
    assert len(schools) == 1
    
    # Filter with multiple values
    combined = filter_by_tag(gdf, 'amenity', ['school', 'university'])
    assert len(combined) == 1

def test_filter_by_tag_empty():
    """Test filter_by_tag with empty GeoDataFrame"""
    empty = gpd.GeoDataFrame(geometry=[], data={"tags":[]}, crs=4326)
    result = filter_by_tag(empty, 'office')
    assert result.empty

def test_to_geodf_nodes():
    """Test converting Overpass JSON (nodes) to GeoDataFrame"""
    overpass_json = {
        "elements": [
            {"type": "node", "lat": -23.55, "lon": -46.63, "tags": {"amenity": "restaurant"}},
            {"type": "node", "lat": -23.56, "lon": -46.64, "tags": {"shop": "clothes"}}
        ]
    }
    gdf = to_geodf(overpass_json)
    assert len(gdf) == 2
    assert gdf.crs.to_string() == "EPSG:4326"
    assert all(gdf.geometry.geom_type == "Point")

def test_to_geodf_ways():
    """Test converting Overpass JSON (ways with center) to GeoDataFrame"""
    overpass_json = {
        "elements": [
            {"type": "way", "center": {"lat": -23.55, "lon": -46.63}, "tags": {"building": "yes"}},
        ]
    }
    gdf = to_geodf(overpass_json)
    assert len(gdf) == 1

def test_to_geodf_empty():
    """Test converting empty Overpass JSON"""
    gdf = to_geodf({"elements": []})
    assert gdf.empty
    assert gdf.crs.to_string() == "EPSG:4326"

def test_normalize():
    """Test feature normalization"""
    assert normalize(50, 100) == 0.5
    assert normalize(100, 100) == 1.0
    assert normalize(150, 100) == 1.0  # Capped
    assert normalize(0, 100) == 0.0
    assert normalize(float('inf'), 100) == 0.0  # Handles infinity
    assert normalize(float('nan'), 100) == 0.0  # Handles NaN
