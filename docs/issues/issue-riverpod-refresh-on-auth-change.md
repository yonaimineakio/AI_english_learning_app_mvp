# Riverpod: authStateProvider 依存で「自動refresh」される流れ（ログイン/ログアウト）

## 目的

ログアウト後に別ユーザーでログインしても、前ユーザーのデータ（復習/保存フレーズ等）が表示され続ける問題があった。

対策として、ユーザー依存データを返す `FutureProvider` が `authStateProvider` を `watch` するように変更したが、ここで「具体的にどこでrefreshしているのか」が分かりづらい。

本ドキュメントは、**`refresh()` を呼ばずに自動的に再フェッチされる仕組み**を整理する。

---

## 結論（重要）

この方式では **`refresh()` を直接呼ばない**。

代わりに、`FutureProvider` の中で `ref.watch(authStateProvider)` を呼ぶことで、`authStateProvider` の値が変わった瞬間に **依存関係が変化 → providerが再評価（再実行）**され、結果として **API再呼び出し＝実質refresh**が起きる。

---

## 具体例（StreakWidget の userStatsProvider）

```dart
final userStatsProvider = FutureProvider<UserStatsModel>((ref) async {
  final auth = ref.watch(authStateProvider);
  if (auth.valueOrNull?.isLoggedIn != true) {
    throw StateError('Not logged in');
  }
  return AuthApi(ApiClient()).getUserStats();
});
```

ポイント:

- `authStateProvider` を `watch` しているので、ログイン/ログアウトで `authStateProvider` が変化すると、`userStatsProvider` が **自動で再評価**
- 未ログイン時は `StateError('Not logged in')` を投げて、**前回の成功データを出し続けない**

---

## ログイン/ログアウトと「再評価」のタイミング

```mermaid
flowchart TD
  A[ログアウト/ログイン操作] --> B[AuthNotifier が state を更新]
  B --> C[authStateProvider の値が変わる]
  C --> D[依存している FutureProvider が自動で再評価]
  D --> E{ログイン済み?}
  E -- No --> F[StateError('Not logged in') を返す]
  E -- Yes --> G[API呼び出し（例: /auth/me/stats）]
  G --> H[新しいユーザーのデータが表示される]
```

### ログアウト時

- `authStateProvider` が「未ログイン」状態へ変化
- `FutureProvider` が再評価される
- 未ログインのガードにより **古いデータが温存されず**、以降の表示が更新される

### 別ユーザーでログイン時

- `authStateProvider` が「ログイン済み」へ変化
- `FutureProvider` が再評価される
- 新しいトークンで API を叩き直すため、**新ユーザーのデータ**が返る

---

## `refresh()` / `invalidate()` との違い（使い分け）

- **`ref.refresh(provider)`**:
  - 明示的に再評価させたいときに呼ぶ
  - UIイベント（プルリフレッシュ等）で使うことが多い

- **`ref.invalidate(provider)`**:
  - キャッシュを破棄して「次に読まれた時に再評価」にする
  - ログアウト時の **`proStatusProvider` のキャッシュ破棄**などに使う

- **本方式（依存の `watch`）**:
  - `authStateProvider` 変更に追従して **宣言的に自動再評価**
  - 「ログアウト時にどのproviderを消すか」を列挙しなくて済む（追加漏れを防げる）

---

## 対象Provider（今回の修正方針）

- Review: 復習アイテム/統計/保存フレーズ
- Rankings: ポイント/ランキング/自分の順位
- Home: streak などのユーザー統計

これらは「ユーザーが変われば内容が変わる」ため、`authStateProvider` 依存を持たせるのが安全。

