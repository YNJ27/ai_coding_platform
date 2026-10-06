from types import SimpleNamespace

import pytest

from app.ai import llm


def test_chat_model_uses_configured_provider_settings(monkeypatch):
    captured = {}

    class FakeChatGoogleGenerativeAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(llm, "ChatGoogleGenerativeAI", FakeChatGoogleGenerativeAI)
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: SimpleNamespace(
            google_api_key="configured-key",
            google_model="configured-model",
            google_temperature=0.35,
        ),
    )
    llm.get_chat_model.cache_clear()

    llm.get_chat_model()

    assert captured == {
        "model": "configured-model",
        "google_api_key": "configured-key",
        "temperature": 0.35,
    }


def test_chat_model_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: SimpleNamespace(
            google_api_key=None,
            google_model="configured-model",
            google_temperature=0.35,
        ),
    )
    llm.get_chat_model.cache_clear()

    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        llm.get_chat_model()
