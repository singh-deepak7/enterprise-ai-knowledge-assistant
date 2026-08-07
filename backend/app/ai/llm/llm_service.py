"""
Service responsible for interacting with the language model.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LLMResponse:
    """
    Structured response returned by the LLM service.
    """

    answer: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str | None
    latency_ms: float


class LLMService:
    """
    Service responsible for interacting with the language model.
    """

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=settings.CHAT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:
        """
        Generate a response from the language model.
        """

        logger.info("Generating LLM response.")

        start = time.perf_counter()

        response = self._llm.invoke(
            [
                HumanMessage(content=prompt),
            ]
        )

        latency_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        usage = getattr(response, "usage_metadata", {}) or {}
        metadata = getattr(response, "response_metadata", {}) or {}

        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        finish_reason = metadata.get("finish_reason")

        logger.info(
            (
                "LLM response generated "
                "(model=%s latency=%.2fms total_tokens=%d)"
            ),
            settings.CHAT_MODEL,
            latency_ms,
            total_tokens,
        )

        return LLMResponse(
            answer=response.content,
            provider="OpenAI",
            model=settings.CHAT_MODEL,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            finish_reason=finish_reason,
            latency_ms=latency_ms,
        )