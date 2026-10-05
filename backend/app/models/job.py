import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.skill import Skill
    from app.models.user import User


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        # Unique URL when present (Postgres allows multiple NULLs).
        UniqueConstraint("source_url", name="uq_jobs_source_url"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Nullable: if the creator deletes their account, the job survives.
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Core fields
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classification
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remote_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    education_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Compensation
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)

    # Dates
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_expired: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    # Source tracking
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    skill_links: Mapped[list["JobSkill"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class JobSkill(Base):
    """
    A skill required or preferred by a job.
    `kind` distinguishes the two. Composite PK (job_id, skill_id) means each
    skill appears at most once per job — required wins if both are indicated.
    """

    __tablename__ = "job_skills"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # "required" | "preferred"
    kind: Mapped[str] = mapped_column(
        String(16), nullable=False, default="required", server_default="required"
    )
    matched_text: Mapped[str] = mapped_column(String(120), nullable=False)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    job: Mapped[Job] = relationship(back_populates="skill_links")
    skill: Mapped["Skill"] = relationship()