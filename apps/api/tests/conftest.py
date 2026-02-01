import os
import sys
from pathlib import Path

# テスト環境ではCloud SQL Connectorを無効化
# これはSettingsクラスがインポートされる前に設定する必要がある
os.environ.setdefault("CLOUD_SQL_USE_CONNECTOR", "false")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ENVIRONMENT", "development")

# Make `app` and `models` importable even when pytest is invoked
# from the repository root (not from `apps/api`).
API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))
