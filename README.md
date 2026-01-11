# AI English Learning App MVP

## 概要
パーソナライズされた英語学習アプリのMVP。インタラクティブな会話ラウンドと即時フィードバックを提供します。

## 主な機能
- パーソナライズ学習
- インタラクティブ会話ラウンド
- 即時フィードバック
- 徹底した復習システム
- 音声録音＆自動文字起こし（Google Speech-to-Text）
- 5秒無音での自動停止と手動停止ボタンを備えた録音UI
- 文字起こし結果と信頼度スコアの表示、代替候補の取得

## 技術スタック
- **フロントエンド**: Next.js + TypeScript + Tailwind CSS
- **バックエンド**: FastAPI (Python, pydantic v2)
- **データベース**: PostgreSQL (開発時はSQLite)
- **API**: REST (OpenAPI自動生成)
- **音声認識**: Google Cloud Speech-to-Text

## アーキテクチャ
このアプリは**レイヤードアーキテクチャ + サービス層パターン**を採用しています。

詳細は [📚 アーキテクチャドキュメント](./docs/architecture.md) を参照してください。

**4層構造：**
- Presentation Layer (Router)
- Business Logic Layer (Service)
- Data Access Layer (Models)
- Infrastructure Layer (DB, External APIs)

## プロジェクト構成（現在）

```
AI_english_learning_app_mvp/
├── apps/
│   ├── web/                  # Next.js フロントエンド
│   │   └── src/
│   │       ├── app/          # App Router ページ
│   │       │   ├── page.tsx                  # ルート（シナリオ選択 or レベルテストへの分岐）
│   │       │   ├── login/                    # ログイン画面
│   │       │   ├── (app)/placement/          # レベル判定テストページ
│   │       │   ├── (app)/sessions/[sessionId]/ # 会話セッション画面
│   │       │   ├── (app)/summary/            # セッションサマリー
│   │       │   └── review/                   # 復習ページ
│   │       ├── components/   # UIコンポーネント群（会話UI・シナリオカードなど）
│   │       ├── hooks/        # `use-session-conversation` などのカスタムフック
│   │       ├── lib/          # APIクライアント・シナリオ定義・TTSヘルパーなど
│   │       ├── contexts/     # 認証コンテキスト
│   │       └── types/        # 型定義
│   └── api/                  # FastAPI バックエンド
│       ├── app/
│       │   ├── main.py       # FastAPI アプリ本体（ルーター登録など）
│       │   ├── core/         # 設定・認証ヘルパー
│       │   ├── db/           # DB セッション・初期化
│       │   ├── prompts/      # シナリオ別システムプロンプト
│       │   ├── routers/      # ルーター定義
│       │   │   ├── auth/     # 認証（/auth/me, /auth/token など）
│       │   │   ├── sessions/ # セッション開始・ターン処理・終了・延長
│       │   │   ├── reviews/  # 復習（/reviews/next, /reviews/{id}/complete）
│       │   │   ├── audio/    # 音声認識・TTS（/audio/transcribe, /audio/tts）
│       │   │   └── placement/# レベル判定テスト（/placement/questions, /placement/submit）
│       │   └── services/
│       │       ├── ai/       # OpenAI / Google Speech / Google TTS プロバイダ
│       │       ├── conversation/ # セッションビジネスロジック
│       │       └── review/   # 復習ビジネスロジック
│       ├── models/
│       │   ├── database/     # SQLAlchemy モデル（users, sessions, session_rounds, review_items など）
│       │   └── schemas/      # Pydantic スキーマ
│       ├── tests/            # pytest テスト
│       └── app.db            # 開発用 SQLite DB
├── infra/                    # Docker, 環境設定, マイグレーション
├── docs/                     # 要件定義, 設計書
└── README.md
```

## 開発環境セットアップ

### 1. リポジトリをクローン
```bash
git clone <repository-url>
cd AI_english_learning_app_mvp
```

### 2. 環境変数を設定

#### バックエンド用環境変数
```bash
# apps/api/.env を作成
cp apps/api/.env.example apps/api/.env

# 以下の値を実際の値に更新
# - OPENAI_API_KEY: OpenAI APIキー（会話生成用）
# - GOOGLE_CLOUD_PROJECT_ID: Google Cloud プロジェクトID（音声認識用）
# - GOOGLE_APPLICATION_CREDENTIALS: ローカルでサービスアカウントキーJSONを使う場合のみ（Cloud Runでは通常不要）
# - DEBUG: true=モックログイン / false=Google認証ログイン
# - GOOGLE_CLIENT_ID: Google OAuth クライアントID
# - GOOGLE_CLIENT_SECRET: Google OAuth クライアントシークレット
```

#### フロントエンド用環境変数
```bash
# apps/web/.env.local を作成
cp apps/web/.env.local.example apps/web/.env.local

# 以下の値を実際の値に更新
# - NEXT_PUBLIC_API_BASE_URL: バックエンドURL（/api/v1 まで含める）
```

### 3. 依存関係のインストール

#### バックエンド
```bash
cd apps/api

# uv を使った依存管理（推奨）
# インストール例:
# - macOS: brew install uv
# - それ以外: 公式手順（astral/uv）に従ってインストール
#
# 依存関係を lockfile から再現（dev も含める）
uv sync --extra dev --frozen

# Google Cloud (Speech-to-Text / Text-to-Speech) 認証は以下どちらか
# A) サービスアカウントキーJSONを使う（ローカルのみ推奨）
# export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/credentials.json
# B) ADC を使う（推奨）
# gcloud auth application-default login
# gcloud auth application-default set-quota-project your_project_id
export GOOGLE_CLOUD_PROJECT_ID=your_project_id
```

#### フロントエンド
```bash
cd apps/web
npm install

# サービスアカウントの認証情報はバックエンドでのみ利用します。
# フロントエンド側でGoogle Cloudの秘密情報を扱う必要はありません。
# フロントエンドはブラウザ標準APIで録音し、バックエンドへBlobを送信します。
```

### 4. 開発サーバーの起動

#### バックエンド
```bash
cd apps/api
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### TTS 動作確認（ローカル）
```bash
cd apps/api
uv run python -m app.scripts.tts_smoke --text "Hello, this is a test." --out ./tts_output.mp3
```

#### フロントエンド
```bash
cd apps/web
npm run dev
```

### 5. アクセス
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## ライセンス
MIT

## 詳細なプロジェクト構成（簡易版）

### バックエンド (apps/api/)

- `app/main.py`  
  - FastAPI アプリのエントリーポイント。CORS 設定とルーター登録（/auth, /sessions, /reviews, /audio, /placement）を行う。
- `app/core/`  
  - `config.py`: 設定（DB, JWT, OpenAI, Google Cloud など）  
  - `deps.py`: 依存関係（`get_db`, `get_current_user` など）  
  - `security.py`: JWT 発行・検証
- `app/db/`  
  - `session.py`: DB セッション管理  
  - `init_db.py`: 初期シナリオなどの投入
- `app/routers/`  
  - `auth/auth.py`: `/auth/me`, `/auth/token`, Google OAuth コールバックなど  
  - `sessions/sessions.py`: `/sessions/start`, `/sessions/{id}/turn`, `/sessions/{id}/end`, `/sessions/{id}/extend`  
  - `reviews/reviews.py`: `/reviews/next`, `/reviews/{id}/complete`  
  - `audio/audio.py`: `/audio/transcribe`（音声→テキスト）, `/audio/tts`（テキスト→音声）  
  - `placement/placement.py`: `/placement/questions`, `/placement/submit`（レベル判定テスト）
- `app/services/`  
  - `ai/`: OpenAIプロバイダ、Google Speech-to-Text, Google Text-to-Speech, モックプロバイダなど  
  - `conversation/session_service.py`: 会話セッションのビジネスロジック（ターン処理・自動終了・サマリー生成）  
  - `review/review_service.py`: 復習用フレーズ生成・スケジューリング
- `models/`  
  - `database/models.py`: `User`, `Session`, `SessionRound`, `ReviewItem`, `Scenario` テーブル定義  
  - `schemas/schemas.py`: Pydanticスキーマ（`SessionStartResponse`, `TurnResponse`, `SessionStatusResponse` など）
- `tests/`  
  - `test_prompt_mapping.py`: シナリオIDとプロンプトのマッピング検証

### フロントエンド (apps/web/)

- `src/app/`  
  - `page.tsx`: ルート。ログイン済みユーザーの `placement_completed_at` を見て `/placement` かシナリオ選択に振り分ける。  
  - `login/page.tsx`: ログイン画面。`useAuth` と `LoginButton` を利用。  
  - `(app)/placement/page.tsx`: レベル判定テスト（20問の自己評価＋Listening問題TTS）。  
  - `(app)/sessions/[sessionId]/page.tsx`: 会話セッション画面。会話ログ、延長モーダル、音声録音UIなど。  
  - `(app)/summary/page.tsx`: セッション終了後のサマリー画面。トップ3フレーズなどを表示。  
  - `review/page.tsx`: 復習クイズ画面。`/reviews/next` と `/reviews/{id}/complete` を使用。
- `src/components/`  
  - `scenario/`: シナリオ選択UI（カード一覧、カテゴリフィルタ、詳細モーダル、ラウンドセレクタなど）。  
  - `conversation/conversation-turn.tsx`: 1ターン分の会話UI（ユーザー発話＋AI応答＋フィードバック＋TTSボタン）。  
  - `audio/audio-recorder.tsx`: 音声録音と `/audio/transcribe` への送信。  
  - `session/extend-modal.tsx`: ラウンド完了時・自動終了時の延長/終了/復習モーダル。  
  - `layout/app-shell.tsx`: 共通レイアウト（ヘッダー・フッター）。  
  - `auth/*`: 認証UI（ログイン/ログアウトボタン、AuthGuard など）。
- `src/hooks/`  
  - `use-session-conversation.ts`: 会話セッション用のメインフック。ターン送信、ステータス取得、自動終了検知など。  
  - `use-audio-recording.ts`: ブラウザ録音処理。  
  - `use-auth.ts`: 認証コンテキストの薄いラッパー。
- `src/lib/`  
  - `api-client.ts`: 認証付き `fetch` ラッパー（401時にログアウト）。  
  - `session.ts`: セッション関連APIクライアント（`startSession`, `submitTurn`, `extendSession`, `endSession`）。  
  - `scenarios.ts`: フロント側のシナリオ定義（カテゴリ・難易度・学習ゴール・キーフレーズなど）。  
  - `placement.ts`: レベルテストAPIクライアント（`fetchPlacementQuestions`, `submitPlacementAnswers`）。  
  - `tts.ts`: Text-to-Speech クライアント (`playTextWithTts`)。  
  - `utils.ts`: 各種ユーティリティ関数。
