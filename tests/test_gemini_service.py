"""Tests for the Gemini API service without network access."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors

from app.config.settings import Settings
from app.services.gemini_service import GeminiService, GeminiServiceError


def test_service_initializes_gemini_client() -> None:
    settings = Settings(api_key="test-key")

    with patch("app.services.gemini_service.genai.Client") as gemini_client:
        service = GeminiService(settings)

    gemini_client.assert_called_once_with(api_key="test-key")
    assert service is not None


def test_generate_answer_returns_response_text_and_sends_history() -> None:
    settings = Settings(api_key="test-key", model="test-model", temperature=0.5)
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(text="  Hello!  ")
    service = GeminiService(settings, client=client)

    answer = service.generate_answer(
        [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello."},
            {"role": "user", "content": "Follow-up"},
        ]
    )

    assert answer == "Hello!"
    call = client.models.generate_content.call_args.kwargs
    assert call["model"] == "test-model"
    assert call["config"].temperature == 0.5
    assert call["config"].system_instruction
    assert [(item.role, item.parts[0].text) for item in call["contents"]] == [
        ("user", "Hi"),
        ("model", "Hello."),
        ("user", "Follow-up"),
    ]


def test_generate_answer_hides_api_error_details() -> None:
    client = MagicMock()
    client.models.generate_content.side_effect = errors.APIError(
        401, {"message": "test-key must not appear"}
    )
    service = GeminiService(Settings(api_key="test-key"), client=client)

    with pytest.raises(GeminiServiceError) as error:
        service.generate_answer([{"role": "user", "content": "Hi"}])

    assert "test-key" not in str(error.value)
    assert "must not appear" not in str(error.value)
    assert "rejected the API key" in str(error.value)


def test_generate_answer_explains_quota_errors_without_provider_details() -> None:
    client = MagicMock()
    client.models.generate_content.side_effect = errors.APIError(
        429, {"message": "private provider response"}
    )
    service = GeminiService(Settings(api_key="test-key"), client=client)

    with pytest.raises(GeminiServiceError) as error:
        service.generate_answer([{"role": "user", "content": "Hi"}])

    assert "quota or rate limit" in str(error.value)
    assert "private provider response" not in str(error.value)


def test_generate_answer_rejects_empty_response_text() -> None:
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(text=" ")
    service = GeminiService(Settings(api_key="test-key"), client=client)

    with pytest.raises(GeminiServiceError):
        service.generate_answer([{"role": "user", "content": "Hi"}])
