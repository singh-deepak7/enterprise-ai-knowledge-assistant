from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.upload import router as upload_router
from app.api.v1.documents import router as documents_router
from app.api.v1 import chat

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router,tags=["Health"],)

api_router.include_router(upload_router,tags=["Upload"],)

api_router.include_router(chat.router,tags=["Chat"],)

api_router.include_router(documents_router,tags=["Documents"],)

