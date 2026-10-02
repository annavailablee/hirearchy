from fastapi import FastAPI

from app.api import auth, health
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"name": settings.app_name, "version": settings.app_version}