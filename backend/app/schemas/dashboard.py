from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.deadline import DeadlineWithPriority
from app.schemas.insights import ApplicationInsightsOut


class TopSkillItem(BaseModel):
    canonical: str
    category: str
    frequency_pct: float
    user_has: bool


class UpcomingItem(BaseModel):
    deadline_id: UUID
    title: str
    kind: str
    due_at: datetime
    priority: str
    job_id: UUID | None
    job_title: str | None
    company: str | None


class AttentionSection(BaseModel):
    overdue_count: int
    urgent_count: int
    top_items: list[DeadlineWithPriority]


class DashboardOut(BaseModel):
    generated_at: datetime
    attention: AttentionSection
    applications: ApplicationInsightsOut
    upcoming: list[UpcomingItem]
    top_skills: list[TopSkillItem]
    gaps: list[str]