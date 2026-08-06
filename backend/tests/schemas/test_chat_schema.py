from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    SourceResponse,
)


def test_chat_request_defaults() -> None:
    request = ChatRequest(
        question="Hello"
    )

    assert request.question == "Hello"
    assert request.top_k == 5


def test_chat_response() -> None:
    response = ChatResponse(
        answer="Hello",
        sources=[
            SourceResponse(
                source="sample.pdf",
                page=2,
                chunk=5,
            )
        ],
    )

    assert response.answer == "Hello"
    assert response.sources[0].source == "sample.pdf"