"""
Maintenance operations run by the background scheduler.

Each function is pure logic on the DB session — no scheduling, no HTTP.
"""
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.deadline import Deadline
from app.models.job import Job

logger = logging.getLogger(__name__)

DEADLINE_AUTO_CLOSE_DAYS = 14


def expire_stale_deadlines(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    cutoff = now - timedelta(days=DEADLINE_AUTO_CLOSE_DAYS)

    stmt = (
        update(Deadline)
        .where(Deadline.completed_at.is_(None), Deadline.due_at < cutoff)
        .values(completed_at=now)
    )
    result = db.execute(stmt)
    db.commit()

    count = result.rowcount or 0
    if count:
        logger.info("Auto-closed %d stale deadlines", count)
    return count


def mark_expired_jobs(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)

    stmt = (
        update(Job)
        .where(
            Job.deadline.is_not(None),
            Job.deadline < now,
            Job.is_expired.is_(False),
        )
        .values(is_expired=True)
    )
    result = db.execute(stmt)
    db.commit()

    count = result.rowcount or 0
    if count:
        logger.info("Marked %d jobs as expired", count)
    return count


def run_all_maintenance(db: Session, now: datetime | None = None) -> dict:
    now = now or datetime.now(UTC)
    return {
        "ran_at": now.isoformat(),
        "deadlines_closed": expire_stale_deadlines(db, now),
        "jobs_expired": mark_expired_jobs(db, now),
    }