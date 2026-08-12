from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

from langsmith import Client

from app.ai.evaluation.evaluators import (
    evaluate_answer_correctness,
    evaluate_source_match,
    evaluate_unanswerable_behavior,
)
from app.core.config import settings
from app.dependencies import get_agentic_workflow


DATASET_NAME = "enterprise-ai-rag-evaluation"


os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
os.environ["LANGSMITH_TRACING"] = str(
    settings.LANGSMITH_TRACING
).lower()
os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT


def target(inputs: dict[str, Any]) -> dict[str, Any]:
    """
    Run one isolated evaluation through the production workflow.
    """

    workflow = get_agentic_workflow()

    session_id = f"evaluation-{uuid4()}"

    result = workflow.invoke(
        question=inputs["question"],
        session_id=session_id,
    )

    return {
        "answer": result.answer,
        "sources": result.sources,
    }


def run_evaluation() -> None:
    client = Client()

    client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[
            evaluate_answer_correctness,
            evaluate_source_match,
            evaluate_unanswerable_behavior,
        ],
        experiment_prefix="enterprise-ai-rag",
        description=(
            "Evaluation of the Enterprise AI Knowledge Assistant "
            "LangGraph RAG workflow."
        ),
    )


if __name__ == "__main__":
    run_evaluation()