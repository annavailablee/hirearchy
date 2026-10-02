import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Education
    education: Mapped[str | None] = mapped_column(String(255), nullable=True)
    degree: Mapped[str | None] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Location
    current_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferred_locations: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list,
        server_default=text("'{}'::text[]"),
    )
    remote_preference: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Job preferences
    preferred_employment_types: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list,
        server_default=text("'{}'::text[]"),
    )
    target_roles: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list,
        server_default=text("'{}'::text[]"),
    )
    experience_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    work_authorization: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="profile")