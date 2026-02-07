from __future__ import annotations

import os
import time
import logging
from typing import Optional

from google.api_core import exceptions as google_exceptions
from google.cloud import texttospeech

from app.core.cost_tracker import calculate_google_tts_cost

logger = logging.getLogger(__name__)


class GoogleTTSProvider:
    """Google Cloud Text-to-Speech provider."""

    def __init__(self) -> None:

        try:
            self._client = texttospeech.TextToSpeechClient()
        except Exception as exc:  # pragma: no cover
            raise ValueError(
                "Google Text-to-Speechクライアントの初期化に失敗しました"
            ) from exc

    async def synthesize_speech(
        self,
        text: str,
        language_code: Optional[str] = None,
        voice_name: Optional[str] = None,
        speaking_rate: Optional[float] = None,
    ) -> bytes:
        """Synthesize speech audio bytes from input text."""
        if not text or not text.strip():
            raise ValueError("読み上げるテキストが空です")

        # 長文はコスト・時間の観点から制限（MVPではシンプルにカット）
        max_chars = 500
        normalized = text.strip()
        if len(normalized) > max_chars:
            normalized = normalized[:max_chars] + "..."

        input_text = texttospeech.SynthesisInput(text=normalized)

        lang = language_code or "en-US"
        voice_params: dict = {"language_code": lang}
        # voice_nameが指定されていない場合はデフォルトで女性の声を使用する。
        if voice_name:
            voice_params["name"] = voice_name
        else:
            voice_params["ssml_gender"] = texttospeech.SsmlVoiceGender.FEMALE
        voice = texttospeech.VoiceSelectionParams(
            **voice_params,
        )

        rate = speaking_rate or 1.0

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=rate,
        )

        start_time = time.perf_counter()

        try:
            response = self._client.synthesize_speech(
                input=input_text,
                voice=voice,
                audio_config=audio_config,
            )
        except google_exceptions.GoogleAPICallError as exc:
            logger.error(f"Google Text-to-Speech APIの呼び出しに失敗しました")
            raise ValueError(
                f"error message: {str(exc.message)}"
            ) from exc
        except google_exceptions.RetryError as exc:
            logger.error(f"Google Text-to-Speech APIの再試行が上限に達しました")
            raise ValueError(
                f"error message: {str(exc.message)}"
            ) from exc
        except Exception as exc:  # pragma: no cover
            raise ValueError(f"error message: {str(exc.message)}") from exc

        latency_ms = int((time.perf_counter() - start_time) * 1000)

        # 料金計算（使用した文字数）
        calculate_google_tts_cost(
            character_count=len(normalized),
            latency_ms=latency_ms,
        )

        return response.audio_content

    async def __aenter__(self) -> "GoogleTTSProvider":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        close_method = getattr(self._client, "close", None)
        if callable(close_method):
            close_method()
