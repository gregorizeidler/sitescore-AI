from ..core.db import SessionLocal
from ..models.project import Project
from shapely.geometry import Point
import random

def run():
    db = SessionLocal()
    pts = [(-46.633, -23.55), (-46.65, -23.56), (-46.62, -23.54)]
    for i,(x,y) in enumerate(pts, start=1):
        p = Point(x,y)
        features = {
            "competition": random.randint(1,20),
            "offices": random.randint(50,200),
            "schools": random.randint(0,10),
            "parks": random.randint(0,5),
            "transit": random.randint(0,30),
            "flow_kde": random.uniform(0,30),
            "mix": random.uniform(0,1),
            "street_centrality": random.uniform(0,1)
        }
        score = min(100, max(0, 50 + (features['flow_kde']*0.5 - features['competition']*0.3)))
        pr = Project(
            name=f"Seed {i}", business_type="restaurante",
            geom=f"SRID=4326;{p.wkt}", centroid=f"SRID=4326;{p.wkt}",
            features=features, score=score
        ); db.add(pr)
    db.commit(); db.close()

if __name__ == "__main__":
    run()
