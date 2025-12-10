"""復習用スピーキング・リスニング問題生成サービス"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Optional

import httpx

from app.core.config import settings
from app.prompts.review_speaking_question import get_speaking_question_prompt
from app.prompts.review_listening_question import get_listening_question_prompt

logger = logging.getLogger(__name__)

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/responses"


@dataclass
class GeneratedQuestion:
    """生成された問題"""
    question_type: str
    prompt: str
    hint: Optional[str] = None
    # スピーキング用: ユーザーが読み上げるターゲット文
    target_sentence: Optional[str] = None
    # リスニング用: TTS読み上げテキスト
    audio_text: Optional[str] = None
    # リスニング用: 単語パズル（正解順の単語リスト）
    puzzle_words: List[str] = field(default_factory=list)


class ReviewQuestionService:
    """復習用の問題を生成するサービス"""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(60.0, connect=5.0, read=60.0),
        )

    async def generate_speaking_question(
        self,
        phrase: str,
        explanation: str,
    ) -> GeneratedQuestion:
        """スピーキング問題を生成する"""
        prompt = get_speaking_question_prompt(phrase, explanation)
        content = await self._call_openai(prompt)
        return self._parse_speaking_response(content)

    async def generate_listening_question(
        self,
        phrase: str,
        explanation: str,
    ) -> GeneratedQuestion:
        """リスニング問題を生成する"""
        prompt = get_listening_question_prompt(phrase, explanation)
        content = await self._call_openai(prompt)
        return self._parse_listening_response(content)

    async def generate_both_questions(
        self,
        phrase: str,
        explanation: str,
    ) -> tuple[GeneratedQuestion, GeneratedQuestion]:
        """スピーキングとリスニング両方の問題を並列で生成する"""
        speaking_task = self.generate_speaking_question(phrase, explanation)
        listening_task = self.generate_listening_question(phrase, explanation)
        
        speaking, listening = await asyncio.gather(speaking_task, listening_task)
        return speaking, listening

    async def _call_openai(self, prompt: str) -> str:
        """OpenAI APIを呼び出す"""
        import json
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "model": settings.OPENAI_MODEL_NAME,
            "input": json.dumps(messages, ensure_ascii=False)
        }
        
        try:
            response = await self._client.post(OPENAI_CHAT_COMPLETIONS_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            texts: list[str] = []
            outputs = data.get("output", [])
            for out in outputs:
                contents = out.get("content") or []
                for item in contents:
                    t = item.get("type")
                    if t in ("output_text", "text"):
                        txt = item.get("text")
                        if txt:
                            texts.append(txt)
            
            content = "".join(texts)
            logger.info("OpenAI response for review question: %s", content[:200])
            return content
            
        except httpx.ReadTimeout as exc:
            logger.warning("OpenAI request timed out: %s", exc)
            raise TimeoutError("OpenAI request timed out") from exc
        except httpx.HTTPError as exc:
            logger.exception("HTTP error while calling OpenAI: %s", exc)
            raise
        except Exception as exc:
            logger.exception("Failed to generate review question via OpenAI: %s", exc)
            raise

    def _parse_speaking_response(self, content: str) -> GeneratedQuestion:
        """スピーキング問題のレスポンスをパースする"""
        lines = content.strip().splitlines()
        target_sentence = ""
        prompt = ""
        hint = None
        
        for line in lines:
            lower_line = line.lower()
            if lower_line.startswith("targetsentence:"):
                target_sentence = line.split(":", 1)[1].strip()
            elif lower_line.startswith("prompt:"):
                prompt = line.split(":", 1)[1].strip()
            elif lower_line.startswith("hint:"):
                hint = line.split(":", 1)[1].strip()
        
        if not target_sentence:
            target_sentence = "This is an example sentence."
        if not prompt:
            prompt = "以下の文を読み上げてください。"
        
        return GeneratedQuestion(
            question_type="speaking",
            prompt=prompt,
            hint=hint,
            target_sentence=target_sentence,
            audio_text=None,
            puzzle_words=[],
        )

    def _parse_listening_response(self, content: str) -> GeneratedQuestion:
        """リスニング問題のレスポンスをパースする"""
        lines = content.strip().splitlines()
        audio_text = ""
        puzzle_words_str = ""
        prompt = ""
        hint = None
        
        for line in lines:
            lower_line = line.lower()
            if lower_line.startswith("audiotext:"):
                audio_text = line.split(":", 1)[1].strip()
            elif lower_line.startswith("puzzlewords:"):
                puzzle_words_str = line.split(":", 1)[1].strip()
            elif lower_line.startswith("prompt:"):
                prompt = line.split(":", 1)[1].strip()
            elif lower_line.startswith("hint:"):
                hint = line.split(":", 1)[1].strip()
        
        if not audio_text:
            audio_text = "This is an example sentence."
        if not prompt:
            prompt = "音声を聞いて、単語を正しい順番に並べてください。"
        
        # 単語リストを生成
        if puzzle_words_str:
            puzzle_words = puzzle_words_str.split()
        else:
            # AudioTextから句読点を除去して単語リストを生成
            import re
            clean_text = re.sub(r'[.,!?;:]', '', audio_text)
            puzzle_words = clean_text.split()
        
        return GeneratedQuestion(
            question_type="listening",
            prompt=prompt,
            hint=hint,
            target_sentence=None,
            audio_text=audio_text,
            puzzle_words=puzzle_words,
        )

    async def close(self) -> None:
        """HTTPクライアントを閉じる"""
        await self._client.aclose()

    async def __aenter__(self) -> "ReviewQuestionService":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
