"""
Planner node for the LangGraph workflow.

Determines how downstream nodes should execute by
classifying user intent and selecting an appropriate
retrieval strategy.
"""

from __future__ import annotations

import logging
import re

from app.ai.agentic.graph_state import GraphState

logger = logging.getLogger(__name__)


class PlannerNode:
    """
    Produces an execution plan for the workflow.
    """

    _GREETING_PATTERN = re.compile(
        r"^(hi|hello|hey|good morning|good afternoon|good evening)\b",
        re.IGNORECASE,
    )

    _COMPARISON_PATTERN = re.compile(
        r"\b(compare|difference|versus|vs)\b",
        re.IGNORECASE,
    )

    _SUMMARY_PATTERN = re.compile(
        r"\b(summarize|summary|summarise)\b",
        re.IGNORECASE,
    )

    _DEFINITION_PATTERN = re.compile(
        r"\b(what is|what are|define|definition)\b",
        re.IGNORECASE,
    )

    def __call__(self, state: GraphState) -> GraphState:
        """
        Generate an execution plan from the user question.
        """

        question = state.question.strip()

        logger.info("Planner evaluating question: %s", question)

        if self._GREETING_PATTERN.search(question):
            state.intent = "greeting"
            state.retrieval_strategy = "none"
            state.top_k = 0
            state.requires_retrieval = False

        elif self._COMPARISON_PATTERN.search(question):
            state.intent = "comparison"
            state.retrieval_strategy = "hybrid"
            state.top_k = 8

        elif self._SUMMARY_PATTERN.search(question):
            state.intent = "summarization"
            state.retrieval_strategy = "semantic"
            state.top_k = 10

        elif self._DEFINITION_PATTERN.search(question):
            state.intent = "definition"
            state.retrieval_strategy = "hybrid"
            state.top_k = 3

        else:
            state.intent = "general_qa"
            state.retrieval_strategy = "hybrid"
            state.top_k = 5

        logger.info(
            "Planner result intent=%s strategy=%s top_k=%s retrieval=%s",
            state.intent,
            state.retrieval_strategy,
            state.top_k,
            state.requires_retrieval,
        )

        return state

planner_node = PlannerNode()