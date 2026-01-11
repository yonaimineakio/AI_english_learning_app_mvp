FROM python:3.12-slim

WORKDIR /app

# uv をインストール（バイナリコピーで高速化）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 依存関係ファイルをコピー
COPY pyproject.toml uv.lock ./

# 依存関係をインストール（本番環境ではdevグループを除外）
RUN uv sync --frozen --no-dev --no-install-project

# アプリケーションコードをコピー
COPY app/ ./app/
COPY models/ ./models/
COPY alembic/ ./alembic/
COPY alembic.ini ./

EXPOSE 8080
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Cloud Run の PORT を確実に拾う
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
