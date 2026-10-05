from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import (
    AttentionSection,
    DashboardOut,
    TopSkillItem,
    UpcomingItem,
)
from app.schemas.deadline import DeadlineOut, DeadlineWithPriority
from app.services.dashboard import build_dashboard
from app.services.deadline_service import compute_priority

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardOut:
    data = build_dashboard(db, user.id)
    now = data["generated_at"]

    def to_priority_out(d):
        return DeadlineWithPriority(
            **DeadlineOut.model_validate(d).model_dump(),
            priority=compute_priority(d.due_at, d.completed_at, now),
        )

    return DashboardOut(
        generated_at=now,
        attention=AttentionSection(
            overdue_count=data["attention"]["overdue_count"],
            urgent_count=data["attention"]["urgent_count"],
            top_items=[to_priority_out(d) for d in data["attention"]["top_items"]],
        ),
        applications=data["applications"],
        upcoming=[
            UpcomingItem(
                deadline_id=u["deadline"].id,
                title=u["deadline"].title,
                kind=u["deadline"].kind,
                due_at=u["deadline"].due_at,
                priority=u["priority"],
                job_id=u["job"].id if u["job"] else None,
                job_title=u["job"].title if u["job"] else None,
                company=u["job"].company if u["job"] else None,
            )
            for u in data["upcoming"]
        ],
        top_skills=[
            TopSkillItem(
                canonical=s.canonical,
                category=s.category,
                frequency_pct=s.frequency_pct,
                user_has=s.user_has,
            )
            for s in data["top_skills"]
        ],
        gaps=data["gaps"],
    )