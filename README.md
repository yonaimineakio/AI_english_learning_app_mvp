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

## プロジェクト構成
```
AI_english_learning_app_mvp/
├── apps/
│   ├── web/          # Next.js フロントエンド
│   └── api/          # FastAPI バックエンド
│       ├── app/routers/audio/        # Google Speech-to-Text連携API
│       └── app/services/ai/google_speech_provider.py
├── infra/            # Docker, 環境設定, マイグレーション
├── docs/             # 要件定義, 設計書
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
cp infra/env/backend.env.example apps/api/.env

# 以下の値を実際の値に更新
# - OPENAI_API_KEY: OpenAI APIキー（会話生成用）
# - GOOGLE_CLOUD_PROJECT_ID: Google Cloud プロジェクトID（音声認識用）
# - GOOGLE_APPLICATION_CREDENTIALS: GoogleサービスアカウントJSONファイルへの絶対パス（バックエンドのみ）
# - GOOGLE_CLIENT_ID: Google OAuth クライアントID
# - GOOGLE_CLIENT_SECRET: Google OAuth クライアントシークレット
```

#### フロントエンド用環境変数
```bash
# apps/web/.env.local を作成
cp infra/env/frontend.env.example apps/web/.env.local

# 以下の値を実際の値に更新
# - NEXT_PUBLIC_GOOGLE_CLIENT_ID: Google OAuth クライアントID
```

### 3. 依存関係のインストール

#### バックエンド
```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Google Cloud Speech-to-Text SDK を利用するために環境変数を設定
export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/credentials.json
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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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

## 詳細なプロジェクト構成

### バックエンド (apps/api/)
```
apps/api/
├── app/                    # FastAPIアプリケーション本体
│   ├── api/               # APIエンドポイント定義
│   │   ├── v1/           # API v1エンドポイント
│   │   │   ├── auth.py   # 認証関連エンドポイント
│   │   │   ├── sessions.py # セッション管理エンドポイント
│   │   │   ├── reviews.py # 復習システムエンドポイント
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/             # コア設定・ユーティリティ
│   │   ├── config.py     # アプリケーション設定
│   │   ├── security.py   # セキュリティ関連（JWT、パスワードハッシュ）
│   │   ├── dependencies.py # 依存性注入
│   │   ├── exceptions.py # カスタム例外
│   │   └── __init__.py
│   ├── db/               # データベース関連
│   │   ├── base.py       # データベースベースクラス
│   │   ├── session.py    # データベースセッション管理
│   │   ├── init_db.py    # 初期データ投入
│   │   └── __init__.py
│   └── __init__.py
├── models/               # データモデル
│   ├── database/         # SQLAlchemyモデル
│   │   ├── user.py       # ユーザーモデル
│   │   ├── session.py    # セッションモデル
│   │   ├── session_round.py # セッションラウンドモデル
│   │   ├── review_item.py # 復習アイテムモデル
│   │   └── __init__.py
│   ├── schemas/          # Pydanticスキーマ
│   │   ├── user.py       # ユーザースキーマ
│   │   ├── session.py    # セッションスキーマ
│   │   ├── session_round.py # セッションラウンドスキーマ
│   │   ├── review_item.py # 復習アイテムスキーマ
│   │   └── __init__.py
│   └── __init__.py
├── routers/              # ルーター定義
│   ├── auth/             # 認証ルーター
│   │   ├── login.py      # ログイン
│   │   ├── register.py   # ユーザー登録
│   │   └── __init__.py
│   ├── sessions/         # セッションルーター
│   │   ├── start.py      # セッション開始
│   │   ├── turn.py       # 会話ターン
│   │   ├── extend.py     # セッション延長
│   │   ├── end.py        # セッション終了
│   │   └── __init__.py
│   ├── reviews/          # 復習ルーター
│   │   ├── next.py       # 次回復習取得
│   │   ├── complete.py   # 復習完了
│   │   └── __init__.py
│   └── __init__.py
├── services/             # ビジネスロジック
│   ├── ai/               # AI関連サービス
│   │   ├── openai_client.py # OpenAI API クライアント
│   │   ├── prompt_builder.py # プロンプト構築
│   │   ├── response_parser.py # レスポンス解析
│   │   └── __init__.py
│   ├── conversation/     # 会話関連サービス
│   │   ├── session_manager.py # セッション管理
│   │   ├── feedback_generator.py # フィードバック生成
│   │   ├── phrase_extractor.py # トップ3フレーズ抽出
│   │   └── __init__.py
│   ├── review/           # 復習関連サービス
│   │   ├── review_scheduler.py # 復習スケジューリング
│   │   ├── quiz_generator.py # クイズ生成
│   │   └── __init__.py
│   └── __init__.py
├── utils/                # ユーティリティ
│   ├── validators.py     # バリデーション関数
│   ├── helpers.py        # ヘルパー関数
│   ├── constants.py      # 定数定義
│   └── __init__.py
├── tests/                # テストファイル
│   ├── conftest.py       # pytest設定
│   ├── test_auth.py      # 認証テスト
│   ├── test_sessions.py  # セッションテスト
│   ├── test_reviews.py   # 復習テスト
│   └── __init__.py
├── main.py               # FastAPIアプリケーションエントリーポイント
├── requirements.txt      # Python依存関係
└── pyproject.toml        # プロジェクト設定
```

### API/app配下の詳細説明

#### `app/api/` - APIエンドポイント定義
- **v1/**: API v1のエンドポイントを定義
- **auth.py**: 認証関連のエンドポイント（ログイン、登録、トークン検証）
- **sessions.py**: セッション管理のエンドポイント（開始、進行、終了、延長）
- **reviews.py**: 復習システムのエンドポイント（復習取得、完了）

#### `app/core/` - コア設定・ユーティリティ
- **config.py**: アプリケーション全体の設定（データベース、JWT、外部API等）
- **security.py**: セキュリティ関連（JWT生成・検証、パスワードハッシュ化）
- **dependencies.py**: FastAPIの依存性注入（認証、データベースセッション等）
- **exceptions.py**: カスタム例外クラス定義

#### `app/db/` - データベース関連
- **base.py**: SQLAlchemyのベースクラスと共通設定
- **session.py**: データベースセッションの管理と接続プール
- **init_db.py**: 初期データの投入とデータベース初期化

### 各ディレクトリの役割

1. **models/**: データの構造定義
   - `database/`: SQLAlchemyモデル（データベーステーブル定義）
   - `schemas/`: Pydanticスキーマ（API リクエスト/レスポンス定義）

2. **routers/**: エンドポイントのルーティング
   - 各機能ごとにディレクトリを分割
   - 認証、セッション、復習の3つの主要機能

3. **services/**: ビジネスロジック
   - `ai/`: AI機能（OpenAI API統合、プロンプト管理）
   - `conversation/`: 会話機能（セッション管理、フィードバック生成）
   - `review/`: 復習機能（スケジューリング、クイズ生成）

4. **utils/**: 共通ユーティリティ
   - バリデーション、ヘルパー関数、定数定義

5. **tests/**: テストファイル
   - 各機能のユニットテストと統合テスト
