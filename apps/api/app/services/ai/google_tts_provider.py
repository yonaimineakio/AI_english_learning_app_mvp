from __future__ import annotations

import os
import time
from typing import Optional

from google.api_core import exceptions as google_exceptions
from google.cloud import texttospeech

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.cost_tracker import calculate_google_tts_cost

logger = get_logger(__name__)


class GoogleTTSProvider:
    """Google Cloud Text-to-Speech provider."""

    def __init__(self) -> None:
        credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS or os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )

        if not credentials_path:
            raise ValueError("Google Cloud認証情報が設定されていません")

        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ.setdefault(
                "GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS
            )

        try:
            self._client = texttospeech.TextToSpeechClient()
        except Exception as exc:  # pragma: no cover
            raise ValueError("Google Text-to-Speechクライアントの初期化に失敗しました") from exc

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
            normalized = normalized[: max_chars] + "..."

        input_text = texttospeech.SynthesisInput(text=normalized)

        lang = language_code or "en-US"
        voice_params: dict = {"language_code": lang}
        if voice_name:
            voice_params["name"] = voice_name

        voice = texttospeech.VoiceSelectionParams(
            **voice_params,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
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
            raise ValueError("Google Text-to-Speech APIの呼び出しに失敗しました") from exc
        except google_exceptions.RetryError as exc:
            raise ValueError("Google Text-to-Speech APIの再試行が上限に達しました") from exc
        except Exception as exc:  # pragma: no cover
            raise ValueError("音声合成中に予期せぬエラーが発生しました") from exc

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


