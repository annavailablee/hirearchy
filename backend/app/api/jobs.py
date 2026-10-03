import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.job import Job, JobSkill
from app.models.skill import Skill, ResumeSkill
from app.models.user import User
from app.schemas.job import JobCreate, JobDetailOut, JobOut, JobSkillOut
from app.services import job_service
from app.services.job_service import DuplicateJobError
from app.models.profile import Profile
from app.models.resume import Resume
from app.schemas.match import MatchResultOut
from app.services.compatibility import (
    JobMatchInput,
    SkillRef,
    UserMatchInput,
    UserSkill,
    compute_match,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobDetailOut, status_code=status.HTTP_201_CREATED)
def create_job(
    data: JobCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDetailOut:
    try:
        job = job_service.create_job(db, user.id, data)
    except DuplicateJobError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job with this source_url already exists (id: {exc.existing_job_id})",
        )
    db.commit()
    db.refresh(job)
    return _to_detail(db, job)


@router.get("", response_model=list[JobOut])
def list_jobs(
    q: str | None = Query(default=None, description="Search in title and company"),
    remote_type: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Job]:
    stmt = select(Job)

    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(or_(Job.title.ilike(pattern), Job.company.ilike(pattern)))
    if remote_type:
        stmt = stmt.where(Job.remote_type == remote_type)
    if employment_type:
        stmt = stmt.where(Job.employment_type == employment_type)

    stmt = stmt.order_by(Job.created_at.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt))


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job(
    job_id: uuid.UUID,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDetailOut:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _to_detail(db, job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.created_by_user_id != user.id:
        # Only the creator can delete. Anyone else gets 403 — they can *see* the
        # job, so hiding it behind 404 would be misleading.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete jobs you created",
        )
    db.delete(job)
    db.commit()


def _to_detail(db: Session, job: Job) -> JobDetailOut:
    """Assemble the detail response with skills included."""
    rows = db.execute(
        select(JobSkill, Skill)
        .join(Skill, Skill.id == JobSkill.skill_id)
        .where(JobSkill.job_id == job.id)
        .order_by(JobSkill.kind.desc(), Skill.canonical)
    ).all()

    skill_list = [
        JobSkillOut(
            canonical=skill.canonical,
            category=skill.category,
            kind=js.kind,
            matched_text=js.matched_text,
            context=js.context,
        )
        for js, skill in rows
    ]

    return JobDetailOut(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        remote_type=job.remote_type,
        employment_type=job.employment_type,
        experience_level=job.experience_level,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        deadline=job.deadline,
        posted_at=job.posted_at,
        source=job.source,
        source_url=job.source_url,
        created_at=job.created_at,
        updated_at=job.updated_at,
        description=job.description,
        education_requirements=job.education_requirements,
        created_by_user_id=job.created_by_user_id,
        skills=skill_list,
    )

@router.post("/{job_id}/match", response_model=MatchResultOut)
def match_job(
    job_id: uuid.UUID,
    resume_id: uuid.UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchResultOut:
    """
    Compute compatibility between a job and a resume.

    If `resume_id` is provided and belongs to the user, that resume is used.
    Otherwise, the user's primary resume is used.
    """
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # Resolve the resume: explicit → primary → error.
    if resume_id is not None:
        resume = db.scalar(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
        )
        if resume is None:
            raise HTTPException(status_code=404, detail="Resume not found")
    else:
        resume = db.scalar(
            select(Resume).where(Resume.user_id == user.id, Resume.is_primary.is_(True))
        )
        if resume is None:
            raise HTTPException(
                status_code=400,
                detail="No primary resume. Upload a resume or specify resume_id.",
            )

    # Gather user's skills with evidence.
    user_rows = db.execute(
        select(Skill.canonical, Skill.category, ResumeSkill.context)
        .join(Skill, Skill.id == ResumeSkill.skill_id)
        .where(ResumeSkill.resume_id == resume.id)
    ).all()
    user_skills = tuple(
        UserSkill(canonical=c, category=cat, context=ctx)
        for c, cat, ctx in user_rows
    )

    # Gather job's skills, split by kind.
    job_rows = db.execute(
        select(Skill.canonical, Skill.category, JobSkill.kind)
        .join(Skill, Skill.id == JobSkill.skill_id)
        .where(JobSkill.job_id == job.id)
    ).all()
    required = tuple(
        SkillRef(canonical=c, category=cat)
        for c, cat, kind in job_rows if kind == "required"
    )
    preferred = tuple(
        SkillRef(canonical=c, category=cat)
        for c, cat, kind in job_rows if kind == "preferred"
    )

    profile = user.profile

    job_input = JobMatchInput(
        required_skills=required,
        preferred_skills=preferred,
        experience_level=job.experience_level,
        education_requirements=job.education_requirements,
        remote_type=job.remote_type,
        location=job.location,
        employment_type=job.employment_type,
    )
    user_input = UserMatchInput(
        skills=user_skills,
        experience_level=profile.experience_level if profile else None,
        preferred_locations=tuple(profile.preferred_locations or []) if profile else (),
        current_location=profile.current_location if profile else None,
        remote_preference=profile.remote_preference if profile else None,
        preferred_employment_types=tuple(profile.preferred_employment_types or []) if profile else (),
        degree=profile.degree if profile else None,
        education=profile.education if profile else None,
    )

    return compute_match(job_input, user_input)