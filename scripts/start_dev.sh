#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/apps/api"
FRONTEND_DIR="$ROOT_DIR/apps/web"
VENV_DIR="$ROOT_DIR/venv"

PIDS=()

cleanup() {
  if (( ${#PIDS[@]} )); then
    echo ""
    echo "Shutting down services..."
    for pid in "${PIDS[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
      fi
    done
    wait "${PIDS[@]}" 2>/dev/null || true
  fi
}

trap cleanup EXIT

start_backend() {
  echo "Starting FastAPI backend..."
  (
    cd "$BACKEND_DIR"
    if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
      # shellcheck disable=SC1091
      source "$VENV_DIR/bin/activate"
    fi
    exec python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ) &
  PIDS+=($!)
}

start_frontend() {
  echo "Starting Next.js frontend..."
  (
    cd "$FRONTEND_DIR"
    exec npm run dev
  ) &
  PIDS+=($!)
}

start_backend
start_frontend

EXIT_CODE=0
for pid in "${PIDS[@]}"; do
  if ! wait "$pid"; then
    EXIT_CODE=$?
  fi
done

exit $EXIT_CODE

