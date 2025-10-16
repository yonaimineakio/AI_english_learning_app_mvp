from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.deps import get_current_user
from app.services.ai.google_speech_provider import (
    GoogleSpeechProvider,
    TranscriptionResponse,
)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音声ファイルが空です"
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Audio transcription failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="音声認識処理中にエラーが発生しました"
        )


@router.get("/health")
async def health_check() -> JSONResponse:
    """音声処理サービスのヘルスチェック"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "audio_transcription",
            "supported_formats": ["wav", "flac", "mp3", "m4a", "ogg", "opus", "webm"],
            "max_file_size": "60MB"
        }
    )
