from fastapi import APIRouter

router = APIRouter()

@router.get("/check")
def check_health():
    """Check the health of the application."""
    return {"status": "ok"}
