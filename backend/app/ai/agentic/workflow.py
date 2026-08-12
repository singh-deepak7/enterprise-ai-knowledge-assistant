"""
LangGraph workflow for the Enterprise AI Knowledge Assistant.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Iterator
from typing import Any

from langchain_core.messages import AIMessageChunk
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

NO_CONTEXT_ANSWER = (
    "I couldn't find that information in the provided documents."
)


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
        session_id: str,
    ) -> GraphState:
        """
        Execute the complete agentic workflow.
        """

        workflow_start = time.perf_counter()
        request_id = str(uuid.uuid4())

        logger.info(
            "Starting agentic workflow "
            "[request_id=%s session_id=%s]",
            request_id,
            session_id,
        )

        initial_state = self._create_initial_state(
            question=question,
            session_id=session_id,
            request_id=request_id,
        )

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
                (
                    time.perf_counter()
                    - workflow_start
                )
                * 1000,
                2,
            )

            result.metadata.setdefault(
                "workflow",
                {},
            )

            result.metadata["workflow"].update(
                {
                    "request_id": request_id,
                    "session_id": session_id,
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
                "[request_id=%s session_id=%s "
                "duration=%.2fms]",
                request_id,
                session_id,
                workflow_duration_ms,
            )

            return result

        except Exception as ex:
            self._log_workflow_failure(
                initial_state=initial_state,
                request_id=request_id,
                session_id=session_id,
                workflow_start=workflow_start,
                exception=ex,
            )

            raise

    def stream(
        self,
        question: str,
        session_id: str,
    ) -> Iterator[dict[str, Any]]:
        """
        Stream workflow updates and LLM tokens.

        Conversation history is loaded before the current user
        message is stored so the current question is not duplicated
        in the prompt.
        """

        workflow_start = time.perf_counter()
        request_id = str(uuid.uuid4())

        logger.info(
            "Starting streaming agentic workflow "
            "[request_id=%s session_id=%s]",
            request_id,
            session_id,
        )

        initial_state = self._create_initial_state(
            question=question,
            session_id=session_id,
            request_id=request_id,
        )

        self._conversation_memory.add_user_message(
            session_id=session_id,
            message=question,
        )

        final_answer = ""

        try:
            for stream_mode, data in self._graph.stream(
                initial_state,
                stream_mode=[
                    "updates",
                    "messages",
                ],
            ):
                if stream_mode == "messages":
                    message, metadata = data

                    if not isinstance(
                        message,
                        AIMessageChunk,
                    ):
                        continue

                    content = message.content

                    if not isinstance(content, str):
                        continue

                    if not content:
                        continue

                    final_answer += content

                    yield {
                        "type": "token",
                        "data": {
                            "content": content,
                            "node": metadata.get(
                                "langgraph_node",
                            ),
                        },
                    }

                    continue

                if stream_mode == "updates":
                    final_answer = (
                        self._extract_answer_from_update(
                            data=data,
                            current_answer=final_answer,
                        )
                    )

                    yield {
                        "type": "updates",
                        "data": data,
                    }

            if final_answer:
                self._conversation_memory.add_assistant_message(
                    session_id=session_id,
                    message=final_answer,
                )

            workflow_duration_ms = round(
                (
                    time.perf_counter()
                    - workflow_start
                )
                * 1000,
                2,
            )

            logger.info(
                "Streaming agentic workflow completed "
                "[request_id=%s session_id=%s "
                "duration=%.2fms]",
                request_id,
                session_id,
                workflow_duration_ms,
            )

        except Exception as ex:
            self._log_workflow_failure(
                initial_state=initial_state,
                request_id=request_id,
                session_id=session_id,
                workflow_start=workflow_start,
                exception=ex,
            )

            raise

    def _create_initial_state(
        self,
        question: str,
        session_id: str,
        request_id: str,
    ) -> GraphState:
        """
        Create workflow state with conversation history.
        """

        history = self._conversation_memory.get_history(
            session_id,
        )

        return GraphState(
            question=question,
            request_id=request_id,
            conversation_history=history,
        )

    @staticmethod
    def _extract_answer_from_update(
        data: Any,
        current_answer: str,
    ) -> str:
        """
        Extract the completed answer from a node update.

        The completed reasoning/validation answer acts as a fallback
        if token streaming did not produce text.
        """

        if not isinstance(data, dict):
            return current_answer

        for value in data.values():
            if not isinstance(value, dict):
                continue

            answer = value.get("answer")

            if (
                isinstance(answer, str)
                and answer
            ):
                return answer

        return current_answer

    @staticmethod
    def _log_workflow_failure(
        initial_state: GraphState,
        request_id: str,
        session_id: str,
        workflow_start: float,
        exception: Exception,
    ) -> None:
        """
        Record and log workflow failure metadata.
        """

        workflow_duration_ms = round(
            (
                time.perf_counter()
                - workflow_start
            )
            * 1000,
            2,
        )

        logger.exception(
            "Agentic workflow failed "
            "[request_id=%s session_id=%s "
            "duration=%.2fms error=%s]",
            request_id,
            session_id,
            workflow_duration_ms,
            type(exception).__name__,
        )

        initial_state.metadata.setdefault(
            "workflow",
            {},
        )

        initial_state.metadata["workflow"].update(
            {
                "request_id": request_id,
                "session_id": session_id,
                "status": "failed",
                "duration_ms": workflow_duration_ms,
                "error_type": type(
                    exception
                ).__name__,
                "error_message": str(
                    exception
                ),
            }
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
            "Planner routing decision: "
            "requires_retrieval=%s",
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
            "no_context",
            self._no_context,
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

        builder.add_conditional_edges(
            "retrieval",
            self._route_after_retrieval,
            {
                "reasoning": "reasoning",
                "no_context": "no_context",
            },
        )

        builder.add_edge(
            "no_context",
            "validation",
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


    def _no_context(
        self,
        state: GraphState,
    ) -> GraphState:
        """
        Build a safe response when retrieval finds no
        sufficiently relevant document chunks.
        """

        logger.info(
            "No relevant context found; skipping LLM reasoning."
        )

        state.answer = NO_CONTEXT_ANSWER

        state.metadata.setdefault(
            "reasoning",
            {},
        )

        state.metadata["reasoning"].update(
            {
                "skipped": True,
                "reason": "no_relevant_context",
            }
        )

        return state


    def _route_after_retrieval(
        self,
        state: GraphState,
    ) -> str:
        """
        Route based on whether retrieval found relevant context.
        """

        has_context = bool(
            state.retrieved_chunks
        )

        logger.debug(
            "Retrieval routing decision: has_context=%s",
            has_context,
        )

        if has_context:
            return "reasoning"

        return "no_context"