from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SkillInsightItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    canonical: str
    category: str
    frequency: int          # number of analyzed jobs that require this skill
    frequency_pct: float    # frequency / jobs_analyzed * 100, rounded to 1 decimal
    user_has: bool          # appears on the analyzed resume
    user_context: str | None


class ResumeRef(BaseModel):
    id: UUID
    name: str


class SkillInsightsOut(BaseModel):
    jobs_analyzed: int
    resume_analyzed: ResumeRef | None
    skills: list[SkillInsightItem]     # sorted by frequency desc
    strengths: list[str]               # canonical names
    gaps: list[str]                    # canonical names


class ApplicationInsightsOut(BaseModel):
    total: int
    by_status: dict[str, int]
    response_rate_pct: float     # (apps that reached ASSESSMENT or beyond) / applied * 100
    interview_rate_pct: float