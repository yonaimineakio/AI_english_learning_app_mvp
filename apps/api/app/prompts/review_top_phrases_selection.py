"""セッション履歴から復習対象フレーズを選定するプロンプト。"""

from __future__ import annotations

import json
from typing import Any, List


REVIEW_TOP_PHRASES_SELECTION_PROMPT = """
あなたは英会話学習セッションの復習設計AIです。
目的は、会話履歴から「学習効果が高い復習フレーズ」を最大3件選ぶことです。

【選定方針】
- 改善効果重視で選ぶ
- phrase は improved_sentence を採用する
- explanation は feedback_short を採用する
- 同じ意味・ほぼ同じ文の重複は除外する
- 学習効果が高い順に並べる

【評価基準（selection_score: 0-100）】
- 90-100: 誤りが明確で再発しやすく、実用頻度も高い
- 70-89: 学習価値が高く、復習で定着が期待できる
- 50-69: 補助的には有効だが優先度は中程度

【入力】
session_rounds:
{session_rounds_json}

【出力ルール（最重要）】
- JSONオブジェクトのみを返す
- キーは top_phrases のみ
- top_phrases は配列、要素は最大3件
- 各要素は以下のキーを必ず含む:
  - round_index: int
  - phrase: string
  - explanation: string
  - reason: string（日本語、簡潔）
  - score: int（0-100）
- 余分なキー、説明文、Markdown、コードブロックは禁止

【出力例】
{{"top_phrases":[{{"round_index":2,"phrase":"I'd like to check in, please.","explanation":"丁寧表現を維持しつつ語順を安定させましょう。","reason":"語順ミスがあり実利用頻度が高い表現","score":88}}]}}
""".strip()


def get_review_top_phrases_selection_prompt(session_rounds: List[dict[str, Any]]) -> str:
    """復習フレーズ選定用プロンプトを返す。"""
    rounds_json = json.dumps(session_rounds, ensure_ascii=False)
    return REVIEW_TOP_PHRASES_SELECTION_PROMPT.format(session_rounds_json=rounds_json)
