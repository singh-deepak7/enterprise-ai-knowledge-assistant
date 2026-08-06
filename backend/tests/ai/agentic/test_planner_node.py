import pytest

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.nodes.planner_node import planner_node


def test_planner_node_success() -> None:
    """
    Planner should initialize workflow metadata.
    """

    state = GraphState(
        question="What is comprehensive coverage?",
    )

    result = planner_node(state)

    assert result is state

    assert "planner" in state.metadata

    planner = state.metadata["planner"]

    assert planner["workflow"] == "rag"
    assert planner["top_k"] == 5
    assert planner["duration_ms"] >= 0


def test_planner_node_preserves_question() -> None:
    """
    Planner should not modify the question.
    """

    state = GraphState(
        question="Coverage?",
    )

    planner_node(state)

    assert state.question == "Coverage?"


def test_planner_node_preserves_existing_metadata() -> None:
    """
    Existing metadata should not be overwritten.
    """

    state = GraphState(
        question="Coverage?",
        metadata={
            "existing": {
                "value": 1,
            },
        },
    )

    planner_node(state)

    assert state.metadata["existing"]["value"] == 1
    assert "planner" in state.metadata


def test_planner_node_empty_question() -> None:
    """
    Empty questions should raise an error.
    """

    state = GraphState(
        question="   ",
    )

    with pytest.raises(ValueError):
        planner_node(state)