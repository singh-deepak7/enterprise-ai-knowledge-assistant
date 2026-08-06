"""
LangGraph Planner Node.

The planner is responsible for initializing the workflow state and
deciding the execution strategy.

Currently, Sprint 7 supports a single RAG workflow. This node exists
to make future routing (SQL, Web Search, Tool Calling, Multi-Agent)
easy to introduce without changing the graph structure.
"""

from __future__ import annotations

import logging
import time

from app.ai.agentic.graph_state import GraphState

logger = logging.getLogger(__name__)


def planner_node(
    state: GraphState,
) -> GraphState:
    """
    Initialize workflow metadata.

    Args:
        state:
            Current graph state.

    Returns:
        Updated GraphState.
    """

    logger.info("Planner node started.")

    start = time.perf_counter()

    if not state.question.strip():
        raise ValueError("Question cannot be empty.")

    state.metadata["planner"] = {
        "workflow": "rag",
        "top_k": 5,
        "duration_ms": round(
            (time.perf_counter() - start) * 1000,
            2,
        ),
    }

    logger.info("Planner node completed.")

    return state