from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    overall = "healthy" if db_status == "connected" else "degraded"

    return {
        "status": overall,
        "database": db_status,
        "version": settings.app_version,
        "environment": settings.environment,
    }