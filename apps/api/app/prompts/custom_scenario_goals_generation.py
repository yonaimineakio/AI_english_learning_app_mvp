"""カスタムシナリオのゴール自動生成用プロンプト

シナリオ作成時にAIで具体的な学習ゴール（3つ）を生成するためのプロンプトテンプレート。
"""


def get_custom_scenario_goals_generation_prompt(
    scenario_name: str,
    description: str,
    user_role: str,
    ai_role: str,
) -> str:
    """カスタムシナリオのゴール生成プロンプトを返す

    Args:
        scenario_name: シナリオ名
        description: シナリオの説明・状況設定
        user_role: ユーザーの役割
        ai_role: AIの役割

    Returns:
        フォーマット済みのプロンプト文字列
    """
    return GOALS_GENERATION_PROMPT_TEMPLATE.format(
        scenario_name=scenario_name,
        description=description,
        user_role=user_role,
        ai_role=ai_role,
    )


GOALS_GENERATION_PROMPT_TEMPLATE = """\
あなたは英会話学習アプリの学習ゴール設計者です。
以下のカスタムシナリオに対して、ユーザーが会話の中で達成すべき具体的な学習ゴールを3つ生成してください。

## シナリオ情報
- シナリオ名: {scenario_name}
- 場面・状況: {description}
- ユーザーの役割: {user_role}
- AIの役割: {ai_role}

## ゴール設計のルール
1. ゴールは3つちょうど生成する
2. 各ゴールはシナリオの場面に具体的に即した内容にする（汎用的すぎる表現は避ける）
3. 各ゴールは「〜する」「〜を伝える」「〜を確認する」のような動作形式で日本語で書く
4. 会話の自然な流れに沿った順番にする（序盤→中盤→終盤）
5. 1つのゴールは30文字以内にする
6. ユーザーの役割の視点で書く（AIの役割の視点ではない）

## 出力形式
以下のJSON形式のみを出力してください。説明文やマークダウンは不要です。

{{"goals": ["ゴール1", "ゴール2", "ゴール3"]}}
"""
