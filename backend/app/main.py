from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import items
from backend.app.routes import app

app = FastAPI(title="AM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app.router)
app.include_router(items.router, prefix="/api")
