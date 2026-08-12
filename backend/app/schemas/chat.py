from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Chat request payload.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="User question.",
    )

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Conversation session identifier.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of documents to retrieve.",
    )


class SourceResponse(BaseModel):
    """
    Source attribution returned to the client.
    """

    source: str
    page: int | None = None
    chunk: int | None = None


class ChatResponse(BaseModel):
    """
    Chat response.
    """

    answer: str
    sources: list[SourceResponse]