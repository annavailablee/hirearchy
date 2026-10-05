from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RemotePreference(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    ANY = "any"


class EmploymentType(StrEnum):
    INTERNSHIP = "internship"
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"


class ExperienceLevel(StrEnum):
    STUDENT = "student"
    FRESHER = "fresher"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class ProfileUpdate(BaseModel):
    """All fields optional — this is effectively a PATCH body behind a PUT verb."""
    education: str | None = Field(default=None, max_length=255)
    degree: str | None = Field(default=None, max_length=255)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    current_location: str | None = Field(default=None, max_length=255)
    preferred_locations: list[str] | None = None
    remote_preference: RemotePreference | None = None
    preferred_employment_types: list[EmploymentType] | None = None
    target_roles: list[str] | None = None
    experience_level: ExperienceLevel | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(default=None, max_length=8)
    work_authorization: str | None = Field(default=None, max_length=64)


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    education: str | None
    degree: str | None
    graduation_year: int | None
    current_location: str | None
    preferred_locations: list[str]
    remote_preference: RemotePreference | None
    preferred_employment_types: list[EmploymentType]
    target_roles: list[str]
    experience_level: ExperienceLevel | None
    salary_min: int | None
    salary_currency: str | None
    work_authorization: str | None
    updated_at: datetime