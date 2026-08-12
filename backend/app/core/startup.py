"""
Application startup validation.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


def validate_startup() -> None:
    """
    Validate application configuration before serving requests.
    """

    logger.info("Running startup validation.")

    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    if not settings.CHAT_MODEL:
        raise RuntimeError(
            "CHAT_MODEL is not configured."
        )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    chroma_dir = Path(settings.CHROMA_DB_DIR)
    chroma_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Upload directory: %s",
        upload_dir.resolve(),
    )

    logger.info(
        "ChromaDB directory: %s",
        chroma_dir.resolve(),
    )

    logger.info(
        "Startup validation completed successfully."
    )