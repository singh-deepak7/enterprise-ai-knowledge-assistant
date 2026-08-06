import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.ai.agentic.workflow import AgenticWorkflow
from app.dependencies import get_agentic_workflow
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
    workflow: AgenticWorkflow = Depends(
        get_agentic_workflow,
    ),
) -> ChatResponse:
    """
    Ask a question using the LangGraph Agentic Workflow.
    """

    logger.info("Received chat request.")

    try:
        state = workflow.invoke(
            question=request.question,
        )

        logger.info("Chat request completed.")

        return ChatResponse(
            answer=state.answer,
            sources=state.sources,
        )

    except Exception as ex:
        logger.exception("Chat request failed.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex),
        ) from ex