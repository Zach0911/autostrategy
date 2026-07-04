"""Tests for LLM client."""

from autostrategy.config import LLMConfig
from autostrategy.llm.client import LLMClient


def test_client_initialization():
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    assert client.config == config


def test_resolve_api_key_from_env(monkeypatch):
    monkeypatch.setenv("AUTOSTRATEGY_LLM_API_KEY", "test-key")
    config = LLMConfig(api_key_env="AUTOSTRATEGY_LLM_API_KEY")
    client = LLMClient(config)
    assert client.api_key == "test-key"


def test_resolve_api_key_missing():
    config = LLMConfig(api_key_env="NON_EXISTENT_KEY")
    client = LLMClient(config)
    assert client.api_key is None


def test_chat_without_api_key_raises_helpful_error(monkeypatch):
    monkeypatch.delenv("AUTOSTRATEGY_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = LLMConfig(provider="openai", api_key_env="NON_EXISTENT_KEY")
    client = LLMClient(config)

    try:
        client.chat([])
    except RuntimeError as exc:
        message = str(exc)
        assert "No LLM API key found" in message
        assert "AUTOSTRATEGY_LLM_API_KEY" in message
    else:
        raise AssertionError("Expected RuntimeError")
