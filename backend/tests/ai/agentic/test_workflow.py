import uuid
from unittest.mock import Mock

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.workflow import AgenticWorkflow
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.memory.conversation_memory import ConversationMemory
from app.ai.retrieval.retrieval_service import RetrievalService
from app.ai.retrieval.source_attribution import SourceAttribution


TEST_SESSION_ID = "test-session"


def build_workflow(
    retrieval_service=None,
    prompt_builder=None,
    llm_service=None,
    source_attribution=None,
    conversation_memory=None,
) -> AgenticWorkflow:
    return AgenticWorkflow(
        retrieval_service=(
            retrieval_service
            or Mock(spec=RetrievalService)
        ),
        prompt_builder=(
            prompt_builder
            or Mock(spec=PromptBuilder)
        ),
        llm_service=(
            llm_service
            or Mock(spec=LLMService)
        ),
        source_attribution=(
            source_attribution
            or Mock(spec=SourceAttribution)
        ),
        conversation_memory=(
            conversation_memory
            or Mock(spec=ConversationMemory)
        ),
    )


def test_route_after_planner_with_retrieval():
    workflow = build_workflow()

    state = GraphState(
        question="What is comprehensive coverage?",
        requires_retrieval=True,
    )

    assert (
        workflow._route_after_planner(state)
        == "retrieval"
    )


def test_route_after_planner_without_retrieval():
    workflow = build_workflow()

    state = GraphState(
        question="Hello",
        requires_retrieval=False,
    )

    assert (
        workflow._route_after_planner(state)
        == "reasoning"
    )


def test_workflow_stores_conversation():
    memory = Mock(spec=ConversationMemory)
    memory.get_history.return_value = []

    workflow = build_workflow(
        conversation_memory=memory,
    )

    workflow._graph = Mock()

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage?",
        answer=(
            "Comprehensive coverage protects "
            "against theft."
        ),
    )

    result = workflow.invoke(
        question="Coverage?",
        session_id=TEST_SESSION_ID,
    )

    assert isinstance(result, GraphState)

    memory.add_user_message.assert_called_once_with(
        session_id=TEST_SESSION_ID,
        message="Coverage?",
    )

    memory.add_assistant_message.assert_called_once_with(
        session_id=TEST_SESSION_ID,
        message=(
            "Comprehensive coverage protects "
            "against theft."
        ),
    )


def test_workflow_returns_graph_state():
    workflow = build_workflow()

    expected = GraphState(
        question="Coverage?",
        answer="Answer",
    )

    workflow._graph = Mock()
    workflow._graph.invoke.return_value = expected

    result = workflow.invoke(
        question="Coverage?",
        session_id=TEST_SESSION_ID,
    )

    assert result is expected


def test_workflow_handles_dictionary_result():
    workflow = build_workflow()

    workflow._graph = Mock()

    workflow._graph.invoke.return_value = {
        "question": "Coverage?",
        "answer": "Answer",
        "sources": [],
        "validated": True,
    }

    result = workflow.invoke(
        question="Coverage?",
        session_id=TEST_SESSION_ID,
    )

    assert isinstance(result, GraphState)
    assert result.answer == "Answer"
    assert result.validated is True


def test_workflow_invokes_graph():
    workflow = build_workflow()

    workflow._graph = Mock()

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage?",
        answer="Answer",
    )

    workflow.invoke(
        question="Coverage?",
        session_id=TEST_SESSION_ID,
    )

    workflow._graph.invoke.assert_called_once()


def test_workflow_uses_conversation_memory():
    retrieval = Mock(spec=RetrievalService)
    prompt_builder = Mock(spec=PromptBuilder)
    llm = Mock(spec=LLMService)
    attribution = Mock(spec=SourceAttribution)
    memory = Mock(spec=ConversationMemory)

    memory.get_history.return_value = []

    workflow = AgenticWorkflow(
        retrieval_service=retrieval,
        prompt_builder=prompt_builder,
        llm_service=llm,
        source_attribution=attribution,
        conversation_memory=memory,
    )

    workflow._graph = Mock()

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage?",
        answer="Answer",
    )

    workflow.invoke(
        question="Coverage?",
        session_id=TEST_SESSION_ID,
    )

    memory.get_history.assert_called_once_with(
        TEST_SESSION_ID,
    )

    memory.add_user_message.assert_called_once_with(
        session_id=TEST_SESSION_ID,
        message="Coverage?",
    )

    memory.add_assistant_message.assert_called_once_with(
        session_id=TEST_SESSION_ID,
        message="Answer",
    )


def test_workflow_records_duration_metadata():
    workflow = build_workflow()

    workflow._graph = Mock()
    workflow._conversation_memory = Mock()
    workflow._conversation_memory.get_history.return_value = []

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage?",
        answer="Answer",
    )

    result = workflow.invoke(
        question="Coverage?",
        session_id=TEST_SESSION_ID,
    )

    assert "workflow" in result.metadata
    assert "duration_ms" in result.metadata["workflow"]
    assert result.metadata["workflow"]["duration_ms"] >= 0


def test_workflow_records_memory_messages():
    workflow = build_workflow()

    workflow._graph = Mock()
    workflow._conversation_memory = Mock()
    workflow._conversation_memory.get_history.return_value = []

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage?",
        answer="Answer",
    )

    workflow.invoke(
        question="Coverage?",
        session_id=TEST_SESSION_ID,
    )

    workflow._conversation_memory.add_user_message.assert_called_once()
    workflow._conversation_memory.add_assistant_message.assert_called_once()


def test_workflow_generates_request_id() -> None:
    workflow = build_workflow()

    workflow._graph = Mock()
    workflow._conversation_memory.get_history.return_value = []

    workflow._graph.invoke.side_effect = (
        lambda state: state
    )

    state = workflow.invoke(
        question="Coverage",
        session_id=TEST_SESSION_ID,
    )

    assert state.request_id != ""

    uuid.UUID(state.request_id)

    assert (
        state.metadata["workflow"]["request_id"]
        == state.request_id
    )


def test_workflow_records_status() -> None:
    """
    Workflow should record overall execution status.
    """

    workflow = build_workflow()

    workflow._graph = Mock()
    workflow._conversation_memory.get_history.return_value = []

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage",
        answer="Answer",
    )

    state = workflow.invoke(
        question="Coverage",
        session_id=TEST_SESSION_ID,
    )

    assert "workflow" in state.metadata

    assert (
        state.metadata["workflow"]["status"]
        == "success"
    )

    assert (
        state.metadata["workflow"]["duration_ms"]
        >= 0
    )


def test_workflow_records_success_status() -> None:
    """
    Workflow should record success metadata.
    """

    workflow = build_workflow()

    workflow._conversation_memory.get_history.return_value = []
    workflow._graph = Mock()

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage",
        answer="Answer",
    )

    state = workflow.invoke(
        question="Coverage",
        session_id=TEST_SESSION_ID,
    )

    assert (
        state.metadata["workflow"]["status"]
        == "success"
    )

    assert (
        state.metadata["workflow"]["duration_ms"]
        >= 0
    )

    assert "request_id" in state.metadata["workflow"]


def test_workflow_records_session_id() -> None:
    """
    Workflow should expose the session ID in metadata.
    """

    workflow = build_workflow()

    workflow._conversation_memory.get_history.return_value = []
    workflow._graph = Mock()

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage",
        answer="Answer",
    )

    state = workflow.invoke(
        question="Coverage",
        session_id=TEST_SESSION_ID,
    )

    assert (
        state.metadata["workflow"]["session_id"]
        == TEST_SESSION_ID
    )

def test_route_after_retrieval_with_context() -> None:
    """
    Workflow should continue to reasoning when
    retrieval returns relevant document chunks.
    """

    workflow = build_workflow()

    state = GraphState(
        question="What is comprehensive coverage?",
        retrieved_chunks=[
            Mock(),
        ],
    )

    assert (
        workflow._route_after_retrieval(state)
        == "reasoning"
    )


def test_route_after_retrieval_without_context() -> None:
    """
    Workflow should skip reasoning when retrieval
    returns no relevant document chunks.
    """

    workflow = build_workflow()

    state = GraphState(
        question="What is leave policy?",
        retrieved_chunks=[],
    )

    assert (
        workflow._route_after_retrieval(state)
        == "no_context"
    )

def test_no_context_sets_safe_fallback_answer() -> None:
    """
    No-context node should return the safe fallback
    without invoking the LLM.
    """

    workflow = build_workflow()

    state = GraphState(
        question="What is leave policy?",
    )

    result = workflow._no_context(state)

    assert (
        result.answer
        == "I couldn't find that information in the provided documents."
    )

    assert (
        result.metadata["reasoning"]["skipped"]
        is True
    )

    assert (
        result.metadata["reasoning"]["reason"]
        == "no_relevant_context"
    )