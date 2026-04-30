from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.models.neighborhood import Neighborhood
from app.models.prediction import Prediction
from app.services.predictor import predict

router = APIRouter(prefix="/predictions", tags=["predictions"])


class PredictionRequest(BaseModel):
    type: str
    neighborhood_id: str
    area: float
    bedrooms: int
    bathrooms: int
    parking: int


class ImpactFactor(BaseModel):
    label: str
    value: float
    weight: float


class PredictionResponse(BaseModel):
    price: float
    min: float
    max: float
    margin_pct: float
    factors: list[ImpactFactor]


@router.post("", response_model=PredictionResponse, status_code=201)
def create_prediction(body: PredictionRequest, session: Session = Depends(get_session)):
    neighborhood = session.exec(
        select(Neighborhood).where(Neighborhood.id == body.neighborhood_id)
    ).first()

    if not neighborhood:
        raise HTTPException(status_code=404, detail="Neighborhood not found")

    result = predict(
        type=body.type,
        neighborhood_name=neighborhood.name,
        area=body.area,
        bedrooms=body.bedrooms,
        bathrooms=body.bathrooms,
        parking=body.parking,
        latitude=neighborhood.latitude,
        longitude=neighborhood.longitude,
    )

    session.add(Prediction(
        type=body.type,
        neighborhood=neighborhood.name,
        area=body.area,
        bedrooms=body.bedrooms,
        bathrooms=body.bathrooms,
        parking=body.parking,
        estimated_price=result["price"],
        price_min=result["min"],
        price_max=result["max"],
    ))
    session.commit()

    return result
