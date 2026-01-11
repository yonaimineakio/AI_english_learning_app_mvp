# ログ関連実装方針

## 概要

FastAPIバックエンドに共通のロギング機構とAPI料金計算機能を実装しました。本ドキュメントでは実装方針と使用方法を説明します。

---

## 1. ロギングアーキテクチャ

### 1.1 設計方針

- **JSON形式の構造化ログ**: 将来的なログ分析・監視ツールとの連携を考慮
- **標準出力への出力**: コンテナ環境でのログ収集に対応
- **リクエストIDによるトレーシング**: リクエスト単位でのログ追跡を可能に
- **環境変数によるログレベル制御**: 本番/開発環境での切り替え

### 1.2 ファイル構成

```
apps/api/app/core/
├── config.py           # 既存の設定
├── logging_config.py   # ロギング設定（新規）
├── middleware.py       # リクエストロギングミドルウェア（新規）
└── cost_tracker.py     # API料金計算（新規）
```

---

## 2. 共通ロギング設定

### 2.1 `logging_config.py`

| 機能 | 説明 |
|------|------|
| `setup_logging()` | アプリ起動時にロギングを初期化 |
| `get_logger(name)` | 名前付きロガーを取得 |
| `set_request_id(id)` | リクエストIDをコンテキストに設定 |
| `get_request_id()` | 現在のリクエストIDを取得 |

### 2.2 使用方法

```python
from app.core.logging_config import get_logger

logger = get_logger(__name__)

logger.info("処理を開始", extra={"user_id": 123, "action": "start"})
```

### 2.3 ログ出力フォーマット

```json
{
  "timestamp": "2025-12-23T10:30:00Z",
  "level": "INFO",
  "logger": "app.services.session_service",
  "message": "処理を開始",
  "request_id": "abc123",
  "user_id": 123,
  "action": "start"
}
```

---

## 3. リクエストロギングミドルウェア

### 3.1 `middleware.py`

全HTTPリクエストに対して以下を自動実行:

1. **リクエストID生成**: `X-Request-ID`ヘッダーがあれば使用、なければ自動生成
2. **リクエスト開始ログ**: メソッド、パス、クエリ、クライアントIPを記録
3. **処理時間計測**: リクエスト処理にかかった時間を計測
4. **レスポンスログ**: ステータスコード、処理時間を記録

### 3.2 自動出力されるログ

```json
// リクエスト開始
{
  "timestamp": "2025-12-23T10:30:00Z",
  "level": "INFO",
  "message": "Request started",
  "request_id": "abc123",
  "method": "POST",
  "path": "/api/v1/sessions/1/turn",
  "client_ip": "192.168.1.1"
}

// リクエスト完了
{
  "timestamp": "2025-12-23T10:30:02Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "abc123",
  "method": "POST",
  "path": "/api/v1/sessions/1/turn",
  "status_code": 200,
  "duration_ms": 2150
}
```

---

## 4. API料金計算機能

### 4.1 `cost_tracker.py`

外部APIの利用料金をリアルタイムで計算・ログ出力します。

### 4.2 対応サービスと料金体系

#### OpenAI

| モデル | 入力 (USD/1K tokens) | 出力 (USD/1K tokens) |
|--------|---------------------|---------------------|
| gpt-4o-mini | $0.00015 | $0.0006 |
| gpt-4o | $0.0025 | $0.01 |
| gpt-4-turbo | $0.01 | $0.03 |
| gpt-3.5-turbo | $0.0005 | $0.0015 |

#### Groq

| モデル | 入力 (USD/1K tokens) | 出力 (USD/1K tokens) |
|--------|---------------------|---------------------|
| openai/gpt-oss-120b | $0.00079 | $0.00099 |
| llama-3.1-405b-reasoning | $0.00079 | $0.00079 |
| llama-3.1-70b-versatile | $0.00059 | $0.00079 |
| llama-3.1-8b-instant | $0.00005 | $0.00008 |
| llama3-70b-8192 | $0.00059 | $0.00079 |
| llama3-8b-8192 | $0.00005 | $0.00008 |
| mixtral-8x7b-32768 | $0.00024 | $0.00024 |
| gemma2-9b-it | $0.00020 | $0.00020 |

#### Google Cloud

| サービス | 単位 | 料金 (USD) |
|----------|------|------------|
| Speech-to-Text | 15秒単位 | $0.006 |
| Text-to-Speech | 1M文字 | $4.00 |

### 4.3 使用方法

```python
from app.core.cost_tracker import (
    calculate_openai_cost,
    calculate_groq_cost,
    calculate_google_stt_cost,
    calculate_google_tts_cost,
)

# OpenAI
calculate_openai_cost(
    model="gpt-4o-mini",
    input_tokens=150,
    output_tokens=80,
    latency_ms=1200,
)

# Groq
calculate_groq_cost(
    model="llama-3.1-70b-versatile",
    input_tokens=150,
    output_tokens=80,
    latency_ms=500,
)

# Google Speech-to-Text
calculate_google_stt_cost(
    audio_duration_seconds=12.5,
    latency_ms=800,
)

# Google Text-to-Speech
calculate_google_tts_cost(
    character_count=200,
    latency_ms=300,
)
```

### 4.4 料金計算ログ出力例

```json
{
  "timestamp": "2025-12-23T10:30:01Z",
  "level": "INFO",
  "message": "API cost calculated",
  "request_id": "abc123",
  "service": "openai",
  "model": "gpt-4o-mini",
  "input_tokens": 150,
  "output_tokens": 80,
  "total_tokens": 230,
  "input_cost_usd": 0.0000225,
  "output_cost_usd": 0.000048,
  "cost_usd": 0.0000705,
  "latency_ms": 1200
}
```

---

## 5. 実装済みプロバイダー

以下のプロバイダーに料金計算ログを統合済み:

| プロバイダー | ファイル | 計算方法 |
|-------------|----------|----------|
| OpenAI | `openai_provider.py` | レスポンスの`usage`フィールドからトークン数取得 |
| Groq | `groq_provider.py` | レスポンスの`usage`フィールドからトークン数取得 |
| Google STT | `google_speech_provider.py` | 音声ファイルの長さを推定して計算 |
| Google TTS | `google_tts_provider.py` | 入力文字数から計算 |

---

## 6. 環境設定

### 6.1 ログレベル制御

`config.py`の`DEBUG`設定でログレベルが変わります:

- `DEBUG=True`: DEBUG レベル（開発環境）
- `DEBUG=False`: INFO レベル（本番環境）

### 6.2 依存パッケージ

```
python-json-logger>=2.0.7
```

インストール:
```bash
pip install python-json-logger
```

---

## 7. 今後の拡張案

- [ ] ログの外部サービス連携（CloudWatch, Datadog等）
- [ ] 料金データのDB保存と集計ダッシュボード
- [ ] アラート設定（異常な料金増加の検知）
- [ ] ユーザー別の利用料金トラッキング

