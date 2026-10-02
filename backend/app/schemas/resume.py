from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResumeOut(BaseModel):
    """List view — no raw_text (could be large)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    original_filename: str
    content_type: str
    file_size: int
    extraction_status: str
    is_primary: bool
    uploaded_at: datetime
    updated_at: datetime


class ResumeDetailOut(ResumeOut):
    """Detail view — includes the extracted text."""
    raw_text: str | None
    extraction_error: str | None


class ResumeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    is_primary: bool | None = None