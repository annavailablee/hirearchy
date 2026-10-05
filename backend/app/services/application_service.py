"""
Application state machine.

Legal transitions are declared in VALID_TRANSITIONS. Any transition not in
the set is rejected with InvalidTransitionError. Terminal states have no
outgoing edges.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationEvent


class InvalidTransitionError(Exception):
    def __init__(self, from_status: str, to_status: str):
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Cannot transition from {from_status} to {to_status}")


class ApplicationAlreadyExistsError(Exception):
    def __init__(self, application_id):
        self.application_id = application_id
        super().__init__(f"Application already exists: {application_id}")


ALL_STATUSES = {
    "DISCOVERED",
    "SAVED",
    "APPLIED",
    "ASSESSMENT",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
    "EXPIRED",
}

TERMINAL_STATUSES = {"OFFER", "REJECTED", "WITHDRAWN", "EXPIRED"}

VALID_TRANSITIONS: dict[str, set[str]] = {
    "DISCOVERED": {"SAVED", "APPLIED", "REJECTED", "WITHDRAWN", "EXPIRED"},
    "SAVED":      {"APPLIED", "REJECTED", "WITHDRAWN", "EXPIRED"},
    "APPLIED":    {"ASSESSMENT", "INTERVIEW", "OFFER", "REJECTED", "WITHDRAWN"},
    "ASSESSMENT": {"INTERVIEW", "OFFER", "REJECTED", "WITHDRAWN"},
    "INTERVIEW":  {"OFFER", "REJECTED", "WITHDRAWN"},
    "OFFER":      set(),
    "REJECTED":   set(),
    "WITHDRAWN":  set(),
    "EXPIRED":    set(),
}


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in VALID_TRANSITIONS.get(from_status, set())


def create_application(
    db: Session,
    user_id,
    job_id,
    initial_status: str = "SAVED",
    notes: str | None = None,
) -> Application:
    """
    Create an application. Initial status must be SAVED or DISCOVERED —
    you can't jump straight into OFFER.
    """
    if initial_status not in {"DISCOVERED", "SAVED"}:
        raise InvalidTransitionError("NONE", initial_status)

    existing = db.scalar(
        select(Application).where(
            Application.user_id == user_id, Application.job_id == job_id
        )
    )
    if existing is not None:
        raise ApplicationAlreadyExistsError(existing.id)

    app = Application(
        user_id=user_id,
        job_id=job_id,
        current_status=initial_status,
        notes=notes,
    )
    db.add(app)
    db.flush()

    db.add(
        ApplicationEvent(
            application_id=app.id,
            from_status=None,
            to_status=initial_status,
            notes="Application created",
        )
    )
    return app


def transition(
    db: Session, application: Application, to_status: str, notes: str | None = None
) -> Application:
    """Apply a state transition. Raises InvalidTransitionError on illegal moves."""
    if to_status not in ALL_STATUSES:
        raise InvalidTransitionError(application.current_status, to_status)
    if not can_transition(application.current_status, to_status):
        raise InvalidTransitionError(application.current_status, to_status)

    from_status = application.current_status
    application.current_status = to_status

    db.add(
        ApplicationEvent(
            application_id=application.id,
            from_status=from_status,
            to_status=to_status,
            notes=notes,
        )
    )
    return application


def get_or_create_saved(db: Session, user_id, job_id) -> Application:
    """
    Idempotent save: if the user already has any application for this job,
    return it. Otherwise create one with status SAVED.
    Used by POST /jobs/{id}/save.
    """
    existing = db.scalar(
        select(Application).where(
            Application.user_id == user_id, Application.job_id == job_id
        )
    )
    if existing is not None:
        return existing
    return create_application(db, user_id, job_id, initial_status="SAVED")