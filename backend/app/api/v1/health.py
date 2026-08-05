from pathlib import Path

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    upload_ready = Path(settings.UPLOAD_DIR).exists()
    chroma_ready = Path(settings.CHROMA_DB_DIR).exists()

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "storage": "ready" if upload_ready else "missing",
            "chromadb": "ready" if chroma_ready else "missing",
            "openai": (
                "configured"
                if settings.OPENAI_API_KEY
                else "not_configured"
            ),
        },
    }