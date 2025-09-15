from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.core.deps import get_db, get_current_user
from models.database.models import User
from models.schemas.schemas import (
    SessionCreate, SessionStartResponse, TurnResponse, SessionEndResponse,
    ErrorResponse
)
from app.services.conversation.session_service import SessionService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start", response_model=SessionStartResponse)
async def start_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """セッションを開始する"""
    try:
        session_service = SessionService(db)
        result = session_service.start_session(current_user.id, session_data)
        
        logger.info(f"Session started for user {current_user.id}")
        return result
        
    except ValueError as e:
        logger.warning(f"Session start failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in session start: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start session"
        )


@router.post("/{session_id}/turn", response_model=TurnResponse)
async def process_turn(
    session_id: int,
    user_input: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """セッションのターンを処理する"""
    try:
        session_service = SessionService(db)
        result = session_service.process_turn(session_id, user_input, current_user.id)
        
        logger.info(f"Turn processed for session {session_id}")
        return result
        
    except ValueError as e:
        logger.warning(f"Turn processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in turn processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process turn"
        )


@router.post("/{session_id}/extend")
async def extend_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """セッションを延長する（+3ラウンド）"""
    try:
        session_service = SessionService(db)
        result = session_service.extend_session(session_id, current_user.id)
        
        logger.info(f"Session {session_id} extended")
        return result
        
    except ValueError as e:
        logger.warning(f"Session extension failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in session extension: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extend session"
        )


@router.post("/{session_id}/end", response_model=SessionEndResponse)
async def end_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """セッションを終了する"""
    try:
        session_service = SessionService(db)
        result = session_service.end_session(session_id, current_user.id)
        
        logger.info(f"Session {session_id} ended")
        return result
        
    except ValueError as e:
        logger.warning(f"Session end failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in session end: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end session"
        )


@router.get("/{session_id}/status")
async def get_session_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """セッションの状態を取得する"""
    try:
        from models.database.models import Session as SessionModel
        
        session = db.query(SessionModel).filter(
            SessionModel.id == session_id,
            SessionModel.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "session_id": session.id,
            "scenario_id": session.scenario_id,
            "round_target": session.round_target,
            "completed_rounds": session.completed_rounds,
            "difficulty": session.difficulty,
            "mode": session.mode,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "is_active": session.ended_at is None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in session status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session status"
        )
