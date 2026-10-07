from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.models.resume import Resume
from app.schemas.profile_suggestions import ProfileSuggestion
from app.services.profile_suggestions import suggest_profile_fields

router = APIRouter(prefix="/profile", tags=["profile"])


def _require_profile(user: User) -> Profile:
    """
    Every user has a profile created at registration. If it's missing,
    something is wrong in the DB — fail loudly rather than silently creating one.
    """
    if user.profile is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile missing for user — data integrity issue",
        )
    return user.profile


@router.get("", response_model=ProfileOut)
def get_profile(user: User = Depends(get_current_user)) -> Profile:
    return _require_profile(user)


@router.put("", response_model=ProfileOut)
def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    profile = _require_profile(user)

    # exclude_unset=True: only apply fields the client actually sent.
    # A field omitted from the JSON body is left untouched.
    # A field explicitly set to null clears it.
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(profile, field, value)
@router.get("/suggestions", response_model=ProfileSuggestion)
def profile_suggestions(
    resume_id: uuid.UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileSuggestion:
    """
    Scan a resume's raw_text and return suggested profile fields.
    Uses the primary resume if resume_id is omitted.
    """
    if resume_id is not None:
        resume = db.scalar(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
        )
        if resume is None:
            raise HTTPException(status_code=404, detail="Resume not found")
    else:
        resume = db.scalar(
            select(Resume).where(
                Resume.user_id == user.id, Resume.is_primary.is_(True)
            )
        )
        if resume is None:
            raise HTTPException(
                status_code=400,
                detail="No primary resume. Upload one or specify resume_id.",
            )

    if resume.extraction_status != "success" or not resume.raw_text:
        raise HTTPException(
            status_code=422,
            detail="This resume has no extractable text to analyze.",
        )

    result = suggest_profile_fields(resume.raw_text)
    return ProfileSuggestion(
        degree=result.degree,
        education=result.education,
        graduation_year=result.graduation_year,
        source_resume_id=str(resume.id),
        source_resume_name=resume.name,
        notes=result.notes,
    )

    db.commit()
    db.refresh(profile)
    return profile