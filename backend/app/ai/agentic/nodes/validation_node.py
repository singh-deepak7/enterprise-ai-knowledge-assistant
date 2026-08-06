"""
LangGraph Validation Node.

This node performs the final workflow validation by building source
attribution and updating the graph state with workflow metadata.
"""

from __future__ import annotations

import logging
import time

from app.ai.agentic.graph_state import GraphState
from app.ai.retrieval.source_attribution import SourceAttribution

logger = logging.getLogger(__name__)


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

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        state.metadata["validation"] = {
            "duration_ms": elapsed_ms,
            "source_count": len(sources),
            "workflow_complete": True,
        }

        logger.info(
            "Validation completed with %d source(s).",
            len(sources),
        )

        return state

    except Exception:
        logger.exception(
            "Validation node failed."
        )
        raise