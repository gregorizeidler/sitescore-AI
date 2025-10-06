from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shapely.geometry import shape
from sqlalchemy import select
from ....core.db import SessionLocal
from ....models.project import Project
from ....schemas import ProjectCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("")
def list_projects(db: Session = Depends(get_db)):
    res = db.execute(select(Project).order_by(Project.id.desc()).limit(200)).scalars().all()
    return [{
        "id": p.id, "name": p.name, "business_type": p.business_type,
        "score": p.score, "created_at": p.created_at.isoformat()
    } for p in res]

@router.get("/{pid}")
def read_project(pid: int, db: Session = Depends(get_db)):
    p = db.get(Project, pid)
    if not p: raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": p.id, "name": p.name, "business_type": p.business_type,
        "features": p.features, "score": p.score, "created_at": p.created_at.isoformat()
    }

@router.post("")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    geom = shape(payload.geometry.model_dump())
    cen = geom.centroid
    p = Project(
        name=payload.name, business_type=payload.business_type,
        geom=f"SRID=4326;{geom.wkt}", centroid=f"SRID=4326;{cen.wkt}",
        features=payload.features, score=payload.score
    )
    db.add(p); db.commit(); db.refresh(p)
    return {"id": p.id}
