from __future__ import annotations

from typing import Any

from langchain_openai import ChatOpenAI

from app.core.config import settings


def evaluate_source_match(
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any],
) -> dict[str, Any]:
    expected_source = reference_outputs.get(
        "expected_source_contains"
    )

    sources = outputs.get("sources", [])

    if expected_source is None:
        return {
            "key": "source_match",
            "score": 1.0 if not sources else 0.0,
        }

    matched = any(
        expected_source.lower()
        in str(source.get("source", "")).lower()
        for source in sources
    )

    return {
        "key": "source_match",
        "score": 1.0 if matched else 0.0,
    }


def evaluate_unanswerable_behavior(
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any],
) -> dict[str, Any]:
    category = reference_outputs.get("category")

    if category != "unanswerable":
        return {
            "key": "safe_refusal",
            "score": 1.0,
        }

    answer = str(outputs.get("answer", "")).lower()

    refusal_phrases = (
        "not enough information",
        "insufficient information",
        "does not contain",
        "do not contain",
        "cannot determine",
        "can't determine",
        "unable to determine",
    )

    refused = any(
        phrase in answer
        for phrase in refusal_phrases
    )

    return {
        "key": "safe_refusal",
        "score": 1.0 if refused else 0.0,
    }


def evaluate_answer_correctness(
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any],
) -> dict[str, Any]:
    question = inputs["question"]
    actual_answer = outputs.get("answer", "")
    expected_answer = reference_outputs.get(
        "expected_answer",
        "",
    )

    llm = ChatOpenAI(
        model=settings.CHAT_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )

    prompt = f"""
You are evaluating the correctness of an AI answer.

Question:
{question}

Reference answer:
{expected_answer}

AI answer:
{actual_answer}

Determine whether the AI answer is factually consistent with the
reference answer.

Return only one number:

1 = correct
0 = incorrect
"""

    response = llm.invoke(prompt)

    text = str(response.content).strip()

    score = 1.0 if text.startswith("1") else 0.0

    return {
        "key": "answer_correctness",
        "score": score,
    }