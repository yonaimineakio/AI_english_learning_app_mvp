"""復習用リスニング問題生成プロンプト

リスニング問題では、TTS読み上げ用の文と単語パズル用の単語リストを生成する。
評価は、ユーザーが並べた単語順が正解と完全に一致するかで行う。
"""

REVIEW_LISTENING_PROMPT = """
あなたは英語学習アシスタントです。
与えられた英語フレーズを含む自然な英文を生成し、単語パズル形式のリスニング問題を作成してください。

## 入力情報
- フレーズ: {phrase}
- 説明: {explanation}

## 出力形式
以下の形式で厳密に出力してください：

AudioText: [フレーズを含む自然な英文（TTS読み上げ用、1文）]
PuzzleWords: [AudioTextの単語をスペース区切りで（句読点は除く）]
Prompt: [ユーザーへの指示（日本語）]
Hint: [回答のヒント（日本語、30文字以内）]

## 生成ルール
1. AudioTextは与えられたフレーズを必ず含む自然な英文にする
2. AudioTextは1文で、5〜10単語程度の長さにする（パズルとして適切な難易度）
3. PuzzleWordsはAudioTextから句読点（.!?,）を除いた単語をスペースで区切る
4. Promptは「音声を聞いて、単語を正しい順番に並べてください」のような指示にする
5. Hintは文の構造や意味のヒントを示す

## 出力例
AudioText: I'm about to leave for the airport.
PuzzleWords: I'm about to leave for the airport
Prompt: 音声を聞いて、単語を正しい順番に並べてください
Hint: 「〜しようとしている」という表現に注目
"""


def get_listening_question_prompt(phrase: str, explanation: str) -> str:
    """リスニング問題生成用のプロンプトを返す"""
    return REVIEW_LISTENING_PROMPT.format(phrase=phrase, explanation=explanation)
