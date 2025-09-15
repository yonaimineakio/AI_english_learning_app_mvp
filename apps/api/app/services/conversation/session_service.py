from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from models.database.models import Session as SessionModel, SessionRound, Scenario, User
from models.schemas.schemas import (
    SessionCreate, SessionStartResponse, TurnResponse, SessionEndResponse,
    SessionRoundCreate, DifficultyLevel, SessionMode
)

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def start_session(self, user_id: int, session_data: SessionCreate) -> SessionStartResponse:
        """セッションを開始する"""
        try:
            # シナリオの存在確認
            scenario = self.db.query(Scenario).filter(
                Scenario.id == session_data.scenario_id,
                Scenario.is_active == True
            ).first()
            
            if not scenario:
                raise ValueError(f"Scenario with id {session_data.scenario_id} not found or inactive")

            # セッション作成
            db_session = SessionModel(
                user_id=user_id,
                scenario_id=session_data.scenario_id,
                round_target=session_data.round_target,
                difficulty=session_data.difficulty,
                mode=session_data.mode,
                started_at=datetime.utcnow()
            )
            
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            
            logger.info(f"Session {db_session.id} started for user {user_id}")
            
            return SessionStartResponse(
                session_id=db_session.id,
                scenario=scenario,
                round_target=db_session.round_target,
                difficulty=db_session.difficulty,
                mode=db_session.mode
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to start session: {str(e)}")
            raise

    def process_turn(self, session_id: int, user_input: str, user_id: int) -> TurnResponse:
        """セッションのターンを処理する"""
        try:
            # セッションの存在確認
            session = self.db.query(SessionModel).filter(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id,
                SessionModel.ended_at.is_(None)  # 終了していないセッション
            ).first()
            
            if not session:
                raise ValueError(f"Active session {session_id} not found for user {user_id}")

            # 現在のラウンド数を取得
            current_round = session.completed_rounds + 1
            
            # ラウンド数上限チェック
            if current_round > session.round_target:
                raise ValueError(f"Session {session_id} has reached maximum rounds ({session.round_target})")

            # AI応答とフィードバック生成（モック実装）
            ai_reply, feedback_short, improved_sentence, tags = self._generate_ai_response(
                user_input, session.difficulty, current_round
            )

            # ラウンド情報を保存
            session_round = SessionRound(
                session_id=session_id,
                round_index=current_round,
                user_input=user_input,
                ai_reply=ai_reply,
                feedback_short=feedback_short,
                improved_sentence=improved_sentence,
                tags=tags,
                score_pronunciation=None,  # 将来実装
                score_grammar=None  # 将来実装
            )
            
            self.db.add(session_round)
            
            # セッションの完了ラウンド数を更新
            session.completed_rounds = current_round
            
            self.db.commit()
            
            logger.info(f"Turn {current_round} processed for session {session_id}")
            
            return TurnResponse(
                round_index=current_round,
                ai_reply=ai_reply,
                feedback_short=feedback_short,
                improved_sentence=improved_sentence,
                tags=tags
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to process turn: {str(e)}")
            raise

    def extend_session(self, session_id: int, user_id: int) -> Dict[str, Any]:
        """セッションを延長する（+3ラウンド）"""
        try:
            session = self.db.query(SessionModel).filter(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id,
                SessionModel.ended_at.is_(None)
            ).first()
            
            if not session:
                raise ValueError(f"Active session {session_id} not found for user {user_id}")

            # 延長回数制限（最大2回まで）
            if hasattr(session, 'extension_count'):
                if session.extension_count >= 2:
                    raise ValueError("Maximum extensions reached (2 times)")
                session.extension_count += 1
            else:
                session.extension_count = 1

            # ラウンド数を+3延長
            session.round_target += 3
            
            self.db.commit()
            
            logger.info(f"Session {session_id} extended by 3 rounds (total: {session.round_target})")
            
            return {
                "session_id": session_id,
                "new_round_target": session.round_target,
                "extension_count": session.extension_count
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to extend session: {str(e)}")
            raise

    def end_session(self, session_id: int, user_id: int) -> SessionEndResponse:
        """セッションを終了し、トップ3フレーズを抽出する"""
        try:
            session = self.db.query(SessionModel).filter(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id,
                SessionModel.ended_at.is_(None)
            ).first()
            
            if not session:
                raise ValueError(f"Active session {session_id} not found for user {user_id}")

            # セッション終了時刻を設定
            session.ended_at = datetime.utcnow()
            
            # トップ3フレーズを抽出（モック実装）
            top_phrases = self._extract_top_phrases(session_id)
            
            # 復習アイテムを作成
            self._create_review_items(user_id, top_phrases)
            
            self.db.commit()
            
            logger.info(f"Session {session_id} ended with {session.completed_rounds} rounds")
            
            return SessionEndResponse(
                session_id=session_id,
                completed_rounds=session.completed_rounds,
                top_phrases=top_phrases
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to end session: {str(e)}")
            raise

    def _generate_ai_response(self, user_input: str, difficulty: DifficultyLevel, round_index: int) -> tuple:
        """AI応答とフィードバックを生成する（モック実装）"""
        # 実際の実装では、OpenAI APIを呼び出して応答を生成
        # 現在はモック実装
        
        difficulty_responses = {
            DifficultyLevel.BEGINNER: {
                "ai_reply": "That's a good start! Let me help you with that.",
                "feedback_short": "Good effort! Try to use more complete sentences.",
                "improved_sentence": "I would like to learn more about this topic."
            },
            DifficultyLevel.INTERMEDIATE: {
                "ai_reply": "I understand your point. Could you elaborate on that?",
                "feedback_short": "Nice expression! Consider using more specific vocabulary.",
                "improved_sentence": "I would appreciate it if you could provide more details about this matter."
            },
            DifficultyLevel.ADVANCED: {
                "ai_reply": "That's an insightful perspective. What are your thoughts on the implications?",
                "feedback_short": "Excellent articulation! You might consider using more nuanced language.",
                "improved_sentence": "I would be interested in exploring the broader implications of this concept."
            }
        }
        
        response = difficulty_responses.get(difficulty, difficulty_responses[DifficultyLevel.INTERMEDIATE])
        
        # ラウンドに応じてタグを生成
        tags = ["conversation", f"round_{round_index}", difficulty.value]
        
        return (
            response["ai_reply"],
            response["feedback_short"],
            response["improved_sentence"],
            tags
        )

    def _extract_top_phrases(self, session_id: int) -> List[Dict[str, Any]]:
        """セッションからトップ3フレーズを抽出する（モック実装）"""
        # 実際の実装では、AIを使用して重要なフレーズを抽出
        # 現在はモック実装
        
        session_rounds = self.db.query(SessionRound).filter(
            SessionRound.session_id == session_id
        ).order_by(SessionRound.created_at.desc()).limit(3).all()
        
        top_phrases = []
        for i, round_data in enumerate(session_rounds, 1):
            top_phrases.append({
                "rank": i,
                "phrase": round_data.improved_sentence,
                "explanation": round_data.feedback_short,
                "round_index": round_data.round_index
            })
        
        return top_phrases

    def _create_review_items(self, user_id: int, top_phrases: List[Dict[str, Any]]):
        """復習アイテムを作成する"""
        from models.database.models import ReviewItem
        
        # 翌日の復習時間を設定
        due_at = datetime.utcnow() + timedelta(days=1)
        
        for phrase_data in top_phrases:
            review_item = ReviewItem(
                user_id=user_id,
                phrase=phrase_data["phrase"],
                explanation=phrase_data["explanation"],
                due_at=due_at
            )
            self.db.add(review_item)
        
        logger.info(f"Created {len(top_phrases)} review items for user {user_id}")
