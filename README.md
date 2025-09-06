# AI English Learning App MVP

## 概要
パーソナライズされた英語学習アプリのMVP。インタラクティブな会話ラウンドと即時フィードバックを提供します。

## 主な機能
- パーソナライズ学習
- インタラクティブ会話ラウンド
- 即時フィードバック
- 徹底した復習システム

## 技術スタック
- **フロントエンド**: Next.js + TypeScript + Tailwind CSS
- **バックエンド**: FastAPI (Python, pydantic v2)
- **データベース**: PostgreSQL (開発時はSQLite)
- **API**: REST (OpenAPI自動生成)

## プロジェクト構成
```
AI_english_learning_app_mvp/
├── apps/
│   ├── web/          # Next.js フロントエンド
│   └── api/          # FastAPI バックエンド
├── infra/            # Docker, 環境設定, マイグレーション
├── docs/             # 要件定義, 設計書
└── README.md
```

## 開発環境セットアップ
1. リポジトリをクローン
2. 環境変数を設定 (`.env.example`を参考)
3. Docker Composeで開発環境を起動
4. フロントエンドとバックエンドを起動

## ライセンス
MIT
