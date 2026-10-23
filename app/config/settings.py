"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping

from dotenv import load_dotenv

DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_TEMPERATURE = 0.2


class ConfigurationError(ValueError):
    """Raised when required or invalid application configuration is found."""


@dataclass(frozen=True)
class Settings:
    """Runtime settings used by the application."""

    api_key: str = field(repr=False)
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Load and validate settings from a mapping or the process environment."""
    if environ is None:
        load_dotenv()
        environ = os.environ

    api_key = environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY is missing. Create a .env file and add your Gemini API key."
        )

    model = environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip()
    if not model:
        raise ConfigurationError("GEMINI_MODEL must not be empty.")

    temperature_value = environ.get("TEMPERATURE", str(DEFAULT_TEMPERATURE))
    try:
        temperature = float(temperature_value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError("TEMPERATURE must be a number between 0 and 2.") from exc
    if not 0 <= temperature <= 2:
        raise ConfigurationError("TEMPERATURE must be between 0 and 2.")

    return Settings(api_key=api_key, model=model, temperature=temperature)
