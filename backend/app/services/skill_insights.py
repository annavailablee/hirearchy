"""
Skill intelligence: what skills recur across the jobs the user is targeting,
and which of those they already have on their resume.

This is a per-user, per-resume snapshot. Not a market statistic.
"""
from dataclasses import dataclass

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.job import JobSkill
from app.models.resume import Resume
from app.models.skill import ResumeSkill, Skill

# A skill must appear in at least this % of analyzed jobs to be reported as a
# "strength" or a "gap". Below this threshold, the skill isn't significant enough.
SIGNIFICANCE_THRESHOLD_PCT = 20.0

# Statuses that mean "no longer part of the user's target set".
_EXCLUDED_STATUSES = ("REJECTED", "WITHDRAWN", "EXPIRED")


@dataclass(frozen=True)
class SkillRow:
    canonical: str
    category: str
    frequency: int
    frequency_pct: float
    user_has: bool
    user_context: str | None


@dataclass(frozen=True)
class SkillInsights:
    jobs_analyzed: int
    resume_id: str | None
    resume_name: str | None
    skills: list[SkillRow]
    strengths: list[str]
    gaps: list[str]


def _resolve_resume(
    db: Session, user_id, resume_id
) -> Resume | None:
    """Explicit resume if it belongs to the user; else the primary; else None."""
    if resume_id is not None:
        return db.scalar(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )
    return db.scalar(
        select(Resume).where(Resume.user_id == user_id, Resume.is_primary.is_(True))
    )


def _target_job_ids(db: Session, user_id) -> list:
    return list(
        db.scalars(
            select(Application.job_id).where(
                Application.user_id == user_id,
                Application.current_status.notin_(_EXCLUDED_STATUSES),
            )
        )
    )


def _job_skill_frequencies(db: Session, job_ids: list) -> list[tuple[str, str, int]]:
    """
    For each skill, how many distinct analyzed jobs require it.
    Returns [(canonical, category, count), ...] sorted by count desc.
    """
    if not job_ids:
        return []

    rows = db.execute(
        select(
            Skill.canonical,
            Skill.category,
            func.count(func.distinct(JobSkill.job_id)).label("cnt"),
        )
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .where(JobSkill.job_id.in_(job_ids))
        .group_by(Skill.id, Skill.canonical, Skill.category)
        .order_by(desc("cnt"), Skill.canonical)
    ).all()

    return [(c, cat, int(cnt)) for c, cat, cnt in rows]


def _resume_skills(db: Session, resume_id) -> dict[str, str | None]:
    """Map canonical -> context for skills on the given resume."""
    if resume_id is None:
        return {}
    rows = db.execute(
        select(Skill.canonical, ResumeSkill.context)
        .join(ResumeSkill, ResumeSkill.skill_id == Skill.id)
        .where(ResumeSkill.resume_id == resume_id)
    ).all()
    return {c: ctx for c, ctx in rows}


def compute_skill_insights(
    db: Session, user_id, resume_id=None
) -> SkillInsights:
    job_ids = _target_job_ids(db, user_id)
    total = len(job_ids)

    resume = _resolve_resume(db, user_id, resume_id)
    user_skills = _resume_skills(db, resume.id if resume else None)

    if total == 0:
        return SkillInsights(
            jobs_analyzed=0,
            resume_id=str(resume.id) if resume else None,
            resume_name=resume.name if resume else None,
            skills=[],
            strengths=[],
            gaps=[],
        )

    freq_rows = _job_skill_frequencies(db, job_ids)

    skill_items: list[SkillRow] = []
    strengths: list[str] = []
    gaps: list[str] = []

    for canonical, category, freq in freq_rows:
        pct = round(100.0 * freq / total, 1)
        has = canonical in user_skills
        item = SkillRow(
            canonical=canonical,
            category=category,
            frequency=freq,
            frequency_pct=pct,
            user_has=has,
            user_context=user_skills.get(canonical),
        )
        skill_items.append(item)

        if pct >= SIGNIFICANCE_THRESHOLD_PCT:
            if has:
                strengths.append(canonical)
            else:
                gaps.append(canonical)

    return SkillInsights(
        jobs_analyzed=total,
        resume_id=str(resume.id) if resume else None,
        resume_name=resume.name if resume else None,
        skills=skill_items,
        strengths=strengths,
        gaps=gaps,
    )