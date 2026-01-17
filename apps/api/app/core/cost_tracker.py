"""
API料金計算モジュール

OpenAI、Google Cloud Speech-to-Text、Text-to-Speechの
各APIリクエストごとの料金を計算してログ出力する。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import logging

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """サービスタイプ"""

    OPENAI = "openai"
    GROQ = "groq"
    GOOGLE_STT = "google_stt"
    GOOGLE_TTS = "google_tts"


# OpenAI料金（2024年12月時点、USD per 1K tokens）
OPENAI_PRICING = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}

# Groq料金（2024年12月時点、USD per 1K tokens）
# 注意: 正確な料金は https://console.groq.com/docs/pricing を参照
# gpt-oss-120bはOpenAIのオープンウェイトモデルでGroq経由で利用
GROQ_PRICING = {
    # OpenAI gpt-oss-120b (120Bパラメータ、推定料金)
    "openai/gpt-oss-120b": {"input": 0.00079, "output": 0.00099},
    # Llama 3.1 models
    "llama-3.1-405b-reasoning": {"input": 0.00079, "output": 0.00079},
    "llama-3.1-70b-versatile": {"input": 0.00059, "output": 0.00079},
    "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
    # Llama 3 models
    "llama3-70b-8192": {"input": 0.00059, "output": 0.00079},
    "llama3-8b-8192": {"input": 0.00005, "output": 0.00008},
    # Mixtral
    "mixtral-8x7b-32768": {"input": 0.00024, "output": 0.00024},
    # Gemma
    "gemma2-9b-it": {"input": 0.00020, "output": 0.00020},
}

# Google Cloud Speech-to-Text料金（USD per 15秒単位）
GOOGLE_STT_PRICE_PER_15_SEC = 0.006

# Google Cloud Text-to-Speech料金（USD per 1M文字）
GOOGLE_TTS_PRICE_PER_1M_CHARS = 4.00


@dataclass
class CostResult:
    """料金計算結果"""

    service: ServiceType
    cost_usd: float
    details: dict


def calculate_openai_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: Optional[int] = None,
) -> CostResult:
    """
    OpenAI APIの料金を計算してログ出力する。

    Args:
        model: モデル名（例: gpt-4o-mini）
        input_tokens: 入力トークン数
        output_tokens: 出力トークン数
        latency_ms: レイテンシ（ミリ秒）

    Returns:
        CostResult: 料金計算結果
    """
    pricing = OPENAI_PRICING.get(model, OPENAI_PRICING["gpt-4o-mini"])

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost

    details = {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_usd": round(input_cost, 8),
        "output_cost_usd": round(output_cost, 8),
    }
    if latency_ms is not None:
        details["latency_ms"] = latency_ms

    logger.info(
        "API cost calculated",
        extra={
            "service": ServiceType.OPENAI.value,
            "cost_usd": round(total_cost, 8),
            **details,
        },
    )

    return CostResult(
        service=ServiceType.OPENAI,
        cost_usd=total_cost,
        details=details,
    )


def calculate_groq_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: Optional[int] = None,
) -> CostResult:
    """
    Groq APIの料金を計算してログ出力する。

    Args:
        model: モデル名（例: openai/gpt-oss-120b, llama-3.1-70b-versatile）
        input_tokens: 入力トークン数
        output_tokens: 出力トークン数
        latency_ms: レイテンシ（ミリ秒）

    Returns:
        CostResult: 料金計算結果

    Note:
        料金は推定値です。最新の正確な料金は
        https://console.groq.com/docs/pricing を参照してください。
    """
    # デフォルトは gpt-oss-120b の料金を使用
    pricing = GROQ_PRICING.get(model, GROQ_PRICING["openai/gpt-oss-120b"])

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost

    details = {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_usd": round(input_cost, 8),
        "output_cost_usd": round(output_cost, 8),
    }
    if latency_ms is not None:
        details["latency_ms"] = latency_ms

    logger.info(
        "API cost calculated",
        extra={
            "service": ServiceType.GROQ.value,
            "cost_usd": round(total_cost, 8),
            **details,
        },
    )

    return CostResult(
        service=ServiceType.GROQ,
        cost_usd=total_cost,
        details=details,
    )


def calculate_google_stt_cost(
    audio_duration_seconds: float,
    latency_ms: Optional[int] = None,
) -> CostResult:
    """
    Google Cloud Speech-to-Text APIの料金を計算してログ出力する。

    Args:
        audio_duration_seconds: 音声の長さ（秒）
        latency_ms: レイテンシ（ミリ秒）

    Returns:
        CostResult: 料金計算結果
    """
    # 15秒単位で切り上げ
    billable_units = -(-int(audio_duration_seconds) // 15)  # ceiling division
    if billable_units < 1:
        billable_units = 1

    total_cost = billable_units * GOOGLE_STT_PRICE_PER_15_SEC

    details = {
        "audio_duration_seconds": round(audio_duration_seconds, 2),
        "billable_units_15sec": billable_units,
    }
    if latency_ms is not None:
        details["latency_ms"] = latency_ms

    logger.info(
        "API cost calculated",
        extra={
            "service": ServiceType.GOOGLE_STT.value,
            "cost_usd": round(total_cost, 8),
            **details,
        },
    )

    return CostResult(
        service=ServiceType.GOOGLE_STT,
        cost_usd=total_cost,
        details=details,
    )


def calculate_google_tts_cost(
    character_count: int,
    latency_ms: Optional[int] = None,
) -> CostResult:
    """
    Google Cloud Text-to-Speech APIの料金を計算してログ出力する。

    Args:
        character_count: 文字数
        latency_ms: レイテンシ（ミリ秒）

    Returns:
        CostResult: 料金計算結果
    """
    total_cost = (character_count / 1_000_000) * GOOGLE_TTS_PRICE_PER_1M_CHARS

    details = {
        "character_count": character_count,
    }
    if latency_ms is not None:
        details["latency_ms"] = latency_ms

    logger.info(
        "API cost calculated",
        extra={
            "service": ServiceType.GOOGLE_TTS.value,
            "cost_usd": round(total_cost, 8),
            **details,
        },
    )

    return CostResult(
        service=ServiceType.GOOGLE_TTS,
        cost_usd=total_cost,
        details=details,
    )
