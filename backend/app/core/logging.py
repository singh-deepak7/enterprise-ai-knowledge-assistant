import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


logger = logging.getLogger("enterprise-ai")

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger for the given module.

    Example:
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)