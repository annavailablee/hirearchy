from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.services.maintenance import run_all_maintenance

router = APIRouter(tags=["health"])


@router.get("/health")
def liveness():
    """
    Liveness: is the process alive?
    Should almost never fail. If this fails, the orchestrator should
    kill and restart the container.
    """
    return {
        "status": "alive",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/ready")
def readiness(db: Session = Depends(get_db)):
    """
    Readiness: can this instance serve traffic?
    Checks the DB connection. If this fails, the load balancer should
    route around this instance — but NOT kill it.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "unavailable"

    ready = db_status == "connected"
    return {
        "status": "ready" if ready else "not_ready",
        "database": db_status,
        "version": settings.app_version,
    }


@router.post("/dev/maintenance/run")
def trigger_maintenance(db: Session = Depends(get_db)):
    """Run maintenance now. Development only."""
    if settings.environment != "development":
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return run_all_maintenance(db)