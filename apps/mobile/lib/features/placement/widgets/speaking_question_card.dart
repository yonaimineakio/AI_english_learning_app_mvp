import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/models/placement_models.dart';
import '../../audio/audio_controller.dart';

/// スピーキング問題カード
class SpeakingQuestionCard extends ConsumerStatefulWidget {
  const SpeakingQuestionCard({
    super.key,
    required this.question,
    required this.onEvaluate,
    this.evaluationResult,
  });

  final PlacementQuestionModel question;
  final Future<void> Function(String transcript) onEvaluate;
  final PlacementSpeakingEvaluateResponseModel? evaluationResult;

  @override
  ConsumerState<SpeakingQuestionCard> createState() =>
      _SpeakingQuestionCardState();
}

class _SpeakingQuestionCardState extends ConsumerState<SpeakingQuestionCard> {
  String? _transcript;
  bool _isEvaluating = false;

  Future<void> _handleEvaluate() async {
    if (_transcript == null || _transcript!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('発話を録音してください')),
      );
      return;
    }

    setState(() => _isEvaluating = true);
    try {
      await widget.onEvaluate(_transcript!);
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
              color: Colors.blue.shade100,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Text(
              'Speaking',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
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

          // 問題説明
          Card(
            color: Colors.blue.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                widget.question.prompt,
                style: const TextStyle(fontSize: 14),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // ターゲット文（読み上げる文）
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '以下の文を読み上げてください',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    widget.question.targetSentence ?? '',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 評価結果がある場合は表示
          if (result != null) ...[
            _buildEvaluationResult(result),
          ] else ...[
            // 音声録音ボタン
            Center(
              child: Column(
                children: [
                  GestureDetector(
                    onLongPressStart: (_) async {
                      if (!audioState.isRecording &&
                          !audioState.isTranscribing) {
                        await audioController.startRecording();
                      }
                    },
                    onLongPressEnd: (_) async {
                      if (audioState.isRecording) {
                        final text = await audioController.stopAndTranscribe();
                        setState(() => _transcript = text);
                      }
                    },
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: audioState.isRecording ? Colors.red : Colors.blue,
                      ),
                      child: Icon(
                        audioState.isRecording ? Icons.stop : Icons.mic,
                        size: 40,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    audioState.isTranscribing
                        ? '認識中...'
                        : audioState.isRecording
                            ? '録音中... 離すと停止'
                            : '長押しで録音',
                    style: const TextStyle(fontSize: 14),
                  ),
                ],
              ),
            ),

            // 録音結果表示
            if (_transcript != null && _transcript!.isNotEmpty) ...[
              const SizedBox(height: 16),
              Card(
                color: Colors.green.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'あなたの発話',
                        style: TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _transcript!,
                        style: const TextStyle(fontSize: 16),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // 評価ボタン
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isEvaluating ? null : _handleEvaluate,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: _isEvaluating
                      ? const CircularProgressIndicator.adaptive()
                      : const Text('評価する'),
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildEvaluationResult(PlacementSpeakingEvaluateResponseModel result) {
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
            const SizedBox(height: 16),

            // 単語一致表示
            const Text(
              '単語一致',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 4,
              runSpacing: 4,
              children: result.matchingWords.map((m) {
                return Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color:
                        m.matched ? Colors.green.shade100 : Colors.red.shade100,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    m.word,
                    style: TextStyle(
                      color: m.matched ? Colors.green : Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

