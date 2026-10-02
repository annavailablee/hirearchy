from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileOut, ProfileUpdate

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

    db.commit()
    db.refresh(profile)
    return profile