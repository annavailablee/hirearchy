from pydantic import BaseModel


class ProfileSuggestion(BaseModel):
    """Fields we could confidently extract from the resume text.
    Missing fields are omitted or None."""
    degree: str | None = None
    education: str | None = None           # institution name
    graduation_year: int | None = None
    source_resume_id: str
    source_resume_name: str
    notes: list[str] = []                  # human-readable explanations