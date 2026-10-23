"""Google Gemini API integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

from google import genai
from google.genai import errors, types

from app.config.settings import Settings
from app.prompts.qa_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiServiceError(RuntimeError):
    """Raised when an answer cannot be generated safely."""


class GeminiService:
    """Generate answers using Google's Gemini generate-content API."""

    def __init__(self, settings: Settings, client: genai.Client | None = None) -> None:
        self._settings = settings
        self._client = (
            client if client is not None else genai.Client(api_key=settings.api_key)
        )

    def generate_answer(
        self, messages: Sequence[Mapping[str, str]]
    ) -> str:
        """Generate an answer from validated user/assistant conversation messages."""
        conversation: list[types.Content] = []
        for message in messages:
            role = message.get("role")
            content = message.get("content")
            if role not in {"user", "assistant"} or not isinstance(content, str):
                raise ValueError("Messages must contain a user or assistant role and text.")
            conversation.append(
                types.Content(
                    role="model" if role == "assistant" else "user",
                    parts=[types.Part.from_text(text=content)],
                )
            )

        try:
            response = self._client.models.generate_content(
                model=self._settings.model,
                contents=conversation,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=self._settings.temperature,
                ),
            )
        except errors.APIError as exc:
            status_code = getattr(exc, "code", None)
            logger.error("Gemini request failed with HTTP status %s.", status_code)
            if status_code == 429:
                message = (
                    "The Gemini API quota or rate limit has been reached. Check "
                    "your Google AI Studio usage and limits for this model, "
                    "then try again later."
                )
            elif status_code in {401, 403}:
                message = (
                    "Gemini rejected the API key or access to this model. Check "
                    "your Gemini API key and account permissions."
                )
            elif status_code == 404:
                message = (
                    "The configured Gemini model was not found. Check GEMINI_MODEL "
                    "and choose a model available to your account."
                )
            else:
                message = (
                    "The answer could not be generated. Please try again in a moment."
                )
            raise GeminiServiceError(message) from None

        answer = response.text
        if not isinstance(answer, str) or not answer.strip():
            logger.error("Gemini response did not contain answer text.")
            raise GeminiServiceError(
                "The answer could not be generated. Please try again in a moment."
            )
        return answer.strip()
