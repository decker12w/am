from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel

from app.database import get_session
from app.models.neighborhood import Neighborhood

router = APIRouter(prefix="/neighborhoods", tags=["neighborhoods"])


class NeighborhoodResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float


@router.get("", response_model=list[NeighborhoodResponse])
def list_neighborhoods(session: Session = Depends(get_session)):
    return session.exec(select(Neighborhood).order_by(Neighborhood.name)).all()
