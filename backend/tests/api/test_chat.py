from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.ai.agentic.graph_state import GraphState
from app.dependencies import get_agentic_workflow
from app.main import app

client = TestClient(
    app,
    raise_server_exceptions=False,
)


def test_chat_success() -> None:
    """
    Chat endpoint should return a successful response.
    """

    workflow = Mock()

    workflow.invoke.return_value = GraphState(
        question="Vacation policy?",
        answer="Employees receive 20 vacation days.",
        sources=[
            {
                "source": "employee.pdf",
                "page": 15,
                "chunk": 2,
            }
        ],
    )

    app.dependency_overrides[
        get_agentic_workflow
    ] = lambda: workflow

    try:
        response = client.post(
            "/api/v1/chat",
            json={
                "question": "Vacation policy?",
                "session_id": "test-session",
                "top_k": 5,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert (
        body["answer"]
        == "Employees receive 20 vacation days."
    )

    assert len(body["sources"]) == 1

    workflow.invoke.assert_called_once_with(
        question="Vacation policy?",
        session_id="test-session",
    )


def test_chat_failure() -> None:
    """
    Chat endpoint should return HTTP 500 on workflow failure.
    """

    workflow = Mock()

    workflow.invoke.side_effect = Exception(
        "Failure"
    )

    app.dependency_overrides[
        get_agentic_workflow
    ] = lambda: workflow

    try:
        response = client.post(
            "/api/v1/chat",
            json={
                "question": "Hello",
                "session_id": "test-session",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Failure",
    }


def test_chat_requires_session_id() -> None:
    """
    Chat endpoint should reject requests without a session ID.
    """

    response = client.post(
        "/api/v1/chat",
        json={
            "question": "Hello",
        },
    )

    assert response.status_code == 422