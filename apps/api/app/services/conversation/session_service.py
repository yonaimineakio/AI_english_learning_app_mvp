from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
import asyncio
import logging
import time

from models.database.models import Session as SessionModel, SessionRound, Scenario, User, CustomScenario
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
    Scenario as ScenarioSchema,
    CustomScenario as CustomScenarioSchema,
)

from app.services.ai import generate_conversation_response
from app.services.ai.goal_progress import evaluate_goal_progress
from app.prompts.scenario_goals import SCENARIO_GOALS, get_goals_for_scenario
from app.prompts.custom_scenario import (
    get_custom_scenario_prompt,
    get_custom_scenario_initial_message,
    get_custom_scenario_goals,
)

logger = logging.getLogger(__name__)


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
            .filter(ReviewItem.user_id == user_id, ReviewItem.due_at.is_not(None))
            .order_by(ReviewItem.due_at.desc())
            .first()
        )

        return item.due_at if item else None

    async def _calculate_goal_progress(
        self, session: SessionModel
    ) -> tuple[int, int, List[int]]:
        """セッション全体の会話履歴から学習ゴール達成率を判定する。"""
        # カスタムシナリオの場合はデフォルトゴールを使用
        if session.custom_scenario_id:
            goals = get_custom_scenario_goals()
        else:
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

    def start_session(
        self, user_id: int, session_data: SessionCreate
    ) -> SessionStartResponse:
        logger.info(f"Starting session for user {user_id} with data: {session_data}")
        """セッションを開始する"""
        try:
            scenario = None
            custom_scenario = None
            scenario_schema = None
            custom_scenario_schema = None
            initial_message = None
            goals_labels = None

            # カスタムシナリオの場合
            if session_data.custom_scenario_id:
                custom_scenario = (
                    self.db.query(CustomScenario)
                    .filter(
                        CustomScenario.id == session_data.custom_scenario_id,
                        CustomScenario.is_active == True,
                        CustomScenario.user_id == user_id,  # 所有者チェック
                    )
                    .first()
                )

                if not custom_scenario:
                    raise ValueError(
                        f"Custom scenario with id {session_data.custom_scenario_id} not found or inactive"
                    )

                # セッション作成（カスタムシナリオ）
                db_session = SessionModel(
                    user_id=user_id,
                    scenario_id=None,
                    custom_scenario_id=session_data.custom_scenario_id,
                    round_target=session_data.round_target,
                    difficulty="intermediate",  # カスタムシナリオは intermediate 固定
                    mode=session_data.mode.value
                    if hasattr(session_data.mode, "value")
                    else session_data.mode,
                    started_at=datetime.now(timezone.utc),
                )

                custom_scenario_schema = CustomScenarioSchema(
                    id=custom_scenario.id,
                    user_id=custom_scenario.user_id,
                    name=custom_scenario.name,
                    description=custom_scenario.description,
                    user_role=custom_scenario.user_role,
                    ai_role=custom_scenario.ai_role,
                    difficulty=custom_scenario.difficulty,
                    is_active=custom_scenario.is_active,
                    created_at=custom_scenario.created_at,
                )

                initial_message = get_custom_scenario_initial_message(
                    custom_scenario.ai_role,
                    custom_scenario.description,
                )
                goals_labels = get_custom_scenario_goals()

            # 通常シナリオの場合
            elif session_data.scenario_id:
                scenario = (
                    self.db.query(Scenario)
                    .filter(
                        Scenario.id == session_data.scenario_id, Scenario.is_active == True
                    )
                    .first()
                )

                if not scenario:
                    raise ValueError(
                        f"Scenario with id {session_data.scenario_id} not found or inactive"
                    )

                # セッション作成（通常シナリオ）
                db_session = SessionModel(
                    user_id=user_id,
                    scenario_id=session_data.scenario_id,
                    custom_scenario_id=None,
                    round_target=session_data.round_target,
                    difficulty=session_data.difficulty.value
                    if hasattr(session_data.difficulty, "value")
                    else session_data.difficulty,
                    mode=session_data.mode.value
                    if hasattr(session_data.mode, "value")
                    else session_data.mode,
                    started_at=datetime.now(timezone.utc),
                )

                scenario_schema = ScenarioSchema(
                    id=scenario.id,
                    name=scenario.name,
                    description=scenario.description,
                    category=self._to_str(scenario.category),
                    difficulty=self._to_str(scenario.difficulty),
                    is_active=scenario.is_active,
                    created_at=scenario.created_at,
                )

                initial_message = self._get_initial_message(scenario)
                goals_labels = get_goals_for_scenario(scenario.id)
            else:
                raise ValueError("Either scenario_id or custom_scenario_id is required")

            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)

            logger.info(f"Session {db_session.id} started for user {user_id}")

            return SessionStartResponse(
                session_id=db_session.id,
                scenario=scenario_schema,
                custom_scenario=custom_scenario_schema,
                round_target=db_session.round_target,
                difficulty=self._to_str(db_session.difficulty),
                mode=self._to_str(db_session.mode),
                initial_ai_message=initial_message,
                goals_labels=goals_labels,
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to start session: {str(e)}")
            raise

    async def process_turn(
        self, session_id: int, user_input: str, user_id: int
    ) -> TurnResponse:
        """セッションのターンを処理する"""
        try:
            # セッションの存在確認
            session = (
                self.db.query(SessionModel)
                .filter(
                    SessionModel.id == session_id,
                    SessionModel.user_id == user_id,
                    SessionModel.ended_at.is_(None),  # 終了していないセッション
                )
                .first()
            )

            if not session:
                raise ValueError(
                    f"Active session {session_id} not found for user {user_id}"
                )

            # 現在のラウンド数を取得
            current_round = session.completed_rounds + 1

            # ラウンド数上限チェック
            if current_round > session.round_target:
                raise ValueError(
                    f"Session {session_id} has reached maximum rounds ({session.round_target})"
                )

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

            # カスタムシナリオの場合
            if session.custom_scenario_id and session.custom_scenario:
                custom_scenario = session.custom_scenario
                scenario_category = "custom"  # カスタムシナリオ用のカテゴリ
                scenario_id = None

                # カスタムシナリオ用のプロンプトを生成して使用
                custom_prompt = get_custom_scenario_prompt(
                    user_role=custom_scenario.user_role,
                    ai_role=custom_scenario.ai_role,
                    description=custom_scenario.description,
                    scenario_name=custom_scenario.name,
                )

                conversation_result = await generate_conversation_response(
                    user_input=user_input,
                    difficulty=session_difficulty,
                    scenario_category=scenario_category,
                    round_index=current_round,
                    context=context,
                    scenario_id=scenario_id,
                    provider_name="groq",
                    custom_system_prompt=custom_prompt,  # カスタムプロンプトを渡す
                )
            else:
                # 通常シナリオの場合
                scenario_category = self._to_str(session.scenario.category)
                scenario_id = session.scenario_id

                conversation_result = await generate_conversation_response(
                    user_input=user_input,
                    difficulty=session_difficulty,
                    scenario_category=scenario_category,
                    round_index=current_round,
                    context=context,
                    scenario_id=scenario_id,
                    provider_name="groq",
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

            # ポイント付与（1ラウンド完了ごと）
            try:
                from app.services.points.point_service import PointService

                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    current_streak = user.current_streak or 0
                    round_points = PointService(self.db).calculate_round_points(
                        session_difficulty,
                        current_streak,
                    )
                    user.total_points = (user.total_points or 0) + round_points
            except Exception as e:
                # ポイント付与に失敗しても会話自体は継続させる（MVPの堅牢性優先）
                logger.warning(f"Failed to award round points: {str(e)}")

            self.db.commit()
            self.db.refresh(session)

            logger.info(f"Turn {current_round} processed for session {session_id}")

            ai_details = getattr(conversation_result, "details", None)

            # 学習ゴール達成率の判定
            (
                goals_total,
                goals_achieved,
                goals_status,
            ) = await self._calculate_goal_progress(session)

            goals_completed = goals_total > 0 and goals_achieved == goals_total
            round_limit_reached = session.completed_rounds >= session.round_target
            # NOTE: should_end_session は「終了提案」フラグ。実際の終了はクライアントが
            # /sessions/{id}/end を呼んだときにのみ行う（ユーザー承認が必要）。
            suggest_end = (
                bool(conversation_result.should_end_session)
                or goals_completed
                or round_limit_reached
            )
            end_prompt_reason: str | None
            if conversation_result.should_end_session:
                end_prompt_reason = "user_intent"
            elif goals_completed:
                end_prompt_reason = "goals_completed"
            elif round_limit_reached:
                end_prompt_reason = "round_limit"
            else:
                end_prompt_reason = None

            # ゴールラベルを取得
            if session.custom_scenario_id:
                goals_labels = get_custom_scenario_goals()
            elif session.scenario_id:
                goals_labels = get_goals_for_scenario(session.scenario_id)
            else:
                goals_labels = None

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
                # NOTE: should_end_session は「終了提案」フラグ。実際の終了はクライアントが
                # /sessions/{id}/end を呼んだときにのみ行う（ユーザー承認が必要）。
                session_status=self._build_session_status(session),
                should_end_session=suggest_end,
                end_prompt_reason=end_prompt_reason,
                goals_total=goals_total,
                goals_achieved=goals_achieved,
                goals_status=goals_status or None,
                goals_labels=goals_labels or None,
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to process turn: {str(e)}")
            raise

    def extend_session(self, session_id: int, user_id: int) -> Dict[str, Any]:
        """セッションを延長する（+3ラウンド）"""
        try:
            session = (
                self.db.query(SessionModel)
                .filter(
                    SessionModel.id == session_id,
                    SessionModel.user_id == user_id,
                    SessionModel.ended_at.is_(None),
                )
                .first()
            )

            if not session:
                raise ValueError(
                    f"Active session {session_id} not found for user {user_id}"
                )

            # 延長回数制限（最大2回まで）
            if hasattr(session, "extension_count"):
                if session.extension_count >= 2:
                    raise ValueError("Maximum extensions reached (2 times)")
                session.extension_count += 1
            else:
                session.extension_count = 1

            # ラウンド数を+3延長
            session.round_target += 3

            self.db.commit()
            self.db.refresh(session)

            logger.info(
                f"Session {session_id} extended by 3 rounds (total: {session.round_target})"
            )

            return self._build_session_status(session)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to extend session: {str(e)}")
            raise

    async def end_session(self, session_id: int, user_id: int) -> SessionEndResponse:
        """セッションを終了し、トップ3フレーズを抽出する"""
        try:
            session = (
                self.db.query(SessionModel)
                .filter(
                    SessionModel.id == session_id,
                    SessionModel.user_id == user_id,
                )
                .first()
            )

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

                # ストリーク更新
                from app.services.streak.streak_service import StreakService
                import pytz

                jst = pytz.timezone("Asia/Tokyo")
                activity_date = datetime.now(jst).date()
                StreakService(self.db).update_streak(user_id, activity_date)

                # セッション完了ボーナス（規定ラウンド到達時のみ）
                try:
                    if session.completed_rounds >= session.round_target:
                        from app.services.points.point_service import PointService

                        user = self.db.query(User).filter(User.id == user_id).first()
                        if user:
                            current_streak = user.current_streak or 0
                            session_bonus = PointService(
                                self.db
                            ).calculate_session_completion_points(
                                self._to_str(session.difficulty),
                                current_streak,
                            )
                            user.total_points = (user.total_points or 0) + session_bonus
                except Exception as e:
                    logger.warning(
                        f"Failed to award session completion points: {str(e)}"
                    )

                self.db.commit()
                self.db.refresh(session)

                logger.info(
                    f"Session {session_id} ended with {session.completed_rounds} rounds"
                )
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
            (
                goals_total,
                goals_achieved,
                goals_status,
            ) = await self._calculate_goal_progress(session)

            # ゴールラベルを取得
            if session.custom_scenario_id:
                goals_labels = get_custom_scenario_goals()
                scenario_name = session.custom_scenario.name if session.custom_scenario else None
            elif session.scenario_id:
                goals_labels = get_goals_for_scenario(session.scenario_id)
                scenario_name = session.scenario.name if session.scenario else None
            else:
                goals_labels = None
                scenario_name = None

            return SessionEndResponse(
                session_id=session_id,
                completed_rounds=session.completed_rounds,
                top_phrases=top_phrases,
                next_review_at=next_review_at,
                scenario_name=scenario_name,
                difficulty=self._to_str(session.difficulty),
                mode=self._to_str(session.mode),
                goals_total=goals_total,
                goals_achieved=goals_achieved,
                goals_status=goals_status or None,
                goals_labels=goals_labels or None,
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to end session: {str(e)}")
            raise

    def _generate_ai_response(
        self, user_input: str, difficulty: DifficultyLevel, round_index: int
    ) -> tuple:
        """AI応答とフィードバックを生成する（モック実装）"""
        # 実際の実装では、OpenAI APIを呼び出して応答を生成
        # 現在はモック実装

        difficulty_responses = {
            DifficultyLevel.BEGINNER: {
                "ai_reply": "That's a good start! Let me help you with that.",
                "feedback_short": "Good effort! Try to use more complete sentences.",
                "improved_sentence": "I would like to learn more about this topic.",
            },
            DifficultyLevel.INTERMEDIATE: {
                "ai_reply": "I understand your point. Could you elaborate on that?",
                "feedback_short": "Nice expression! Consider using more specific vocabulary.",
                "improved_sentence": "I would appreciate it if you could provide more details about this matter.",
            },
            DifficultyLevel.ADVANCED: {
                "ai_reply": "That's an insightful perspective. What are your thoughts on the implications?",
                "feedback_short": "Excellent articulation! You might consider using more nuanced language.",
                "improved_sentence": "I would be interested in exploring the broader implications of this concept.",
            },
        }

        response = difficulty_responses.get(
            difficulty, difficulty_responses[DifficultyLevel.INTERMEDIATE]
        )

        # ラウンドに応じてタグを生成
        tags = ["conversation", f"round_{round_index}", difficulty.value]

        return (
            response["ai_reply"],
            response["feedback_short"],
            response["improved_sentence"],
            tags,
        )

    def _extract_top_phrases(self, session_id: int) -> List[Dict[str, Any]]:
        """セッションからトップ3フレーズを抽出する（モック実装）"""
        # 実際の実装では、AIを使用して重要なフレーズを抽出
        # 現在はモック実装

        session_rounds = (
            self.db.query(SessionRound)
            .filter(SessionRound.session_id == session_id)
            .order_by(SessionRound.created_at.desc())
            .limit(3)
            .all()
        )

        top_phrases = []
        for i, round_data in enumerate(session_rounds, 1):
            top_phrases.append(
                {
                    "rank": i,
                    "phrase": round_data.improved_sentence,
                    "explanation": round_data.feedback_short,
                    "round_index": round_data.round_index,
                }
            )

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
        def _to_str(value):
            return value.value if hasattr(value, "value") else value

        # カスタムシナリオの場合
        is_custom_scenario = session.custom_scenario_id is not None
        if is_custom_scenario and session.custom_scenario:
            scenario_name = session.custom_scenario.name
            initial_message = get_custom_scenario_initial_message(
                session.custom_scenario.ai_role,
                session.custom_scenario.description,
            )
        elif session.scenario:
            scenario_name = session.scenario.name
            initial_message = self._get_initial_message(session.scenario)
        else:
            scenario_name = None
            initial_message = None

        difficulty_label = _to_str(session.difficulty) if session.difficulty else None
        mode_label = _to_str(session.mode) if session.mode else None
        extension_offered = session.completed_rounds >= session.round_target
        can_extend = (
            extension_offered
            and session.extension_count < 2
            and session.ended_at is None
        )

        return SessionStatusResponse(
            session_id=session.id,
            scenario_id=session.scenario_id,
            custom_scenario_id=session.custom_scenario_id,
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
            is_custom_scenario=is_custom_scenario,
            initial_ai_message=initial_message,
        )
