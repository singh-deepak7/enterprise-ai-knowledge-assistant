from __future__ import annotations

from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.nodes.retrieval_node import retrieval_node
from app.ai.retrieval.retrieval_service import RetrievalService


def test_retrieval_node_success() -> None:
    """
    Retrieval node should populate the graph state with
    retrieved documents and observability metadata.
    """

    documents = [
        Document(
            page_content="Coverage information",
            metadata={
                "source": "policy.pdf",
                "page": 1,
            },
        ),
        Document(
            page_content="Collision coverage",
            metadata={
                "source": "policy.pdf",
                "page": 2,
            },
        ),
    ]

    retrieval_service = Mock(spec=RetrievalService)
    retrieval_service.retrieve.return_value = documents

    state = GraphState(
        question="What is comprehensive coverage?",
        retrieval_strategy="hybrid",
        top_k=5,
    )

    result = retrieval_node(
        state=state,
        retrieval_service=retrieval_service,
    )

    retrieval_service.retrieve.assert_called_once_with(
        query="What is comprehensive coverage?",
        top_k=5,
    )

    assert result is state
    assert len(result.retrieved_chunks) == 2
    assert result.retrieved_chunks == documents

    assert "retrieval" in result.metadata

    metadata = result.metadata["retrieval"]

    assert metadata["strategy"] == "hybrid"
    assert metadata["requested_top_k"] == 5
    assert metadata["returned_chunks"] == 2
    assert metadata["duration_ms"] >= 0


def test_retrieval_node_empty_result() -> None:
    """
    Retrieval node should handle empty retrieval results.
    """

    retrieval_service = Mock(spec=RetrievalService)
    retrieval_service.retrieve.return_value = []

    state = GraphState(
        question="Unknown question",
        retrieval_strategy="hybrid",
        top_k=5,
    )

    result = retrieval_node(
        state=state,
        retrieval_service=retrieval_service,
    )

    assert result.retrieved_chunks == []

    metadata = result.metadata["retrieval"]

    assert metadata["strategy"] == "hybrid"
    assert metadata["requested_top_k"] == 5
    assert metadata["returned_chunks"] == 0
    assert metadata["duration_ms"] >= 0


def test_retrieval_node_propagates_exception() -> None:
    """
    Retrieval exceptions should be propagated to the caller.
    """

    retrieval_service = Mock(spec=RetrievalService)

    retrieval_service.retrieve.side_effect = RuntimeError(
        "Vector store unavailable"
    )

    state = GraphState(
        question="Coverage",
        retrieval_strategy="hybrid",
        top_k=5,
    )

    with pytest.raises(RuntimeError):
        retrieval_node(
            state=state,
            retrieval_service=retrieval_service,
        )


def test_retrieval_node_preserves_question() -> None:
    """
    Retrieval node should not modify the original question.
    """

    retrieval_service = Mock(spec=RetrievalService)

    retrieval_service.retrieve.return_value = []

    state = GraphState(
        question="What is liability insurance?",
        retrieval_strategy="hybrid",
        top_k=5,
    )

    retrieval_node(
        state=state,
        retrieval_service=retrieval_service,
    )

    assert state.question == "What is liability insurance?"


def test_retrieval_node_preserves_existing_metadata() -> None:
    """
    Existing metadata should not be overwritten.
    """

    retrieval_service = Mock(spec=RetrievalService)

    retrieval_service.retrieve.return_value = []

    state = GraphState(
        question="Coverage",
        retrieval_strategy="hybrid",
        top_k=5,
        metadata={
            "planner": {
                "workflow": "rag",
            }
        },
    )

    retrieval_node(
        state=state,
        retrieval_service=retrieval_service,
    )

    assert "planner" in state.metadata
    assert "retrieval" in state.metadata

    assert state.metadata["planner"]["workflow"] == "rag"

    retrieval_metadata = state.metadata["retrieval"]

    assert retrieval_metadata["strategy"] == "hybrid"
    assert retrieval_metadata["requested_top_k"] == 5
    assert retrieval_metadata["returned_chunks"] == 0
    assert retrieval_metadata["duration_ms"] >= 0