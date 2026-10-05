"""
Dashboard orchestration.

Assembles data from multiple existing services into one response.
Does NOT contain business logic — that lives in the underlying services.
If a query here gets complex, it belongs in the underlying service, not here.
"""
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.deadline import Deadline
from app.models.job import Job
from app.services.deadline_service import (
    compute_priority,
    priority_rank,
    within_attention_window,
)
from app.services.skill_insights import compute_skill_insights

# Limits to keep the dashboard fast and focused.
UPCOMING_LIMIT = 10
TOP_SKILLS_LIMIT = 8
ATTENTION_TOP_ITEMS = 5


def _application_counts(db: Session, user_id) -> dict[str, int]:
    rows = db.execute(
        select(Application.current_status, func.count())
        .where(Application.user_id == user_id)
        .group_by(Application.current_status)
    ).all()
    return {status: int(cnt) for status, cnt in rows}


def _funnel_from_counts(by_status: dict[str, int]):
    """
    Compute response and interview rates from a status-count dict.
    Extracted from the applications insights endpoint — same math, one source.
    """
    submitted_statuses = {"APPLIED", "ASSESSMENT", "INTERVIEW", "OFFER", "REJECTED"}
    submitted = sum(by_status.get(s, 0) for s in submitted_statuses)

    reached_assessment = sum(
        by_status.get(s, 0) for s in {"ASSESSMENT", "INTERVIEW", "OFFER"}
    )
    reached_interview = sum(by_status.get(s, 0) for s in {"INTERVIEW", "OFFER"})

    response_rate = round(100.0 * reached_assessment / submitted, 1) if submitted else 0.0
    interview_rate = round(100.0 * reached_interview / submitted, 1) if submitted else 0.0
    return response_rate, interview_rate


def _attention_items(db: Session, user_id, now: datetime):
    """All deadlines within the attention window (7 days), sorted by urgency."""
    rows = db.scalars(
        select(Deadline).where(Deadline.user_id == user_id)
    ).all()

    items = [
        d for d in rows
        if within_attention_window(d.due_at, d.completed_at, days=7, now=now)
    ]
    def sort_key(d):
        return (priority_rank(compute_priority(d.due_at, d.completed_at, now)), d.due_at)
    items.sort(key=sort_key)
    return items


def _upcoming_items(db: Session, user_id, now: datetime, limit: int):
    """
    Join Deadline → Application → Job so the dashboard can show context
    ("OA due tomorrow for Backend Intern at Acme").
    """
    rows = db.execute(
        select(Deadline, Job)
        .outerjoin(Application, Application.id == Deadline.application_id)
        .outerjoin(Job, Job.id == Application.job_id)
        .where(
            Deadline.user_id == user_id,
            Deadline.completed_at.is_(None),
            Deadline.due_at >= now,
        )
        .order_by(Deadline.due_at.asc())
        .limit(limit)
    ).all()
    return rows


def build_dashboard(db: Session, user_id) -> dict:
    """
    Return a plain dict; the endpoint converts to Pydantic.
    This keeps the service free of schema imports.
    """
    now = datetime.now(UTC)

    # ---- Applications ----
    by_status = _application_counts(db, user_id)
    total = sum(by_status.values())
    response_rate, interview_rate = _funnel_from_counts(by_status)

    # ---- Attention ----
    attention_items = _attention_items(db, user_id, now)
    overdue = [
        d for d in attention_items
        if compute_priority(d.due_at, d.completed_at, now) == "OVERDUE"
    ]
    urgent = [
        d for d in attention_items
        if compute_priority(d.due_at, d.completed_at, now) == "URGENT"
    ]

    # ---- Upcoming ----
    upcoming_rows = _upcoming_items(db, user_id, now, UPCOMING_LIMIT)
    upcoming = [
        {
            "deadline": d,
            "job": j,
            "priority": compute_priority(d.due_at, d.completed_at, now),
        }
        for d, j in upcoming_rows
    ]

    # ---- Skills ----
    skill_result = compute_skill_insights(db, user_id)
    top_skills = skill_result.skills[:TOP_SKILLS_LIMIT]

    return {
        "generated_at": now,
        "attention": {
            "overdue_count": len(overdue),
            "urgent_count": len(urgent),
            "top_items": attention_items[:ATTENTION_TOP_ITEMS],
        },
        "applications": {
            "total": total,
            "by_status": by_status,
            "response_rate_pct": response_rate,
            "interview_rate_pct": interview_rate,
        },
        "upcoming": upcoming,
        "top_skills": top_skills,
        "gaps": skill_result.gaps,
    }