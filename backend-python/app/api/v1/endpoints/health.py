from fastapi import APIRouter
from ....core.config import settings
from ....core.gtfs import get_gtfs_status

router = APIRouter()

@router.get("/health")
def health():
    gtfs_status = get_gtfs_status()
    return {
        "status": "ok", 
        "overpass_url": settings.OVERPASS_URL,
        "gtfs": gtfs_status
    }
