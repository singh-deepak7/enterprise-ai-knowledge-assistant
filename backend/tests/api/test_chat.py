from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.v1.chat.RAGService")
def test_chat_success(mock_rag_service):
    mock_instance = mock_rag_service.return_value

    mock_instance.generate_answer.return_value = {
        "answer": "Employees receive 20 vacation days.",
        "sources": [
            {
                "source": "employee.pdf",
                "page": 15,
                "chunk": 2,
            }
        ],
    }

    response = client.post(
        "/api/v1/chat",
        json={
            "question": "Vacation policy?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["answer"] == "Employees receive 20 vacation days."
    assert len(body["sources"]) == 1


@patch("app.api.v1.chat.RAGService")
def test_chat_failure(mock_rag_service):
    mock_instance = mock_rag_service.return_value

    mock_instance.generate_answer.side_effect = Exception(
        "Failure"
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "question": "Hello"
        },
    )

    assert response.status_code == 500