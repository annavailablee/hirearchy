import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import Application
from app.models.user import User
from app.schemas.insights import (
    ApplicationInsightsOut,
    ResumeRef,
    SkillInsightItem,
    SkillInsightsOut,
)
from app.services.skill_insights import compute_skill_insights

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/skills", response_model=SkillInsightsOut)
def skill_insights(
    resume_id: uuid.UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkillInsightsOut:
    if resume_id is not None:
        from app.models.resume import Resume
        exists = db.scalar(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
        )
        if exists is None:
            raise HTTPException(status_code=404, detail="Resume not found")

    result = compute_skill_insights(db, user.id, resume_id)

    return SkillInsightsOut(
        jobs_analyzed=result.jobs_analyzed,
        resume_analyzed=(
            ResumeRef(id=uuid.UUID(result.resume_id), name=result.resume_name)
            if result.resume_id else None
        ),
        skills=[
            SkillInsightItem(
                canonical=s.canonical,
                category=s.category,
                frequency=s.frequency,
                frequency_pct=s.frequency_pct,
                user_has=s.user_has,
                user_context=s.user_context,
            )
            for s in result.skills
        ],
        strengths=result.strengths,
        gaps=result.gaps,
    )


@router.get("/applications", response_model=ApplicationInsightsOut)
def application_insights(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApplicationInsightsOut:
    """
    Simple funnel metrics over the user's applications.
    Rates are computed only over applications that have progressed past SAVED
    (i.e., that were actually submitted).
    """
    rows = db.execute(
        select(Application.current_status, func.count())
        .where(Application.user_id == user.id)
        .group_by(Application.current_status)
    ).all()
    by_status = {status: int(cnt) for status, cnt in rows}

    total = sum(by_status.values())

    # "Submitted" = anything past SAVED/DISCOVERED.
    submitted_statuses = {"APPLIED", "ASSESSMENT", "INTERVIEW", "OFFER", "REJECTED"}
    submitted = sum(by_status.get(s, 0) for s in submitted_statuses)

    # Reached assessment or beyond
    reached_assessment = sum(
        by_status.get(s, 0) for s in {"ASSESSMENT", "INTERVIEW", "OFFER"}
    )
    reached_interview = sum(by_status.get(s, 0) for s in {"INTERVIEW", "OFFER"})

    response_rate = round(100.0 * reached_assessment / submitted, 1) if submitted else 0.0
    interview_rate = round(100.0 * reached_interview / submitted, 1) if submitted else 0.0

    return ApplicationInsightsOut(
        total=total,
        by_status=by_status,
        response_rate_pct=response_rate,
        interview_rate_pct=interview_rate,
    )