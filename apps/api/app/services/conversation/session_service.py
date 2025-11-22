from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
import asyncio
import logging
import time

from models.database.models import Session as SessionModel, SessionRound, Scenario, User
from models.schemas.schemas import (
    SessionCreate,
    SessionStartResponse,
    TurnResponse,
    SessionEndResponse,
    SessionRoundCreate,
    DifficultyLevel,
    SessionMode,
    SessionStatusResponse,
    ScenarioCategory,
)

from app.services.ai import generate_conversation_response
from app.services.ai.goal_progress import evaluate_goal_progress

logger = logging.getLogger(__name__)


SCENARIO_GOALS: Dict[int, List[str]] = {
    1: [
        "予約名を伝えてチェックインを開始する",
        "座席の希望（窓側・通路側）を伝える",
        "荷物の預け入れについて確認する",
    ],
    2: [
        "会議の冒頭で自分の意見を述べる",
        "他の参加者の提案に賛成・反対を表明する",
        "次のアクションアイテムを確認する",
    ],
    3: [
        "ウェイターを呼んでメニューを依頼する",
        "おすすめ料理やサイドメニューについて尋ねる",
        "アレルギーや食材の制限を伝える",
    ],
    4: [
        "会議の冒頭で自己紹介とアイスブレイクを行う",
        "自社の提案内容を簡潔に説明する",
        "相手の質問に答えて懸念点を解消する",
    ],
    5: [
        "予約名を伝えてチェックイン手続きを開始する",
        "部屋のアップグレードや追加リクエストを依頼する",
        "ホテルの設備やサービスについて質問する",
    ],
    6: [
        "行きたい旅行先とその理由を説明する",
        "滞在期間と予算の希望を伝える",
        "おすすめのアクティビティや観光地を尋ねる",
    ],
    7: [
        "訪問したい観光地を提案して魅力を説明する",
        "移動手段（電車・バス・タクシー）と所要時間を伝える",
        "相手の興味や好みを聞いて計画を調整する",
    ],
    8: [
        "訪問目的（観光・ビジネス）と滞在期間を答える",
        "滞在先のホテル名と住所を伝える",
        "持ち込み品の申告や追加質問に対応する",
    ],
    9: [
        "行きたい場所と日程の候補を提案する",
        "相手の都合や希望を聞いて調整する",
        "予算とやりたいアクティビティを共有する",
    ],
    10: [
        "いつどこで財布を無くしたかを説明する",
        "財布の色・形・中身（カード・現金）を伝える",
        "遺失物届の手続きについて確認する",
    ],
    11: [
        "商品の不具合や問題点を具体的に説明する",
        "返品・交換・返金のいずれかを依頼する",
        "担当者の提案を確認して対応を決める",
    ],
    12: [
        "おすすめのドリンクや季節限定メニューを尋ねる",
        "店の雰囲気やインテリアについてコメントする",
        "天気や最近の出来事について軽く話す",
    ],
    13: [
        "希望の日時と人数を伝える",
        "座席の種類（前方・中央・後方）と価格を確認する",
        "空席がない場合は別の日時を相談する",
    ],
    14: [
        "天気や公園の雰囲気について話しかける",
        "相手の趣味やこの公園に来る頻度を尋ねる",
        "別れ際に「また会いましょう」と挨拶する",
    ],
    15: [
        "予定変更が必要な理由を簡潔に伝える",
        "代替の日時候補を2〜3つ提案する",
        "相手の都合を確認して謝罪の言葉を添える",
    ],
    16: [
        "会議の目的と所要時間を伝える",
        "複数の候補日時を提示する",
        "参加者全員の都合を確認して日程を確定する",
    ],
    17: [
        "会議の冒頭でアジェンダを提示する",
        "各議題で参加者の意見を引き出す",
        "決定事項とアクションアイテムを確認する",
    ],
    18: [
        "価格・納期・支払い条件について確認する",
        "自社の希望条件と譲歩できる範囲を伝える",
        "相手の提案に対して代替案を提示する",
    ],
    19: [
        "調査の概要（期間・対象・方法）を説明する",
        "主要な数値結果とその変化を伝える",
        "結果から導かれる改善提案を述べる",
    ],
    20: [
        "遅延の事実と原因を正直に説明する",
        "謝罪の言葉と責任の所在を明確にする",
        "新しいスケジュールと再発防止策を提示する",
    ],
    21: [
        "体調不良の症状（熱・頭痛など）を伝える",
        "休みたい日数と復帰予定を説明する",
        "担当業務の引き継ぎ先を相談する",
    ],
}


def get_goals_for_scenario(scenario_id: int) -> List[str]:
    """Return learning goals for a given scenario id (up to 3 goals)."""
    return SCENARIO_GOALS.get(scenario_id, [])


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_str(value):
        return value.value if hasattr(value, "value") else value

    def _get_existing_review_due(self, session: SessionModel, user_id: int):
        from models.database.models import ReviewItem

        if session.ended_at is None:
            return None

        item = (
            self.db.query(ReviewItem)
            .filter(
                ReviewItem.user_id == user_id,
                ReviewItem.due_at.is_not(None)
            )
            .order_by(ReviewItem.due_at.desc())
            .first()
        )

        return item.due_at if item else None

    async def _calculate_goal_progress(self, session: SessionModel) -> tuple[int, int, List[int]]:
        """セッション全体の会話履歴から学習ゴール達成率を判定する。"""
        goals = get_goals_for_scenario(session.scenario_id)
        goals_total: int = len(goals)
        if goals_total == 0:
            return 0, 0, []

        # セッション全体の履歴を取得（時系列順）
        history_rounds = (
            self.db.query(SessionRound)
            .filter(SessionRound.session_id == session.id)
            .order_by(SessionRound.round_index.asc())
            .all()
        )
        history_payload = [
            {
                "round_index": r.round_index,
                "user_input": r.user_input,
                "ai_reply": r.ai_reply,
            }
            for r in history_rounds
        ]

        try:
            new_status = await evaluate_goal_progress(goals, history_payload)
            # evaluate_goal_progress 側で長さ調整は行っているが、念のため再チェック
            if len(new_status) != goals_total:
                if len(new_status) < goals_total:
                    new_status.extend([0] * (goals_total - len(new_status)))
                else:
                    new_status = new_status[:goals_total]
            goals_status = new_status
            goals_achieved = sum(goals_status)
        except Exception as eval_exc:  # noqa: BLE001
            logger.warning("Goal progress evaluation failed: %s", eval_exc)
            goals_status = [0] * goals_total
            goals_achieved = 0

        return goals_total, goals_achieved, goals_status

    def _get_initial_message(self, scenario: Scenario) -> Optional[str]:
        """シナリオIDに応じた初期メッセージを返す（モック実装）。"""
        try:
            scenario_id = scenario.id
        except AttributeError:
            return None

        messages = {
            # 1–5: 既存シナリオ
            1: "Hi, I'm the airline staff. Let's check you in for your flight. Where are you flying today?",
            2: "Hi, thanks for joining the meeting. Could you briefly introduce yourself and your role?",
            3: "Welcome to our restaurant! Are you ready to order, or would you like some recommendations?",
            4: "Thanks for joining this online business call. What would you like to achieve in this negotiation?",
            5: "Welcome to our hotel. Do you have a reservation, or would you like to book a room today?",
            # 6–10: 旅行系シナリオ
            6: "Let’s plan your perfect vacation together. What kind of trip are you dreaming about?",
            7: "You’re showing a foreign friend around Japan today. Where would you like to take them first?",
            8: "You’ve just arrived at immigration. The officer is asking you questions. How will you respond?",
            9: "You’re talking with a friend about your next trip. Where do you want to go and why?",
            10: "You’ve lost your wallet while traveling. How would you explain the situation to the police?",
            # 11–14: 日常会話シナリオ
            11: "You’re calling customer service about a problem. How would you start the conversation?",
            12: "You’re chatting with a barista at a stylish cafe. What would you like to order today?",
            13: "You want to get tickets for a show. How would you ask about available seats?",
            14: "You’re talking with someone in the park. How would you start a light, friendly conversation?",
            # 15–21: ビジネスシナリオ
            15: "You need to reschedule a meeting. How would you politely ask to change the time?",
            16: "You’re setting up a new meeting. Who would you like to invite and what is the purpose?",
            17: "You’re leading a meeting. How would you open the session and share the agenda?",
            18: "You’re negotiating contract terms. What is the most important point you want to discuss first?",
            19: "You’re presenting customer survey results. What key finding would you like to share first?",
            20: "Your project is delayed and you must apologize. How would you explain the situation?",
            21: "You’re calling your manager to say you’re sick. How would you explain your condition and absence?",
        }

        return messages.get(scenario_id)

    def start_session(self, user_id: int, session_data: SessionCreate) -> SessionStartResponse:
        logger.info(f"Starting session for user {user_id} with data: {session_data}")
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
                difficulty=session_data.difficulty.value if hasattr(session_data.difficulty, 'value') else session_data.difficulty,
                mode=session_data.mode.value if hasattr(session_data.mode, 'value') else session_data.mode,
                started_at=datetime.now(timezone.utc)
            )
            
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            
            logger.info(f"Session {db_session.id} started for user {user_id}")
            
            # Scenarioオブジェクトを手動で構築（Enum値を文字列に変換）
            from models.schemas.schemas import Scenario as ScenarioSchema

            scenario_schema = ScenarioSchema(
                id=scenario.id,
                name=scenario.name,
                description=scenario.description,
                category=self._to_str(scenario.category),
                difficulty=self._to_str(scenario.difficulty),
                is_active=scenario.is_active,
                created_at=scenario.created_at
            )

            initial_message = self._get_initial_message(scenario)

            return SessionStartResponse(
                session_id=db_session.id,
                scenario=scenario_schema,
                round_target=db_session.round_target,
                difficulty=self._to_str(db_session.difficulty),
                mode=self._to_str(db_session.mode),
                initial_ai_message=initial_message,
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to start session: {str(e)}")
            raise

    async def process_turn(self, session_id: int, user_input: str, user_id: int) -> TurnResponse:
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

            # AI応答とフィードバック生成
            context_records = (
                self.db.query(SessionRound)
                .filter(SessionRound.session_id == session_id)
                .order_by(SessionRound.round_index.desc())
                .limit(2)
                .all()
            )

            context = [
                {
                    "round_index": record.round_index,
                    "user_input": record.user_input,
                    "ai_reply": record.ai_reply,
                }
                for record in reversed(context_records)
            ]

            start_time = time.perf_counter()
            
            session_difficulty = self._to_str(session.difficulty)
            scenario_category = self._to_str(session.scenario.category)
            scenario_id = session.scenario_id

            conversation_result = await generate_conversation_response(
                user_input=user_input,
                difficulty=session_difficulty,
                scenario_category=scenario_category,
                round_index=current_round,
                context=context,
                scenario_id=scenario_id,
            )
            latency_ms = conversation_result.latency_ms
            if latency_ms is None:
                latency_ms = int((time.perf_counter() - start_time) * 1000)

            # ラウンド情報を保存
            session_round = SessionRound(
                session_id=session_id,
                round_index=current_round,
                user_input=user_input,
                ai_reply=conversation_result.ai_reply,
                feedback_short=conversation_result.feedback_short,
                improved_sentence=conversation_result.improved_sentence,
                tags=conversation_result.tags,
                score_pronunciation=None,  # 将来実装
                score_grammar=None,  # 将来実装
            )
            
            self.db.add(session_round)
            
            # セッションの完了ラウンド数を更新
            session.completed_rounds = current_round
            
            self.db.commit()
            self.db.refresh(session)

            logger.info(f"Turn {current_round} processed for session {session_id}")

            ai_details = getattr(conversation_result, "details", None)

            # 学習ゴール達成率の判定
            goals_total, goals_achieved, goals_status = await self._calculate_goal_progress(session)

            # 終了判定チェック
            session_ended = False
            
            if conversation_result.should_end_session:
                # 自動終了処理を実行
                logger.info(f"Auto-ending session {session_id} due to user's end intent")
                await self.end_session(session_id, user_id)
                session_ended = True

            return TurnResponse(
                round_index=current_round,
                ai_reply={
                    "message": conversation_result.ai_reply,
                    "feedback_short": conversation_result.feedback_short,
                    "improved_sentence": conversation_result.improved_sentence,
                    "tags": conversation_result.tags,
                    "details": ai_details,
                    "scores": getattr(conversation_result, "scores", None),
                },
                feedback_short=conversation_result.feedback_short,
                improved_sentence=conversation_result.improved_sentence,
                tags=conversation_result.tags,
                response_time_ms=latency_ms,
                provider=conversation_result.provider,
                session_status=self._build_session_status(session) if not session_ended else None,
                should_end_session=conversation_result.should_end_session,
                goals_total=goals_total,
                goals_achieved=goals_achieved,
                goals_status=goals_status or None,
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
            self.db.refresh(session)

            logger.info(f"Session {session_id} extended by 3 rounds (total: {session.round_target})")

            return self._build_session_status(session)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to extend session: {str(e)}")
            raise

    async def end_session(self, session_id: int, user_id: int) -> SessionEndResponse:
        """セッションを終了し、トップ3フレーズを抽出する"""
        try:
            session = self.db.query(SessionModel).filter(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id,
            ).first()

            if not session:
                raise ValueError(f"Session {session_id} not found for user {user_id}")

            already_ended = session.ended_at is not None

            if not already_ended:
                # セッション終了時刻を設定
                session.ended_at = datetime.now(timezone.utc)

                # トップ3フレーズを抽出（モック実装）
                top_phrases = self._extract_top_phrases(session_id)

                # 復習アイテムを作成
                next_review_at = self._create_review_items(user_id, top_phrases)

                self.db.commit()
                self.db.refresh(session)

                logger.info(f"Session {session_id} ended with {session.completed_rounds} rounds")
            else:
                # 既に終了している場合は、既存データを返却して冪等性を担保
                top_phrases = self._extract_top_phrases(session_id)
                next_review_at = self._get_existing_review_due(session, user_id)

                logger.info(
                    "Session %s already ended at %s. Returning stored summary.",
                    session_id,
                    session.ended_at,
                )

            # セッション全体の学習ゴール達成率を計算
            goals_total, goals_achieved, goals_status = await self._calculate_goal_progress(session)

            return SessionEndResponse(
                session_id=session_id,
                completed_rounds=session.completed_rounds,
                top_phrases=top_phrases,
                next_review_at=next_review_at,
                scenario_name=session.scenario.name if session.scenario else None,
                difficulty=self._to_str(session.difficulty),
                mode=self._to_str(session.mode),
                goals_total=goals_total,
                goals_achieved=goals_achieved,
                goals_status=goals_status or None,
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

        if not top_phrases:
            return None

        # 翌日の復習時間を設定
        due_at = datetime.now(timezone.utc) + timedelta(days=1)

        for phrase_data in top_phrases:
            review_item = ReviewItem(
                user_id=user_id,
                phrase=phrase_data["phrase"],
                explanation=phrase_data["explanation"],
                due_at=due_at,
            )
            self.db.add(review_item)

        logger.info(f"Created {len(top_phrases)} review items for user {user_id}")
        return due_at

    def _build_session_status(self, session: SessionModel) -> SessionStatusResponse:
        scenario_name = session.scenario.name if session.scenario else None

        def _to_str(value):
            return value.value if hasattr(value, "value") else value

        difficulty_label = _to_str(session.difficulty) if session.difficulty else None
        mode_label = _to_str(session.mode) if session.mode else None
        extension_offered = session.completed_rounds >= session.round_target
        can_extend = extension_offered and session.extension_count < 2 and session.ended_at is None

        initial_message = self._get_initial_message(session.scenario) if session.scenario else None

        return SessionStatusResponse(
            session_id=session.id,
            scenario_id=session.scenario_id,
            round_target=session.round_target,
            completed_rounds=session.completed_rounds,
            difficulty=_to_str(session.difficulty),
            mode=_to_str(session.mode),
            is_active=session.ended_at is None,
            difficulty_label=difficulty_label,
            mode_label=mode_label,
            extension_offered=extension_offered,
            scenario_name=scenario_name,
            can_extend=can_extend,
            initial_ai_message=initial_message,
        )
