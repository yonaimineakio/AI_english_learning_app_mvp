# Issue: リスニング問題で同じ単語が複数ある場合に正しく動作しない

## 概要

Placementテストおよび復習機能のリスニング問題（単語並び替えパズル）において、同じ単語（例: "to"）が複数存在する場合、2つ目の同じ単語を選択すると1つ目が消えてしまうバグがある。

## 再現手順

1. Placementテストまたは復習のリスニング問題を開く
2. "I want to go to the store" のような文（"to"が2回登場）が出題される
3. 単語を並べていき、最初の"to"をスロットに配置
4. 2つ目の"to"をスロットに配置しようとする
5. **期待**: 2つ目の"to"が新しいスロットに入る
6. **実際**: 1つ目の"to"がスロットから消える

## 原因

### Placementテスト (`listening_question_card.dart:54-61`)

```dart
void _placeWord(int slotIndex, String word) {
  setState(() {
    // 既に別スロットに同じ単語が入っていたら外す（安全策）
    for (var i = 0; i < _answerSlots.length; i++) {
      if (_answerSlots[i] == word) {  // ← 文字列で比較しているため、同じ単語がすべて削除される
        _answerSlots[i] = null;
      }
    }
    // ...
  });
}
```

このコードは「同じ**値**の単語」をすべて削除してしまう。"to"が2つある場合、どちらも`word == "to"`なので両方削除される。

### 復習画面 (`review_screen.dart:801-812`)

```dart
void _selectWord(String word) {
  setState(() {
    _shuffledWords.remove(word);  // ← List.remove()は最初の一致要素のみ削除
    _selectedWords.add(word);
  });
}

void _unselectWord(String word) {
  setState(() {
    _selectedWords.remove(word);  // ← 同上
    _shuffledWords.add(word);
  });
}
```

`List.remove()`は最初に一致した要素のみ削除するため、ある程度動作するが、選択・解除を繰り返すと意図しない単語が操作される可能性がある。

## 影響範囲

| ファイル | 影響 |
|---------|------|
| `apps/mobile/lib/features/placement/widgets/listening_question_card.dart` | Placementテストのリスニング問題 |
| `apps/mobile/lib/features/review/review_screen.dart` | 復習機能のリスニング問題 |

## 修正案

### 方法1: インデックス付きの単語リストを使用（推奨）

単語を文字列ではなく、ユニークなインデックスと組み合わせたレコード型で管理する。

```dart
// 変更前
List<String> _availableWords = [];

// 変更後
List<({int id, String word})> _availableWords = [];
```

初期化:
```dart
void _resetWords() {
  final words = widget.question.puzzleWords ?? [];
  setState(() {
    _availableWords = words
        .asMap()
        .entries
        .map((e) => (id: e.key, word: e.value))
        .toList()
      ..shuffle();
    _answerSlots = List<({int id, String word})?>.filled(words.length, null);
  });
}
```

配置処理:
```dart
void _placeWord(int slotIndex, ({int id, String word}) item) {
  setState(() {
    // 既に同じIDの単語が入っていたら外す
    for (var i = 0; i < _answerSlots.length; i++) {
      if (_answerSlots[i]?.id == item.id) {
        _answerSlots[i] = null;
      }
    }
    
    final prev = _answerSlots[slotIndex];
    if (prev != null) {
      _availableWords.add(prev);
    }
    
    _answerSlots[slotIndex] = item;
    _availableWords.removeWhere((w) => w.id == item.id);
  });
}
```

### 方法2: 元のインデックスで管理

単語リストのインデックスを使って、選択状態を`Set<int>`で管理する。

```dart
List<String> _originalWords = [];  // シャッフルしない元のリスト
List<int> _shuffledIndices = [];   // シャッフルされたインデックス
List<int?> _answerSlotIndices = []; // スロットに入っている単語のインデックス
```

## 優先度

**中** - ユーザー体験に直接影響するバグだが、ワークアラウンド（リセットボタン）で回避可能

## チェックリスト

- [x] `listening_question_card.dart` を修正
- [x] `review_screen.dart` を修正
- [ ] 同じ単語が3つ以上ある場合のテスト
- [ ] ドラッグ&ドロップとタップの両方で動作確認
