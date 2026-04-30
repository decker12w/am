from sqlmodel import SQLModel, Field
from datetime import datetime
from app.models.utils import utcnow, new_ulid


class Prediction(SQLModel, table=True):
    id: str = Field(default_factory=new_ulid, primary_key=True)
    type: str
    neighborhood: str
    area: float
    bedrooms: int
    bathrooms: int
    parking: int
    estimated_price: float
    price_min: float
    price_max: float
    created_at: datetime = Field(default_factory=utcnow)
