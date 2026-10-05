"""
Background job scheduler.

Runs inside the FastAPI process via lifespan. Single-instance assumption —
see note in the code for horizontal scaling.
"""
import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services.maintenance import run_all_maintenance

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _run_maintenance() -> None:
    db = SessionLocal()
    try:
        summary = run_all_maintenance(db)
        logger.info("Maintenance complete: %s", summary)
    except Exception:
        logger.exception("Maintenance job failed")
    finally:
        db.close()


@asynccontextmanager
async def lifespan_scheduler(app):
    global _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        _run_maintenance,
        trigger="interval",
        hours=6,
        id="maintenance",
        replace_existing=True,
        next_run_time=None,
    )
    _scheduler.start()
    logger.info("Background scheduler started")

    try:
        yield
    finally:
        _scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped")