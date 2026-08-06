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
        top_k = state.metadata.get("top_k", 5)
        documents = retrieval_service.retrieve(
            query=state.question,
            top_k=top_k,
        )

        state.retrieved_chunks = documents

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        state.metadata["retrieval"] = {
            "chunk_count": len(documents),
            "duration_ms": elapsed_ms,
        }

        if documents:
            logger.info(
                "Retrieved %d document(s).",
                len(documents),
            )
        else:
            logger.warning(
                "No relevant documents retrieved."
            )

        logger.info("Retrieval node completed.")

        return state

    except Exception:
        logger.exception(
            "Retrieval node failed."
        )
        raise