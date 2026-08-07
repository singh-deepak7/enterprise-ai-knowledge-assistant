from __future__ import annotations

from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.nodes.validation_node import validation_node
from app.ai.retrieval.source_attribution import SourceAttribution


def test_validation_node_success() -> None:
    """
    Validation node should build source attribution and
    update the graph state.
    """

    documents = [
        Document(
            page_content="Coverage",
            metadata={
                "source": "policy.pdf",
                "page": 2,
                "chunk": 1,
            },
        ),
        Document(
            page_content="Collision",
            metadata={
                "source": "policy.pdf",
                "page": 3,
                "chunk": 2,
            },
        ),
    ]

    sources = [
        {
            "source": "policy.pdf",
            "page": 2,
            "chunk": 1,
        },
        {
            "source": "policy.pdf",
            "page": 3,
            "chunk": 2,
        },
    ]

    source_attribution = Mock(spec=SourceAttribution)
    source_attribution.build_sources.return_value = sources

    state = GraphState(
        question="What is comprehensive coverage?",
        retrieved_chunks=documents,
        answer="Comprehensive coverage protects against theft.",
    )

    result = validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    source_attribution.build_sources.assert_called_once_with(
        documents,
    )

    assert result is state
    assert result.sources == sources

    assert "validation" in result.metadata

    metadata = result.metadata["validation"]

    assert metadata["duration_ms"] >= 0
    assert metadata["source_count"] == 2
    assert metadata["workflow_complete"] is True


def test_validation_node_empty_documents() -> None:
    """
    Validation node should support workflows with no
    retrieved documents.
    """

    source_attribution = Mock(spec=SourceAttribution)
    source_attribution.build_sources.return_value = []

    state = GraphState(
        question="Unknown question",
    )

    result = validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert result.sources == []

    metadata = result.metadata["validation"]

    assert metadata["source_count"] == 0
    assert metadata["workflow_complete"] is True


def test_validation_node_preserves_answer() -> None:
    """
    Validation should never modify the generated answer.
    """

    source_attribution = Mock(spec=SourceAttribution)
    source_attribution.build_sources.return_value = []

    state = GraphState(
        question="Coverage",
        answer="Existing answer",
    )

    validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert state.answer == "Existing answer"


def test_validation_node_preserves_existing_metadata() -> None:
    """
    Existing workflow metadata should remain intact.
    """

    source_attribution = Mock(spec=SourceAttribution)
    source_attribution.build_sources.return_value = []

    state = GraphState(
        question="Coverage",
        metadata={
            "planner": {
                "workflow": "rag",
            },
            "retrieval": {
                "chunk_count": 5,
            },
            "reasoning": {
                "answer_length": 120,
            },
        },
    )

    validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert state.metadata["planner"]["workflow"] == "rag"
    assert state.metadata["retrieval"]["chunk_count"] == 5
    assert state.metadata["reasoning"]["answer_length"] == 120
    assert "validation" in state.metadata


def test_validation_node_propagates_exception() -> None:
    """
    Exceptions from SourceAttribution should be propagated.
    """

    source_attribution = Mock(spec=SourceAttribution)

    source_attribution.build_sources.side_effect = RuntimeError(
        "Source attribution failed"
    )

    state = GraphState(
        question="Coverage",
    )

    with pytest.raises(RuntimeError):
        validation_node(
            state=state,
            source_attribution=source_attribution,
        )


def test_validation_node_preserves_question() -> None:
    """
    Validation node should not modify the original question.
    """

    source_attribution = Mock(spec=SourceAttribution)
    source_attribution.build_sources.return_value = []

    state = GraphState(
        question="What is liability insurance?",
    )

    validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert state.question == "What is liability insurance?"

def test_validation_assigns_full_confidence():
    attribution = Mock(spec=SourceAttribution)

    attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 2,
            
        }
    ]

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=[
            Document(
                page_content="Coverage",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                    "relevance_score": 0.60,
                },
            )
        ],
        answer="Comprehensive coverage protects against theft.",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.validated is True
    assert result.confidence_score == 1.0

def test_validation_zero_confidence_without_answer():
    attribution = Mock(spec=SourceAttribution)

    attribution.build_sources.return_value = []

    state = GraphState(
        question="Coverage?",
        answer="",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.confidence_score == 0.0


def test_validation_reduces_confidence_for_fallback_answer():
    attribution = Mock(spec=SourceAttribution)

    attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 2,
        }
    ]

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=[
            Document(
                page_content="Coverage",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                },
            )
        ],
        answer=(
            "I couldn't find that information "
            "in the provided documents."
        ),
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.confidence_score == 0.0

def test_validation_populates_sources():
    attribution = Mock(spec=SourceAttribution)

    attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 5,
        }
    ]

    state = GraphState(
        question="Coverage?",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.sources == [
        {
            "source": "policy.pdf",
            "page": 5,
        }
    ]

def test_validation_confidence_uses_relevance_scores():
    attribution = Mock(spec=SourceAttribution)

    attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 2,
        }
    ]

    state = GraphState(
        question="What is comprehensive coverage?",
        retrieved_chunks=[
            Document(
                page_content="Coverage",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                    "relevance_score": 0.24,
                },
            )
        ],
        answer="Comprehensive coverage protects against theft.",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.confidence_score == 0.55

def test_validation_zero_confidence_without_relevance_scores():
    attribution = Mock(spec=SourceAttribution)

    attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 2,
        }
    ]

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=[
            Document(
                page_content="Coverage",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                },
            )
        ],
        answer="Coverage answer.",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.confidence_score == 0.0