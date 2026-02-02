import asyncio
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"

class TranscriptionAlternative(BaseModel):
    text: str
    confidence: Optional[float] = None

class TranscriptionResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    duration: Optional[float] = None
    alternatives: List[TranscriptionAlternative] = Field(default_factory=list)


class WhisperProvider:
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            timeout=httpx.Timeout(30.0, connect=5.0, read=30.0),
        )

    async def transcribe_audio(
        self,
        audio_file: bytes,
        filename: str,
        language: Optional[str] = None,
        model: str = "whisper-1",
    ) -> TranscriptionResponse:
        """音声ファイルをテキストに変換"""
        start_time = asyncio.get_event_loop().time()

        try:
            # ファイル形式の検証
            self._validate_audio_file(filename, audio_file)

            # リクエストデータの準備
            files = {"file": (filename, audio_file, self._get_content_type(filename))}
            data = {
                "model": model,
                "response_format": "verbose_json",
            }

            if language:
                data["language"] = language

            response = await self._client.post(WHISPER_API_URL, files=files, data=data)
            response.raise_for_status()

            result = response.json()
            duration = asyncio.get_event_loop().time() - start_time

            return TranscriptionResponse(
                text=result.get("text", ""),
                confidence=result.get("confidence"),
                language=result.get("language"),
                duration=duration,
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Whisper API HTTP error: {e.response.status_code} - {e.response.text}"
            )
            if e.response.status_code == 413:
                raise ValueError("音声ファイルが大きすぎます（25MB以下にしてください）")
            elif e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get("error", {}).get(
                        "message", "音声ファイルの形式が正しくありません"
                    )
                except:
                    error_message = "音声ファイルの形式が正しくありません"
                raise ValueError(error_message)
            elif e.response.status_code == 401:
                raise ValueError("API認証に失敗しました。設定を確認してください。")
            elif e.response.status_code == 429:
                raise ValueError(
                    "APIの利用制限に達しました。しばらく待ってから再試行してください。"
                )
            else:
                raise ValueError(f"音声認識に失敗しました: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("Whisper API timeout")
            raise ValueError(
                "音声認識の処理時間が長すぎます。ファイルサイズを小さくして再試行してください。"
            )
        except httpx.ConnectError:
            logger.error("Whisper API connection error")
            raise ValueError(
                "音声認識サービスに接続できません。ネットワーク接続を確認してください。"
            )
        except Exception as exc:
            logger.exception("Failed to transcribe audio via Whisper: %s", exc)
            raise ValueError(f"音声認識処理中にエラーが発生しました: {str(exc)}")

    def _validate_audio_file(self, filename: str, audio_file: bytes) -> None:
        """音声ファイルの検証"""
        # ファイルサイズチェック（25MB制限）
        max_size = 25 * 1024 * 1024  # 25MB
        if len(audio_file) > max_size:
            raise ValueError(f"音声ファイルが大きすぎます（最大25MB）")

        # ファイル形式チェック
        allowed_extensions = {".mp3", ".wav", ".m4a", ".flac", ".webm", ".mp4"}
        file_ext = filename.lower().split(".")[-1] if "." in filename else ""
        if f".{file_ext}" not in allowed_extensions:
            raise ValueError(
                f"サポートされていないファイル形式です。対応形式: {', '.join(allowed_extensions)}"
            )

        # 最小サイズチェック（空ファイル防止）
        if len(audio_file) < 1024:  # 1KB
            raise ValueError("音声ファイルが小さすぎます")

    def _get_content_type(self, filename: str) -> str:
        """ファイル名からContent-Typeを取得"""
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        content_types = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4",
            "flac": "audio/flac",
            "webm": "audio/webm",
            "mp4": "audio/mp4",
        }
        return content_types.get(ext, "audio/mpeg")

    async def __aenter__(self) -> "WhisperProvider":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._client.aclose()


async def warm_up_whisper() -> None:
    """Whisper APIのウォームアップ（オプション）"""
    if not settings.OPENAI_API_KEY:
        return
    # 実際のウォームアップは音声ファイルが必要なため、ここではスキップ
    logger.info("Whisper provider initialized")
