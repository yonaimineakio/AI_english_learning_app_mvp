from __future__ import annotations

import asyncio
import io
import os
import wave
from typing import List, Optional

from google.api_core import exceptions as google_exceptions
from google.cloud import speech
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.cost_tracker import calculate_google_stt_cost

logger = get_logger(__name__)


class TranscriptionAlternative(BaseModel):
    text: str
    confidence: Optional[float] = None


class TranscriptionResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    duration: Optional[float] = None
    alternatives: List[TranscriptionAlternative] = Field(default_factory=list)


class GoogleSpeechProvider:
    """Google Cloud Speech-to-Text provider."""

    _MAX_FILE_SIZE_BYTES = 60 * 1024 * 1024  # 60MB
    _MIN_FILE_SIZE_BYTES = 1 * 1024  # 1KB
    _ALLOWED_EXTENSIONS = {
        ".wav",
        ".flac",
        ".mp3",
        ".m4a",
        ".ogg",
        ".opus",
        ".webm",
    }

    def __init__(self) -> None:
        # credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS or os.environ.get(
        #     "GOOGLE_APPLICATION_CREDENTIALS"
        # )

        # if not credentials_path:
        #     raise ValueError("Google Cloud認証情報が設定されていません")

        # if settings.GOOGLE_APPLICATION_CREDENTIALS:
        #     os.environ.setdefault(
        #         "GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS
        #     )

        try:
            self._client = speech.SpeechClient()
        except Exception as exc:  # pragma: no cover
            raise ValueError("Google Speech-to-Textクライアントの初期化に失敗しました") from exc

    async def transcribe_audio(
        self,
        audio_file: bytes,
        filename: str,
        language: Optional[str] = None,
        max_alternatives: int = 3,
    ) -> TranscriptionResponse:
        """Transcribe audio bytes via Google Cloud Speech-to-Text."""

        self._validate_audio_file(filename, audio_file)

        encoding = self._detect_encoding(filename)
        language_code = language or "en-US"

        config_kwargs = {
            "language_code": language_code,
            "alternative_language_codes": ["en-GB", "en-AU"],
            "enable_automatic_punctuation": True,
            "enable_word_time_offsets": True,
            "max_alternatives": max(1, max_alternatives),
            "model": "latest_long",
        }

        if encoding != speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED:
            config_kwargs["encoding"] = encoding

        sample_rate = self._guess_sample_rate_hz(audio_file, encoding)
        if sample_rate:
            config_kwargs["sample_rate_hertz"] = sample_rate

        config = speech.RecognitionConfig(**config_kwargs)

        audio = speech.RecognitionAudio(content=audio_file)

        async def _recognize() -> speech.RecognizeResponse:
            return await asyncio.to_thread(self._client.recognize, config=config, audio=audio)

        start_time = asyncio.get_running_loop().time()

        try:
            response = await _recognize()
        except google_exceptions.Forbidden as exc:
            raise ValueError("Google Speech-to-Text APIの権限が不足しています") from exc
        except google_exceptions.InvalidArgument as exc:
            raise ValueError("音声ファイルの形式がサポートされていません") from exc
        except google_exceptions.ResourceExhausted as exc:
            raise ValueError("Google Speech-to-Textの利用制限に達しました") from exc
        except google_exceptions.GoogleAPICallError as exc:
            raise ValueError("音声認識処理に失敗しました") from exc
        except Exception as exc:  # pragma: no cover
            raise ValueError("音声認識処理中に予期せぬエラーが発生しました") from exc

        duration = asyncio.get_running_loop().time() - start_time
        latency_ms = int(duration * 1000)

        # 音声時間を推定（WAVの場合は正確に計算、それ以外はファイルサイズから推定）
        audio_duration_seconds = self._estimate_audio_duration(audio_file, encoding)
        
        # 料金計算
        calculate_google_stt_cost(
            audio_duration_seconds=audio_duration_seconds,
            latency_ms=latency_ms,
        )

        segments: List[str] = []
        alternatives: List[TranscriptionAlternative] = []
        confidences: List[float] = []
        detected_language: Optional[str] = None

        for result in response.results:
            if detected_language is None:
                detected_language = getattr(result, "language_code", None)

            if not result.alternatives:
                continue

            primary = result.alternatives[0]
            segments.append(primary.transcript.strip())
            if primary.confidence:
                confidences.append(primary.confidence)

            for alt in result.alternatives[1:]:
                alternatives.append(
                    TranscriptionAlternative(
                        text=alt.transcript.strip(),
                        confidence=alt.confidence if alt.confidence else None,
                    )
                )

        combined_text = " ".join(segment for segment in segments if segment).strip()
        confidence = sum(confidences) / len(confidences) if confidences else None

        return TranscriptionResponse(
            text=combined_text,
            confidence=confidence,
            language=detected_language or language_code,
            duration=duration,
            alternatives=alternatives,
        )

    def _validate_audio_file(self, filename: str, audio_file: bytes) -> None:
        if len(audio_file) < self._MIN_FILE_SIZE_BYTES:
            raise ValueError("音声ファイルが小さすぎます")

        if len(audio_file) > self._MAX_FILE_SIZE_BYTES:
            raise ValueError("音声ファイルが大きすぎます（最大60MB）")

        extension = self._extract_extension(filename)
        if extension not in self._ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ext.strip(".") for ext in self._ALLOWED_EXTENSIONS))
            raise ValueError(f"サポートされていないファイル形式です。対応形式: {allowed}")

    def _detect_encoding(self, filename: str) -> speech.RecognitionConfig.AudioEncoding:
        extension = self._extract_extension(filename)

        mapping = {
            ".wav": speech.RecognitionConfig.AudioEncoding.LINEAR16,
            ".flac": speech.RecognitionConfig.AudioEncoding.FLAC,
            ".mp3": speech.RecognitionConfig.AudioEncoding.MP3,
            ".ogg": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            ".opus": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            ".webm": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        }

        return mapping.get(extension, speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED)

    def _extract_extension(self, filename: str) -> str:
        if "." not in filename:
            return ""
        return f".{filename.lower().rsplit('.', 1)[-1]}"

    def _guess_sample_rate_hz(
        self,
        audio_file: bytes,
        encoding: speech.RecognitionConfig.AudioEncoding,
    ) -> Optional[int]:
        if encoding != speech.RecognitionConfig.AudioEncoding.LINEAR16:
            return None

        try:
            with wave.open(io.BytesIO(audio_file)) as wav_file:
                return wav_file.getframerate()
        except Exception:
            return None

    def _estimate_audio_duration(
        self,
        audio_file: bytes,
        encoding: speech.RecognitionConfig.AudioEncoding,
    ) -> float:
        """音声ファイルの長さを推定する（秒）"""
        # WAVファイルの場合は正確に計算
        if encoding == speech.RecognitionConfig.AudioEncoding.LINEAR16:
            try:
                with wave.open(io.BytesIO(audio_file)) as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    if rate > 0:
                        return frames / rate
            except Exception:
                pass
        
        # その他の形式はファイルサイズから概算（平均ビットレート128kbps想定）
        # 128kbps = 16KB/sec
        estimated_bitrate_kbps = 128
        file_size_kb = len(audio_file) / 1024
        return file_size_kb / (estimated_bitrate_kbps / 8)

    async def __aenter__(self) -> "GoogleSpeechProvider":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        close_method = getattr(self._client, "close", None)
        if callable(close_method):
            await asyncio.to_thread(close_method)
            return

        transport_close = getattr(getattr(self._client, "transport", None), "close", None)
        if callable(transport_close):
            await asyncio.to_thread(transport_close)

