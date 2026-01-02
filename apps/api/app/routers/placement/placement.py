from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_pro_user
from app.services.review.review_service import ReviewService
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
        target_sentence: Optional[str] = None,  # Speaking用: ユーザーが読み上げる文
        audio_text: Optional[str] = None,  # Listening用: TTS読み上げテキスト
        puzzle_words: Optional[List[str]] = None,  # Listening用: 並べ替え単語リスト
    ) -> None:
        self.id = id
        self.type = qtype  # "listening" | "speaking"
        self.prompt = prompt
        self.scenario_hint = scenario_hint
        self.target_sentence = target_sentence
        self.audio_text = audio_text
        self.puzzle_words = puzzle_words or []


QUESTIONS: List[PlacementQuestionSchema] = [
    # 旅行系（listening/speaking）
    PlacementQuestionSchema(
        id=1,
        qtype="listening",
        prompt="音声を聞いて、単語を正しい順番に並べてください。",
        scenario_hint="空港チェックイン・搭乗前",
        audio_text="I'm about to board my flight to New York.",
        puzzle_words=["I'm", "about", "to", "board", "my", "flight", "to", "New", "York."],
    ),
    PlacementQuestionSchema(
        id=2,
        qtype="speaking",
        prompt="チェックインカウンターで荷物を預けたいと伝えてください。",
        scenario_hint="空港チェックイン・荷物預け",
        target_sentence="I'd like to drop off my baggage, please.",
    ),
    PlacementQuestionSchema(
        id=3,
        qtype="listening",
        prompt="音声を聞いて、単語を正しい順番に並べてください。",
        scenario_hint="空港・ルールの説明",
        audio_text="We're supposed to check in two hours before departure.",
        puzzle_words=["We're", "supposed", "to", "check", "in", "two", "hours", "before", "departure."],
    ),
    PlacementQuestionSchema(
        id=4,
        qtype="speaking",
        prompt="ビーチリゾートで一週間過ごしたいと伝えてください。",
        scenario_hint="最高のバケーション",
        target_sentence="I'd love to spend a week at a beach resort.",
    ),
    PlacementQuestionSchema(
        id=5,
        qtype="speaking",
        prompt="友達に京都を訪れることを提案してください。",
        scenario_hint="日本を案内する",
        target_sentence="Why don't we visit Kyoto? It's a beautiful city.",
    ),
    # 日常会話系
    PlacementQuestionSchema(
        id=6,
        qtype="speaking",
        prompt="警察に財布を紛失したことを報告してください。",
        scenario_hint="財布を無くして警察に相談",
        target_sentence="Excuse me, I lost my wallet and I'd like to report it.",
    ),
    PlacementQuestionSchema(
        id=7,
        qtype="listening",
        prompt="音声を聞いて、単語を正しい順番に並べてください。",
        scenario_hint="カスタマーサービスに相談",
        audio_text="I'd like to ask about a problem with my order.",
        puzzle_words=["I'd", "like", "to", "ask", "about", "a", "problem", "with", "my", "order."],
    ),
    PlacementQuestionSchema(
        id=8,
        qtype="speaking",
        prompt="カフェで季節限定ドリンクを試してみたいと伝えてください。",
        scenario_hint="おしゃれカフェで店員と雑談",
        target_sentence="I feel like trying the seasonal drink today.",
    ),
    PlacementQuestionSchema(
        id=9,
        qtype="listening",
        prompt="音声を聞いて、単語を正しい順番に並べてください。",
        scenario_hint="ショーチケットを入手",
        audio_text="I'm looking for two tickets for tonight's show.",
        puzzle_words=["I'm", "looking", "for", "two", "tickets", "for", "tonight's", "show."],
    ),
    PlacementQuestionSchema(
        id=10,
        qtype="speaking",
        prompt="公園で天気について軽く話しかけてください。",
        scenario_hint="公園で雑談",
        target_sentence="What a lovely day, isn't it?",
    ),
    # ビジネス系
    PlacementQuestionSchema(
        id=11,
        qtype="speaking",
        prompt="急用ができたのでミーティングをリスケしたいと伝えてください。",
        scenario_hint="ミーティングをリスケする",
        target_sentence="Something urgent came up. Could we reschedule the meeting?",
    ),
    PlacementQuestionSchema(
        id=12,
        qtype="speaking",
        prompt="来週30分のミーティングを設定したいと伝えてください。",
        scenario_hint="ミーティングを立てる",
        target_sentence="Are you available for a 30-minute meeting next week?",
    ),
    PlacementQuestionSchema(
        id=13,
        qtype="listening",
        prompt="音声を聞いて、単語を正しい順番に並べてください。",
        scenario_hint="会議を進行する",
        audio_text="Let's move on to the next agenda item.",
        puzzle_words=["Let's", "move", "on", "to", "the", "next", "agenda", "item."],
    ),
    PlacementQuestionSchema(
        id=14,
        qtype="speaking",
        prompt="契約延長の条件として割引を提案してください。",
        scenario_hint="契約条件の交渉",
        target_sentence="If you extend the contract, we're willing to offer a discount.",
    ),
    PlacementQuestionSchema(
        id=15,
        qtype="speaking",
        prompt="調査結果の主要な発見を共有したいと伝えてください。",
        scenario_hint="顧客満足度の調査結果をプレゼン",
        target_sentence="I'd like to share the key findings from the survey.",
    ),
    # レベル境界を測るための少し難しめの質問
    PlacementQuestionSchema(
        id=16,
        qtype="listening",
        prompt="音声を聞いて、単語を正しい順番に並べてください。",
        scenario_hint="プロジェクトの遅延を謝罪する",
        audio_text="We've been trying to catch up with the schedule.",
        puzzle_words=["We've", "been", "trying", "to", "catch", "up", "with", "the", "schedule."],
    ),
    PlacementQuestionSchema(
        id=17,
        qtype="speaking",
        prompt="遅延をお詫びし、再発防止策を説明してください。",
        scenario_hint="プロジェクトの遅延を謝罪する",
        target_sentence="I apologize for the delay. We'll make sure it doesn't happen again.",
    ),
    PlacementQuestionSchema(
        id=18,
        qtype="listening",
        prompt="音声を聞いて、単語を正しい順番に並べてください。",
        scenario_hint="体調不良で休む",
        audio_text="I'm not feeling well today and need to take the day off.",
        puzzle_words=["I'm", "not", "feeling", "well", "today", "and", "need", "to", "take", "the", "day", "off."],
    ),
    PlacementQuestionSchema(
        id=19,
        qtype="speaking",
        prompt="病欠の連絡とタスクの引き継ぎを伝えてください。",
        scenario_hint="体調不良で休む・引き継ぎ",
        target_sentence="I need to call in sick today. I'll hand over my tasks.",
    ),
    PlacementQuestionSchema(
        id=20,
        qtype="speaking",
        prompt="新しい話題を切り出してください。",
        scenario_hint="ビジネスミーティング全般",
        target_sentence="If I may, I'd like to bring up a new topic.",
    ),
]


# --- Pydantic モデル ---

class WordMatch(BaseModel):
    """単語の一致情報"""
    word: str
    matched: bool
    index: int


class EvaluateSpeakingRequest(BaseModel):
    """スピーキング評価リクエスト"""
    question_id: int
    user_transcription: str


class EvaluateSpeakingResponse(BaseModel):
    """スピーキング評価レスポンス"""
    question_id: int
    score: int
    is_correct: bool
    matching_words: List[WordMatch]
    target_sentence: str


class EvaluateListeningRequest(BaseModel):
    """リスニング評価リクエスト"""
    question_id: int
    user_answer: List[str]


class EvaluateListeningResponse(BaseModel):
    """リスニング評価レスポンス"""
    question_id: int
    score: int
    is_correct: bool
    correct_answer: str


class PlacementSubmitRequest(BaseModel):
    """レベル判定テスト提出リクエスト"""
    answers: List[dict]


# --- ヘルパー関数 ---

def _get_question_by_id(question_id: int) -> Optional[PlacementQuestionSchema]:
    """IDで問題を取得"""
    for q in QUESTIONS:
        if q.id == question_id:
            return q
    return None


def _calculate_total_score(answers: List[dict]) -> int:
    """新しい評価方式での合計スコア計算（各問題のスコア平均）"""
    if not answers:
        return 0
    total = sum(a.get("score", 0) for a in answers)
    return int(total / len(answers))


def _decide_level(score: int) -> DifficultyLevel:
    """平均スコア(0-100)からレベルを決定."""
    if score <= 40:
        return DifficultyLevel.BEGINNER
    if score <= 70:
        return DifficultyLevel.INTERMEDIATE
    return DifficultyLevel.ADVANCED


@router.get("/questions")
async def get_placement_questions(
    current_user: User = Depends(require_pro_user),
) -> dict:
    """レベル判定テスト用の全20問を返す."""
    return {
        "questions": [
            {
                "id": q.id,
                "type": q.type,
                "prompt": q.prompt,
                "scenario_hint": q.scenario_hint,
                "target_sentence": q.target_sentence,
                "audio_text": q.audio_text,
                "puzzle_words": q.puzzle_words,
            }
            for q in QUESTIONS
        ]
    }


@router.post("/evaluate-speaking", response_model=EvaluateSpeakingResponse)
async def evaluate_speaking(
    payload: EvaluateSpeakingRequest,
    current_user: User = Depends(require_pro_user),
) -> EvaluateSpeakingResponse:
    """スピーキング問題を評価する（単語レベル一致率）"""
    question = _get_question_by_id(payload.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {payload.question_id} not found",
        )

    if question.type != "speaking":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question {payload.question_id} is not a speaking question",
        )

    if not question.target_sentence:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Target sentence not configured for this question",
        )

    # ReviewServiceの評価ロジックを使用
    result = ReviewService.evaluate_speaking(
        target_sentence=question.target_sentence,
        user_transcription=payload.user_transcription,
    )

    return EvaluateSpeakingResponse(
        question_id=payload.question_id,
        score=result.score,
        is_correct=result.is_correct,
        matching_words=[
            WordMatch(word=m.word, matched=m.matched, index=m.index)
            for m in result.matching_words
        ],
        target_sentence=question.target_sentence,
    )


@router.post("/evaluate-listening", response_model=EvaluateListeningResponse)
async def evaluate_listening(
    payload: EvaluateListeningRequest,
    current_user: User = Depends(require_pro_user),
) -> EvaluateListeningResponse:
    """リスニング問題を評価する（単語パズル完全一致）"""
    question = _get_question_by_id(payload.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {payload.question_id} not found",
        )

    if question.type != "listening":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question {payload.question_id} is not a listening question",
        )

    if not question.puzzle_words:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Puzzle words not configured for this question",
        )

    # ReviewServiceの評価ロジックを使用
    result = ReviewService.evaluate_listening(
        correct_words=question.puzzle_words,
        user_answer=payload.user_answer,
    )

    return EvaluateListeningResponse(
        question_id=payload.question_id,
        score=result.score,
        is_correct=result.is_correct,
        correct_answer=result.correct_answer or "",
    )


@router.post("/submit")
async def submit_placement_answers(
    payload: PlacementSubmitRequest,
    current_user: User = Depends(require_pro_user),
    db: Session = Depends(get_db),
) -> dict:
    """レベル判定テストの回答を受け取り、スコアとレベルを決定して保存する。

    新しい形式: answers = [{"question_id": 1, "score": 85}, ...]
    """
    answers = payload.answers
    if not answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="answers must be a non-empty list",
        )

    # 平均スコアを計算（0-100）
    average_score = _calculate_total_score(answers)
    max_score = 100  # 新形式では100点満点
    level = _decide_level(average_score)

    # ユーザーに結果を保存
    user: User = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.placement_level = level
    user.placement_score = average_score
    user.placement_completed_at = datetime.now(timezone.utc)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "score": average_score,
        "max_score": max_score,
        "placement_level": level.value,
        "placement_completed_at": user.placement_completed_at.isoformat(),
    }


