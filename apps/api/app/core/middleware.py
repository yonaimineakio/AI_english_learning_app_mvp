"""
リクエストロギングミドルウェア

全リクエスト/レスポンスのログ出力、処理時間計測、リクエストID管理を行う。
"""
from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import get_logger, set_request_id

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    リクエストロギングミドルウェア

    - リクエストIDの生成と伝播
    - リクエスト/レスポンスのログ出力
    - 処理時間の計測
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # リクエストIDを生成（クライアントから渡された場合はそれを使用）
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        set_request_id(request_id)

        # リクエスト開始時刻
        start_time = time.perf_counter()

        # リクエスト情報をログ
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params) if request.query_params else None,
                "client_ip": request.client.host if request.client else None,
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            # 例外発生時のログ
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(
                "Request failed with exception",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

        # 処理時間を計算
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # レスポンスにリクエストIDを追加
        response.headers["X-Request-ID"] = request_id

        # レスポンス情報をログ
        log_level = "warning" if response.status_code >= 400 else "info"
        getattr(logger, log_level)(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response
