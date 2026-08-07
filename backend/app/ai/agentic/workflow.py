"""
LangGraph workflow for the Enterprise AI Knowledge Assistant.
"""

from __future__ import annotations

import logging
import time
import uuid

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.nodes.planner_node import planner_node
from app.ai.agentic.nodes.reasoning_node import reasoning_node
from app.ai.agentic.nodes.retrieval_node import retrieval_node
from app.ai.agentic.nodes.validation_node import validation_node
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.memory.conversation_memory import ConversationMemory
from app.ai.retrieval.retrieval_service import RetrievalService
from app.ai.retrieval.source_attribution import SourceAttribution

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
        conversation_memory: ConversationMemory | None = None,
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

        self._conversation_memory = (
            conversation_memory or ConversationMemory()
        )

        self._graph = self._build_graph()

    def invoke(
        self,
        question: str,
    ) -> GraphState:
        """
        Execute the complete agentic workflow.
        """

        workflow_start = time.perf_counter()

        session_id = "default"
        request_id = str(uuid.uuid4())

        logger.info(
            "Starting agentic workflow [request_id=%s]",
            request_id,
        )

        history = self._conversation_memory.get_history(
            session_id,
        )

        initial_state = GraphState(
            question=question,
            request_id=request_id,
            conversation_history=history,
        )

        # Store current user message after loading history so
        # it isn't duplicated in the current prompt.
        self._conversation_memory.add_user_message(
            session_id=session_id,
            message=question,
        )

        try:
            result = self._graph.invoke(
                initial_state,
            )

            if not isinstance(result, GraphState):
                result = GraphState(**result)

            workflow_duration_ms = round(
                (time.perf_counter() - workflow_start) * 1000,
                2,
            )

            result.metadata.setdefault(
                "workflow",
                {},
            )

            result.metadata["workflow"].update(
                {
                    "request_id": request_id,
                    "status": "success",
                    "duration_ms": workflow_duration_ms,
                }
            )

            self._conversation_memory.add_assistant_message(
                session_id=session_id,
                message=result.answer,
            )

            logger.info(
                "Agentic workflow completed "
                "[request_id=%s duration=%.2fms]",
                request_id,
                workflow_duration_ms,
            )

            return result

        except Exception as ex:
            workflow_duration_ms = round(
                (time.perf_counter() - workflow_start) * 1000,
                2,
            )

            logger.exception(
                "Agentic workflow failed "
                "[request_id=%s duration=%.2fms error=%s]",
                request_id,
                workflow_duration_ms,
                type(ex).__name__,
            )

            # Preserve failure metadata for future observability.
            initial_state.metadata.setdefault(
                "workflow",
                {},
            )

            initial_state.metadata["workflow"].update(
                {
                    "request_id": request_id,
                    "status": "failed",
                    "duration_ms": workflow_duration_ms,
                    "error_type": type(ex).__name__,
                    "error_message": str(ex),
                }
            )

            raise

    def stream(
        self,
        question: str,
    ):
        """
        Stream LangGraph workflow events.

        Used by the SSE chat endpoint.
        """

        session_id = "default"
        request_id = str(uuid.uuid4())

        logger.info(
            "Starting streaming workflow [request_id=%s]",
            request_id,
        )

        history = self._conversation_memory.get_history(
            session_id,
        )

        initial_state = GraphState(
            question=question,
            request_id=request_id,
            conversation_history=history,
        )

        self._conversation_memory.add_user_message(
            session_id=session_id,
            message=question,
        )

        return self._graph.stream(
            initial_state,
            stream_mode="updates",
        )

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
        Route the workflow after planning.
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

    def _build_graph(
        self,
    ) -> CompiledStateGraph:
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