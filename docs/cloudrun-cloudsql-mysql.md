# Cloud Run + Cloud SQL(MySQL) セットアップ手順（MVP）

本ドキュメントは、本番環境で **Cloud Run(FastAPI)** から **Cloud SQL for MySQL** に接続するための最小手順です。

## 前提

- Cloud SQL: MySQL 8.0
- Cloud Run: 同一リージョン
- 接続方式: **cloud-sql-python-connector を使用**（アプリ内で安全に接続を確立）

## 1. Cloud SQL（MySQL）を用意

- インスタンスを作成（例: `asia-northeast1`）
- DB（例: `ai_english_learning`）を作成
- アプリ用ユーザーを作成（最小権限）
- 自動バックアップを有効化（可能ならPITRも）

※ `INSTANCE_CONNECTION_NAME` は `PROJECT_ID:REGION:INSTANCE_ID` 形式です。

## 2. Secret Manager を用意

### 推奨: DB接続情報を Secret として持つ（Connector方式）

Connector方式では、`DATABASE_URL` にUnixソケットURLを入れる必要はありません。
Cloud Runの環境変数（またはSecret参照）で以下を注入します。

- `CLOUD_SQL_USE_CONNECTOR=true`
- `CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_ID`
- `DB_NAME=ai_english_learning`
- `DB_USER=...`
- `DB_PASSWORD=...`（IAM DB Auth を使う場合は不要にできます）
- `CLOUD_SQL_IP_TYPE=private`（既定。publicにする場合は `public`）
- `CLOUD_SQL_ENABLE_IAM_AUTH=false`（IAM DB Auth を使うなら `true`）

補足:
- `CLOUD_SQL_IP_TYPE=private` の場合、Cloud Runが対象VPCへ到達できるネットワーク経路（Serverless VPC Access等）が必要です。

### 追加（任意）: 接続プールを小さくする

Cloud Runは水平スケールするため、アプリ側のpoolを小さくして Cloud SQL の接続枯渇を避けます。

- `DB_POOL_SIZE`（既定: 5）
- `DB_MAX_OVERFLOW`（既定: 0）
- `DB_POOL_TIMEOUT`（既定: 30）
- `DB_POOL_RECYCLE`（既定: 1800）

## 3. Cloud Run サービスアカウント権限

Cloud Runの実行サービスアカウントに以下を付与します。

- Cloud SQL Client（Cloud SQLへ接続）
- Secret Manager Secret Accessor（Secret参照）

## 4. Cloud Run へデプロイ（設定）

Cloud Runに以下を設定します。

- 環境変数（`CLOUD_SQL_*`, `DB_*`）をSecretから注入
-（任意）`DB_POOL_*` を環境変数で設定

補足:
- Connector方式では Cloud SQLのアタッチ（Unixソケット前提の設定）は不要です。

## 5. 動作確認（疎通）

Cloud Runへデプロイ後、以下が満たされればOKです。

- 起動時にDB接続エラーが出ない
- APIの主要フローが成功する（`/sessions/start` → `/turn` → `/end` → `/reviews/next`）



