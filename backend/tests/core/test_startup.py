from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.startup import validate_startup


def test_validate_startup_success(
    tmp_path: Path,
) -> None:
    with patch(
        "app.core.startup.settings.OPENAI_API_KEY",
        "key",
    ), patch(
        "app.core.startup.settings.CHAT_MODEL",
        "gpt-4.1-mini",
    ), patch(
        "app.core.startup.settings.UPLOAD_DIR",
        str(tmp_path / "uploads"),
    ), patch(
        "app.core.startup.settings.CHROMA_DB_DIR",
        str(tmp_path / "chroma"),
    ):
        validate_startup()

        assert (tmp_path / "uploads").exists()
        assert (tmp_path / "chroma").exists()


def test_validate_startup_missing_api_key() -> None:
    with patch(
        "app.core.startup.settings.OPENAI_API_KEY",
        "",
    ):
        with pytest.raises(
            RuntimeError,
            match="OPENAI_API_KEY",
        ):
            validate_startup()


def test_validate_startup_missing_model() -> None:
    with patch(
        "app.core.startup.settings.OPENAI_API_KEY",
        "key",
    ), patch(
        "app.core.startup.settings.CHAT_MODEL",
        "",
    ):
        with pytest.raises(
            RuntimeError,
            match="CHAT_MODEL",
        ):
            validate_startup()