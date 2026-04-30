from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from app.config import settings

engine = create_engine(str(settings.DATABASE_URL))


def create_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
