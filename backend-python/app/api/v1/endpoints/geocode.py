from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx
from ....core.cache import get_cache, set_cache

router = APIRouter()

@router.get("")
async def geocode(q: str = Query(min_length=3, max_length=200), limit: int = 5):
    cache_q = {"q": q, "limit": limit}
    cached = get_cache("geocode", cache_q)
    if cached: return JSONResponse(cached)
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": q, "format": "json", "limit": limit, "addressdetails": 1}
    headers = {"User-Agent": "SiteScoreAI/0.2 (admin@example.com)"}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
    results = [{
        "display_name": d.get("display_name"),
        "lat": float(d.get("lat")), "lon": float(d.get("lon")),
        "bbox": d.get("boundingbox")
    } for d in data]
    set_cache("geocode", cache_q, results, ttl_seconds=86400)
    return JSONResponse(results)
