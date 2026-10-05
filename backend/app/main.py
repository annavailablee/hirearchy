from fastapi import FastAPI

from app.api import (
    applications,
    auth,
    dashboard,
    deadlines,
    health,
    insights,
    jobs,
    profile,
    resumes,
)
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(deadlines.router)
app.include_router(insights.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"name": settings.app_name, "version": settings.app_version}