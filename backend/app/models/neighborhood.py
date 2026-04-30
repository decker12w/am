from sqlmodel import SQLModel, Field
from app.models.utils import new_ulid


class Neighborhood(SQLModel, table=True):
    id: str = Field(default_factory=new_ulid, primary_key=True)
    name: str = Field(unique=True, index=True)
    latitude: float
    longitude: float
