from datetime import datetime, UTC
from ulid import ULID


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_ulid() -> str:
    return str(ULID())
