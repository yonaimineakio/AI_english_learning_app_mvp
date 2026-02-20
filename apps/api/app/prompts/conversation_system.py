"""会話システムプロンプト

ユーザー入力に対するAIの応答生成時に使用する
共通のシステムプロンプトを管理します。

Note: 終了判定・出力フォーマットは common_rules.py に集約されています。
"""

from .common_rules import get_common_conversation_rules


def get_conversation_system_prompt(
    difficulty: str, user_input: str, goals_info: dict | None = None
) -> str:
    """会話システムプロンプトを生成する

    Args:
        difficulty: 難易度 ('beginner', 'intermediate', 'advanced')
        user_input: ユーザーの入力テキスト
        goals_info: ゴール情報（任意）

    Returns:
        フォーマット済みのシステムプロンプト
    """
    # 共通ルールを使用（終了判定・出力フォーマット含む）
    return f"あなたは英会話学習用AIです。\n{get_common_conversation_rules(difficulty, user_input, goals_info=goals_info)}"
