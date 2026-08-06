from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.nodes.planner_node import PlannerNode


def test_planner_detects_greeting():
    planner = PlannerNode()

    state = GraphState(question="Hello")

    result = planner(state)

    assert result.intent == "greeting"
    assert result.requires_retrieval is False
    assert result.retrieval_strategy == "none"
    assert result.top_k == 0


def test_planner_detects_definition():
    planner = PlannerNode()

    state = GraphState(question="What is comprehensive coverage?")

    result = planner(state)

    assert result.intent == "definition"
    assert result.retrieval_strategy == "hybrid"
    assert result.top_k == 3
    assert result.requires_retrieval is True


def test_planner_detects_comparison():
    planner = PlannerNode()

    state = GraphState(
        question="Compare collision and comprehensive coverage"
    )

    result = planner(state)

    assert result.intent == "comparison"
    assert result.retrieval_strategy == "hybrid"
    assert result.top_k == 8


def test_planner_detects_summary():
    planner = PlannerNode()

    state = GraphState(question="Summarize this policy")

    result = planner(state)

    assert result.intent == "summarization"
    assert result.retrieval_strategy == "semantic"
    assert result.top_k == 10


def test_planner_defaults_to_general_qa():
    planner = PlannerNode()

    state = GraphState(
        question="Does my policy cover hail damage?"
    )

    result = planner(state)

    assert result.intent == "general_qa"
    assert result.retrieval_strategy == "hybrid"
    assert result.top_k == 5
    assert result.requires_retrieval is True