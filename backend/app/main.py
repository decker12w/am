from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import create_db
from app.routes.neighborhoods import router as neighborhoods_router
from app.routes.predictions import router as predictions_router
from app.routes.model import router as model_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    create_db()
    yield


application = FastAPI(title="AM API", lifespan=lifespan)

application.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application.include_router(neighborhoods_router, prefix="/api")
application.include_router(predictions_router, prefix="/api")
application.include_router(model_router, prefix="/api")
