from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/neighborhoods")
def list_neighborhoods():
    return {"status": "ok"}

@router.get("/predictions")
def health_check():
    return {"status": "ok"}
