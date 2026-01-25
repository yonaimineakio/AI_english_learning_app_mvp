import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_tts/flutter_tts.dart';

import '../../shared/services/api_client.dart';
import '../auth/auth_providers.dart';
import 'shadowing_api.dart';
import 'shadowing_models.dart';

/// シナリオ別シャドーイング文プロバイダー
final scenarioShadowingProvider = FutureProvider.family<ScenarioShadowingResponse, int>((ref, scenarioId) async {
  final auth = ref.watch(authStateProvider);
  if (auth.valueOrNull?.isLoggedIn != true) {
    throw StateError('Not logged in');
  }
  final api = ShadowingApi(ApiClient());
  return api.getScenarioShadowing(scenarioId: scenarioId);
});

/// シャドーイング練習画面
class ShadowingPracticeScreen extends ConsumerStatefulWidget {
  const ShadowingPracticeScreen({
    super.key,
    required this.scenarioId,
    this.scenarioName,
  });

  final int scenarioId;
  final String? scenarioName;

  @override
  ConsumerState<ShadowingPracticeScreen> createState() => _ShadowingPracticeScreenState();
}

class _ShadowingPracticeScreenState extends ConsumerState<ShadowingPracticeScreen> {
  late FlutterTts _tts;
  int _currentIndex = 0;
  bool _isPlaying = false;
  bool _showTranslation = false;
  int? _selfScore;

  @override
  void initState() {
    super.initState();
    _initTts();
  }

  void _initTts() {
    _tts = FlutterTts();
    _tts.setLanguage('en-US');
    _tts.setSpeechRate(0.5);
    _tts.setCompletionHandler(() {
      if (!mounted) {
        return;
      }
      setState(() => _isPlaying = false);
    });
    _tts.setErrorHandler((msg) {
      if (!mounted) {
        return;
      }
      setState(() => _isPlaying = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('音声再生エラー: $msg')),
      );
    });
  }

  @override
  void dispose() {
    _tts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final shadowingAsync = ref.watch(scenarioShadowingProvider(widget.scenarioId));

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.scenarioName ?? 'シャドーイング'),
      ),
      body: shadowingAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.red),
              const SizedBox(height: 16),
              Text('エラー: $e'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(scenarioShadowingProvider(widget.scenarioId)),
                child: const Text('再読み込み'),
              ),
            ],
          ),
        ),
        data: (data) => _buildPracticeView(data),
      ),
    );
  }

  Widget _buildPracticeView(ScenarioShadowingResponse data) {
    if (data.sentences.isEmpty) {
      return const Center(
        child: Text('シャドーイング文がありません'),
      );
    }

    final sentence = data.sentences[_currentIndex];

    return SafeArea(
      child: Column(
        children: [
          // 進捗インジケーター
          LinearProgressIndicator(
            value: (_currentIndex + 1) / data.sentences.length,
            minHeight: 4,
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${_currentIndex + 1} / ${data.sentences.length}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Row(
                  children: [
                    Icon(
                      Icons.check_circle,
                      size: 16,
                      color: sentence.userProgress?.isCompleted == true
                          ? Colors.green
                          : Colors.grey.shade300,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '完了: ${data.completedCount}/${data.totalSentences}',
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // キーフレーズ
                  Card(
                    color: Colors.blue.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          const Icon(Icons.lightbulb_outline, color: Colors.blue),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              sentence.keyPhrase,
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Colors.blue,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // 英文
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.volume_up, color: Colors.grey),
                              const SizedBox(width: 8),
                              const Text(
                                '読み上げ文',
                                style: TextStyle(
                                  color: Colors.grey,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Text(
                            sentence.sentenceEn,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w500,
                              height: 1.5,
                            ),
                          ),
                          const SizedBox(height: 16),
                          // 日本語訳
                          GestureDetector(
                            onTap: () => setState(() => _showTranslation = !_showTranslation),
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade100,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    _showTranslation ? Icons.visibility : Icons.visibility_off,
                                    color: Colors.grey,
                                    size: 20,
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _showTranslation ? sentence.sentenceJa : '日本語訳を表示',
                                      style: TextStyle(
                                        color: _showTranslation ? Colors.black87 : Colors.grey,
                                        fontSize: 14,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // 再生ボタン
                  Center(
                    child: ElevatedButton.icon(
                      onPressed: _isPlaying ? null : () => _speakSentence(sentence.sentenceEn),
                      icon: Icon(_isPlaying ? Icons.stop : Icons.play_arrow),
                      label: Text(_isPlaying ? '再生中...' : 'AIの発音を聞く'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // 自己評価
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            '自己評価',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            '声に出して練習した後、自分の発音を評価してください',
                            style: TextStyle(
                              color: Colors.grey,
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              _buildScoreButton(60, 'もう一度', Colors.orange),
                              _buildScoreButton(80, 'まあまあ', Colors.blue),
                              _buildScoreButton(100, 'バッチリ', Colors.green),
                            ],
                          ),
                          if (sentence.userProgress != null) ...[
                            const SizedBox(height: 12),
                            Text(
                              '練習回数: ${sentence.userProgress!.attemptCount}回 / '
                              'ベスト: ${sentence.userProgress!.bestScore ?? "-"}点',
                              style: TextStyle(
                                color: Colors.grey.shade600,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // ナビゲーションボタン
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                if (_currentIndex > 0)
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _previousSentence,
                      icon: const Icon(Icons.arrow_back),
                      label: const Text('前へ'),
                    ),
                  )
                else
                  const Expanded(child: SizedBox()),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _currentIndex < data.sentences.length - 1
                        ? _nextSentence
                        : () => Navigator.of(context).pop(),
                    icon: Icon(_currentIndex < data.sentences.length - 1
                        ? Icons.arrow_forward
                        : Icons.check),
                    label: Text(_currentIndex < data.sentences.length - 1
                        ? '次へ'
                        : '完了'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScoreButton(int score, String label, Color color) {
    final isSelected = _selfScore == score;
    return ElevatedButton(
      onPressed: () => _submitScore(score),
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected ? color : Colors.grey.shade200,
        foregroundColor: isSelected ? Colors.white : Colors.black87,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
      child: Text(label),
    );
  }

  Future<void> _speakSentence(String text) async {
    setState(() => _isPlaying = true);
    await _tts.speak(text);
  }

  Future<void> _submitScore(int score) async {
    final shadowingAsync = ref.read(scenarioShadowingProvider(widget.scenarioId));
    final data = shadowingAsync.valueOrNull;
    if (data == null) return;

    final sentence = data.sentences[_currentIndex];

    setState(() => _selfScore = score);

    try {
      final api = ShadowingApi(ApiClient());
      final result = await api.recordAttempt(
        sentenceId: sentence.id,
        score: score,
      );

      if (mounted) {
        if (result.isNewBest) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('ベストスコア更新！ ${result.bestScore}点'),
              backgroundColor: Colors.green,
            ),
          );
        }

        // 進捗を更新
        ref.invalidate(scenarioShadowingProvider(widget.scenarioId));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('スコア記録エラー: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _previousSentence() {
    if (_currentIndex > 0) {
      setState(() {
        _currentIndex--;
        _selfScore = null;
        _showTranslation = false;
      });
    }
  }

  void _nextSentence() {
    final shadowingAsync = ref.read(scenarioShadowingProvider(widget.scenarioId));
    final data = shadowingAsync.valueOrNull;
    if (data == null) return;

    if (_currentIndex < data.sentences.length - 1) {
      setState(() {
        _currentIndex++;
        _selfScore = null;
        _showTranslation = false;
      });
    }
  }
}
