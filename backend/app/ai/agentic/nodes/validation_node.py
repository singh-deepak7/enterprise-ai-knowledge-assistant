"""
LangGraph Validation Node.

This node performs the final workflow validation by building source
attribution, calculating confidence, and updating the graph state with
workflow metadata.
"""

from __future__ import annotations

import logging
import time

from app.ai.agentic.graph_state import GraphState
from app.ai.retrieval.source_attribution import SourceAttribution

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I couldn't find that information in the provided documents."
)


def _calculate_confidence(state: GraphState) -> float:
    """
    Calculate a deterministic confidence score.

    Scoring:
        +0.30 -> Retrieved documents
        +0.30 -> Sources attributed
        +0.20 -> Non-empty answer
        +0.20 -> Answer is not fallback

    Maximum = 1.0
    """

    score = 0.0

    if state.retrieved_chunks:
        score += 0.30

    if state.sources:
        score += 0.30

    if state.answer.strip():
        score += 0.20

    if (
        state.answer.strip()
        and state.answer.strip() != FALLBACK_RESPONSE
    ):
        score += 0.20

    return round(min(score, 1.0), 2)


def validation_node(
    state: GraphState,
    source_attribution: SourceAttribution,
) -> GraphState:
    """
    Build source attribution and finalize the workflow.

    Args:
        state:
            Current workflow state.

        source_attribution:
            Existing SourceAttribution service.

    Returns:
        Updated GraphState.
    """

    logger.info("Validation node started.")

    start = time.perf_counter()

    try:
        logger.debug(
            "Building source attribution from %d retrieved document(s).",
            len(state.retrieved_chunks),
        )

        sources = source_attribution.build_sources(
            state.retrieved_chunks,
        )

        state.sources = sources
        state.validated = True
        state.confidence_score = _calculate_confidence(state)

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        # Preserve any existing metadata
        state.metadata.setdefault("validation", {})

        state.metadata["validation"].update(
            {
                "duration_ms": elapsed_ms,
                "source_count": len(sources),
                "workflow_complete": True,
                "validated": True,
                "confidence_score": state.confidence_score,
            }
        )

        logger.info(
            (
                "Validation completed with %d source(s). "
                "Confidence %.2f"
            ),
            len(sources),
            state.confidence_score,
        )

        return state

    except Exception:
        logger.exception(
            "Validation node failed."
        )
        raise