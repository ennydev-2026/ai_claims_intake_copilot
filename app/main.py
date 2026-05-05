from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import init_db
from app.routers.claims import router as claims_router
from app.utils.logging import configure_logging

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description='V2 MVP for AI-driven insurance claims intake using FastAPI + Gemini structured output + PostgreSQL + Java mock integration.',
    lifespan=lifespan,
)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'app': settings.app_name, 'version': settings.app_version}


app.include_router(claims_router, prefix='/api/v1/claims', tags=['claims'])
