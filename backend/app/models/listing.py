from sqlmodel import SQLModel, Field
from datetime import datetime
from app.models.utils import utcnow, new_ulid


class Listing(SQLModel, table=True):
    id: str = Field(default_factory=new_ulid, primary_key=True)
    source: str = Field(index=True)
    source_code: str
    type: str
    purpose: str
    rent_price: float | None = None
    neighborhood: str = Field(index=True)
    latitude: float | None = None
    longitude: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    parking: int | None = None
    useful_area: float | None = None
    built_area: float | None = None
    url: str | None = None
    scraped_at: datetime = Field(default_factory=utcnow)
