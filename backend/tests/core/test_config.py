from app.core.config import settings


def test_settings_loaded():
    assert settings.APP_NAME is not None
    assert settings.CHAT_MODEL is not None
    assert settings.EMBEDDING_MODEL is not None