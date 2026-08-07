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


def _calculate_confidence(
        state: GraphState,
    ) -> float:
        """
        Calculate confidence using retrieval relevance.

        Confidence represents evidence strength rather than
        simply the presence of retrieved documents.

        Rules:
            - Empty answer -> 0.0
            - Fallback answer -> 0.0
            - No retrieved evidence -> 0.0
            - Otherwise derive confidence from the average
            retrieval relevance score.
        """

        answer = state.answer.strip()

        if not answer:
            return 0.0

        if answer == FALLBACK_RESPONSE:
            return 0.0

        if not state.retrieved_chunks:
            return 0.0

        relevance_scores: list[float] = []

        for document in state.retrieved_chunks:
            score = document.metadata.get(
                "relevance_score"
            )

            if isinstance(score, (int, float)):
                relevance_scores.append(
                    float(score)
                )

        if not relevance_scores:
            return 0.0

        average_relevance = (
            sum(relevance_scores)
            / len(relevance_scores)
        )

        # Map accepted retrieval relevance into a more
        # understandable evidence-confidence range.
        #
        # relevance 0.20 -> confidence 0.50
        # relevance 0.40 -> confidence 0.75
        # relevance 0.60 -> confidence 1.00
        confidence = (
            0.25
            + (average_relevance * 1.25)
        )

        return round(
            max(
                0.0,
                min(confidence, 1.0),
            ),
            2,
        )


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