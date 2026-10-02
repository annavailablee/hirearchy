"""Filesystem-backed storage for uploaded files.

Interface is intentionally S3-shaped: put(key, data) / delete(key) / absolute_path(key).
When we swap to S3, only this module changes.
"""
from pathlib import Path

from app.config import settings


def _base_dir() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def resume_key(user_id: str, resume_id: str) -> str:
    """Stable, collision-free key. We never use the user-supplied filename on disk."""
    return f"{user_id}/{resume_id}.pdf"


def put(key: str, data: bytes) -> str:
    """Write bytes to disk. Returns the absolute path (what we store in DB)."""
    target = _base_dir() / key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return str(target)


def delete(key: str) -> None:
    """Delete a file. Missing files are not an error — the DB row is the source of truth."""
    target = _base_dir() / key
    target.unlink(missing_ok=True)


def absolute_path(key: str) -> Path:
    return _base_dir() / key