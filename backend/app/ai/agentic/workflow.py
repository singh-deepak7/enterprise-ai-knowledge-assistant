"""
LangGraph workflow for the Enterprise AI Knowledge Assistant.
"""

from __future__ import annotations

import logging

from langgraph.graph import END, START, StateGraph

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.nodes.planner_node import planner_node
from app.ai.agentic.nodes.reasoning_node import reasoning_node
from app.ai.agentic.nodes.retrieval_node import retrieval_node
from app.ai.agentic.nodes.validation_node import validation_node
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.retrieval.retrieval_service import RetrievalService
from app.ai.retrieval.source_attribution import SourceAttribution
from langgraph.graph.state import CompiledStateGraph


logger = logging.getLogger(__name__)


class AgenticWorkflow:
    """
    LangGraph workflow orchestrating the Enterprise AI
    Knowledge & Decision Support System.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        prompt_builder: PromptBuilder | None = None,
        llm_service: LLMService | None = None,
        source_attribution: SourceAttribution | None = None,
    ) -> None:
        self._retrieval_service = (
            retrieval_service or RetrievalService()
        )
        self._prompt_builder = (
            prompt_builder or PromptBuilder()
        )
        self._llm_service = (
            llm_service or LLMService()
        )
        self._source_attribution = (
            source_attribution or SourceAttribution()
        )

        self._graph = self._build_graph()

    def invoke(
    self,
    question: str,
    ) -> GraphState:
        """
        Execute the complete agentic workflow.
        """

        logger.info(
            "Starting agentic workflow."
        )

        initial_state = GraphState(
            question=question,
        )

        result = self._graph.invoke(
            initial_state,
        )

        logger.info(
            "Agentic workflow completed."
        )

        if isinstance(result, GraphState):
            return result

        return GraphState(**result)

    def _planner(
        self,
        state: GraphState,
    ) -> GraphState:
        """
        Planner wrapper.
        """

        return planner_node(state)

    def _route_after_planner(
        self,
        state: GraphState,
    ) -> str:
        """
        Determine the next workflow step after planning.
        """

        logger.debug(
            "Planner routing decision: requires_retrieval=%s",
            state.requires_retrieval,
        )

        if state.requires_retrieval:
            return "retrieval"

        return "reasoning"

    def _retrieval(
        self,
        state: GraphState,
    ) -> GraphState:
        """
        Retrieval wrapper.
        """

        return retrieval_node(
            state=state,
            retrieval_service=self._retrieval_service,
        )

    def _reasoning(
        self,
        state: GraphState,
    ) -> GraphState:
        """
        Reasoning wrapper.
        """

        return reasoning_node(
            state=state,
            prompt_builder=self._prompt_builder,
            llm_service=self._llm_service,
        )

    def _validation(
        self,
        state: GraphState,
    ) -> GraphState:
        """
        Validation wrapper.
        """

        return validation_node(
            state=state,
            source_attribution=self._source_attribution,
        )

    def _build_graph(self) -> CompiledStateGraph:
        """
        Build and compile the LangGraph workflow.
        """

        logger.info(
            "Building LangGraph workflow."
        )

        builder = StateGraph(GraphState)

        builder.add_node(
            "planner",
            self._planner,
        )

        builder.add_node(
            "retrieval",
            self._retrieval,
        )

        builder.add_node(
            "reasoning",
            self._reasoning,
        )

        builder.add_node(
            "validation",
            self._validation,
        )

        builder.add_edge(
            START,
            "planner",
        )

        builder.add_conditional_edges(
            "planner",
            self._route_after_planner,
                {
                    "retrieval": "retrieval",
                    "reasoning": "reasoning",
                },
        )

        builder.add_edge(
            "retrieval",
            "reasoning",
        )

        builder.add_edge(
            "reasoning",
            "validation",
        )

        builder.add_edge(
            "validation",
            END,
        )

        logger.info(
            "LangGraph workflow compiled."
        )

        return builder.compile()