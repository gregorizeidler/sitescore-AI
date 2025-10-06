from fastapi import APIRouter
from .endpoints.scoring import router as scoring_router
from .endpoints.layers import router as layers_router
from .endpoints.projects import router as projects_router
from .endpoints.geocode import router as geocode_router
from .endpoints.health import router as health_router
from .endpoints.advanced_analysis import router as advanced_router

api_router = APIRouter()
api_router.include_router(scoring_router, prefix="/score", tags=["score"])
api_router.include_router(layers_router, prefix="/layers", tags=["layers"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(geocode_router, prefix="/geocode", tags=["geocoding"])
api_router.include_router(advanced_router, prefix="/analysis", tags=["advanced"])

api_router.include_router(health_router, tags=["health"])