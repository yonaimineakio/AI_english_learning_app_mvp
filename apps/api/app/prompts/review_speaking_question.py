"""復習用スピーキング問題生成プロンプト

スピーキング問題では、ユーザーが読み上げるべきターゲット文を生成する。
評価は、音声認識結果とターゲット文の単語レベル一致率で行う。
"""

REVIEW_SPEAKING_PROMPT = """
あなたは英語学習アシスタントです。
与えられた英語フレーズを使って、ユーザーが読み上げる練習用の文を生成してください。

## 入力情報
- フレーズ: {phrase}
- 説明: {explanation}

## 出力形式
以下の形式で厳密に出力してください：

TargetSentence: [フレーズを含む自然な英文（ユーザーが読み上げる文、1文）]
Prompt: [この文を読み上げるシチュエーションの説明（日本語、50文字以内）]
Hint: [発音のヒント（日本語、30文字以内）]

## 生成ルール
1. TargetSentenceは与えられたフレーズを必ず含む自然な英文にする
2. TargetSentenceは1文で、5〜15単語程度の長さにする
3. 日常会話で実際に使われそうな自然な文にする
4. Promptはシチュエーションを簡潔に説明する
5. Hintは発音や強調のポイントを示す

## 出力例
TargetSentence: I'm about to leave for the airport now.
Prompt: 空港に向けて出発しようとしている場面です
Hint: "about to"を強調して発音しましょう
"""


def get_speaking_question_prompt(phrase: str, explanation: str) -> str:
    """スピーキング問題生成用のプロンプトを返す"""
    return REVIEW_SPEAKING_PROMPT.format(phrase=phrase, explanation=explanation)
