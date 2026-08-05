from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging, logger

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

logger.info("Application starting...")
logger.info("Testing logging")
logger.warning("Warning test")
logger.error("Error test")