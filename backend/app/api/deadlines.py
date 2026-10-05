import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import Application
from app.models.deadline import Deadline
from app.models.user import User
from app.schemas.deadline import (
    DeadlineCreate,
    DeadlineOut,
    DeadlineUpdate,
    DeadlineWithPriority,
)
from app.services.deadline_service import (
    compute_priority,
    priority_rank,
    within_attention_window,
)

router = APIRouter(prefix="/deadlines", tags=["deadlines"])


def _get_owned(deadline_id: uuid.UUID, user: User, db: Session) -> Deadline:
    d = db.scalar(
        select(Deadline).where(Deadline.id == deadline_id, Deadline.user_id == user.id)
    )
    if d is None:
        raise HTTPException(status_code=404, detail="Deadline not found")
    return d


@router.post("", response_model=DeadlineOut, status_code=status.HTTP_201_CREATED)
def create_deadline(
    data: DeadlineCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Deadline:
    # If an application is given, it must belong to the user.
    if data.application_id is not None:
        app = db.scalar(
            select(Application).where(
                Application.id == data.application_id,
                Application.user_id == user.id,
            )
        )
        if app is None:
            raise HTTPException(status_code=404, detail="Application not found")

    d = Deadline(
        user_id=user.id,
        application_id=data.application_id,
        title=data.title,
        kind=data.kind.value,
        due_at=data.due_at,
        notes=data.notes,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.get("", response_model=list[DeadlineWithPriority])
def list_deadlines(
    include_completed: bool = Query(default=False),
    kind: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeadlineWithPriority]:
    stmt = select(Deadline).where(Deadline.user_id == user.id)
    if not include_completed:
        stmt = stmt.where(Deadline.completed_at.is_(None))
    if kind:
        stmt = stmt.where(Deadline.kind == kind)
    stmt = stmt.order_by(Deadline.due_at.asc())

    rows = db.scalars(stmt).all()
    return [
        DeadlineWithPriority(
            **DeadlineOut.model_validate(d).model_dump(),
            priority=compute_priority(d.due_at, d.completed_at),
        )
        for d in rows
    ]


@router.get("/attention", response_model=list[DeadlineWithPriority])
def attention_queue(
    days: int = Query(default=7, ge=1, le=30),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeadlineWithPriority]:
    """
    The 'needs attention' queue: overdue + due within `days`.
    Sorted by urgency (OVERDUE first, then by due_at).
    """
    rows = db.scalars(
        select(Deadline).where(Deadline.user_id == user.id)
    ).all()

    now = datetime.now(timezone.utc)
    in_window = [
        d for d in rows
        if within_attention_window(d.due_at, d.completed_at, days=days, now=now)
    ]

    result = [
        DeadlineWithPriority(
            **DeadlineOut.model_validate(d).model_dump(),
            priority=compute_priority(d.due_at, d.completed_at, now=now),
        )
        for d in in_window
    ]
    result.sort(key=lambda x: (priority_rank(x.priority), x.due_at))
    return result


@router.get("/{deadline_id}", response_model=DeadlineWithPriority)
def get_deadline(
    deadline_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeadlineWithPriority:
    d = _get_owned(deadline_id, user, db)
    return DeadlineWithPriority(
        **DeadlineOut.model_validate(d).model_dump(),
        priority=compute_priority(d.due_at, d.completed_at),
    )


@router.patch("/{deadline_id}", response_model=DeadlineWithPriority)
def update_deadline(
    deadline_id: uuid.UUID,
    data: DeadlineUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeadlineWithPriority:
    d = _get_owned(deadline_id, user, db)
    updates = data.model_dump(exclude_unset=True)

    if "completed" in updates:
        completed = updates.pop("completed")
        d.completed_at = datetime.now(timezone.utc) if completed else None

    for field, value in updates.items():
        setattr(d, field, value)

    db.commit()
    db.refresh(d)
    return DeadlineWithPriority(
        **DeadlineOut.model_validate(d).model_dump(),
        priority=compute_priority(d.due_at, d.completed_at),
    )


@router.delete("/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deadline(
    deadline_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    d = _get_owned(deadline_id, user, db)
    db.delete(d)
    db.commit()