from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    job_id: UUID
    initial_status: str = Field(default="SAVED", pattern="^(DISCOVERED|SAVED)$")
    notes: str | None = None


class ApplicationTransition(BaseModel):
    to_status: str
    notes: str | None = None


class ApplicationEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    from_status: str | None
    to_status: str
    notes: str | None
    occurred_at: datetime


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    current_status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ApplicationDetailOut(ApplicationOut):
    events: list[ApplicationEventOut]