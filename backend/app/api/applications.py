import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDetailOut,
    ApplicationOut,
    ApplicationTransition,
)
from app.services import application_service
from app.services.application_service import (
    ApplicationAlreadyExistsError,
    InvalidTransitionError,
)

router = APIRouter(prefix="/applications", tags=["applications"])


def _get_owned_application(
    application_id: uuid.UUID, user: User, db: Session
) -> Application:
    app = db.scalar(
        select(Application)
        .options(selectinload(Application.events))
        .where(Application.id == application_id, Application.user_id == user.id)
    )
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.post("", response_model=ApplicationDetailOut, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Application:
    job = db.get(Job, data.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        app = application_service.create_application(
            db, user.id, data.job_id, data.initial_status, data.notes
        )
    except ApplicationAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Application already exists (id: {exc.application_id})",
        )
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    db.commit()
    db.refresh(app)
    return app


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Application]:
    stmt = select(Application).where(Application.user_id == user.id)
    if status_filter:
        stmt = stmt.where(Application.current_status == status_filter)
    stmt = stmt.order_by(Application.updated_at.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt))


@router.get("/{application_id}", response_model=ApplicationDetailOut)
def get_application(
    application_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Application:
    return _get_owned_application(application_id, user, db)


@router.patch("/{application_id}", response_model=ApplicationDetailOut)
def transition_application(
    application_id: uuid.UUID,
    data: ApplicationTransition,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Application:
    app = _get_owned_application(application_id, user, db)
    try:
        application_service.transition(db, app, data.to_status, data.notes)
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    db.commit()
    db.refresh(app)
    return app


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    app = _get_owned_application(application_id, user, db)
    db.delete(app)
    db.commit()