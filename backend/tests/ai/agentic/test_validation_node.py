from __future__ import annotations

from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.nodes.validation_node import (
    FALLBACK_RESPONSE,
    MIN_VALIDATION_CONFIDENCE,
    validation_node,
)
from app.ai.retrieval.source_attribution import SourceAttribution


def test_validation_node_success() -> None:
    """
    Validation node should validate a supported answer,
    build source attribution, and update graph metadata.
    """

    documents = [
        Document(
            page_content="Coverage",
            metadata={
                "source": "policy.pdf",
                "page": 2,
                "chunk": 1,
                "relevance_score": 0.24,
            },
        ),
        Document(
            page_content="Collision",
            metadata={
                "source": "policy.pdf",
                "page": 3,
                "chunk": 2,
                "relevance_score": 0.22,
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
        answer=(
            "Comprehensive coverage protects against theft."
        ),
    )

    result = validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    source_attribution.build_sources.assert_called_once_with(
        documents,
    )

    assert result is state
    assert result.validated is True
    assert result.sources == sources
    assert result.answer == (
        "Comprehensive coverage protects against theft."
    )

    assert "validation" in result.metadata

    metadata = result.metadata["validation"]

    assert metadata["duration_ms"] >= 0
    assert metadata["source_count"] == 2
    assert metadata["workflow_complete"] is True
    assert metadata["validated"] is True
    assert (
        metadata["confidence_score"]
        == result.confidence_score
    )


def test_validation_node_empty_documents() -> None:
    """
    Validation should reject a response when no retrieved
    documents are available.
    """

    source_attribution = Mock(spec=SourceAttribution)
    source_attribution.build_sources.return_value = []

    state = GraphState(
        question="Unknown question",
        answer="Some generated answer.",
    )

    result = validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert result.validated is False
    assert result.answer == FALLBACK_RESPONSE
    assert result.sources == []
    assert result.confidence_score == 0.0

    metadata = result.metadata["validation"]

    assert metadata["source_count"] == 0
    assert metadata["workflow_complete"] is True
    assert metadata["validated"] is False


def test_validation_rejects_empty_answer() -> None:
    """
    Validation should reject an empty generated answer.
    """

    source_attribution = Mock(spec=SourceAttribution)

    source_attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 2,
        }
    ]

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=[
            Document(
                page_content="Coverage information.",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                    "relevance_score": 0.30,
                },
            )
        ],
        answer="",
    )

    result = validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert result.validated is False
    assert result.answer == FALLBACK_RESPONSE
    assert result.sources == []
    assert result.confidence_score == 0.0


def test_validation_rejects_fallback_answer() -> None:
    """
    A fallback answer should never be considered a
    validated grounded response.
    """

    source_attribution = Mock(spec=SourceAttribution)

    source_attribution.build_sources.return_value = [
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
                    "relevance_score": 0.30,
                },
            )
        ],
        answer=FALLBACK_RESPONSE,
    )

    result = validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert result.validated is False
    assert result.answer == FALLBACK_RESPONSE
    assert result.sources == []
    assert result.confidence_score == 0.0


def test_validation_rejects_when_no_sources() -> None:
    """
    Validation should reject an answer when retrieved
    evidence exists but no source attribution can be built.
    """

    source_attribution = Mock(spec=SourceAttribution)
    source_attribution.build_sources.return_value = []

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=[
            Document(
                page_content="Coverage information.",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                    "relevance_score": 0.30,
                },
            )
        ],
        answer="Coverage protects against certain losses.",
    )

    result = validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert result.validated is False
    assert result.answer == FALLBACK_RESPONSE
    assert result.sources == []
    assert result.confidence_score > 0.0


def test_validation_accepts_supported_answer() -> None:
    """
    Validation should accept an answer backed by evidence,
    sources, and sufficient confidence.
    """

    source_attribution = Mock(spec=SourceAttribution)

    sources = [
        {
            "source": "CommonInsuranceTerms.pdf",
            "page": 2,
        }
    ]

    source_attribution.build_sources.return_value = sources

    state = GraphState(
        question=(
            "What does comprehensive coverage "
            "protect against?"
        ),
        retrieved_chunks=[
            Document(
                page_content=(
                    "Comprehensive coverage includes theft, "
                    "fire, vandalism, flood, and hail."
                ),
                metadata={
                    "source": "CommonInsuranceTerms.pdf",
                    "page": 2,
                    "relevance_score": 0.20,
                },
            )
        ],
        answer=(
            "Comprehensive coverage protects against "
            "non-collision losses such as theft and fire."
        ),
    )

    result = validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert result.validated is True
    assert result.answer != FALLBACK_RESPONSE
    assert result.sources == sources
    assert (
        result.confidence_score
        >= MIN_VALIDATION_CONFIDENCE
    )


def test_validation_node_preserves_supported_answer() -> None:
    """
    Validation should preserve a generated answer when it
    satisfies all validation requirements.
    """

    source_attribution = Mock(spec=SourceAttribution)

    source_attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 2,
        }
    ]

    state = GraphState(
        question="Coverage",
        retrieved_chunks=[
            Document(
                page_content="Coverage information.",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                    "relevance_score": 0.25,
                },
            )
        ],
        answer="Existing answer",
    )

    validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert state.validated is True
    assert state.answer == "Existing answer"


def test_validation_node_replaces_unsupported_answer() -> None:
    """
    Validation should replace an unsupported generated
    answer with the safe fallback response.
    """

    source_attribution = Mock(spec=SourceAttribution)
    source_attribution.build_sources.return_value = []

    state = GraphState(
        question="Coverage",
        answer="Unsupported generated answer",
    )

    validation_node(
        state=state,
        source_attribution=source_attribution,
    )

    assert state.validated is False
    assert state.answer == FALLBACK_RESPONSE


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

    assert (
        state.metadata["planner"]["workflow"]
        == "rag"
    )
    assert (
        state.metadata["retrieval"]["chunk_count"]
        == 5
    )
    assert (
        state.metadata["reasoning"]["answer_length"]
        == 120
    )
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

    with pytest.raises(
        RuntimeError,
        match="Source attribution failed",
    ):
        validation_node(
            state=state,
            source_attribution=source_attribution,
        )


def test_validation_node_preserves_question() -> None:
    """
    Validation should not modify the original question.
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

    assert (
        state.question
        == "What is liability insurance?"
    )


def test_validation_assigns_full_confidence() -> None:
    """
    A relevance score of 0.60 should map to the maximum
    confidence score of 1.0.
    """

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
        answer=(
            "Comprehensive coverage protects "
            "against theft."
        ),
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.validated is True
    assert result.confidence_score == 1.0


def test_validation_zero_confidence_without_answer() -> None:
    """
    An empty answer should have zero confidence.
    """

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

    assert result.validated is False
    assert result.confidence_score == 0.0
    assert result.answer == FALLBACK_RESPONSE


def test_validation_reduces_confidence_for_fallback_answer() -> None:
    """
    The workflow fallback response should always produce
    zero confidence.
    """

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
                    "relevance_score": 0.30,
                },
            )
        ],
        answer=FALLBACK_RESPONSE,
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.validated is False
    assert result.confidence_score == 0.0
    assert result.answer == FALLBACK_RESPONSE
    assert result.sources == []


def test_validation_populates_sources_for_valid_answer() -> None:
    """
    Validation should preserve source attribution when an
    answer passes validation.
    """

    attribution = Mock(spec=SourceAttribution)

    sources = [
        {
            "source": "policy.pdf",
            "page": 5,
        }
    ]

    attribution.build_sources.return_value = sources

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=[
            Document(
                page_content="Coverage information.",
                metadata={
                    "source": "policy.pdf",
                    "page": 5,
                    "relevance_score": 0.25,
                },
            )
        ],
        answer="Coverage answer.",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.validated is True
    assert result.sources == sources


def test_validation_clears_sources_for_invalid_answer() -> None:
    """
    Sources should not be exposed for a response that fails
    validation.
    """

    attribution = Mock(spec=SourceAttribution)

    attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 5,
        }
    ]

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=[
            Document(
                page_content="Coverage information.",
                metadata={
                    "source": "policy.pdf",
                    "page": 5,
                },
            )
        ],
        answer="Coverage answer.",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.validated is False
    assert result.sources == []
    assert result.answer == FALLBACK_RESPONSE


def test_validation_confidence_uses_relevance_scores() -> None:
    """
    Validation confidence should be calculated from
    retrieval relevance scores.
    """

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
        answer=(
            "Comprehensive coverage protects "
            "against theft."
        ),
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    assert result.validated is True
    assert result.confidence_score == 0.55


def test_validation_uses_average_relevance_score() -> None:
    """
    Confidence should use the average relevance score when
    multiple retrieved chunks are present.
    """

    attribution = Mock(spec=SourceAttribution)

    attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 2,
        },
        {
            "source": "policy.pdf",
            "page": 3,
        },
    ]

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=[
            Document(
                page_content="First chunk",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                    "relevance_score": 0.20,
                },
            ),
            Document(
                page_content="Second chunk",
                metadata={
                    "source": "policy.pdf",
                    "page": 3,
                    "relevance_score": 0.28,
                },
            ),
        ],
        answer="Supported coverage answer.",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    # Average relevance = 0.24
    # 0.25 + (0.24 * 1.25) = 0.55
    assert result.confidence_score == 0.55
    assert result.validated is True


def test_validation_zero_confidence_without_relevance_scores() -> None:
    """
    Retrieved documents without relevance scores should
    result in zero confidence and fail validation.
    """

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
    assert result.validated is False
    assert result.answer == FALLBACK_RESPONSE
    assert result.sources == []


def test_validation_rejects_below_minimum_confidence() -> None:
    """
    A response with evidence below the minimum validation
    confidence should be replaced with the fallback.
    """

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
                page_content="Weakly related content.",
                metadata={
                    "source": "policy.pdf",
                    "page": 2,
                    "relevance_score": 0.10,
                },
            )
        ],
        answer="Potentially unsupported answer.",
    )

    result = validation_node(
        state=state,
        source_attribution=attribution,
    )

    # 0.25 + (0.10 * 1.25) = 0.375 -> 0.38
    assert result.confidence_score == 0.38
    assert (
        result.confidence_score
        < MIN_VALIDATION_CONFIDENCE
    )
    assert result.validated is False
    assert result.answer == FALLBACK_RESPONSE
    assert result.sources == []