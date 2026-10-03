import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.job import JobSkill


class Skill(Base):
    """Canonical skill dictionary, seeded from the taxonomy on first upload."""

    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    canonical: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    resume_links: Mapped[list["ResumeSkill"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )

class ResumeSkill(Base):
    """
    A skill detected on a specific resume.
    Composite PK (resume_id, skill_id) means each skill appears at most once per resume.
    """

    __tablename__ = "resume_skills"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    matched_text: Mapped[str] = mapped_column(String(120), nullable=False)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    skill: Mapped[Skill] = relationship(back_populates="resume_links")

    resume: Mapped["Resume"] = relationship(back_populates="skill_links")