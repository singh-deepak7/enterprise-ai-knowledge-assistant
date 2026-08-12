"""
Service responsible for interacting with the language model.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)

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
    retry_count: int


class LLMService:
    """
    Service responsible for interacting with the language model.
    """

    MAX_RETRIES = 3
    INITIAL_BACKOFF_SECONDS = 1

    def __init__(
        self,
        llm: ChatOpenAI | None = None,
    ) -> None:
        self._llm = llm or ChatOpenAI(
            model=settings.CHAT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:
        """
        Generate a complete response from the language model with
        automatic retry for transient failures.
        """

        start = time.perf_counter()
        retry_count = 0

        while True:
            try:
                logger.info(
                    "Generating LLM response (attempt %d).",
                    retry_count + 1,
                )

                response = self._llm.invoke(
                    [
                        HumanMessage(content=prompt),
                    ]
                )

                latency_ms = round(
                    (time.perf_counter() - start) * 1000,
                    2,
                )

                usage = (
                    getattr(response, "usage_metadata", {})
                    or {}
                )

                metadata = (
                    getattr(response, "response_metadata", {})
                    or {}
                )

                prompt_tokens = usage.get(
                    "input_tokens",
                    0,
                )

                completion_tokens = usage.get(
                    "output_tokens",
                    0,
                )

                total_tokens = usage.get(
                    "total_tokens",
                    0,
                )

                finish_reason = metadata.get(
                    "finish_reason"
                )

                logger.info(
                    (
                        "LLM response generated "
                        "(model=%s latency=%.2fms "
                        "tokens=%d retries=%d)"
                    ),
                    settings.CHAT_MODEL,
                    latency_ms,
                    total_tokens,
                    retry_count,
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
                    retry_count=retry_count,
                )

            except (
                APIConnectionError,
                APITimeoutError,
                RateLimitError,
                InternalServerError,
            ):
                retry_count += 1

                if retry_count > self.MAX_RETRIES:
                    logger.exception(
                        "LLM failed after %d retries.",
                        self.MAX_RETRIES,
                    )
                    raise

                backoff = (
                    self.INITIAL_BACKOFF_SECONDS
                    * (2 ** (retry_count - 1))
                )

                logger.warning(
                    (
                        "Transient LLM failure. "
                        "Retry %d/%d in %.1f second(s)."
                    ),
                    retry_count,
                    self.MAX_RETRIES,
                    backoff,
                )

                time.sleep(backoff)

    def stream(
        self,
        prompt: str,
    ) -> Iterator[str]:
        """
        Stream text chunks from the language model.

        Yields:
            Individual text chunks as they are generated.
        """

        logger.info(
            "Starting streaming LLM response."
        )

        start = time.perf_counter()

        try:
            for chunk in self._llm.stream(
                [
                    HumanMessage(content=prompt),
                ]
            ):
                content = chunk.content

                if isinstance(content, str) and content:
                    yield content

            latency_ms = round(
                (time.perf_counter() - start) * 1000,
                2,
            )

            logger.info(
                (
                    "Streaming LLM response completed "
                    "(model=%s latency=%.2fms)"
                ),
                settings.CHAT_MODEL,
                latency_ms,
            )

        except Exception:
            logger.exception(
                "Streaming LLM response failed."
            )
            raise