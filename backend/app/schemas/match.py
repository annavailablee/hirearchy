from pydantic import BaseModel


class CategoryScore(BaseModel):
    name: str
    earned: float
    possible: float
    percent: float


class SkillEvidence(BaseModel):
    canonical: str
    category: str
    context: str | None  # snippet from the resume showing where the skill was found


class MatchResultOut(BaseModel):
    score: int  # 0-100
    breakdown: list[CategoryScore]
    matched_required_skills: list[SkillEvidence]
    matched_preferred_skills: list[SkillEvidence]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]
    notes: list[str]  # human-readable explanations for the score