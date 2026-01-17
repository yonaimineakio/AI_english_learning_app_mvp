from __future__ import annotations

import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.deps import get_current_user
from app.services.ai.google_speech_provider import (
    GoogleSpeechProvider,
    TranscriptionResponse,
)
from app.services.ai.google_tts_provider import GoogleTTSProvider
from models.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="音声ファイル"),
    language: Optional[str] = Form(None, description="音声の言語コード（例: ja, en）"),
    current_user: User = Depends(get_current_user),
) -> TranscriptionResponse:
    """
    音声ファイルをテキストに変換する

    Args:
        audio_file: 音声ファイル（WAV, FLAC, MP3, M4A, OGG, OPUS, WEBM対応）
        language: 音声の言語コード（オプション）
        current_user: 認証されたユーザー

    Returns:
        TranscriptionResponse: 変換結果
    """
    try:
        # ファイルの読み込み
        audio_content = await audio_file.read()

        if not audio_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="音声ファイルが空です"
            )

        # Google Speech-to-Textで音声認識
        async with GoogleSpeechProvider() as speech_provider:
            result = await speech_provider.transcribe_audio(
                audio_file=audio_content,
                filename=audio_file.filename or "audio.webm",
                language=language,
            )

        logger.info(
            f"Audio transcription completed for user {current_user.id}: "
            f"duration={result.duration:.2f}s, text_length={len(result.text)}"
        )

        return result

    except ValueError as e:
        logger.warning(f"Audio transcription validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Audio transcription failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="音声認識処理中にエラーが発生しました",
        )


class TTSRequest(BaseModel):
    text: str
    voice_profile: Optional[str] = None


@router.post("/tts")
async def text_to_speech(
    payload: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """
    テキストを音声（MP3）に変換して返す。
    """
    text = payload.text or ""
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="text は必須です",
        )

    # 長すぎるテキストは制限
    if len(text) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="テキストが長すぎます（最大2000文字）",
        )

    language_code = settings.GOOGLE_TTS_LANGUAGE
    voice_name: Optional[str] = None
    speaking_rate = settings.GOOGLE_TTS_SPEAKING_RATE

    # voice_profile に応じて将来的に切り替え可能（MVPでは1パターン）
    if payload.voice_profile == "placement_listening":
        speaking_rate = 0.9

    try:
        async with GoogleTTSProvider() as tts_provider:
            audio_bytes = await tts_provider.synthesize_speech(
                text=text,
                language_code=language_code,
                voice_name=voice_name,
                speaking_rate=speaking_rate,
            )
    except ValueError as e:
        logger.warning(f"TTS validation/API error for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"TTS synthesis failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="音声合成処理中にエラーが発生しました",
        )

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": 'inline; filename="speech.mp3"',
        },
    )


@router.get("/health")
async def health_check() -> JSONResponse:
    """音声処理サービスのヘルスチェック"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "audio_transcription",
            "supported_formats": ["wav", "flac", "mp3", "m4a", "ogg", "opus", "webm"],
            "max_file_size": "60MB",
        }
    )
