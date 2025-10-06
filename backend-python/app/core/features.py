from typing import Dict, List
import math
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np

def _elements_to_points(elements) -> List[Point]:
    pts = []
    for el in elements:
        if el.get('type') == 'node':
            lat = el.get('lat')
            lon = el.get('lon')
            if lat is not None and lon is not None:
                pts.append(Point(lon, lat))
        else:
            center = el.get('center')
            if center:
                pts.append(Point(center['lon'], center['lat']))
    return pts

def to_geodf(overpass_json) -> gpd.GeoDataFrame:
    els = overpass_json.get('elements', [])
    geoms, tags = [], []
    for el in els:
        t = el.get('tags', {}) or {}
        if el.get('type') == 'node':
            lat = el.get('lat'); lon = el.get('lon')
            if lat is not None and lon is not None:
                geoms.append(Point(lon, lat)); tags.append(t)
        else:
            center = el.get('center')
            if center:
                geoms.append(Point(center['lon'], center['lat'])); tags.append(t)
    if not geoms:
        return gpd.GeoDataFrame(geometry=[], data={"tags":[]}, crs="EPSG:4326")
    return gpd.GeoDataFrame(geometry=geoms, data={"tags": tags}, crs="EPSG:4326")

def project_to_meters(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.empty: return gdf
    return gdf.to_crs(3857)

def ring_buffer(point: Point, meters: float):
    p = gpd.GeoSeries([point], crs=4326).to_crs(3857).geometry.values[0]
    buf = p.buffer(meters)
    return gpd.GeoSeries([buf], crs=3857).to_crs(4326).geometry.values[0]

def count_within_radius(gdf: gpd.GeoDataFrame, point: Point, meters: float) -> int:
    if gdf.empty: return 0
    radius = ring_buffer(point, meters)
    return int(gdf.within(radius).sum())

def nearest_distance_meters(gdf: gpd.GeoDataFrame, point: Point) -> float:
    if gdf.empty: return float('inf')
    gdf_m = project_to_meters(gdf)
    p_m = gpd.GeoSeries([point], crs=4326).to_crs(3857).geometry.values[0]
    dists = gdf_m.distance(p_m)
    return float(dists.min())

def kde_value(point: Point, sources: List[gpd.GeoDataFrame], bandwidth_m: float = 200) -> float:
    p_m = gpd.GeoSeries([point], crs=4326).to_crs(3857).geometry.values[0]
    val = 0.0; two_sigma2 = 2 * (bandwidth_m ** 2)
    for gdf in sources:
        if gdf is None or gdf.empty: continue
        gm = project_to_meters(gdf)
        for geom in gm.geometry:
            d = geom.distance(p_m)
            val += math.exp(-(d**2) / two_sigma2)
    return float(val)

def normalize(x: float, cap: float) -> float:
    if not math.isfinite(x): return 0.0
    x = min(x, cap)
    return x / cap

def entropy_mix(counts: Dict[str, int]) -> float:
    total = sum(counts.values()) or 1
    ent = 0.0
    for v in counts.values():
        p = v/total
        if p>0: ent += -p * math.log(p, 2)
    k = max(1, len([c for c in counts.values() if c>0]))
    return ent / (math.log(k,2) if k>1 else 1)

def filter_by_tag(gdf: gpd.GeoDataFrame, key: str, values=None) -> gpd.GeoDataFrame:
    if gdf.empty: return gdf
    if values is None:
        mask = gdf['tags'].apply(lambda t: key in t)
    else:
        if isinstance(values, str): values = [values]
        values_set = set(values)
        mask = gdf['tags'].apply(lambda t: t.get(key) in values_set)
    return gdf[mask]


# ============================================================================
# NOVAS FEATURES AVANÇADAS
# ============================================================================

def residential_density(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 1000) -> float:
    """
    Calcula densidade de edificações residenciais por km²
    """
    if gdf_all.empty: return 0.0
    residential = filter_by_tag(gdf_all, 'building', 'residential')
    if residential.empty: return 0.0
    count = count_within_radius(residential, point, radius_m)
    area_km2 = (math.pi * (radius_m ** 2)) / 1_000_000
    return count / area_km2 if area_km2 > 0 else 0.0


def sidewalk_quality(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 500) -> float:
    """
    % de ruas com sidewalk tag (indicador de qualidade de calçadas)
    """
    if gdf_all.empty: return 0.0
    roads = filter_by_tag(gdf_all, 'highway')
    if roads.empty: return 0.0
    roads_in_radius = roads[roads.distance(point) * 111000 < radius_m]  # aprox lat/lon to meters
    if len(roads_in_radius) == 0: return 0.0
    with_sidewalk = roads_in_radius[roads_in_radius['tags'].apply(
        lambda t: t.get('sidewalk') in ['both', 'left', 'right', 'yes']
    )]
    return len(with_sidewalk) / len(roads_in_radius)


def lighting_score(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 500) -> float:
    """
    Densidade de iluminação pública (street_lamp + lit roads)
    """
    if gdf_all.empty: return 0.0
    lamps = filter_by_tag(gdf_all, 'highway', 'street_lamp')
    lit_roads = gdf_all[gdf_all['tags'].apply(lambda t: t.get('lit') == 'yes')]
    total = len(lamps) + len(lit_roads)
    count = count_within_radius(lamps, point, radius_m) if not lamps.empty else 0
    count += count_within_radius(lit_roads, point, radius_m) if not lit_roads.empty else 0
    area_km2 = (math.pi * (radius_m ** 2)) / 1_000_000
    return count / area_km2 if area_km2 > 0 else 0.0


def green_score(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 1000) -> float:
    """
    Score de áreas verdes (parques, jardins, florestas)
    """
    if gdf_all.empty: return 0.0
    parks = filter_by_tag(gdf_all, 'leisure', ['park', 'garden', 'nature_reserve'])
    forests = filter_by_tag(gdf_all, 'landuse', ['forest', 'grass', 'meadow'])
    greens = gpd.GeoDataFrame(pd.concat([parks, forests], ignore_index=True)) if not parks.empty and not forests.empty else (parks if not parks.empty else forests)
    if greens.empty: return 0.0
    return count_within_radius(greens, point, radius_m)


def bike_infrastructure(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 1000) -> float:
    """
    Contagem de infraestrutura para bicicletas (ciclovias, estacionamentos)
    """
    if gdf_all.empty: return 0.0
    cycleways = filter_by_tag(gdf_all, 'highway', ['cycleway', 'path'])
    bike_parking = filter_by_tag(gdf_all, 'amenity', 'bicycle_parking')
    total = gpd.GeoDataFrame(pd.concat([cycleways, bike_parking], ignore_index=True)) if not cycleways.empty and not bike_parking.empty else (cycleways if not cycleways.empty else bike_parking)
    if total.empty: return 0.0
    return count_within_radius(total, point, radius_m)


def parking_availability(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 500) -> int:
    """
    Número de estacionamentos no raio
    """
    if gdf_all.empty: return 0
    parking = filter_by_tag(gdf_all, 'amenity', 'parking')
    return count_within_radius(parking, point, radius_m) if not parking.empty else 0


def walkability_score(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 500) -> float:
    """
    Índice de caminhabilidade combinando calçadas, POIs e verde
    """
    sidewalk = sidewalk_quality(gdf_all, point, radius_m)
    pois = count_within_radius(gdf_all, point, radius_m) / 100.0  # normalizado
    green = green_score(gdf_all, point, radius_m) / 10.0  # normalizado
    return (sidewalk * 0.4 + pois * 0.4 + green * 0.2)


def safety_infrastructure(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 1000) -> float:
    """
    Score de infraestrutura de segurança (polícia, iluminação, etc)
    """
    if gdf_all.empty: return 0.0
    police = filter_by_tag(gdf_all, 'amenity', ['police', 'fire_station'])
    lighting = lighting_score(gdf_all, point, radius_m)
    police_count = count_within_radius(police, point, radius_m) if not police.empty else 0
    return (police_count * 5.0 + lighting * 0.1)  # combinação ponderada


def building_density(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 500) -> float:
    """
    Densidade de edificações por km²
    """
    if gdf_all.empty: return 0.0
    buildings = filter_by_tag(gdf_all, 'building')
    if buildings.empty: return 0.0
    count = count_within_radius(buildings, point, radius_m)
    area_km2 = (math.pi * (radius_m ** 2)) / 1_000_000
    return count / area_km2 if area_km2 > 0 else 0.0


def street_connectivity(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 500) -> float:
    """
    Densidade de cruzamentos de ruas (conectividade da malha viária)
    """
    if gdf_all.empty: return 0.0
    # Aproximação: contagem de nodes de highway que são intersecções
    roads = filter_by_tag(gdf_all, 'highway')
    if roads.empty: return 0.0
    count = count_within_radius(roads, point, radius_m)
    area_km2 = (math.pi * (radius_m ** 2)) / 1_000_000
    return count / area_km2 if area_km2 > 0 else 0.0


def public_space_ratio(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 1000) -> float:
    """
    Proporção de espaço público (praças, parques, áreas comunitárias)
    """
    if gdf_all.empty: return 0.0
    public_spaces = gdf_all[gdf_all['tags'].apply(
        lambda t: t.get('leisure') in ['park', 'playground', 'garden'] or 
                  t.get('amenity') == 'community_centre'
    )]
    if public_spaces.empty: return 0.0
    return count_within_radius(public_spaces, point, radius_m) / 10.0  # normalizado


def amenity_diversity(gdf_all: gpd.GeoDataFrame, point: Point, radius_m: float = 1000) -> float:
    """
    Diversidade de tipos de amenidades (usa entropia)
    """
    if gdf_all.empty: return 0.0
    amenities_in_radius = gdf_all[gdf_all.distance(point) * 111000 < radius_m]
    if amenities_in_radius.empty: return 0.0
    
    type_counts = {}
    for tags in amenities_in_radius['tags']:
        amenity_type = tags.get('amenity') or tags.get('shop') or tags.get('leisure') or 'other'
        type_counts[amenity_type] = type_counts.get(amenity_type, 0) + 1
    
    return entropy_mix(type_counts)
