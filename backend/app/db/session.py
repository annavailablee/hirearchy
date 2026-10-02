from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # detect dead connections before using them
    echo=False,           # set True locally if you want to see SQL
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI dependency: yields a session per request and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()