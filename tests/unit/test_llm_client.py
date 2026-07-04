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
