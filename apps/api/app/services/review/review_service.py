from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.database.models import ReviewItem


# スコア閾値（これ以上で「合格」とみなす）
PASSING_SCORE = 70


class WordMatchResult:
    """単語の一致結果"""

    def __init__(self, word: str, matched: bool, index: int):
        self.word = word
        self.matched = matched
        self.index = index


class EvaluationResult:
    """評価結果"""

    def __init__(
        self,
        score: int,
        is_correct: bool,
        matching_words: Optional[List[WordMatchResult]] = None,
        correct_answer: Optional[str] = None,
    ):
        self.score = score
        self.is_correct = is_correct
        self.matching_words = matching_words or []
        self.correct_answer = correct_answer


class ReviewService:
    """復習アイテムの取得・完了処理を担うサービス"""

    def __init__(self, db: Session):
        self.db = db

    def get_due_items(self, user_id: int, limit: int = 10) -> List[ReviewItem]:
        """現在期限切れになっている復習アイテムを取得する"""

        now = datetime.utcnow()
        return (
            self.db.query(ReviewItem)
            .filter(
                ReviewItem.user_id == user_id,
                ReviewItem.is_completed.is_(False),
                ReviewItem.due_at <= now,
            )
            .order_by(ReviewItem.due_at.asc(), ReviewItem.created_at.asc())
            .limit(limit)
            .all()
        )

    def count_due_items(self, user_id: int) -> int:
        now = datetime.utcnow()
        return (
            self.db.query(func.count(ReviewItem.id))
            .filter(
                ReviewItem.user_id == user_id,
                ReviewItem.is_completed.is_(False),
                ReviewItem.due_at <= now,
            )
            .scalar()
            or 0
        )

    def get_history(self, user_id: int, limit: int = 20) -> List[ReviewItem]:
        """最近完了した復習アイテム"""

        return (
            self.db.query(ReviewItem)
            .filter(
                ReviewItem.user_id == user_id,
                ReviewItem.is_completed.is_(True),
                ReviewItem.completed_at.isnot(None),
            )
            .order_by(ReviewItem.completed_at.desc())
            .limit(limit)
            .all()
        )

    def get_stats(self, user_id: int) -> Dict[str, float]:
        """累計の復習統計を取得する

        Returns:
            dict: {
                "total_items": 累計復習アイテム数,
                "completed_items": 完了した復習アイテム数,
                "completion_rate": 完了率 (0.0 - 100.0)
            }
        """
        total_items = (
            self.db.query(func.count(ReviewItem.id))
            .filter(ReviewItem.user_id == user_id)
            .scalar()
            or 0
        )

        completed_items = (
            self.db.query(func.count(ReviewItem.id))
            .filter(
                ReviewItem.user_id == user_id,
                ReviewItem.is_completed.is_(True),
            )
            .scalar()
            or 0
        )

        completion_rate = 0.0
        if total_items > 0:
            completion_rate = round((completed_items / total_items) * 100, 1)

        return {
            "total_items": total_items,
            "completed_items": completed_items,
            "completion_rate": completion_rate,
        }

    def complete_review_item(
        self, user_id: int, item_id: int, result: str
    ) -> Tuple[ReviewItem, bool]:
        """復習結果を保存する。

        Returns:
            ReviewItem: 更新後のアイテム
            bool: 正解だった場合は True
        """

        item = (
            self.db.query(ReviewItem)
            .filter(ReviewItem.id == item_id, ReviewItem.user_id == user_id)
            .first()
        )

        if not item:
            raise ValueError("Review item not found")

        now = datetime.utcnow()
        normalized = result.lower()
        if normalized not in {"correct", "incorrect"}:
            raise ValueError("Invalid review result")

        if normalized == "correct":
            item.is_completed = True
            item.completed_at = now
        else:
            # 翌日再出題（シンプルな復習間隔）
            item.is_completed = False
            item.due_at = now + timedelta(days=1)
            item.completed_at = None

        self.db.commit()
        self.db.refresh(item)

        return item, normalized == "correct"

    @staticmethod
    def evaluate_speaking(
        target_sentence: str,
        user_transcription: str,
    ) -> EvaluationResult:
        """スピーキング問題を評価する（単語レベル一致率）

        Args:
            target_sentence: ターゲット文（正解）
            user_transcription: ユーザーの発話認識結果

        Returns:
            EvaluationResult: 評価結果（スコア、一致情報）
        """

        # 正規化: 小文字化、句読点除去
        def normalize(text: str) -> List[str]:
            clean = re.sub(r'[.,!?;:\'"()-]', "", text.lower())
            return clean.split()

        target_words = normalize(target_sentence)
        user_words = normalize(user_transcription)

        if not target_words:
            return EvaluationResult(
                score=0,
                is_correct=False,
                matching_words=[],
                correct_answer=target_sentence,
            )

        # 各ターゲット単語に対して一致を確認
        matching_words: List[WordMatchResult] = []
        matched_count = 0

        for i, target_word in enumerate(target_words):
            # ユーザーの発話に含まれているかチェック
            matched = target_word in user_words
            if matched:
                matched_count += 1
                # 一致した単語はユーザーリストから除去（重複カウント防止）
                user_words.remove(target_word)
            matching_words.append(
                WordMatchResult(
                    word=target_word,
                    matched=matched,
                    index=i,
                )
            )

        # スコア計算（0-100）
        score = int((matched_count / len(target_words)) * 100)
        is_correct = score >= PASSING_SCORE

        return EvaluationResult(
            score=score,
            is_correct=is_correct,
            matching_words=matching_words,
            correct_answer=target_sentence,
        )

    @staticmethod
    def evaluate_listening(
        correct_words: List[str],
        user_answer: List[str],
    ) -> EvaluationResult:
        """リスニング問題を評価する（単語パズル完全一致）

        Args:
            correct_words: 正解の単語リスト（順序通り）
            user_answer: ユーザーが並べた単語リスト

        Returns:
            EvaluationResult: 評価結果（スコア、正解/不正解）
        """

        # 正規化: 小文字化して比較
        def normalize_list(words: List[str]) -> List[str]:
            return [w.lower().strip() for w in words if w.strip()]

        correct_normalized = normalize_list(correct_words)
        user_normalized = normalize_list(user_answer)

        # 完全一致判定
        is_correct = correct_normalized == user_normalized

        # スコア: 完全一致なら100点、それ以外は部分点
        if is_correct:
            score = 100
        else:
            # 部分点: 正しい位置にある単語の割合
            if not correct_normalized:
                score = 0
            else:
                correct_positions = sum(
                    1
                    for i, word in enumerate(user_normalized)
                    if i < len(correct_normalized) and word == correct_normalized[i]
                )
                score = int((correct_positions / len(correct_normalized)) * 100)

        correct_answer = " ".join(correct_words)

        return EvaluationResult(
            score=score,
            is_correct=is_correct,
            matching_words=None,
            correct_answer=correct_answer,
        )

    def evaluate_and_update(
        self,
        user_id: int,
        item_id: int,
        question_type: str,
        score: int,
        is_correct: bool,
    ) -> Tuple[ReviewItem, bool, Optional[datetime]]:
        """評価結果に基づいて復習アイテムを更新する。

        Args:
            user_id: ユーザーID
            item_id: 復習アイテムID
            question_type: 問題タイプ ("speaking" or "listening")
            score: 評価スコア (0-100)
            is_correct: 正解かどうか

        Returns:
            ReviewItem: 更新後のアイテム
            bool: 復習アイテムが完了したかどうか
            datetime: 次回の復習予定日（再出題の場合）
        """
        item = (
            self.db.query(ReviewItem)
            .filter(ReviewItem.id == item_id, ReviewItem.user_id == user_id)
            .first()
        )

        if not item:
            raise ValueError("Review item not found")

        if question_type not in {"speaking", "listening"}:
            raise ValueError("Invalid question type")

        now = datetime.utcnow()
        next_due_at: Optional[datetime] = None

        # リスニング問題（最後の問題）の評価時に完了判定
        if question_type == "listening":
            if is_correct:
                item.is_completed = True
                item.completed_at = now
            else:
                # 不正解の場合は翌日再出題
                item.is_completed = False
                item.due_at = now + timedelta(days=1)
                item.completed_at = None
                next_due_at = item.due_at

        # スピーキング問題で不正解の場合も翌日再出題
        elif question_type == "speaking" and not is_correct:
            item.is_completed = False
            item.due_at = now + timedelta(days=1)
            item.completed_at = None
            next_due_at = item.due_at

        self.db.commit()
        self.db.refresh(item)

        return item, item.is_completed, next_due_at
