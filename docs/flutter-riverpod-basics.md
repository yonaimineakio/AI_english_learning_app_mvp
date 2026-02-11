# Flutter と Riverpod の基礎：Riverpod とは / StatelessWidget と ConsumerWidget の違い

本ドキュメントは、本プロジェクトのモバイルアプリ（Flutter + Riverpod）で使っている用語と概念を整理する。

---

## Riverpod とは

**Riverpod** は Flutter 向けの **状態管理・依存性注入ライブラリ**（Provider の後継・改良版）。

### 主な役割

1. **状態の保持・共有**
   - アプリ全体で共有したいデータ（認証状態、API クライアント、取得した一覧データなど）を「プロバイダー」として定義し、どこからでも参照できる。

2. **依存性の注入**
   - ウィジェットのツリーを遡らずに、`ref` 経由で必要なオブジェクト（API クライアントやキャッシュされたデータ）にアクセスできる。

3. **キャッシュと再計算の制御**
   - プロバイダーは「キャッシュ」を持ち、`watch` / `read` / `invalidate` などで「いつ再計算するか」を制御できる。
   - `FutureProvider.autoDispose` のように、リスナーがいなくなったら自動で破棄するオプションもある。

### 本プロジェクトでの利用例

- **認証状態**: `authStateProvider` でログイン状態・ユーザー情報を保持
- **復習データ**: `reviewItemsProvider` で復習一覧、`reviewStatsProvider` で統計を保持
- **セッション**: `sessionControllerProvider` で会話セッションの状態を管理

プロバイダーにアクセスするには、**ConsumerWidget や ConsumerStatefulWidget の `ref`** を使う（後述）。

---

## StatelessWidget と ConsumerWidget の違い

どちらも「自分自身では状態を持たない」ウィジェット。違いは **Riverpod の `ref` が使えるかどうか**。

### StatelessWidget（Flutter 標準）

- **`build(BuildContext context)` のみ**を受け取る。
- Riverpod のプロバイダーには **直接アクセスできない**。
- プロバイダーの値の取得や `invalidate` は行えない。

```dart
class MyScreen extends StatelessWidget {
  const MyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // context だけ使える（Theme, Navigator, MediaQuery など）
    return Text('Hello');
  }
}
```

### ConsumerWidget（Riverpod 提供）

- **`build(BuildContext context, WidgetRef ref)`** を受け取る。
- **`ref`** でプロバイダーにアクセスできる。
  - `ref.watch(provider)` … 値を監視し、変化で再ビルド
  - `ref.read(provider)` … 一度だけ値を取得（イベントハンドラ内など）
  - `ref.invalidate(provider)` … キャッシュを破棄し、次回アクセス時に再計算

```dart
class MyScreen extends ConsumerWidget {
  const MyScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ref でプロバイダーを操作できる
    ref.invalidate(reviewItemsProvider);
    return Text('Hello');
  }
}
```

### 対応関係の整理

| 項目           | StatelessWidget | ConsumerWidget      |
|----------------|-----------------|---------------------|
| 提供元         | Flutter 標準    | Riverpod パッケージ |
| build の引数   | `(context)`     | `(context, ref)`    |
| プロバイダー利用 | 不可            | 可（watch/read/invalidate） |

**ConsumerWidget は「StatelessWidget + ref が使える版」** と考えるとよい。

### 状態付きの場合は ConsumerStatefulWidget

- ウィジェット自身が状態（`State`）を持つ場合は **ConsumerStatefulWidget** + **ConsumerState** を使う。
- こちらも `ref` が使える（`ConsumerState` の `ref`）。

---

## 参考：本プロジェクト内の関連ドキュメント

- [Riverpod: authStateProvider 依存で自動 refresh される流れ](issues/issue-riverpod-refresh-on-auth-change.md) … `watch` による依存と再評価の説明
- サマリ画面から復習画面へ遷移する際の `invalidate(reviewItemsProvider)` は、上記「明示的に再取得したいタイミング」の例として [summary_screen.dart](../apps/mobile/lib/features/summary/summary_screen.dart) に実装されている。
