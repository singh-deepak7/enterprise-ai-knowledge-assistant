import logging

from fastapi import APIRouter, HTTPException, status

from app.ai.retrieval.rag_service import RAGService
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    request: ChatRequest,
) -> ChatResponse:
    """
    Ask a question using Retrieval-Augmented Generation.
    """

    logger.info("Received chat request.")

    try:
        rag_service = RAGService()

        result = rag_service.generate_answer(
            question=request.question,
            top_k=request.top_k,
        )

        logger.info("Chat request completed.")

        return ChatResponse(**result)

    except Exception as ex:
        logger.exception("Chat request failed.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex),
        )