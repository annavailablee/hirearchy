"""
Explainable job–resume compatibility engine.

Deterministic. No LLM. Every point is traceable to a rule.

Category weights sum to 100:
- Skills: 50 (40 required + 10 preferred)
- Experience level: 20
- Education: 10
- Location / remote fit: 10
- Employment type: 10

The algorithm is a pure function: takes job and user inputs, returns a score.
It does not touch the database — the endpoint assembles inputs and calls it.
"""
from dataclasses import dataclass

from app.schemas.match import CategoryScore, MatchResultOut, SkillEvidence

WEIGHTS = {
    "skills": 50,
    "experience": 20,
    "education": 10,
    "location": 10,
    "employment_type": 10,
}

_EXPERIENCE_ORDER = {
    "student": 0,
    "fresher": 1,
    "junior": 2,
    "mid": 3,
    "senior": 4,
}

_DEGREE_LEVELS = (
    ("phd", ("phd", "ph.d", "doctorate", "doctoral")),
    ("master", ("master", "m.tech", "mtech", "m.sc", "msc", "mba", "mca", "ms in")),
    ("bachelor", ("bachelor", "b.tech", "btech", "b.e.", "b.sc", "bsc", "bca", "b.s.")),
)
_DEGREE_ORDER = {"bachelor": 1, "master": 2, "phd": 3}


@dataclass(frozen=True)
class SkillRef:
    canonical: str
    category: str


@dataclass(frozen=True)
class UserSkill:
    canonical: str
    category: str
    context: str | None


@dataclass(frozen=True)
class JobMatchInput:
    required_skills: tuple[SkillRef, ...] = ()
    preferred_skills: tuple[SkillRef, ...] = ()
    experience_level: str | None = None
    education_requirements: str | None = None
    remote_type: str | None = None
    location: str | None = None
    employment_type: str | None = None


@dataclass(frozen=True)
class UserMatchInput:
    skills: tuple[UserSkill, ...] = ()
    experience_level: str | None = None
    preferred_locations: tuple[str, ...] = ()
    current_location: str | None = None
    remote_preference: str | None = None
    preferred_employment_types: tuple[str, ...] = ()
    degree: str | None = None
    education: str | None = None


# ---------------------------------------------------------------------------
# Sub-scorers
# ---------------------------------------------------------------------------

def _score_skills(
    job: JobMatchInput, user: UserMatchInput
) -> tuple[float, float, dict]:
    """Returns (earned, possible, evidence_dict)."""
    user_set = {s.canonical for s in user.skills}
    required = {s.canonical for s in job.required_skills}
    preferred = {s.canonical for s in job.preferred_skills}

    matched_required = user_set & required
    matched_preferred = user_set & preferred
    missing_required = required - user_set
    missing_preferred = preferred - user_set

    # 40 for required, 10 for preferred. If a bucket is empty, give full credit
    # (nothing to match = nothing to miss).
    if required:
        earned = 40.0 * len(matched_required) / len(required)
    else:
        earned = 40.0

    if preferred:
        earned += 10.0 * len(matched_preferred) / len(preferred)
    else:
        earned += 10.0

    return earned, 50.0, {
        "matched_required": matched_required,
        "matched_preferred": matched_preferred,
        "missing_required": missing_required,
        "missing_preferred": missing_preferred,
    }


def _detect_degree_level(text: str | None) -> str | None:
    if not text:
        return None
    lower = text.lower()
    for level, keywords in _DEGREE_LEVELS:
        if any(kw in lower for kw in keywords):
            return level
    return None


def _score_education(job: JobMatchInput, user: UserMatchInput) -> tuple[float, float, str | None]:
    if not job.education_requirements:
        return 10.0, 10.0, None

    job_level = _detect_degree_level(job.education_requirements)
    if job_level is None:
        # We can't parse the requirement — don't penalize.
        return 10.0, 10.0, None

    user_level = _detect_degree_level(f"{user.degree or ''} {user.education or ''}")
    if user_level is None:
        return 5.0, 10.0, "Add your degree to your profile for a more accurate score."

    if _DEGREE_ORDER[user_level] >= _DEGREE_ORDER[job_level]:
        return 10.0, 10.0, None
    return 3.0, 10.0, f"Job lists {job_level}-level education requirements."


def _score_experience(job: JobMatchInput, user: UserMatchInput) -> tuple[float, float, str | None]:
    if not job.experience_level or not user.experience_level:
        return 20.0, 20.0, None

    if (
        job.experience_level not in _EXPERIENCE_ORDER
        or user.experience_level not in _EXPERIENCE_ORDER
    ):
        return 20.0, 20.0, None

    gap = (
        _EXPERIENCE_ORDER[job.experience_level]
        - _EXPERIENCE_ORDER[user.experience_level]
    )

    if gap <= 0:
        return 20.0, 20.0, None
    if gap == 1:
        return 15.0, 20.0, None
    if gap == 2:
        return 8.0, 20.0, f"Job targets {job.experience_level}-level experience."
    return 0.0, 20.0, f"Job requires {job.experience_level}-level experience."

def _score_location(job: JobMatchInput, user: UserMatchInput) -> tuple[float, float, str | None]:
    # If we know nothing about the user's location prefs, we can't evaluate.
    if not user.remote_preference and not user.preferred_locations and not user.current_location:
        return 5.0, 10.0, None

    # Remote job — user's remote preference drives the score.
    if job.remote_type == "remote":
        if user.remote_preference in ("remote", "any", None):
            return 10.0, 10.0, None
        return 7.0, 10.0, None

    # Non-remote — check location string match.
    if job.location:
        job_loc = job.location.lower()
        candidates = list(user.preferred_locations)
        if user.current_location:
            candidates.append(user.current_location)
        for loc in candidates:
            if loc and loc.lower() in job_loc:
                return 10.0, 10.0, None
        # No string match.
        if job.remote_type == "hybrid":
            return 5.0, 10.0, None
        return 3.0, 10.0, "Job location is outside your preferred locations."

    return 5.0, 10.0, None


def _score_employment(job: JobMatchInput, user: UserMatchInput) -> tuple[float, float, str | None]:
    if not job.employment_type:
        return 10.0, 10.0, None
    if not user.preferred_employment_types:
        return 5.0, 10.0, None
    if job.employment_type in user.preferred_employment_types:
        return 10.0, 10.0, None
    prefs = ", ".join(user.preferred_employment_types)
    return 0.0, 10.0, f"Job is {job.employment_type}; you prefer {prefs}."

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def compute_match(job: JobMatchInput, user: UserMatchInput) -> MatchResultOut:
    notes: list[str] = []

    skills_earned, skills_possible, skill_data = _score_skills(job, user)
    exp_earned, exp_possible, exp_note = _score_experience(job, user)
    edu_earned, edu_possible, edu_note = _score_education(job, user)
    loc_earned, loc_possible, loc_note = _score_location(job, user)
    emp_earned, emp_possible, emp_note = _score_employment(job, user)

    for n in (exp_note, edu_note, loc_note, emp_note):
        if n:
            notes.append(n)

    if not job.required_skills and not job.preferred_skills:
        notes.append("No skills could be extracted from this job description.")

    breakdown = [
        CategoryScore(name="skills", earned=skills_earned, possible=skills_possible,
                      percent=round(100 * skills_earned / skills_possible, 1)),
        CategoryScore(name="experience", earned=exp_earned, possible=exp_possible,
                      percent=round(100 * exp_earned / exp_possible, 1)),
        CategoryScore(name="education", earned=edu_earned, possible=edu_possible,
                      percent=round(100 * edu_earned / edu_possible, 1)),
        CategoryScore(name="location", earned=loc_earned, possible=loc_possible,
                      percent=round(100 * loc_earned / loc_possible, 1)),
        CategoryScore(name="employment_type", earned=emp_earned, possible=emp_possible,
                      percent=round(100 * emp_earned / emp_possible, 1)),
    ]

    total_earned = sum(c.earned for c in breakdown)
    total_possible = sum(c.possible for c in breakdown)
    score = round(100 * total_earned / total_possible) if total_possible else 0

    user_skill_map = {s.canonical: s for s in user.skills}

    def evidence(canonicals: set[str]) -> list[SkillEvidence]:
        out = []
        for c in sorted(canonicals):
            s = user_skill_map[c]
            out.append(SkillEvidence(canonical=c, category=s.category, context=s.context))
        return out

    return MatchResultOut(
        score=score,
        breakdown=breakdown,
        matched_required_skills=evidence(skill_data["matched_required"]),
        matched_preferred_skills=evidence(skill_data["matched_preferred"]),
        missing_required_skills=sorted(skill_data["missing_required"]),
        missing_preferred_skills=sorted(skill_data["missing_preferred"]),
        notes=notes,
    )