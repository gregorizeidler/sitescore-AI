from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.db import init_db
from .api.v1.router import api_router
from .core.metrics import setup_instrumentation
from .core.gtfs import load_gtfs
import os

app = FastAPI(title="SiteScore AI", version="0.2.0")

# Setup Prometheus ANTES de qualquer outra coisa
setup_instrumentation(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    gtfs_path = os.getenv("GTFS_ZIP_PATH", "")
    if gtfs_path and os.path.exists(gtfs_path):
        load_gtfs(gtfs_path)

app.include_router(api_router, prefix="/api/v1")
