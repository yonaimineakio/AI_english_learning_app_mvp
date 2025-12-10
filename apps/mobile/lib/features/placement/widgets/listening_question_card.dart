import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/models/placement_models.dart';
import '../../audio/audio_controller.dart';

/// リスニング問題カード
class ListeningQuestionCard extends ConsumerStatefulWidget {
  const ListeningQuestionCard({
    super.key,
    required this.question,
    required this.onEvaluate,
    this.evaluationResult,
  });

  final PlacementQuestionModel question;
  final Future<void> Function(List<String> userAnswer) onEvaluate;
  final PlacementListeningEvaluateResponseModel? evaluationResult;

  @override
  ConsumerState<ListeningQuestionCard> createState() =>
      _ListeningQuestionCardState();
}

class _ListeningQuestionCardState extends ConsumerState<ListeningQuestionCard> {
  List<String> _shuffledWords = [];
  List<String> _selectedWords = [];
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
    final words = List<String>.from(widget.question.puzzleWords ?? []);
    words.shuffle(Random());
    setState(() {
      _shuffledWords = words;
      _selectedWords = [];
    });
  }

  void _selectWord(String word) {
    setState(() {
      _shuffledWords.remove(word);
      _selectedWords.add(word);
    });
  }

  void _unselectWord(String word) {
    setState(() {
      _selectedWords.remove(word);
      _shuffledWords.add(word);
    });
  }

  Future<void> _handleEvaluate() async {
    if (_selectedWords.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('単語を並べてください')),
      );
      return;
    }

    setState(() => _isEvaluating = true);
    try {
      await widget.onEvaluate(_selectedWords);
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
                                  .playTts(widget.question.audioText!);
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
            // 選択済み単語（回答エリア）
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
              child: _selectedWords.isEmpty
                  ? Text(
                      '下の単語をタップして並べてください',
                      style: TextStyle(
                        color: Colors.grey.shade500,
                        fontStyle: FontStyle.italic,
                      ),
                    )
                  : Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _selectedWords.map((word) {
                        return InkWell(
                          onTap: () => _unselectWord(word),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.blue,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              word,
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
            ),
            const SizedBox(height: 16),

            // シャッフルされた単語（選択肢）
            const Text(
              '単語を選択',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _shuffledWords.map((word) {
                return InkWell(
                  onTap: () => _selectWord(word),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: Colors.grey.shade400),
                    ),
                    child: Text(
                      word,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
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
                    _selectedWords.isNotEmpty && !_isEvaluating ? _handleEvaluate : null,
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
          ],
        ),
      ),
    );
  }
}

