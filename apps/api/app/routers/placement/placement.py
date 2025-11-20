from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from models.database.models import User
from models.schemas.schemas import DifficultyLevel

router = APIRouter(tags=["placement"])


class PlacementQuestionSchema:
    """静的に管理するレベル判定テストの質問定義."""

    def __init__(
        self,
        id: int,
        qtype: str,
        prompt: str,
        scenario_hint: str,
    ) -> None:
        self.id = id
        self.type = qtype  # "listening" | "speaking"
        self.prompt = prompt
        self.scenario_hint = scenario_hint


QUESTIONS: List[PlacementQuestionSchema] = [
    # 旅行系（listening/speaking）
    PlacementQuestionSchema(
        id=1,
        qtype="listening",
        prompt="You hear: \"I'm about to board my flight to New York.\" What does \"about to\" mean here?",
        scenario_hint="空港チェックイン・搭乗前",
    ),
    PlacementQuestionSchema(
        id=2,
        qtype="speaking",
        prompt="At the check-in counter, how would you say that you need to drop off your baggage?",
        scenario_hint="空港チェックイン・荷物預け",
    ),
    PlacementQuestionSchema(
        id=3,
        qtype="listening",
        prompt="You hear: \"We’re supposed to check in two hours before departure.\" What does \"be supposed to\" express?",
        scenario_hint="空港・ルールの説明",
    ),
    PlacementQuestionSchema(
        id=4,
        qtype="speaking",
        prompt="You want to say that you’d love to spend a week at a beach resort. How would you express that?",
        scenario_hint="最高のバケーション",
    ),
    PlacementQuestionSchema(
        id=5,
        qtype="speaking",
        prompt="You are guiding a friend in Japan and want to suggest visiting Kyoto. How would you make that suggestion?",
        scenario_hint="日本を案内する",
    ),
    # 日常会話系
    PlacementQuestionSchema(
        id=6,
        qtype="speaking",
        prompt="You lost your wallet. How would you politely tell the police that you need to report it?",
        scenario_hint="財布を無くして警察に相談",
    ),
    PlacementQuestionSchema(
        id=7,
        qtype="listening",
        prompt="You hear: \"I’d like to ask about a problem with my order.\" What situation is this phrase useful for?",
        scenario_hint="カスタマーサービスに相談",
    ),
    PlacementQuestionSchema(
        id=8,
        qtype="speaking",
        prompt="At a café, how would you say that you feel like trying the seasonal drink?",
        scenario_hint="おしゃれカフェで店員と雑談",
    ),
    PlacementQuestionSchema(
        id=9,
        qtype="listening",
        prompt="You hear: \"I’m looking for two tickets for tonight’s show.\" What is this person trying to do?",
        scenario_hint="ショーチケットを入手",
    ),
    PlacementQuestionSchema(
        id=10,
        qtype="speaking",
        prompt="In a park, you want to start a light conversation about the nice weather. What would you say?",
        scenario_hint="公園で雑談",
    ),
    # ビジネス系
    PlacementQuestionSchema(
        id=11,
        qtype="speaking",
        prompt="You need to reschedule a meeting because something urgent came up. How would you explain that?",
        scenario_hint="ミーティングをリスケする",
    ),
    PlacementQuestionSchema(
        id=12,
        qtype="speaking",
        prompt="You want to set up a 30-minute meeting next week. How would you ask about the other person’s availability?",
        scenario_hint="ミーティングを立てる",
    ),
    PlacementQuestionSchema(
        id=13,
        qtype="listening",
        prompt="You hear: \"Let’s move on to the next agenda item.\" In what situation would you use this?",
        scenario_hint="会議を進行する",
    ),
    PlacementQuestionSchema(
        id=14,
        qtype="speaking",
        prompt="In a negotiation, how would you say that you’re willing to offer a discount if the contract is extended?",
        scenario_hint="契約条件の交渉",
    ),
    PlacementQuestionSchema(
        id=15,
        qtype="speaking",
        prompt="You are presenting survey results. How would you start by saying you’d like to share the key findings?",
        scenario_hint="顧客満足度の調査結果をプレゼン",
    ),
    # レベル境界を測るための少し難しめの質問
    PlacementQuestionSchema(
        id=16,
        qtype="listening",
        prompt="You hear: \"We’ve been trying to catch up with the schedule.\" What does this suggest about the project?",
        scenario_hint="プロジェクトの遅延を謝罪する",
    ),
    PlacementQuestionSchema(
        id=17,
        qtype="speaking",
        prompt="You need to apologize for a delay and explain how you plan to prevent it from happening again. How would you say that?",
        scenario_hint="プロジェクトの遅延を謝罪する",
    ),
    PlacementQuestionSchema(
        id=18,
        qtype="listening",
        prompt="You hear: \"I’m not feeling well today and need to take the day off.\" What is this person doing?",
        scenario_hint="体調不良で休む",
    ),
    PlacementQuestionSchema(
        id=19,
        qtype="speaking",
        prompt="You want to say that you’re about to call in sick and hand over your tasks. How would you express that?",
        scenario_hint="体調不良で休む・引き継ぎ",
    ),
    PlacementQuestionSchema(
        id=20,
        qtype="speaking",
        prompt="In a business meeting, you want to gently bring up a new topic. How would you start that?",
        scenario_hint="ビジネスミーティング全般",
    ),
]


def _score_answers(answers: List[dict]) -> int:
    """自己評価ベースのシンプルな採点ロジック."""
    score = 0
    for a in answers:
        self_score = a.get("self_score")
        if isinstance(self_score, int) and 0 <= self_score <= 5:
            score += self_score
    return score


def _decide_level(score: int) -> DifficultyLevel:
    """合計スコアからレベルを決定."""
    if score <= 40:
        return DifficultyLevel.BEGINNER
    if score <= 70:
        return DifficultyLevel.INTERMEDIATE
    return DifficultyLevel.ADVANCED


@router.get("/questions")
async def get_placement_questions(
    current_user: User = Depends(get_current_user),
) -> dict:
    """レベル判定テスト用の全20問を返す."""
    return {
        "questions": [
            {
                "id": q.id,
                "type": q.type,
                "prompt": q.prompt,
                "scenario_hint": q.scenario_hint,
            }
            for q in QUESTIONS
        ]
    }


@router.post("/submit")
async def submit_placement_answers(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """レベル判定テストの回答を受け取り、スコアとレベルを決定して保存する。"""
    answers: Optional[List[dict]] = payload.get("answers")
    if not answers or not isinstance(answers, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="answers must be a non-empty list",
        )

    score = _score_answers(answers)
    max_score = 5 * len(QUESTIONS)
    level = _decide_level(score)

    # ユーザーに結果を保存
    user: User = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.placement_level = level
    user.placement_score = score
    user.placement_completed_at = datetime.now(timezone.utc)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "score": score,
        "max_score": max_score,
        "placement_level": level.value,
        "placement_completed_at": user.placement_completed_at.isoformat(),
    }


