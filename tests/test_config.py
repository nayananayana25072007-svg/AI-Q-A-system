"""Tests for environment-backed settings."""

import pytest

from app.config.settings import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    ConfigurationError,
    load_settings,
)


def test_load_settings_uses_defaults_and_environment_values() -> None:
    settings = load_settings({"GEMINI_API_KEY": "test-key"})

    assert settings.api_key == "test-key"
    assert settings.model == DEFAULT_MODEL
    assert settings.temperature == DEFAULT_TEMPERATURE


def test_load_settings_reads_configurable_values() -> None:
    settings = load_settings(
        {
            "GEMINI_API_KEY": "test-key",
            "GEMINI_MODEL": "test-model",
            "TEMPERATURE": "0.7",
        }
    )

    assert settings.model == "test-model"
    assert settings.temperature == 0.7


@pytest.mark.parametrize(
    "environ",
    [
        {},
        {"GEMINI_API_KEY": "  "},
    ],
)
def test_load_settings_requires_api_key(environ: dict[str, str]) -> None:
    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY is missing"):
        load_settings(environ)


@pytest.mark.parametrize("temperature", ["not-a-number", "-0.1", "2.1"])
def test_load_settings_rejects_invalid_temperature(temperature: str) -> None:
    with pytest.raises(ConfigurationError, match="TEMPERATURE"):
        load_settings({"GEMINI_API_KEY": "test-key", "TEMPERATURE": temperature})
