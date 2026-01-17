import pytest
from unittest.mock import MagicMock, patch

from app.services.ai.google_tts_provider import GoogleTTSProvider


@pytest.mark.asyncio
async def test_synthesize_speech_empty_text_raises() -> None:
    with patch(
        "app.services.ai.google_tts_provider.texttospeech.TextToSpeechClient",
        return_value=MagicMock(),
    ):
        provider = GoogleTTSProvider()

    with pytest.raises(ValueError, match="読み上げるテキストが空です"):
        await provider.synthesize_speech("")


@pytest.mark.asyncio
async def test_synthesize_speech_truncates_and_calls_client() -> None:
    fake_client = MagicMock()
    fake_client.synthesize_speech.return_value = MagicMock(audio_content=b"mp3-bytes")

    with patch(
        "app.services.ai.google_tts_provider.texttospeech.TextToSpeechClient",
        return_value=fake_client,
    ), patch(
        "app.services.ai.google_tts_provider.calculate_google_tts_cost"
    ) as mock_cost:
        provider = GoogleTTSProvider()
        audio = await provider.synthesize_speech("a" * 600, language_code="en-US")

    assert audio == b"mp3-bytes"
    _, kwargs = fake_client.synthesize_speech.call_args
    assert kwargs["input"].text == ("a" * 500 + "...")
    mock_cost.assert_called_once()


@pytest.mark.asyncio
async def test_context_manager_closes_client_when_available() -> None:
    fake_client = MagicMock()
    fake_client.close = MagicMock()

    with patch(
        "app.services.ai.google_tts_provider.texttospeech.TextToSpeechClient",
        return_value=fake_client,
    ):
        async with GoogleTTSProvider() as provider:
            assert provider is not None

    fake_client.close.assert_called_once()
