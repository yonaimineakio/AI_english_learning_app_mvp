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
    required this.onRetry,
    this.evaluationResult,
    this.transcript,
  });

  final PlacementQuestionModel question;
  final Future<void> Function(String transcript) onEvaluate;
  final VoidCallback onRetry;
  final PlacementSpeakingEvaluateResponseModel? evaluationResult;
  final String? transcript;

  @override
  ConsumerState<SpeakingQuestionCard> createState() =>
      _SpeakingQuestionCardState();
}

class _SpeakingQuestionCardState extends ConsumerState<SpeakingQuestionCard> {
  String? _transcript;
  bool _isEvaluating = false;

  Future<void> _handleEvaluate() async {
    final text = _transcript?.trim() ?? '';
    if (text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('発話を録音してください')),
      );
      return;
    }

    setState(() => _isEvaluating = true);
    try {
      await widget.onEvaluate(text);
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
    final evaluatedTranscript = widget.transcript?.trim().isNotEmpty == true
        ? widget.transcript!.trim()
        : (_transcript?.trim().isNotEmpty == true ? _transcript!.trim() : null);

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
            _buildEvaluationResult(result, evaluatedTranscript),
          ] else ...[
            // 音声録音ボタン
            Center(
              child: Column(
                children: [
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: audioState.isRecording ? Colors.red : Colors.blue,
                    ),
                    child: IconButton(
                      onPressed: audioState.isTranscribing
                          ? null
                          : () async {
                              try {
                                if (audioState.isRecording) {
                                  final text = await audioController.stopAndTranscribe();
                                  if (!context.mounted) return;
                                  setState(() => _transcript = text);
                                } else {
                                  await audioController.startRecording();
                                }
                              } catch (e) {
                                if (!context.mounted) return;
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('マイク操作に失敗しました: $e')),
                                );
                              }
                            },
                      icon: audioState.isTranscribing
                          ? const SizedBox(
                              width: 28,
                              height: 28,
                              child: CircularProgressIndicator(
                                strokeWidth: 3,
                                color: Colors.white,
                              ),
                            )
                          : Icon(
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
                            ? '録音中...'
                            : 'タップして録音',
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

  Widget _buildEvaluationResult(
    PlacementSpeakingEvaluateResponseModel result,
    String? transcript,
  ) {
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

            const Text(
              'あなたの発話',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            if (transcript != null && transcript.isNotEmpty)
              _buildHighlightedTranscript(transcript, result)
            else
              const Text('（発話テキストがありません）'),

            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () {
                  setState(() => _transcript = null);
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

  Widget _buildHighlightedTranscript(
    String transcript,
    PlacementSpeakingEvaluateResponseModel result,
  ) {
    // 可能ならバックエンドが返した matching_words を優先して使う
    if (result.matchingWords.isNotEmpty) {
      return Wrap(
        children: result.matchingWords.map((m) {
          return Padding(
            padding: const EdgeInsets.only(right: 6, bottom: 4),
            child: Text(
              m.word,
              style: TextStyle(
                color: m.matched ? Colors.green.shade700 : Colors.grey.shade500,
                fontWeight: m.matched ? FontWeight.w600 : FontWeight.normal,
                decoration: m.matched ? null : TextDecoration.lineThrough,
              ),
            ),
          );
        }).toList(),
      );
    }

    // フォールバック: ターゲット文に含まれる単語を緑（表示用の近似）
    final targetWords = (result.targetSentence)
        .toLowerCase()
        .split(RegExp(r'\s+'))
        .where((w) => w.isNotEmpty)
        .toSet();
    final words = transcript.split(RegExp(r'\s+')).where((w) => w.isNotEmpty).toList();

    return Wrap(
      children: words.map((w) {
        final normalized = w.toLowerCase();
        final matched = targetWords.contains(normalized);
        return Padding(
          padding: const EdgeInsets.only(right: 6, bottom: 4),
          child: Text(
            w,
            style: TextStyle(
              color: matched ? Colors.green.shade700 : Colors.grey.shade500,
              fontWeight: matched ? FontWeight.w600 : FontWeight.normal,
              decoration: matched ? null : TextDecoration.lineThrough,
            ),
          ),
        );
      }).toList(),
    );
  }
}

