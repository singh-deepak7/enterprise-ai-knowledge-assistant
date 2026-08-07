from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from openai import APIConnectionError

from app.ai.llm.llm_service import LLMResponse, LLMService


class FakeResponse:
    """
    Fake AIMessage returned by LangChain.
    """

    def __init__(self) -> None:
        self.content = "Coverage answer"

        self.usage_metadata = {
            "input_tokens": 15,
            "output_tokens": 8,
            "total_tokens": 23,
        }

        self.response_metadata = {
            "finish_reason": "stop",
        }


def create_service() -> tuple[LLMService, Mock]:
    """
    Create an LLMService backed by a mocked ChatOpenAI.
    """

    fake_llm = Mock()

    service = LLMService(
        llm=fake_llm,
    )

    return service, fake_llm


def test_generate_success() -> None:
    """
    Successful invocation returns a populated LLMResponse.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.return_value = FakeResponse()

    result = service.generate("Prompt")

    assert isinstance(result, LLMResponse)

    assert result.answer == "Coverage answer"
    assert result.provider == "OpenAI"
    assert result.model
    assert result.prompt_tokens == 15
    assert result.completion_tokens == 8
    assert result.total_tokens == 23
    assert result.finish_reason == "stop"
    assert result.retry_count == 0
    assert result.latency_ms >= 0

    fake_llm.invoke.assert_called_once()


@patch("app.ai.llm.llm_service.time.sleep")
def test_generate_retries_then_success(
    mock_sleep: Mock,
) -> None:
    """
    Transient failures should be retried.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.side_effect = [
        APIConnectionError(
            message="network",
            request=Mock(),
        ),
        FakeResponse(),
    ]

    result = service.generate("Prompt")

    assert result.answer == "Coverage answer"
    assert result.retry_count == 1

    assert fake_llm.invoke.call_count == 2

    mock_sleep.assert_called_once_with(1)


@patch("app.ai.llm.llm_service.time.sleep")
def test_generate_exhausts_retries(
    mock_sleep: Mock,
) -> None:
    """
    Retries should stop after MAX_RETRIES.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.side_effect = APIConnectionError(
        message="network",
        request=Mock(),
    )

    with pytest.raises(APIConnectionError):
        service.generate("Prompt")

    assert (
        fake_llm.invoke.call_count
        == service.MAX_RETRIES + 1
    )

    assert mock_sleep.call_count == service.MAX_RETRIES


def test_generate_non_retryable_exception() -> None:
    """
    Non-retryable exceptions should immediately propagate.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.side_effect = ValueError(
        "Bad prompt"
    )

    with pytest.raises(ValueError):
        service.generate("Prompt")

    assert fake_llm.invoke.call_count == 1


def test_generate_returns_latency() -> None:
    """
    Latency should always be recorded.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.return_value = FakeResponse()

    result = service.generate("Prompt")

    assert result.latency_ms >= 0


def test_generate_returns_provider() -> None:
    """
    Provider metadata should be populated.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.return_value = FakeResponse()

    result = service.generate("Prompt")

    assert result.provider == "OpenAI"


def test_generate_returns_finish_reason() -> None:
    """
    Finish reason should be preserved.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.return_value = FakeResponse()

    result = service.generate("Prompt")

    assert result.finish_reason == "stop"


def test_generate_returns_model_name() -> None:
    """
    Model name should be populated.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.return_value = FakeResponse()

    result = service.generate("Prompt")

    assert result.model is not None


def test_generate_returns_token_usage() -> None:
    """
    Token usage should be extracted from the response.
    """

    service, fake_llm = create_service()

    fake_llm.invoke.return_value = FakeResponse()

    result = service.generate("Prompt")

    assert result.prompt_tokens == 15
    assert result.completion_tokens == 8
    assert result.total_tokens == 23