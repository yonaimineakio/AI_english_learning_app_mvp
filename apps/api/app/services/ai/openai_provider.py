from __future__ import annotations

import asyncio
from typing import List

import httpx

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.cost_tracker import calculate_openai_cost
from models.schemas.schemas import DifficultyLevel, ScenarioCategory

from .types import ConversationProvider, ConversationResponse
from app.prompts import (
    get_prompt_by_category_difficulty,
    get_prompt_by_scenario_id,
    get_conversation_system_prompt,
)
import json

logger = get_logger(__name__)


class OpenAIConversationProvider(ConversationProvider):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            # 全体60秒、接続5秒、読み取り60秒に延長
            timeout=httpx.Timeout(60.0, connect=5.0, read=60.0),
        )

    async def generate_response(
        self,
        user_input: str,
        difficulty: str,
        scenario_category: str,
        round_index: int,
        context: List[dict],
        scenario_id: int | None = None,
        custom_system_prompt: str | None = None,
        goals_info: dict | None = None,
    ) -> ConversationResponse:
        start_time = asyncio.get_event_loop().time()
        logger.info(
            "OpenAI request payload: user_input=%s, difficulty=%s, "
            "scenario_category=%s, round_index=%s, scenario_id=%s, context=%s, custom_prompt=%s",
            user_input,
            difficulty,
            scenario_category,
            round_index,
            scenario_id,
            context,
            "provided" if custom_system_prompt else "none",
        )
        payload = self._build_request_payload(
            user_input=user_input,
            difficulty=difficulty,
            scenario_category=scenario_category,
            context=context,
            scenario_id=scenario_id,
            custom_system_prompt=custom_system_prompt,
        )

        try:
            response = await self._client.post(
                settings.OPENAI_CHAT_COMPLETIONS_URL, json=payload
            )
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

            # トークン使用量を取得して料金計算
            usage = data.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

            if input_tokens > 0 or output_tokens > 0:
                calculate_openai_cost(
                    model=settings.OPENAI_MODEL_NAME,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms,
                )

            logger.info("OpenAI response: %s", content)
            (
                ai_reply,
                feedback_short,
                improved_sentence,
                should_end_session,
            ) = self._parse_response(content)
        except httpx.ReadTimeout as exc:
            # OpenAI側のタイムアウトはアプリ側で扱いやすいように TimeoutError にラップして伝播させる
            logger.warning("OpenAI request timed out: %s", exc)
            raise TimeoutError("OpenAI request timed out") from exc
        except httpx.HTTPError as exc:
            logger.exception("HTTP error while calling OpenAI: %s", exc)
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to generate AI response via OpenAI: %s", exc)
            raise

        tags = ["conversation", f"round_{round_index}", difficulty] + [
            scenario_category
        ]
        latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        details = {"explanation": None, "suggestions": None}
        scores = None

        return ConversationResponse(
            ai_reply=ai_reply,
            feedback_short=feedback_short[:120],
            improved_sentence=improved_sentence,
            tags=tags,
            details=details,
            scores=scores,
            latency_ms=latency_ms,
            provider="openai",
            should_end_session=should_end_session,
        )

    def _build_request_payload(
        self,
        user_input: str,
        difficulty: str,
        scenario_category: str,
        context: List[dict],
        scenario_id: int | None = None,
        custom_system_prompt: str | None = None,
    ) -> dict:
        # カスタムシナリオの場合は、渡されたプロンプトを使用
        if custom_system_prompt:
            system_prompt = custom_system_prompt
        else:
            # まずシナリオIDに対応するプロンプトを優先的に使用する（一対一対応）
            system_prompt = None
            if scenario_id is not None:
                system_prompt = get_prompt_by_scenario_id(scenario_id)

            # シナリオIDで取得できなかった場合は、カテゴリ×難易度でのプロンプトにフォールバック
            if not system_prompt:
                system_prompt = (
                    get_prompt_by_category_difficulty(scenario_category, difficulty) or ""
                )
        messages = [{"role": "assistant", "content": system_prompt}]

        for turn in context[-2:]:  # Include last two rounds as context
            messages.extend(
                [
                    {"role": "user", "content": turn.get("user_input", "")},
                    {"role": "assistant", "content": turn.get("ai_reply", "")},
                ]
            )

        # 会話システムプロンプト（外部ファイルから取得）
        conversation_prompt = get_conversation_system_prompt(
            difficulty=difficulty,
            user_input=user_input,
        )
        messages.append(
            {
                "role": "assistant",
                "content": conversation_prompt,
            }
        )

        return {
            "model": settings.OPENAI_MODEL_NAME,
            "input": json.dumps(messages, ensure_ascii=False),
        }

    def _parse_response(self, content: str) -> tuple[str, str, str, bool]:
        """
        Returns: (ai_reply, feedback_short, improved_sentence, should_end_session)
        """
        lines = content.strip().splitlines()
        ai_reply = ""
        feedback_short = ""
        improved_sentence = ""
        should_end_session = False

        # [END_SESSION]マーカーの検知
        if "[END_SESSION]" in content:
            should_end_session = True
            content = content.replace("[END_SESSION]", "").strip()
            lines = content.strip().splitlines()

        for line in lines:
            if line.lower().startswith("ai:"):
                ai_reply = line.split(":", 1)[1].strip()
            elif line.lower().startswith("feedback:"):
                feedback_short = line.split(":", 1)[1].strip()
            elif line.lower().startswith("improved:"):
                improved_sentence = line.split(":", 1)[1].strip()

        if not ai_reply:
            ai_reply = content.strip()
        if not feedback_short:
            feedback_short = "改善点を120字以内で記述してください。"
        if not improved_sentence:
            improved_sentence = "Please provide an improved sentence."

        return ai_reply, feedback_short, improved_sentence, should_end_session

    async def __aenter__(self) -> OpenAIConversationProvider:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._client.aclose()


async def warm_up_provider() -> None:
    if not settings.OPENAI_API_KEY:
        return
    provider = OpenAIConversationProvider()
    try:
        await provider.generate_response(
            user_input="Hello",
            difficulty=DifficultyLevel.INTERMEDIATE.value,
            scenario_category=ScenarioCategory.BUSINESS.value,
            round_index=1,
            context=[],
            scenario_id=2,
        )
    except Exception:  # noqa: BLE001
        logger.info("OpenAI warm-up failed (expected if key invalid)")
    finally:
        await provider._client.aclose()
