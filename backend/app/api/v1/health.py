from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict[str, object]:
    """
    Liveness endpoint.

    Used by Kubernetes, Docker, ECS, etc.
    Returns whether the application process is alive.
    """

    upload_ready = Path(settings.UPLOAD_DIR).exists()
    chroma_ready = Path(settings.CHROMA_DB_DIR).exists()

    healthy = (
        upload_ready
        and chroma_ready
        and bool(settings.OPENAI_API_KEY)
    )

    return {
        "status": "healthy" if healthy else "degraded",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(
            timezone.utc,
        ).isoformat(),
        "services": {
            "storage": (
                "ready"
                if upload_ready
                else "missing"
            ),
            "chromadb": (
                "ready"
                if chroma_ready
                else "missing"
            ),
            "openai": (
                "configured"
                if settings.OPENAI_API_KEY
                else "not_configured"
            ),
            "model": settings.CHAT_MODEL,
        },
    }


@router.get("/ready")
async def readiness() -> dict[str, object]:
    """
    Readiness endpoint.

    Used by orchestrators before routing traffic.
    """

    upload_ready = Path(settings.UPLOAD_DIR).exists()
    chroma_ready = Path(settings.CHROMA_DB_DIR).exists()
    openai_ready = bool(settings.OPENAI_API_KEY)

    ready = (
        upload_ready
        and chroma_ready
        and openai_ready
    )

    return {
        "status": "ready" if ready else "not_ready",
        "ready": ready,
    }


@router.get("/version")
async def version() -> dict[str, str]:
    """
    Version information.
    """

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "model": settings.CHAT_MODEL,
    }