import json
import logging
from collections.abc import Iterator

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import StreamingResponse

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

    logger.info(
        "Received chat request "
        "[session_id=%s].",
        request.session_id,
    )

    try:
        state = workflow.invoke(
            question=request.question,
            session_id=request.session_id,
        )

        logger.info(
            "Chat request completed "
            "[session_id=%s].",
            request.session_id,
        )

        return ChatResponse(
            answer=state.answer,
            sources=state.sources,
        )

    except Exception as ex:
        logger.exception(
            "Chat request failed "
            "[session_id=%s].",
            request.session_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex),
        ) from ex


@router.post(
    "/stream",
    status_code=status.HTTP_200_OK,
)
def chat_stream(
    request: ChatRequest,
    workflow: AgenticWorkflow = Depends(
        get_agentic_workflow,
    ),
) -> StreamingResponse:
    """
    Stream workflow events using Server-Sent Events.
    """

    logger.info(
        "Received streaming chat request "
        "[session_id=%s].",
        request.session_id,
    )

    def event_generator() -> Iterator[str]:
        try:
            for event in workflow.stream(
                question=request.question,
                session_id=request.session_id,
            ):
                yield (
                    "data: "
                    + json.dumps(
                        event,
                        default=str,
                    )
                    + "\n\n"
                )

            yield (
                "event: done\n"
                "data: {}\n\n"
            )

        except Exception as ex:
            logger.exception(
                "Streaming chat request failed "
                "[session_id=%s].",
                request.session_id,
            )

            yield (
                "event: error\n"
                "data: "
                + json.dumps(
                    {
                        "detail": str(ex),
                    }
                )
                + "\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )