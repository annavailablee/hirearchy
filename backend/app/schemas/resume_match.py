from uuid import UUID

from pydantic import BaseModel


class ResumeMatchSummary(BaseModel):
    id: UUID
    name: str
    is_primary: bool
    score: int
    matched_skills: list[str]      # canonical names, sorted
    missing_skills: list[str]      # required skills the resume lacks, sorted
    is_recommended: bool
    note: str | None = None        # reason a resume was skipped, if applicable


class BestResumeOut(BaseModel):
    job_id: UUID
    resumes: list[ResumeMatchSummary]   # sorted by score desc, ties broken by primary then recency