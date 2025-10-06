from fastapi import APIRouter, Query, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from shapely.geometry import Point
from typing import Optional
from ....core.overpass_client import (
    build_query, BUSINESS_TAGS, POI_TAGS_COMMON, TRANSIT_TAGS, fetch_overpass,
    WALKABILITY_TAGS, CYCLABILITY_TAGS, GREEN_TAGS, PARKING_TAGS, LIGHTING_TAGS,
    OverpassError, OverpassRateLimitError
)
from ....core.auth import get_current_user, User
from ....core.rate_limit import enforce_quota, inc_overpass_count
from ....core.features import to_geodf, kde_value
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{layer_name}")
async def get_layer(layer_name: str,
                    request: Request,
                    user: User = Depends(get_current_user),
                    business_type: Optional[str] = Query(default="restaurante"),
                    bbox: Optional[str] = Query(default=None)):
    enforce_quota(user.sub, limit_per_minute=120)
    
    # Validar business_type
    if business_type not in BUSINESS_TAGS:
        raise HTTPException(
            status_code=400,
            detail=f"business_type '{business_type}' inválido. Tipos válidos: {', '.join(BUSINESS_TAGS.keys())}"
        )
    
    if bbox:
        W, S, E, N = [float(x) for x in bbox.split(",")]
        bbox_tuple = (S, W, N, E)
    else:
        bbox_tuple = (-23.7, -46.8, -23.5, -46.6)

    if layer_name == "competition":
        q = build_query(bbox_tuple, BUSINESS_TAGS[business_type])
    elif layer_name == "pois":
        q = build_query(bbox_tuple, POI_TAGS_COMMON)
    elif layer_name == "transit":
        q = build_query(bbox_tuple, TRANSIT_TAGS)
    elif layer_name == "flow":
        q1 = build_query(bbox_tuple, POI_TAGS_COMMON)
        q2 = build_query(bbox_tuple, TRANSIT_TAGS)
        async def run(q):
            inc_overpass_count(user.sub)
            try:
                return await fetch_overpass(q)
            except (OverpassError, OverpassRateLimitError) as e:
                logger.warning(f"Erro ao buscar dados para flow: {e}")
                return {"elements": []}
        
        poi, tr = await asyncio.gather(run(q1), run(q2))
        poi_gdf = to_geodf(poi); tr_gdf = to_geodf(tr)
        
        if poi_gdf.empty and tr_gdf.empty:
            return JSONResponse({ 
                "type": "FeatureCollection", 
                "features": [],
                "error": "rate_limit_exceeded",
                "message": "Limite de requisições atingido. Aguarde alguns segundos e tente novamente."
            })
        
        minx, miny, maxx, maxy = (bbox_tuple[1], bbox_tuple[0], bbox_tuple[3], bbox_tuple[2])
        step = max((maxx-minx), (maxy-miny)) / 50.0
        feats = []
        y = miny
        while y <= maxy:
            x = minx
            while x <= maxx:
                val = kde_value(Point(x, y), [poi_gdf, tr_gdf], 200)
                feats.append({ "type": "Feature", "geometry": { "type": "Point", "coordinates": [x, y] }, "properties": { "value": val } })
                x += step
            y += step
        return JSONResponse({ "type": "FeatureCollection", "features": feats })
    elif layer_name == "buildings":
        # Query personalizada para buildings (pega todos os ways com tag building)
        S, W, N, E = bbox_tuple
        q = f"""
        [out:json][timeout:25];
        (
          way["building"]({S},{W},{N},{E});
        );
        out geom;
        """
        inc_overpass_count(user.sub)
        
        try:
            data = await fetch_overpass(q)
        except (OverpassError, OverpassRateLimitError) as e:
            logger.warning(f"Erro ao buscar buildings: {e}")
            return JSONResponse({ 
                "type": "FeatureCollection", 
                "features": [],
                "error": "rate_limit_exceeded",
                "message": "Limite de requisições atingido. Aguarde alguns segundos e tente novamente."
            })
        
        # Processar buildings como polígonos
        features = []
        for el in data.get("elements", []):
            if el.get("type") == "way" and "nodes" in el:
                # Tentar obter coordenadas se disponíveis
                if "geometry" in el:
                    coords = [[n["lon"], n["lat"]] for n in el["geometry"]]
                    if len(coords) >= 3:
                        # Fechar o polígono se necessário
                        if coords[0] != coords[-1]:
                            coords.append(coords[0])
                        
                        building_type = el.get("tags", {}).get("building", "yes")
                        features.append({
                            "type": "Feature",
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [coords]
                            },
                            "properties": {
                                "building": building_type,
                                "name": el.get("tags", {}).get("name", "")
                            }
                        })
        return JSONResponse({ "type": "FeatureCollection", "features": features })
    
    elif layer_name == "walkability":
        q = build_query(bbox_tuple, WALKABILITY_TAGS)
    elif layer_name == "cyclability":
        q = build_query(bbox_tuple, CYCLABILITY_TAGS)
    elif layer_name == "green_spaces":
        q = build_query(bbox_tuple, GREEN_TAGS)
    elif layer_name == "parking":
        q = build_query(bbox_tuple, PARKING_TAGS)
    elif layer_name == "lighting":
        q = build_query(bbox_tuple, LIGHTING_TAGS)
    else:
        return JSONResponse({ "type": "FeatureCollection", "features": [] })

    inc_overpass_count(user.sub)
    
    try:
        data = await fetch_overpass(q)
    except (OverpassError, OverpassRateLimitError) as e:
        logger.warning(f"Erro ao buscar layer {layer_name}: {e}")
        # Retornar GeoJSON vazio ao invés de erro 500
        return JSONResponse({ 
            "type": "FeatureCollection", 
            "features": [],
            "error": "rate_limit_exceeded",
            "message": "Limite de requisições atingido. Aguarde alguns segundos e tente novamente."
        })
    
    # Processar elementos preservando todas as informações
    features = []
    for el in data.get("elements", []):
        # Obter coordenadas
        lat = el.get("lat")
        lon = el.get("lon")
        
        # Se não tiver coordenadas diretas, tentar obter do centro (para ways)
        if lat is None or lon is None:
            if "center" in el:
                lat = el["center"]["lat"]
                lon = el["center"]["lon"]
            else:
                continue  # Skip se não tiver coordenadas
        
        # Montar properties com todas as informações
        properties = {
            "id": el.get("id"),
            "type": el.get("type"),
            "lat": lat,
            "lon": lon,
            "tags": el.get("tags", {})
        }
        
        # Adicionar nome se existir
        if "tags" in el and "name" in el["tags"]:
            properties["name"] = el["tags"]["name"]
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": properties
        })
    
    return JSONResponse({ "type": "FeatureCollection", "features": features })
