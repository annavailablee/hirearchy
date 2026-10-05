from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.profile import EmploymentType, ExperienceLevel, RemotePreference


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    description: str | None = None

    location: str | None = Field(default=None, max_length=255)
    remote_type: RemotePreference | None = None
    employment_type: EmploymentType | None = None
    experience_level: ExperienceLevel | None = None
    education_requirements: str | None = None

    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(default=None, max_length=8)

    deadline: datetime | None = None
    posted_at: datetime | None = None

    source: str = Field(default="manual", max_length=32)
    source_url: str | None = Field(default=None, max_length=1024)


class JobSkillOut(BaseModel):
    canonical: str
    category: str
    kind: str
    matched_text: str
    context: str | None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    company: str
    location: str | None
    remote_type: str | None
    employment_type: str | None
    experience_level: str | None
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    deadline: datetime | None
    posted_at: datetime | None
    source: str
    source_url: str | None
    created_at: datetime
    updated_at: datetime


class JobDetailOut(JobOut):
    description: str | None
    education_requirements: str | None
    created_by_user_id: UUID | None
    skills: list[JobSkillOut] = []