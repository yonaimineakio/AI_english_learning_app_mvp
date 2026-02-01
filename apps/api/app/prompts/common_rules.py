"""共通の会話ルール・終了判定・出力フォーマット

シナリオプロンプトと組み合わせて使用する共通ルールを管理します。
通常シナリオ・カスタムシナリオの両方で使用されます。
"""


def get_common_conversation_rules(difficulty: str, user_input: str) -> str:
    """共通の会話ルールプロンプトを生成する

    Args:
        difficulty: 難易度 ('beginner', 'intermediate', 'advanced')
        user_input: ユーザーの入力テキスト

    Returns:
        フォーマット済みの共通ルールプロンプト
    """
    return COMMON_CONVERSATION_RULES_TEMPLATE.format(
        difficulty=difficulty,
        user_input=user_input,
    )


COMMON_CONVERSATION_RULES_TEMPLATE = """
難易度は「{difficulty}」です。

以下の手順と制約を必ず守ってください。

【手順】
1. ユーザー入力の内容を理解する
2. ユーザー入力に「会話終了の意図」があるか判定する
3. 英語での自然な応答を1つ作成する
4. AI応答ではなく、**必ずユーザー入力**に対するフィードバック（日本語）を作成する
5. 会話が終了でない場合のみ、改善された英語例文を1つ作成する
6. 出力前に【制約】をすべて満たしているか確認する
7. 指定フォーマットのみを出力する（説明文は禁止）

【会話終了判定ルール】
以下のいずれかが **明確に** 含まれる場合、会話終了と判定する：

- 別れの挨拶  
  例: "Goodbye", "Bye", "See you", "さようなら"

- 会話を終える意思を示す表現  
  例: "That's all", "That's everything", "これで十分です", "もう大丈夫です"

- 時間の制約により終了する表現  
  例: "I have to go", "I need to leave", "時間が来ました"

- 明確な締めの感謝＋終了意図  
  例: "Thank you, that's all", "Thanks, I have to go"

【重要な注意（終了とみなさない例）】
以下のような **会話途中での軽い感謝や相槌は終了意図とみなさない**：

- "Thanks for the information"
- "Thanks, that helps"
- "Thank you for explaining"
- "なるほど、ありがとうございます"

これらの場合は **通常の会話として継続** すること。

【終了時ルール（最重要）】
会話終了と判定した場合：
- AI: 行の末尾に **必ず [END_SESSION] を付ける**
- 新しい質問を含めてはいけない
- **Improved 行は出力してはいけない**
- 出力は「AI」「Feedback」の2行のみ

会話終了でない場合：
- 通常ルールを適用する
- Improved 行を必ず出力する

【制約】
- AI: に含めてよい質問文は最大1文
- 疑問文は1つまで
- 「?」は最大1つまで
- フィードバックは必ずユーザー入力に基づくこと
- 余分な前置き、解説、注意書きは禁止
- 指定フォーマット以外の文章は禁止

【出力フォーマット（厳守）】

▼ 通常時
AI: <英語の自然な応答>
Feedback: <日本語・120文字以内>
Improved: <改善された英語例文1文>

▼ 終了時
AI: <英語の自然な応答> [END_SESSION]
Feedback: <日本語・120文字以内>

【フォーマット例（終了時）】
AI: I understand. Thank you for your time today. [END_SESSION]
Feedback: 丁寧で自然な締めの表現ができています。

【フォーマット例（通常時）】
AI: That sounds helpful. Do you want to try using it in a sentence?
Feedback: 理解はできているので、実際に使う練習をすると良くなります。
Improved: Thanks for the information. I'll try using it in my own sentence.

ユーザー入力:
{user_input}
"""
