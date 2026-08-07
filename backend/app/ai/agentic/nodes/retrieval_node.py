"""
LangGraph Retrieval Node.

This node retrieves relevant document chunks using the existing
RetrievalService.
"""

from __future__ import annotations

import logging
import time

from app.ai.agentic.graph_state import GraphState
from app.ai.retrieval.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


def retrieval_node(
    state: GraphState,
    retrieval_service: RetrievalService,
) -> GraphState:
    """
    Retrieve relevant document chunks and update the graph state.

    Args:
        state:
            Current workflow state.

        retrieval_service:
            Existing RetrievalService instance.

    Returns:
        Updated GraphState.
    """

    logger.info("Retrieval node started.")

    start = time.perf_counter()

    try:
        logger.debug(
            "Retrieving documents (strategy=%s, top_k=%d).",
            state.retrieval_strategy,
            state.top_k,
        )

        documents = retrieval_service.retrieve(
            query=state.question,
            top_k=state.top_k,
        )

        state.retrieved_chunks = documents

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        state.metadata["retrieval"] = {
            "strategy": state.retrieval_strategy,
            "requested_top_k": state.top_k,
            "returned_chunks": len(documents),
            "duration_ms": elapsed_ms,
        }

        if documents:
            logger.info(
                "Retrieved %d document(s) in %.2f ms.",
                len(documents),
                elapsed_ms,
            )
        else:
            logger.warning(
                "No relevant documents retrieved."
            )

        return state

    except Exception:
        logger.exception(
            "Retrieval node failed."
        )
        raise