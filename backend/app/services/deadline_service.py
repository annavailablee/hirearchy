"""
Deadline priority and attention-queue logic.

All pure functions on datetimes and simple objects — no DB, no HTTP.
The endpoint assembles inputs and calls these.
"""
from datetime import UTC, datetime, timedelta

_PRIORITY_ORDER = {
    "OVERDUE": 0,
    "URGENT": 1,
    "HIGH": 2,
    "NORMAL": 3,
    "LATER": 4,
    "COMPLETED": 5,
}


def compute_priority(
    due_at: datetime, completed_at: datetime | None, now: datetime | None = None
) -> str:
    if completed_at is not None:
        return "COMPLETED"

    now = now or datetime.now(UTC)
    delta = due_at - now

    if delta.total_seconds() < 0:
        return "OVERDUE"

    hours = delta.total_seconds() / 3600
    if hours <= 24:
        return "URGENT"
    if hours <= 72:
        return "HIGH"
    if hours <= 24 * 7:
        return "NORMAL"
    return "LATER"


def priority_rank(priority: str) -> int:
    return _PRIORITY_ORDER.get(priority, 99)


def within_attention_window(
    due_at: datetime, completed_at: datetime | None, days: int = 7,
    now: datetime | None = None,
) -> bool:
    """
    True if this deadline belongs in the attention queue:
    - not completed, AND
    - overdue OR due within `days`
    """
    if completed_at is not None:
        return False
    now = now or datetime.now(UTC)
    return due_at <= now + timedelta(days=days)