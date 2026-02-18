import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/models/placement_models.dart';
import '../../audio/audio_controller.dart';

/// インデックス付き単語（同じ単語が複数ある場合を区別するため）
typedef IndexedWord = ({int id, String word});

/// リスニング問題カード
class ListeningQuestionCard extends ConsumerStatefulWidget {
  const ListeningQuestionCard({
    super.key,
    required this.question,
    required this.onEvaluate,
    required this.onRetry,
    this.evaluationResult,
  });

  final PlacementQuestionModel question;
  final Future<void> Function(List<String> userAnswer) onEvaluate;
  final VoidCallback onRetry;
  final PlacementListeningEvaluateResponseModel? evaluationResult;

  @override
  ConsumerState<ListeningQuestionCard> createState() =>
      _ListeningQuestionCardState();
}

class _ListeningQuestionCardState extends ConsumerState<ListeningQuestionCard> {
  List<IndexedWord> _availableWords = [];
  List<IndexedWord?> _answerSlots = [];
  bool _isEvaluating = false;

  @override
  void initState() {
    super.initState();
    _resetWords();
  }

  @override
  void didUpdateWidget(ListeningQuestionCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.question.id != widget.question.id) {
      _resetWords();
    }
  }

  void _resetWords() {
    final words = widget.question.puzzleWords ?? [];
    setState(() {
      _availableWords = words
          .asMap()
          .entries
          .map((e) => (id: e.key, word: e.value))
          .toList()
        ..shuffle();
      _answerSlots = List<IndexedWord?>.filled(words.length, null);
    });
  }

  void _placeWord(int slotIndex, IndexedWord item) {
    setState(() {
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

  void _tapToPlace(IndexedWord item) {
    final emptyIdx = _answerSlots.indexWhere((s) => s == null);
    if (emptyIdx == -1) return;
    _placeWord(emptyIdx, item);
  }

  void _removeFromSlot(int slotIndex) {
    setState(() {
      final item = _answerSlots[slotIndex];
      if (item == null) return;
      _answerSlots[slotIndex] = null;
      _availableWords.add(item);
    });
  }

  Future<void> _handleEvaluate() async {
    final filled = _answerSlots.whereType<IndexedWord>().toList();
    if (filled.length != _answerSlots.length) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('すべてのスロットを埋めてください')),
      );
      return;
    }

    setState(() => _isEvaluating = true);
    try {
      // 単語のみのリストに変換して送信
      await widget.onEvaluate(filled.map((e) => e.word).toList());
    } finally {
      if (mounted) {
        setState(() => _isEvaluating = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final audioState = ref.watch(audioControllerProvider);
    final audioController = ref.read(audioControllerProvider.notifier);
    final result = widget.evaluationResult;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 問題タイプラベル
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.green.shade100,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Text(
              'Listening',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.green,
              ),
            ),
          ),
          const SizedBox(height: 16),

          // シナリオヒント
          Text(
            widget.question.scenarioHint,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),

          // TTS再生ボタン
          Card(
            color: Colors.green.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Text(
                    widget.question.prompt,
                    style: const TextStyle(fontSize: 14),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: audioState.isPlaying
                        ? null
                        : () async {
                            if (widget.question.audioText != null) {
                              await audioController
                                  .playTts(widget.question.audioText!, profile: 'placement_listening');
                            }
                          },
                    icon: Icon(
                      audioState.isPlaying ? Icons.volume_up : Icons.play_arrow,
                    ),
                    label: Text(audioState.isPlaying ? '再生中...' : '音声を再生'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 32,
                        vertical: 16,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 評価結果がある場合は表示
          if (result != null) ...[
            _buildEvaluationResult(result),
          ] else ...[
            // 回答エリア（スロット）
            const Text(
              'あなたの回答',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              constraints: const BoxConstraints(minHeight: 80),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: List.generate(_answerSlots.length, (idx) {
                  final item = _answerSlots[idx];
                  return GestureDetector(
                    onTap: item == null ? null : () => _removeFromSlot(idx),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      decoration: BoxDecoration(
                        color: item == null ? Colors.white : Colors.blue,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Colors.grey.shade300,
                        ),
                      ),
                      child: Text(
                        item?.word ?? '____',
                        style: TextStyle(
                          color: item == null ? Colors.grey.shade600 : Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  );
                }),
              ),
            ),
            const SizedBox(height: 16),

            // 単語パーツ（タップで配置）
            const Text(
              '単語をタップして並べ替え',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _availableWords.map((item) {
                return GestureDetector(
                  onTap: () => _tapToPlace(item),
                  child: _WordChip(word: item.word),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            // リセットボタン
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                TextButton.icon(
                  onPressed: _resetWords,
                  icon: const Icon(Icons.refresh),
                  label: const Text('リセット'),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // 評価ボタン
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed:
                    _answerSlots.whereType<IndexedWord>().length == _answerSlots.length &&
                            !_isEvaluating
                        ? _handleEvaluate
                        : null,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.green,
                ),
                child: _isEvaluating
                    ? const CircularProgressIndicator.adaptive()
                    : const Text('回答を送信'),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildEvaluationResult(PlacementListeningEvaluateResponseModel result) {
    return Card(
      color: result.isCorrect ? Colors.green.shade50 : Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      result.isCorrect ? Icons.check_circle : Icons.info,
                      color: result.isCorrect ? Colors.green : Colors.orange,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      result.isCorrect ? '正解！' : '惜しい！',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: result.isCorrect ? Colors.green : Colors.orange,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    '${result.score}点',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            if (!result.isCorrect) ...[
              const SizedBox(height: 16),
              const Text(
                '正解',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 8),
              Text(
                result.correctAnswer,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () {
                  _resetWords();
                  widget.onRetry();
                },
                child: const Text('Retry'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _WordChip extends StatelessWidget {
  const _WordChip({required this.word});

  final String word;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade400),
      ),
      child: Text(
        word,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
    );
  }
}
