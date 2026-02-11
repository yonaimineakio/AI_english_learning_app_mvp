# [Docs] Riverpod とは / StatelessWidget と ConsumerWidget の違いをドキュメント化

---

## GitHub で Issue を作成する場合

**Title（コピー用）:**
```
[Docs] Riverpod と StatelessWidget / ConsumerWidget の違いをドキュメント化
```

**Body（コピー用）:** 以下の「概要」〜「関連」までをそのまま Issue の本文に貼り付けてください。

---

## 概要

Flutter モバイルアプリで使用している **Riverpod** および **StatelessWidget と ConsumerWidget の違い** を、開発者向けドキュメントとしてまとめた。

## 目的

- 新規参加者や将来の自分が、Riverpod と Flutter のウィジェットの関係をすぐ理解できるようにする。
- 「なぜ SummaryScreen を ConsumerWidget にしたか」「ref.invalidate は何をしているか」などの判断根拠を残す。

## 実施内容

1. **ドキュメントの追加**
   - ファイル: `docs/flutter-riverpod-basics.md`
   - 内容:
     - **Riverpod とは**: 状態管理・依存性注入ライブラリであること、本プロジェクトでの利用例（authStateProvider, reviewItemsProvider など）
     - **StatelessWidget と ConsumerWidget の違い**: build の引数（context のみ vs context + ref）、プロバイダー（watch/read/invalidate）の利用可否
     - 対応表とコード例
     - 参考: 既存の `issue-riverpod-refresh-on-auth-change.md` やサマリ→復習遷移での invalidate の例

2. **既存ドキュメントとのつながり**
   - `docs/issues/issue-riverpod-refresh-on-auth-change.md` への参照を追加（watch による自動再評価と invalidate の使い分け）。

## 受け入れ条件

- [ ] `docs/flutter-riverpod-basics.md` が存在し、Riverpod の説明と StatelessWidget/ConsumerWidget の違いが記載されている
- [ ] 本 issue の内容がドキュメントと一致している

## 関連

- サマリ画面から復習画面へ遷移する際の `ref.invalidate(reviewItemsProvider)` 実装: `apps/mobile/lib/features/summary/summary_screen.dart`
- 既存ドキュメント: `docs/issues/issue-riverpod-refresh-on-auth-change.md`
