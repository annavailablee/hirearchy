from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeadlineKind(str, Enum):
    APPLICATION = "application"
    ASSESSMENT = "assessment"
    INTERVIEW = "interview"
    FOLLOW_UP = "follow_up"
    CUSTOM = "custom"


class DeadlineCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    kind: DeadlineKind = DeadlineKind.CUSTOM
    due_at: datetime
    application_id: UUID | None = None
    notes: str | None = None


class DeadlineUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    due_at: datetime | None = None
    notes: str | None = None
    completed: bool | None = None  # True sets completed_at=now, False clears it


class DeadlineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID | None
    title: str
    kind: str
    due_at: datetime
    completed_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class DeadlineWithPriority(DeadlineOut):
    priority: str