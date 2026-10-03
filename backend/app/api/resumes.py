import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import settings
from app.db.session import get_db
from app.models.resume import Resume
from app.models.user import User
from app.services import storage
from app.services.pdf_extraction import PdfExtractionError, extract_text_from_pdf, looks_like_pdf
from app.models.skill import ResumeSkill, Skill
from app.schemas.resume import ResumeDetailOut, ResumeOut, ResumeSkillOut, ResumeUpdate
from app.services.skill_extraction import extract_skills
from app.services.skill_repository import persist_resume_skills

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _get_owned_resume(resume_id: uuid.UUID, user: User, db: Session) -> Resume:
    """
    Fetch a resume ONLY if it belongs to the current user.
    Returning 404 (not 403) for other users' resumes prevents enumeration.
    """
    resume = db.scalar(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


@router.post("", response_model=ResumeDetailOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    name: str = Form(..., min_length=1, max_length=120),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    # 1. Read the file body. Small limit means we can safely hold it in memory.
    data = await file.read()

    # 2. Size check.
    if len(data) == 0:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")
    if len(data) > settings.max_resume_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_resume_size_bytes} bytes",
        )

    # 3. Magic-bytes check — do NOT trust Content-Type.
    if not looks_like_pdf(data):
        raise HTTPException(status_code=422, detail="File is not a valid PDF")

    # 4. Duplicate name check (case-insensitive per user).
    existing = db.scalar(
        select(Resume).where(Resume.user_id == user.id, Resume.name == name)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You already have a resume named '{name}'",
        )

    # 5. Extract text BEFORE writing to disk, so we can reject garbage early.
    try:
        raw_text = extract_text_from_pdf(data)
        extraction_status = "success"
        extraction_error = None
    except PdfExtractionError as exc:
        # We still store the file so the user can see what they uploaded, but
        # mark the extraction as failed. Matching will ignore this resume.
        raw_text = None
        extraction_status = "failed"
        extraction_error = str(exc)

    # 6. Persist.
    resume_id = uuid.uuid4()
    key = storage.resume_key(str(user.id), str(resume_id))
    absolute_path = storage.put(key, data)

    # Is this the user's first resume? If so, mark it primary.
    has_any = db.scalar(select(Resume.id).where(Resume.user_id == user.id).limit(1))

    resume = Resume(
        id=resume_id,
        user_id=user.id,
        name=name,
        original_filename=file.filename or "resume.pdf",
        content_type=file.content_type or "application/pdf",
        file_size=len(data),
        storage_path=absolute_path,
        raw_text=raw_text,
        extraction_status=extraction_status,
        extraction_error=extraction_error,
        is_primary=(has_any is None),
    )
    db.add(resume)
    db.flush()  # ensure resume.id is usable for FK inserts

    if extraction_status == "success" and raw_text:
        persist_resume_skills(db, resume, extract_skills(raw_text))

    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeOut])
def list_resumes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Resume]:
    return list(
        db.scalars(
            select(Resume)
            .where(Resume.user_id == user.id)
            .order_by(Resume.uploaded_at.desc())
        )
    )


@router.get("/{resume_id}", response_model=ResumeDetailOut)
def get_resume(
    resume_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    return _get_owned_resume(resume_id, user, db)


@router.patch("/{resume_id}", response_model=ResumeDetailOut)
def update_resume(
    resume_id: uuid.UUID,
    data: ResumeUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    resume = _get_owned_resume(resume_id, user, db)

    updates = data.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] != resume.name:
        clash = db.scalar(
            select(Resume).where(
                Resume.user_id == user.id,
                Resume.name == updates["name"],
                Resume.id != resume.id,
            )
        )
        if clash is not None:
            raise HTTPException(status_code=409, detail="Name already in use")

    if updates.get("is_primary") is True:
        # Demote any other primary resume for this user.
        db.execute(
            Resume.__table__.update()
            .where(Resume.user_id == user.id, Resume.id != resume.id)
            .values(is_primary=False)
        )

    for field, value in updates.items():
        setattr(resume, field, value)

    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    resume = _get_owned_resume(resume_id, user, db)
    storage_path = resume.storage_path
    db.delete(resume)
    db.commit()
    # Delete the file after the DB row is gone. If the file delete fails,
    # the DB is consistent and we just have an orphan — acceptable.
    storage.delete(storage_path)

@router.get("/{resume_id}/skills", response_model=list[ResumeSkillOut])
def list_resume_skills(
    resume_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResumeSkillOut]:
    resume = _get_owned_resume(resume_id, user, db)

    rows = db.execute(
        select(ResumeSkill, Skill)
        .join(Skill, Skill.id == ResumeSkill.skill_id)
        .where(ResumeSkill.resume_id == resume.id)
        .order_by(Skill.canonical)
    ).all()

    return [
        ResumeSkillOut(
            canonical=skill.canonical,
            category=skill.category,
            matched_text=rs.matched_text,
            context=rs.context,
        )
        for rs, skill in rows
    ]