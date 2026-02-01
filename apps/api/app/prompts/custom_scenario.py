"""カスタム（オリジナル）シナリオ用のプロンプト生成

ユーザーが作成したオリジナルシナリオに対して、
動的にシステムプロンプトを生成する機能を提供します。

Note: 終了判定・出力フォーマットは common_rules.py に集約されており、
      groq_provider等でこのプロンプトと結合されます。
"""


def get_custom_scenario_prompt(
    user_role: str,
    ai_role: str,
    description: str,
    scenario_name: str = "",
) -> str:
    """カスタムシナリオ用のシステムプロンプトを生成する

    Args:
        user_role: ユーザーの役割（例: 「旅行者」「新入社員」）
        ai_role: AIの役割（例: 「ホテルのフロント係」「上司」）
        description: シナリオの説明・状況設定
        scenario_name: シナリオ名（オプション）

    Returns:
        フォーマット済みのシステムプロンプト
    """
    return CUSTOM_SCENARIO_PROMPT_TEMPLATE.format(
        user_role=user_role,
        ai_role=ai_role,
        description=description,
        scenario_name=scenario_name,
    )


CUSTOM_SCENARIO_PROMPT_TEMPLATE = """あなたは英会話学習用のAIパートナーです。以下のカスタムシナリオ設定に従って会話してください。

## シナリオ設定
- **シナリオ名**: {scenario_name}
- **場面・状況**: {description}
- **あなたの役割**: {ai_role}
- **ユーザーの役割**: {user_role}
- **難易度**: 中級 (intermediate)

## 会話の進め方
1. 設定された状況に沿った自然な英会話を行う
2. ユーザーの役割に応じた質問や対話を展開する
3. AIの役割になりきって応答する
4. 必要に応じて会話を発展させる
5. ユーザーが使える表現を自然に引き出す

## 指導方針
- ユーザーの発言を尊重し、自然な会話を心がける
- 中級レベルの表現を中心に使用する
- 分からない単語があれば、文脈から推測できるようにする
- 実践的で日常使いできる表現を優先する

## フィードバックのポイント
- 文法的な正確さ
- 場面に適した表現の選択
- 自然な会話の流れ
- ボキャブラリーの適切な使用

## 禁止事項
- 複雑すぎる文法や専門用語の多用
- 長すぎる説明や独り言
- シナリオの設定を逸脱した会話
- 個人的な質問やプライベートな内容への深入り

## 重要
- ユーザーが学習できるような自然な対話を心がけてください
- 会話終了の意図がない限り、会話を継続させるような応答をしてください
"""


# カスタムシナリオの初期AIメッセージを生成
def get_custom_scenario_initial_message(
    ai_role: str,
    description: str,
) -> str:
    """カスタムシナリオの初期AIメッセージを生成する

    Args:
        ai_role: AIの役割
        description: シナリオの説明

    Returns:
        初期メッセージ
    """
    return CUSTOM_SCENARIO_INITIAL_MESSAGE_TEMPLATE.format(
        ai_role=ai_role,
        description=description,
    )


CUSTOM_SCENARIO_INITIAL_MESSAGE_TEMPLATE = """Hello! I'll be playing the role of {ai_role} in this conversation.

The scenario is: {description}

Feel free to start the conversation whenever you're ready. How can I help you today?"""


# カスタムシナリオのデフォルトゴール
CUSTOM_SCENARIO_DEFAULT_GOALS = [
    "シナリオに沿った自然な会話ができる",
    "適切な表現を使って意思疎通ができる",
    "相手の発言を理解し、適切に応答できる",
]


def get_custom_scenario_goals() -> list[str]:
    """カスタムシナリオのデフォルトゴールを取得する

    Returns:
        ゴールのリスト
    """
    return CUSTOM_SCENARIO_DEFAULT_GOALS.copy()
