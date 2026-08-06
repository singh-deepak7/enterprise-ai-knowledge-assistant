from __future__ import annotations

from unittest.mock import Mock

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.workflow import AgenticWorkflow
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.retrieval.retrieval_service import RetrievalService
from app.ai.retrieval.source_attribution import SourceAttribution

from unittest.mock import MagicMock

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.workflow import AgenticWorkflow


def test_workflow_compiles() -> None:
    """
    Workflow should compile successfully.
    """
    retrieval_service = Mock(spec=RetrievalService)
    retrieval_service.retrieve.return_value = []

    workflow = AgenticWorkflow(
        retrieval_service=retrieval_service,
        prompt_builder=Mock(spec=PromptBuilder),
        llm_service=Mock(spec=LLMService),
        source_attribution=Mock(spec=SourceAttribution),
    )

    assert workflow._graph is not None


def test_workflow_invokes_graph() -> None:
    """
    invoke() should execute the compiled graph.
    """

    workflow = AgenticWorkflow(
        retrieval_service=Mock(spec=RetrievalService),
        prompt_builder=Mock(spec=PromptBuilder),
        llm_service=Mock(spec=LLMService),
        source_attribution=Mock(spec=SourceAttribution),
    )

    expected_state = GraphState(
        question="Coverage?",
        answer="Answer",
    )

    workflow._graph = Mock()
    workflow._graph.invoke.return_value = expected_state

    result = workflow.invoke("Coverage?")

    workflow._graph.invoke.assert_called_once()

    state = workflow._graph.invoke.call_args.args[0]

    assert isinstance(state, GraphState)
    assert state.question == "Coverage?"

    assert result is expected_state


def test_retrieval_wrapper() -> None:
    """
    Retrieval wrapper should delegate to RetrievalService.
    """
    retrieval_service = Mock(spec=RetrievalService)
    retrieval_service.retrieve.return_value = []

    workflow = AgenticWorkflow(
        retrieval_service=retrieval_service,
        prompt_builder=Mock(spec=PromptBuilder),
        llm_service=Mock(spec=LLMService),
        source_attribution=Mock(spec=SourceAttribution),
    )

    state = GraphState(question="Coverage")

    result = workflow._retrieval(state)

    retrieval_service.retrieve.assert_called_once()

    assert result is state


def test_reasoning_wrapper() -> None:
    """
    Reasoning wrapper should delegate to PromptBuilder and LLM.
    """

    prompt_builder = Mock(spec=PromptBuilder)
    prompt_builder.build_prompt.return_value = "PROMPT"

    llm_service = Mock(spec=LLMService)
    llm_service.generate.return_value = "ANSWER"

    workflow = AgenticWorkflow(
        retrieval_service=Mock(spec=RetrievalService),
        prompt_builder=prompt_builder,
        llm_service=llm_service,
        source_attribution=Mock(spec=SourceAttribution),
    )

    state = GraphState(question="Coverage")

    result = workflow._reasoning(state)

    assert result is state
    prompt_builder.build_prompt.assert_called_once()
    llm_service.generate.assert_called_once()


def test_validation_wrapper() -> None:
    """
    Validation wrapper should delegate to SourceAttribution.
    """

    source_service = Mock(spec=SourceAttribution)
    source_service.build_sources.return_value = []

    workflow = AgenticWorkflow(
        retrieval_service=Mock(spec=RetrievalService),
        prompt_builder=Mock(spec=PromptBuilder),
        llm_service=Mock(spec=LLMService),
        source_attribution=source_service,
    )

    state = GraphState(question="Coverage")

    result = workflow._validation(state)

    assert result is state

    source_service.build_sources.assert_called_once()

def test_route_after_planner_with_retrieval():
    workflow = create_workflow()

    state = GraphState(
        question="What is comprehensive coverage?",
        requires_retrieval=True,
    )

    assert workflow._route_after_planner(state) == "retrieval"


def test_route_after_planner_without_retrieval():
    workflow = create_workflow()

    state = GraphState(
        question="Hello",
        requires_retrieval=False,
    )

    assert workflow._route_after_planner(state) == "reasoning"

def create_workflow():
    return AgenticWorkflow(
        retrieval_service=MagicMock(),
        prompt_builder=MagicMock(),
        llm_service=MagicMock(),
        source_attribution=MagicMock(),
    )