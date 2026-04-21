from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float


@router.get("/items")
def list_items():
    return []


@router.post("/items", status_code=201)
def create_item(item: Item):
    return item
