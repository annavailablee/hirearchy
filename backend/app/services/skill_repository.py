"""
Persistence for extracted skills.
Kept separate from extraction so extraction stays pure and testable.
"""
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.skill import ResumeSkill, Skill
from app.services.skill_extraction import ExtractedSkill, _load_taxonomy


def upsert_taxonomy_skills(db: Session) -> dict[str, Skill]:
    """
    Ensure every skill in the taxonomy exists in the `skills` table.
    Returns a map canonical_name -> Skill. Idempotent.
    """
    existing = {s.canonical: s for s in db.scalars(select(Skill))}

    to_create: list[Skill] = []
    for entry in _load_taxonomy():
        canonical = entry["canonical"]
        if canonical not in existing:
            skill = Skill(canonical=canonical, category=entry["category"])
            to_create.append(skill)
            existing[canonical] = skill

    if to_create:
        db.add_all(to_create)
        db.flush()  # assign IDs without ending the transaction

    return existing


def persist_resume_skills(
    db: Session, resume: Resume, extracted: list[ExtractedSkill]
) -> int:
    """
    Attach extracted skills to a resume. Replaces any existing links
    (idempotent — safe to re-run). Returns the count persisted.
    """
    skill_map = upsert_taxonomy_skills(db)

    # Clear any existing links for this resume.
    db.execute(delete(ResumeSkill).where(ResumeSkill.resume_id == resume.id))

    count = 0
    for item in extracted:
        skill = skill_map.get(item.canonical)
        if skill is None:
            continue
        db.add(
            ResumeSkill(
                resume_id=resume.id,
                skill_id=skill.id,
                matched_text=item.matched_text,
                context=item.context,
            )
        )
        count += 1

    return count