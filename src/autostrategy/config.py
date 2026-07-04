"""Configuration management for autostrategy.

Settings are stored in ~/.autostrategy/settings.yaml.
API keys should be stored via keyring or environment variables, not in this file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from autostrategy import __version__


DEFAULT_PROVIDER: Literal[
    "openai", "deepseek", "kimi", "qwen", "zai", "minimax", "gemini", "local"
] = "openai"


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = DEFAULT_PROVIDER
    model: str = "gpt-4o-mini"
    base_url: str | None = None
    api_key_env: str = "AUTOSTRATEGY_LLM_API_KEY"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class Settings(BaseModel):
    """Top-level application settings."""

    version: str = __version__
    llm: LLMConfig = Field(default_factory=LLMConfig)
    default_market: str = "A股"
    data_cache_dir: str | None = None


def get_settings_dir() -> Path:
    """Return the user-level settings directory."""
    return Path.home() / ".autostrategy"


def get_default_settings_path() -> Path:
    """Return the default settings file path."""
    return get_settings_dir() / "settings.yaml"


def save_settings(settings: Settings, path: Path | None = None) -> None:
    """Save settings to YAML file."""
    target = path or get_default_settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        yaml.safe_dump(settings.model_dump(), f, allow_unicode=True, sort_keys=False)


def load_settings(path: Path | None = None) -> Settings:
    """Load settings from YAML file, returning defaults if missing."""
    target = path or get_default_settings_path()
    if not target.exists():
        return Settings()
    with open(target, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Settings(**data)


def init_settings() -> Settings:
    """Initialize settings directory and return current settings."""
    settings = load_settings()
    save_settings(settings)
    return settings
