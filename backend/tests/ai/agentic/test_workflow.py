from unittest.mock import Mock, patch
from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.workflow import AgenticWorkflow
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.memory.conversation_memory import ConversationMemory
from app.ai.retrieval.retrieval_service import RetrievalService
from app.ai.retrieval.source_attribution import SourceAttribution
import uuid



def build_workflow(
    retrieval_service=None,
    prompt_builder=None,
    llm_service=None,
    source_attribution=None,
    conversation_memory=None,
) -> AgenticWorkflow:
    return AgenticWorkflow(
        retrieval_service=retrieval_service or Mock(spec=RetrievalService),
        prompt_builder=prompt_builder or Mock(spec=PromptBuilder),
        llm_service=llm_service or Mock(spec=LLMService),
        source_attribution=source_attribution
        or Mock(spec=SourceAttribution),
        conversation_memory=conversation_memory
        or Mock(spec=ConversationMemory),
    )


def test_route_after_planner_with_retrieval():
    workflow = build_workflow()

    state = GraphState(
        question="What is comprehensive coverage?",
        requires_retrieval=True,
    )

    assert workflow._route_after_planner(state) == "retrieval"


def test_route_after_planner_without_retrieval():
    workflow = build_workflow()

    state = GraphState(
        question="Hello",
        requires_retrieval=False,
    )

    assert workflow._route_after_planner(state) == "reasoning"


def test_workflow_stores_conversation():
    memory = Mock(spec=ConversationMemory)

    workflow = build_workflow(
        conversation_memory=memory,
    )

    workflow._graph = Mock()

    workflow._graph.invoke.return_value = GraphState(
        question="Coverage?",
        answer="Comprehensive coverage protects against theft.",
    )

    result = workflow.invoke("Coverage?")

    assert isinstance(result, GraphState)

    memory.add_user_message.assert_called_once_with(
        session_id="default",
        message="Coverage?",
    )

    memory.add_assistant_message.assert_called_once_with(
        session_id="default",
        message="Comprehensive coverage protects against theft.",
    )


def test_workflow_returns_graph_state():
    workflow = build_workflow()

    expected = GraphState(
        question="Coverage?",
        answer="Answer",
    )

    workflow._graph = Mock()
    workflow._graph.invoke.return_value = expected

    result = workflow.invoke("Coverage?")

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

    result = workflow.invoke("Coverage?")

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

    workflow.invoke("Coverage?")

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

    workflow.invoke("Coverage?")

    memory.get_history.assert_called_once_with("default")

    memory.add_user_message.assert_called_once_with(
        session_id="default",
        message="Coverage?",
    )

    memory.add_assistant_message.assert_called_once_with(
        session_id="default",
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

    result = workflow.invoke("Coverage?")

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

    workflow.invoke("Coverage?")

    workflow._conversation_memory.add_user_message.assert_called_once()

    workflow._conversation_memory.add_assistant_message.assert_called_once()

def test_workflow_generates_request_id() -> None:
    workflow = build_workflow()

    workflow._graph = Mock()

    workflow._graph.invoke.side_effect = (
        lambda state: state
    )

    state = workflow.invoke("Coverage")

    assert state.request_id != ""

    uuid.UUID(state.request_id)

    assert (
        state.metadata["workflow"]["request_id"]
        == state.request_id
    )