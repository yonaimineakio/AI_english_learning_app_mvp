"""
共通ロギング設定

JSON形式の構造化ロギングを提供する。
リクエストIDの伝播やログレベルの環境変数制御をサポート。
"""
from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from pythonjsonlogger import jsonlogger

from app.core.config import settings

# リクエストIDを保持するコンテキスト変数
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """カスタムJSONフォーマッター"""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # タイムスタンプをISO形式で追加
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        log_record["level"] = record.levelname
        log_record["logger"] = record.name

        # リクエストIDがあれば追加
        request_id = request_id_var.get()
        if request_id:
            log_record["request_id"] = request_id


def setup_logging() -> None:
    """
    アプリケーション全体のロギング設定を初期化する。
    JSON形式のログを標準出力に出力する。
    """
    # ログレベルを環境変数から取得（デフォルトはINFO）
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 既存のハンドラをクリア
    root_logger.handlers.clear()

    # JSONフォーマッターを設定
    formatter = CustomJsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "name": "logger"},
    )

    # 標準出力ハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # uvicornとfastapiのログレベルを調整
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    # SQLAlchemyのログを抑制（本番では特に重要）
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    名前付きロガーを取得する。
    
    Args:
        name: ロガー名（通常は __name__ を使用）
    
    Returns:
        設定済みのロガー
    """
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """リクエストIDをコンテキストに設定する"""
    request_id_var.set(request_id)


def get_request_id() -> str | None:
    """現在のリクエストIDを取得する"""
    return request_id_var.get()