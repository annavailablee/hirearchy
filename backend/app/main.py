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
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.core.scheduler import lifespan_scheduler


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan_scheduler,
    )

    # Middleware runs in reverse order of addition for responses,
    # so add order matters for response-side behavior.
    app.add_middleware(RequestContextMiddleware)

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

    return app


app = create_app()