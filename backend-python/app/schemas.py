from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Geometry(BaseModel):
    type: str
    coordinates: Any

class ScoreRequest(BaseModel):
    geometry: Geometry
    business_type: str = Field(pattern="^(restaurante|academia|varejo_moda)$")
    name: Optional[str] = None

class FeatureContribution(BaseModel):
    name: str
    value: float
    weight: float
    contribution: float
    description: str

class ScoreResponse(BaseModel):
    score: float
    features: List[FeatureContribution]
    explanation: str
    center: List[float]
    layer_refs: Dict[str, str]

class ProjectCreate(BaseModel):
    name: str
    business_type: str
    geometry: Geometry
    features: Dict[str, float]
    score: float
