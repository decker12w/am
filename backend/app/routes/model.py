import json
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/model", tags=["model"])

METRICS_PATH = Path(__file__).parents[2] / "models" / "metrics.json"


class ModelMetrics(BaseModel):
    model: str
    mae: float
    r2: float
    n_samples: int


@router.get("/metrics", response_model=ModelMetrics)
def get_metrics():
    return json.loads(METRICS_PATH.read_text())
