# MVP仕様サマリ（会話セッション中心）

本ドキュメントは、英会話学習アプリMVPの仕様を「会話セッション」「即時フィードバック」「復習」を中心に一枚に集約したものです。  
詳細は `docs/` 配下の各ドキュメントに分割して拡張していく前提で、ここでは **MVPの判断基準になる要点** を優先してまとめます。

---

### 1. プロダクト方針 / MVPの価値

- **価値の柱**: ①パーソナライズ学習 ②インタラクティブ会話ラウンド ③即時フィードバック ④徹底した復習
- **スコープ外（MVPではやらない）**:
  - 高度な発音採点
  - 大量のシナリオ
  - マルチ言語UI
  - （原則）モバイルアプリの本格提供

---

### 2. 画面/学習フロー（ハッピーパス）

- ログイン → シナリオ選択 → 設定（難易度/ラウンド数） → 会話 → 終了 → 翌日復習

参照:
- `docs/web-screen-structure.md`（Web版画面構成と遷移）
- `docs/auth-flow.md`（認証フロー）

---

### 3. ドメイン仕様（会話セッション）

#### 3.1 シナリオカテゴリ

- カテゴリ: **旅行 / ビジネス / 日常会話**

#### 3.2 ラウンド定義

- **1ラウンド** = ユーザー発話 → AI応答 → フィードバック

#### 3.3 ラウンド数設定

- プリセット:
  - Quick = 4
  - Standard = 6
  - Deep = 10
- 自由設定:
  - 4〜12ラウンド（下限4）
- 規定到達時:
  - **「+3ラウンド延長」**を提示（必要に応じて続行）

#### 3.4 即時フィードバック（各ラウンド）

- **短評（1〜2行）** + **改善例1文**
- 制約:
  - `feedback_short`: **120字以内**
  - `improved_sentence`: **1文のみ**
- UX:
  - 会話UIでは **改善例1文のみを必ず表示**
  - 詳細説明は折りたたみ（必要な場合のみ）

---

### 4. 復習（セッション終了時/翌日）

- セッション終了時に **「改善トップ3フレーズ」** を保存
- 翌日冒頭に **クイズ形式**で提示

---

### 5. 連続学習日数（Streak）仕様（現状実装）

本MVPでは「学習した日」の判定は **“セッションを終了した日”** を採用しています。

- **更新タイミング**: セッション終了（`/sessions/{id}/end`）時に更新
- **日付の基準**: **Asia/Tokyo（JST）の当日 `date`**
- **判定ロジック（要約）**:
  - 初回（`last_activity_date` が未設定）: `current_streak = 1`, `longest_streak = 1`
  - 同日（`last_activity_date == activity_date`）: 変更なし（同日に何回終了しても増えない）
  - 連続（`last_activity_date == activity_date - 1日`）: `current_streak += 1`（必要なら `longest_streak` 更新）
  - それ以外（2日以上空いた）: `current_streak = 1` にリセット

実装参照:
- `apps/api/app/services/streak/streak_service.py`
- `apps/api/app/services/conversation/session_service.py`（セッション終了時にJST日付で更新）

---

### 6. API契約（MVP）

セッション中心のAPI（最小セット）は以下です。

- `POST /sessions/start` : セッション開始
- `POST /sessions/{id}/turn` : 発話送信 → AI応答 + フィードバック返却
- `POST /sessions/{id}/extend` : ラウンド延長
- `POST /sessions/{id}/end` : セッション終了 → トップ3フレーズ返却
- `GET /reviews/next` : 翌日の復習フレーズ取得

補足:
- OpenAPI自動生成（FastAPI）を前提
- 実装は `apps/api/app/routers/` 配下（例: `routers/sessions/`, `routers/reviews/`）

---

### 7. データモデル（必須）

MVPに必要な主要テーブルは以下です（開発時はSQLite可）。

- **users**
  - `id`, `sub`, `name`, `email`, `created_at`
- **sessions**
  - `id`, `user_id`, `scenario_id`, `round_target`, `completed_rounds`, `difficulty`, `mode`, `started_at`, `ended_at`
- **session_rounds**
  - `id`, `session_id`, `round_index`, `user_input`, `ai_reply`, `feedback_short`, `improved_sentence`, `tags[]`, `score_pron`, `score_grammar`
  - 制約: `session_rounds(session_id, round_index)` **ユニーク**
- **review_items**
  - `id`, `user_id`, `phrase`, `explanation`, `due_at`

---

### 8. AI呼び出しポリシー（MVP）

- 入力:
  - ユーザー発話 + 直前2ラウンド + 難易度/カテゴリ
- 出力（必須フィールド）:
  - `ai_reply`
  - `feedback_short`（120字以内）
  - `improved_sentence`（1文のみ）
- 禁止:
  - 長文講義的な解説
  - 個人情報の送信

---

### 9. UXルール（MVP）

- **モバイル表示最優先**
- ラウンド設定時に **所要時間を即時計算**
- タイムゾーンは **Asia/Tokyo固定**

---

### 10. セキュリティ / 運用

- JWT必須、`.env` 管理、HTTPS前提
- 個人情報は最小限保存
- 監査ログ（ユーザーID、操作時刻）を残す

---

### 11. 性能・信頼性（目標）

- 1ターン応答: **p50 < 2.5s**
- タイムアウト: **12s**

---

### 12. 現状のシナリオ数（実装状況）

- 現時点のシナリオは **合計21個**
  - Web定義: `apps/web/src/lib/scenarios.ts`（`SCENARIO_LIST` が 1〜21）
  - API側学習ゴール: `apps/api/app/prompts/scenario_goals.py`（1〜21）


