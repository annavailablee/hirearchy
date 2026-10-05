"""
Business logic for creating and querying jobs.
Kept separate from endpoints so the duplicate-detection and skill-extraction
logic is unit-testable without HTTP.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job, JobSkill
from app.schemas.job import JobCreate
from app.services.skill_extraction import extract_skills
from app.services.skill_repository import upsert_taxonomy_skills


class DuplicateJobError(Exception):
    """Raised when a job with the same source_url already exists."""
    def __init__(self, existing_job_id):
        self.existing_job_id = existing_job_id
        super().__init__(f"Duplicate job (existing id: {existing_job_id})")


def find_duplicate(db: Session, source_url: str | None) -> Job | None:
    """Return an existing job with the same source_url, if any."""
    if not source_url:
        return None
    return db.scalar(select(Job).where(Job.source_url == source_url))


def create_job(db: Session, user_id, data: JobCreate) -> Job:
    """
    Create a job, extract skills from title+description, and attach them.
    Raises DuplicateJobError if source_url collides with an existing job.
    """
    existing = find_duplicate(db, data.source_url)
    if existing is not None:
        raise DuplicateJobError(existing.id)

    job = Job(
        created_by_user_id=user_id,
        title=data.title,
        company=data.company,
        description=data.description,
        location=data.location,
        remote_type=data.remote_type.value if data.remote_type else None,
        employment_type=data.employment_type.value if data.employment_type else None,
        experience_level=data.experience_level.value if data.experience_level else None,
        education_requirements=data.education_requirements,
        salary_min=data.salary_min,
        salary_max=data.salary_max,
        salary_currency=data.salary_currency,
        deadline=data.deadline,
        posted_at=data.posted_at,
        source=data.source,
        source_url=data.source_url,
    )
    db.add(job)
    db.flush()

    _attach_skills(db, job, f"{data.title}\n{data.description or ''}")

    return job


def _attach_skills(db: Session, job: Job, text: str) -> None:
    """
    Extract skills from job text and persist as JobSkill rows.
    Everything is marked 'required' for MVP — see Step 7b design notes.
    """
    extracted = extract_skills(text)
    if not extracted:
        return

    skill_map = upsert_taxonomy_skills(db)

    for item in extracted:
        skill = skill_map.get(item.canonical)
        if skill is None:
            continue
        db.add(
            JobSkill(
                job_id=job.id,
                skill_id=skill.id,
                kind="required",
                matched_text=item.matched_text,
                context=item.context,
            )
        )