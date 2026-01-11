# 📚 アーキテクチャドキュメント

## 🏷️ 目的

このドキュメントは、AI English Learning App MVPの設計思想とアーキテクチャパターンを記録したものです。
将来の開発者や自分自身が設計判断の背景を理解できるように、採用しているパターンと理由を明文化します。

**作成日**: 2025-11-22  
**対象バージョン**: v1.0.0 (MVP)

---

## 🏗️ 採用アーキテクチャ

### **レイヤードアーキテクチャ + サービス層パターン**

このMVPは以下の4層構造を採用しています：

```
┌─────────────────────────────────────────────┐
│  Presentation Layer (プレゼンテーション層)    │  
│  📍 役割: HTTPリクエスト/レスポンス処理        │
│  📁 場所: app/routers/**/*.py                │
│  例: @router.post("/{session_id}/turn")     │
└─────────────────────────────────────────────┘
              ↓ 依存
┌─────────────────────────────────────────────┐
│  Business Logic Layer (ビジネスロジック層)     │
│  📍 役割: ビジネスルール、ドメインロジック        │
│  📁 場所: app/services/**/*.py               │
│  例: SessionService.process_turn()          │
└─────────────────────────────────────────────┘
              ↓ 依存
┌─────────────────────────────────────────────┐
│  Data Access Layer (データアクセス層)          │
│  📍 役割: DB操作、永続化                       │
│  📁 場所: models/database/models.py          │
│  例: db.query(Session).filter(...)          │
└─────────────────────────────────────────────┘
              ↓ 依存
┌─────────────────────────────────────────────┐
│  Infrastructure Layer (インフラ層)            │
│  📍 役割: DB、外部API、ファイルシステム          │
│  📁 場所: app/services/ai/*, db/session.py   │
│  例: OpenAI API, Google TTS, PostgreSQL     │
└─────────────────────────────────────────────┘
```

**重要な特徴：**
- 依存関係は**一方向（上から下）**のみ
- 各層は自分の下の層にのみ依存可能
- 下の層は上の層を知らない

---

## 📋 各層の責任と実装

### 1️⃣ Presentation Layer (プレゼンテーション層)

**場所**: `apps/api/app/routers/**/*.py`

**責任：**
- HTTPリクエストの受付
- リクエストバリデーション
- 認証・認可の確認
- HTTPステータスコードの決定
- レスポンスのフォーマット

**実装例：**
```python
# apps/api/app/routers/sessions/sessions.py
@router.post("/{session_id}/turn", response_model=TurnResponse)
async def process_turn(
    session_id: int,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        session_service = SessionService(db)
        user_input = payload.get("user_input")
        
        if not user_input:
            raise HTTPException(status_code=400, detail="user_input is required")
        
        result = await session_service.process_turn(session_id, user_input, current_user.id)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail="AI応答がタイムアウトしました")
```

**やってはいけないこと：**
- ❌ ビジネスロジックの実装
- ❌ 直接DB操作
- ❌ 外部API呼び出し

---

### 2️⃣ Business Logic Layer (ビジネスロジック層)

**場所**: `apps/api/app/services/**/*.py`

**責任：**
- ビジネスルールの実装
- トランザクション管理
- 複数のデータ操作の調整
- ドメインロジック（ラウンド数チェック、延長可否判定など）

**主要サービス：**

#### SessionService
```python
# apps/api/app/services/conversation/session_service.py
class SessionService:
    def __init__(self, db: Session):
        self.db = db
    
    async def process_turn(self, session_id: int, user_input: str, user_id: int):
        """ターン処理のビジネスロジック"""
        # 1. データ取得
        session = self.db.query(SessionModel).filter(...).first()
        
        # 2. ビジネスルール検証
        if session.ended_at is not None:
            raise ValueError("Session has already ended")
        
        # 3. 外部サービス呼び出し
        ai_response = await generate_conversation_response(...)
        
        # 4. データ永続化
        new_round = SessionRound(...)
        self.db.add(new_round)
        session.completed_rounds += 1
        self.db.commit()
        
        return TurnResponse(...)
```

**サービス層の3つの役割：**

1. **トランザクション境界の定義**
   - 一連の操作を1つのトランザクションとして管理

2. **複数のデータ操作の調整**
   - セッション終了 + 復習アイテム作成など

3. **ビジネスルールの集約**
   - 延長可能性判定、完了判定など

**やってはいけないこと：**
- ❌ HTTPステータスコードの決定
- ❌ リクエスト/レスポンスの直接操作

---

### 3️⃣ Data Access Layer (データアクセス層)

**場所**: `apps/api/models/database/models.py`

**責任：**
- データ構造の定義
- テーブルマッピング
- リレーションシップの定義

**実装例：**
```python
# models/database/models.py
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    completed_rounds = Column(Integer, default=0)
    round_target = Column(Integer, nullable=False)
    
    # リレーション
    user = relationship("User", back_populates="sessions")
    session_rounds = relationship("SessionRound", back_populates="session")
```

**データモデル設計：**
```
users (1) ─── (N) sessions (N) ─── (1) scenarios
                    │
                    └── (N) session_rounds
users (1) ─── (N) review_items
```

**注意：**
- 現在は「貧血症モデル」（データのみ、ビジネスロジックなし）
- これはMVP段階では適切な選択

---

### 4️⃣ Infrastructure Layer (インフラ層)

**場所**: `apps/api/app/services/ai/*`, `apps/api/app/db/session.py`

**責任：**
- 外部APIとの通信
- データベース接続管理
- ファイルシステム操作
- データフォーマット変換

**実装例：**
```python
# app/services/ai/openai_provider.py
class OpenAIConversationProvider:
    async def generate_response(self, user_input: str, ...):
        # OpenAI API呼び出し
        response = await asyncio.wait_for(
            self._call_openai_api(messages),
            timeout=30.0
        )
        return ConversationResponse(...)
```

---

## 🎯 重要な設計パターン

### 1. **Strategy + Factory パターン（AIプロバイダー抽象化）**

複数のAIプロバイダーに対応できるよう、Strategy + Factoryパターンを採用。

```python
# types.py - Protocol (Interface)
class ConversationProvider(Protocol):
    async def generate_response(...) -> ConversationResponse:
        ...

# factory.py - プロバイダー登録
def initialize_providers() -> None:
    AIProviderRegistry.register("mock", MockConversationProvider)
    AIProviderRegistry.register("openai", OpenAIConversationProvider)
    AIProviderRegistry.register("groq", GroqConversationProvider)
    AIProviderRegistry.set_default(settings.AI_PROVIDER_DEFAULT)

# 使用側
async def generate_conversation_response(..., provider_name: str | None = None):
    provider_cls = AIProviderRegistry.get_provider(provider_name)
    provider = provider_cls()
    return await provider.generate_response(...)
```

**メリット：**
- ✅ 複数のAIプロバイダー（OpenAI、Groq、Claude、Geminiなど）に対応可能
- ✅ 開発時はMockプロバイダーでオフライン開発
- ✅ 本番環境では環境変数で切り替え（`AI_PROVIDER_DEFAULT=openai` または `groq`）
- ✅ プロバイダー追加時も既存コードに影響なし（Open/Closed Principle）

**現在対応しているプロバイダー：**
| プロバイダー | クラス | 用途 |
|-------------|--------|------|
| mock | `MockConversationProvider` | 開発・テスト用（オフライン） |
| openai | `OpenAIConversationProvider` | 本番（GPT-4o, GPT-4o-mini等） |
| groq | `GroqConversationProvider` | 本番（Llama 3.1, Mixtral等、高速推論） |

---

### 2. **依存性注入（Dependency Injection）**

FastAPIの`Depends`を活用した依存性注入パターン。

```python
# deps.py
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    # 認証ロジック
    ...

# Router
@router.post("/sessions/start")
async def start_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user と db が自動注入される
    ...
```

**メリット：**
- ✅ テスト容易性（モック可能）
- ✅ 疎結合
- ✅ 環境別の切り替えが簡単（開発用devユーザー自動生成など）

---

### 3. **プロンプト管理の分離**

各シナリオのプロンプトを個別ファイル化。

```
prompts/
  ├── conversation_system.py        # 共通会話システム
  ├── goal_progress_evaluation.py   # ゴール達成度評価
  ├── scenario_goals.py             # シナリオ別ゴール定義
  │
  ├── # Travel シナリオ
  ├── airport_checkin.py
  ├── hotel_checkin.py
  ├── immigration_customs.py
  ├── restaurant_ordering.py
  ├── best_vacation.py
  ├── guide_japan.py
  ├── travel_planning_friend.py
  │
  ├── # Business シナリオ
  ├── business_meeting.py
  ├── schedule_meeting.py
  ├── reschedule_meeting.py
  ├── run_meeting.py
  ├── online_negotiation.py
  ├── contract_negotiation_detail.py
  ├── customer_survey_presentation.py
  ├── apologize_delay.py
  ├── sick_leave.py
  │
  ├── # Daily シナリオ
  ├── cafe_small_talk.py
  ├── park_small_talk.py
  ├── customer_service.py
  ├── show_tickets.py
  ├── lost_wallet_police.py
  │
  └── # 復習問題生成
  ├── review_speaking_question.py
  └── review_listening_question.py
```

**メリット：**
- ✅ プロンプトの変更がコードに影響しない
- ✅ シナリオ追加が容易
- ✅ バージョン管理が明確
- ✅ プロンプトエンジニアリングが独立して可能

---

### 4. **サービス層の単一責任原則（SRP）**

各サービスが明確な責任を持つ：

- `SessionService`: セッション開始・ターン処理・終了・延長
- `ReviewService`: 復習アイテムの管理
- `GoalProgressService`: 学習ゴール達成率判定

---

## 🎨 フロントエンド設計

### React + TypeScript アーキテクチャ

```
src/
  ├── app/              # Next.js App Router (Pages)
  ├── components/       # UIコンポーネント
  │   ├── ui/          # Atoms（基本部品）
  │   ├── audio/       # Molecules
  │   ├── conversation/# Molecules
  │   ├── scenario/    # Organisms
  │   └── layout/      # Templates
  ├── hooks/           # カスタムフック
  ├── lib/             # ユーティリティ・APIクライアント
  ├── contexts/        # React Context
  └── types/           # TypeScript型定義
```

### 主要パターン

#### 1. **Hooks中心のロジック分離**

```typescript
// hooks/use-session-conversation.ts
export function useSessionConversation({
  sessionId,
  onSessionEnd,
  onRoundCompleted
}) {
  // セッション状態管理
  // ターン送信ロジック
  // 自動音声再生
  // ゴール進捗管理
}
```

**メリット：**
- UIとロジックの分離
- 再利用性の向上
- テスト容易性

---

#### 2. **React Query によるサーバー状態管理**

```typescript
const statusQuery = useQuery({
  queryKey: ['session-status', sessionId],
  queryFn: () => fetchSessionStatus(sessionId),
  staleTime: 30_000,
})

const submitMutation = useMutation({
  mutationFn: (message: string) => submitTurn(sessionId, message),
  onSuccess: ...
})
```

**メリット：**
- ✅ キャッシュ管理自動化
- ✅ 楽観的更新（Optimistic Updates）
- ✅ エラーハンドリングの一元化
- ✅ リトライ・ポーリングの標準化

---

#### 3. **型安全性の徹底**

```typescript
// types/conversation.ts
export interface ConversationTurn {
  id: string
  roundIndex: number
  userMessage: string
  aiReply: AIReply
  createdAt: string
}

export interface SessionGoalProgress {
  total: number
  achieved: number
  status: boolean[]
}
```

TypeScriptで型安全性を徹底し、バグを削減。

---

## 🆚 他のアーキテクチャとの比較

### クリーンアーキテクチャとの違い

| 項目 | レイヤードアーキテクチャ（採用） | クリーンアーキテクチャ |
|------|---------------------------|-------------------|
| **依存方向** | 一方向（上→下） | 内側向き（外→内） |
| **コア層の独立性** | ❌ インフラに依存 | ✅ 完全に独立 |
| **テスト容易性** | 🟡 DBモック必要 | ✅ 簡単（Interface） |
| **実装コスト** | 🟢 低い | 🔴 高い（抽象層追加） |
| **変更への強さ** | 🟡 中程度 | ✅ 非常に強い |
| **学習コスト** | 🟢 低い | 🔴 高い |
| **MVPに向くか** | ✅ 向く | ❌ 過剰 |

#### 依存関係の違い

**レイヤードアーキテクチャ（現在）：**
```
Presentation (Router)
    ↓ 依存（直接参照）
Business Logic (Service)
    ↓ 依存（直接参照）
Data Access (Models)
    ↓ 依存（直接参照）
Infrastructure (DB, OpenAI)
```

**クリーンアーキテクチャ：**
```
         Frameworks & Drivers (最外層)
                   ↑
              Interface Adapters
                   ↑
            Application Business Rules
                   ↑
         Enterprise Business Rules (中心)
         
※すべての依存が内側（ビジネスルール）を向く
```

---

### DDD（ドメイン駆動設計）との違い

現在のアプリは**完全なDDDではない**。

#### DDDではない部分

1. **貧血症ドメインモデル**
   - 現在のモデルはデータ保持のみ
   - ビジネスロジックはServiceに実装

2. **リポジトリパターンの欠如**
   - ServiceがSQLAlchemyを直接操作

3. **集約（Aggregate）の未定義**
   - SessionとSessionRoundの整合性管理が明確でない

4. **ドメインイベントの欠如**
   - 重要なビジネスイベントが暗黙的

#### わずかにDDDっぽい部分

1. ✅ **ユビキタス言語の使用**
   - Session, SessionRound, Scenario などビジネス用語がそのままコードに

2. ✅ **境界づけられたコンテキストの分離**
   - 会話コンテキスト、復習コンテキスト、認証コンテキストなど

3. ✅ **ドメインサービスの存在**
   - SessionServiceは一種のドメインサービス

---

## ✅ 設計判断の理由

### なぜレイヤードアーキテクチャを選んだか

1. **MVP段階に最適**
   - 開発速度が速い
   - 理解しやすい
   - 十分な保守性

2. **学習コストが低い**
   - チームメンバーがすぐに理解できる
   - FastAPIの標準的なパターン

3. **段階的な進化が可能**
   - 必要になれば徐々に改善可能

### なぜクリーンアーキテクチャを採用しなかったか

1. **過剰な抽象化**
   - MVPには不要な複雑性
   - 開発速度の低下

2. **YAGNI原則**
   - "You Aren't Gonna Need It"
   - 今必要ない機能は実装しない

3. **適用タイミングを見極め**
   - ビジネスルールが複雑化したら移行

---

## 🚀 将来の進化パス

必要に応じて段階的に進化させる：

```
現在: レイヤード + サービス層（MVP）
  ↓
ステップ1: リポジトリパターン追加
  - データアクセスを抽象化
  - テスト容易性向上
  ↓
ステップ2: リッチドメインモデル
  - モデルにビジネスロジックを移動
  - ドメインイベント導入
  ↓
ステップ3: クリーンアーキテクチャ
  - 依存性逆転の原則適用
  - 完全な独立性確保
```

### 移行を検討すべきタイミング

- ✅ ビジネスルールが複雑化したとき
- ✅ 複数チームで開発するとき
- ✅ テストカバレッジを大幅に上げたいとき
- ✅ 外部システムへの依存が増えたとき
- ✅ マイクロサービス化を検討するとき

---

## 📊 特に優れた設計判断

### 1. **冪等性の担保**

```python
def end_session(self, session_id: int, user_id: int):
    if session.ended_at:
        # 既に終了済みの場合も同じサマリーを返す
        return self._build_end_response(session, db_rounds)
```

**メリット：**
- ネットワークエラー時の再送に対応
- UIの安定性向上

---

### 2. **単調増加制御（ゴール達成率）**

```python
# 達成率が0→1のみ許可、1→0は禁止（AI判定の揺れ対策）
new_status[i] = prev_status[i] or current_status[i]
```

**メリット：**
- AIの判定揺れに対応
- ユーザー体験の一貫性

---

### 3. **楽観的UI更新**

```typescript
onMutate: async (message) => {
  // APIレスポンス前にUIを即座に更新
  setTurns((prev) => [...prev, pendingTurn])
}
```

**メリット：**
- 即座のフィードバック
- 体感速度の向上

---

### 4. **開発体験の最適化**

- DEBUGモードでdevユーザー自動生成
- Mockプロバイダーでオフライン開発可能
- ホットリロード対応

---

### 5. **エラーハンドリングの階層化**

各層で適切なエラー処理：

```python
# Service層: ビジネスエラー
raise ValueError("Session has already ended")

# Router層: HTTPエラーに変換
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

---

## 📚 参考資料

### 書籍
- 『エンタープライズ アプリケーションアーキテクチャパターン』 Martin Fowler
- 『Clean Architecture』 Robert C. Martin
- 『実践ドメイン駆動設計』 Vaughn Vernon

### オンライン
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [React Architecture Patterns](https://react.dev/learn/thinking-in-react)
- [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html)

---

## 🔄 更新履歴

| 日付 | 変更内容 |
|------|---------|
| 2025-11-22 | 初版作成（v1.0.0 MVP時点） |
| 2026-01-11 | Groqプロバイダー追加、プロンプト一覧更新 |

---

## 👥 コントリビューター

このドキュメントは開発チームによって維持されています。
質問や提案があれば、Issueまたはプルリクエストでお知らせください。

