from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ....core.db import SessionLocal
from ....schemas import ScoreRequest, ScoreResponse
from ....core.overpass_client import build_query, BUSINESS_TAGS, POI_TAGS_COMMON, TRANSIT_TAGS, POI_TAGS_OFFICES, POI_TAGS_SCHOOLS, POI_TAGS_PARKS, fetch_overpass
from ....core.features import to_geodf, nearest_distance_meters, count_within_radius, kde_value, entropy_mix, filter_by_tag
from ....core.centrality import street_centrality_value
from ....core.gtfs import GTFS, is_gtfs_available
from ....core.auth import get_current_user, User
from ....core.rate_limit import enforce_quota, inc_overpass_count
from ....core.audit import log_overpass_audit
from shapely.geometry import shape, Point
import asyncio, os, joblib

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def bbox_from_geom(geom):
    if geom.geom_type == "Point":
        delta = 0.003
        return (geom.y - delta, geom.x - delta, geom.y + delta, geom.x + delta)
    else:
        xs, ys = zip(*list(geom.envelope.exterior.coords))
        return (min(ys), min(xs), max(ys), max(xs))

def _maybe_ml_predict(business_type: str, raw_features: dict, segment: str | None):
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models_store")
    fname = f"{business_type}.joblib" if not segment else f"{business_type}_{segment}.joblib"
    path = os.path.join(models_dir, fname)
    if not os.path.exists(path): return None
    try:
        model = joblib.load(path)
        feats = ['competition','offices','schools','parks','transit','flow_kde','mix','street_centrality']
        X = [[ raw_features.get(k, 0.0) for k in feats ]]
        pred = float(model.predict(X)[0])
        return max(0.0, min(100.0, pred))
    except Exception:
        return None

@router.post("", response_model=ScoreResponse)
async def score_location(req: ScoreRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_quota(user.sub, limit_per_minute=60)
    
    # Validar business_type
    if req.business_type not in BUSINESS_TAGS:
        valid_types = list(BUSINESS_TAGS.keys())
        raise HTTPException(
            status_code=400, 
            detail=f"business_type '{req.business_type}' inválido. Tipos válidos: {', '.join(valid_types)}"
        )
    
    geom = shape(req.geometry.model_dump())
    if geom.geom_type not in ("Point", "Polygon", "MultiPolygon"):
        raise HTTPException(status_code=400, detail="Geometry deve ser Point ou (Multi)Polygon")
    center_pt = geom if geom.geom_type == "Point" else geom.centroid
    bbox = bbox_from_geom(geom)

    q_comp = build_query(bbox, BUSINESS_TAGS[req.business_type])
    q_pois = build_query(bbox, POI_TAGS_COMMON + POI_TAGS_OFFICES + POI_TAGS_SCHOOLS + POI_TAGS_PARKS)
    q_tran = build_query(bbox, TRANSIT_TAGS)

    async def run(q):
        inc_overpass_count(user.sub)
        try:
            data = await fetch_overpass(q)
            log_overpass_audit(db, user.sub, q, str(bbox), status="success")
            return data
        except Exception:
            log_overpass_audit(db, user.sub, q, str(bbox), status="error")
            raise

    comp_json, poi_json, transit_json = await asyncio.gather(run(q_comp), run(q_pois), run(q_tran))
    comp_gdf = to_geodf(comp_json)
    poi_gdf = to_geodf(poi_json)
    transit_gdf = to_geodf(transit_json)

    # Usar GTFS se disponível, senão usa dados do Overpass
    if is_gtfs_available():
        transit_gdf = GTFS['stops'][['geometry','trips_per_hour']].copy()
        # Log para debugging
        import logging
        logging.getLogger(__name__).info(f"✅ Usando dados GTFS: {len(transit_gdf)} paradas")

    if geom.geom_type != "Point":
        comp_gdf = comp_gdf[comp_gdf.within(geom)]
        poi_gdf = poi_gdf[poi_gdf.within(geom)]
        if hasattr(transit_gdf, 'within'):
            transit_gdf = transit_gdf[transit_gdf.within(geom)]

    offices_gdf = filter_by_tag(poi_gdf, 'office')
    schools_gdf = filter_by_tag(poi_gdf, 'amenity', ['school','university'])
    parks_gdf   = filter_by_tag(poi_gdf, 'leisure', ['park'])

    comp_500   = count_within_radius(comp_gdf, center_pt, 500)
    offices_500= count_within_radius(offices_gdf, center_pt, 500)
    schools_500= count_within_radius(schools_gdf, center_pt, 500)
    parks_500  = count_within_radius(parks_gdf, center_pt, 500)
    transit_300= count_within_radius(transit_gdf, center_pt, 300) if hasattr(transit_gdf, 'geometry') else 0
    dist_transit = nearest_distance_meters(transit_gdf, center_pt) if hasattr(transit_gdf, 'geometry') else float('inf')
    flow = kde_value(center_pt, [transit_gdf, offices_gdf, comp_gdf], bandwidth_m=200)

    street_centrality = street_centrality_value(bbox, center_pt.x, center_pt.y)
    mix = entropy_mix({"offices":offices_500, "schools":schools_500, "parks":parks_500, "comp":comp_500})

    raw_features = {
        "competition": comp_500,
        "offices": offices_500,
        "schools": schools_500,
        "parks": parks_500,
        "transit": transit_300,
        "flow_kde": flow,
        "mix": mix,
        "dist_transit_m": dist_transit,
        "street_centrality": street_centrality
    }

    segment = request.query_params.get("segment")
    ml_score = _maybe_ml_predict(req.business_type, raw_features, segment)
    if ml_score is None:
        from ....core.scoring_model import compute_score
        score, contributions, explanation = compute_score(req.business_type, raw_features)
    else:
        score = ml_score
        contributions = [{"name": k, "value": v, "weight": 0.0, "contribution": 0.0, "description": "ML model"} for k,v in raw_features.items()]
        explanation = "Score gerado por modelo treinado (ML)."

    return JSONResponse({
        "score": score,
        "features": contributions,
        "explanation": explanation,
        "center": [center_pt.x, center_pt.y],
        "layer_refs": {
            "competition": "/api/v1/layers/competition",
            "pois": "/api/v1/layers/pois",
            "transit": "/api/v1/layers/transit",
            "flow": "/api/v1/layers/flow"
        }
    })
