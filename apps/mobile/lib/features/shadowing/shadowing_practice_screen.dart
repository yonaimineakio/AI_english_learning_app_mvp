import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/models/scenario_static.dart';
import '../../shared/services/api_client.dart';
import '../audio/audio_controller.dart';
import '../auth/auth_providers.dart';
import '../session/session_controller.dart';
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
  int _currentIndex = 0;
  bool _showTranslation = false;

  // 練習キュー（シャドーイング2問 + 瞬間英作2問 × 熟語3つ = 12問）
  List<PracticeQuestion> _questionQueue = [];

  // 音声録音・評価用の状態
  String? _transcription;
  ShadowingSpeakResponse? _speakResult;
  InstantTranslateSpeakResponse? _instantTranslateResult;
  bool _isEvaluating = false;
  String? _errorMessage;

  /// kScenarioList から関連シナリオを検索する。見つからなければ null。
  ScenarioSummary? get _relatedScenario {
    try {
      return kScenarioList.firstWhere((s) => s.id == widget.scenarioId);
    } catch (_) {
      return null;
    }
  }


  /// 9文からシャドーイング2問＋瞬間英作2問の12問キューを構築
  ///
  /// 熟語ごとに先頭2文を使い：
  ///   - シャドーイング問題（英文を聞いて繰り返す）× 2
  ///   - 瞬間英作問題（日本語を見て英語で答える）× 2
  /// の順番で並べる。
  List<PracticeQuestion> _buildQuestionQueue(List<ShadowingSentence> sentences) {
    // key_phrase でグループ化（出現順を保持）
    final groups = <String, List<ShadowingSentence>>{};
    for (final s in sentences) {
      groups.putIfAbsent(s.keyPhrase, () => []).add(s);
    }

    final queue = <PracticeQuestion>[];
    for (final group in groups.values) {
      // orderIndex でソートし先頭2文を使用
      final sorted = List<ShadowingSentence>.from(group)
        ..sort((a, b) => a.orderIndex.compareTo(b.orderIndex));
      final pair = sorted.take(2).toList();

      // シャドーイング2問
      for (final s in pair) {
        queue.add(PracticeQuestion(sentence: s, type: QuestionType.shadowing));
      }
      // 瞬間英作2問（同じ文を別モードで）
      for (final s in pair) {
        queue.add(PracticeQuestion(sentence: s, type: QuestionType.instantTranslation));
      }
    }
    return queue;
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
                onPressed: () {
                  setState(() => _questionQueue = []);
                  ref.invalidate(scenarioShadowingProvider(widget.scenarioId));
                },
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
      return const Center(child: Text('シャドーイング文がありません'));
    }

    // キューが未構築の場合に構築（初回または再読み込み後）
    if (_questionQueue.isEmpty) {
      _questionQueue = _buildQuestionQueue(data.sentences);
    }

    if (_questionQueue.isEmpty) {
      return const Center(child: Text('問題を準備できませんでした'));
    }

    final currentQuestion = _questionQueue[_currentIndex];
    final isLastQuestion = _currentIndex == _questionQueue.length - 1;

    return SafeArea(
      child: Column(
        children: [
          // 進捗インジケーター
          LinearProgressIndicator(
            value: (_currentIndex + 1) / _questionQueue.length,
            minHeight: 4,
            color: currentQuestion.type == QuestionType.shadowing
                ? Colors.blue
                : Colors.orange,
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${_currentIndex + 1} / ${_questionQueue.length}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                // 問題種別バッジ
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: currentQuestion.type == QuestionType.shadowing
                        ? Colors.blue.shade100
                        : Colors.orange.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    currentQuestion.type == QuestionType.shadowing
                        ? 'シャドーイング'
                        : '瞬間英作',
                    style: TextStyle(
                      color: currentQuestion.type == QuestionType.shadowing
                          ? Colors.blue.shade700
                          : Colors.orange.shade700,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),

          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: currentQuestion.type == QuestionType.shadowing
                  ? _buildShadowingContent(currentQuestion.sentence)
                  : _buildInstantTranslationContent(currentQuestion.sentence),
            ),
          ),

          // ナビゲーションボタン
          _buildNavigationButtons(isLastQuestion),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────
  // シャドーイング問題 UI
  // ─────────────────────────────────────────────

  Widget _buildShadowingContent(ShadowingSentence sentence) {
    return Column(
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
                const Row(
                  children: [
                    Icon(Icons.volume_up, color: Colors.grey),
                    SizedBox(width: 8),
                    Text(
                      '読み上げ文',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
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
                // 日本語訳（任意表示）
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
        Builder(builder: (context) {
          final audioState = ref.watch(audioControllerProvider);
          return Center(
            child: ElevatedButton.icon(
              onPressed: audioState.isPlaying ? null : () => _speakSentence(sentence.sentenceEn),
              icon: Icon(audioState.isPlaying ? Icons.stop : Icons.play_arrow),
              label: Text(audioState.isPlaying ? '再生中...' : 'AIの発音を聞く'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
            ),
          );
        }),

        const SizedBox(height: 24),

        _buildRecordingCard(
          sentence: sentence,
          questionType: QuestionType.shadowing,
          accentColor: Colors.deepPurple,
          title: '発話して評価',
          instruction: 'マイクボタンを押して、文章を声に出して読んでください',
          result: _speakResult != null
              ? _buildEvaluationResult(
                  score: _speakResult!.score,
                  isNewBest: _speakResult!.isNewBest,
                  isCompleted: _speakResult!.isCompleted,
                  attemptCount: _speakResult!.attemptCount,
                  bestScore: _speakResult!.bestScore,
                  matchingWords: _speakResult!.matchingWords,
                )
              : null,
        ),
        const SizedBox(height: 24),
      ],
    );
  }

  // ─────────────────────────────────────────────
  // 瞬間英作問題 UI
  // ─────────────────────────────────────────────

  Widget _buildInstantTranslationContent(ShadowingSentence sentence) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // キーフレーズ（ヒント）
        Card(
          color: Colors.orange.shade50,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                const Icon(Icons.lightbulb_outline, color: Colors.orange),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'このフレーズを使って英語で言ってみよう',
                        style: TextStyle(color: Colors.orange, fontSize: 11),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        sentence.keyPhrase,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.orange,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 24),

        // 日本語（メイン表示）
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.translate, color: Colors.grey),
                    SizedBox(width: 8),
                    Text(
                      '以下の日本語を英語にしよう',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  sentence.sentenceJa,
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w600,
                    height: 1.6,
                  ),
                ),
                // 評価後に正解英文を表示
                if (_instantTranslateResult != null) ...[
                  const SizedBox(height: 16),
                  const Divider(),
                  const SizedBox(height: 8),
                  const Text(
                    '正解',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    sentence.sentenceEn,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey.shade700,
                      height: 1.5,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),

        const SizedBox(height: 24),

        _buildRecordingCard(
          sentence: sentence,
          questionType: QuestionType.instantTranslation,
          accentColor: Colors.orange,
          title: '英語で発話して評価',
          instruction: 'マイクボタンを押して、上の日本語を英語で言ってみてください',
          result: _instantTranslateResult != null
              ? _buildEvaluationResult(
                  score: _instantTranslateResult!.score,
                  isNewBest: _instantTranslateResult!.isNewBest,
                  isCompleted: _instantTranslateResult!.isCompleted,
                  attemptCount: _instantTranslateResult!.attemptCount,
                  bestScore: _instantTranslateResult!.bestScore,
                  matchingWords: _instantTranslateResult!.matchingWords,
                )
              : null,
        ),
        const SizedBox(height: 24),
      ],
    );
  }

  // ─────────────────────────────────────────────
  // 共通ウィジェット
  // ─────────────────────────────────────────────

  Widget _buildRecordingCard({
    required ShadowingSentence sentence,
    required QuestionType questionType,
    required Color accentColor,
    required String title,
    required String instruction,
    Widget? result,
  }) {
    final audioState = ref.watch(audioControllerProvider);
    final isRecording = audioState.isRecording;
    final isTranscribing = audioState.isTranscribing;
    final isBusy = isTranscribing || _isEvaluating;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.mic, color: accentColor),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              instruction,
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 16),

            // マイクボタン
            Center(
              child: GestureDetector(
                onTap: isBusy ? null : () => _toggleRecording(sentence, questionType),
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isRecording ? Colors.red : (isBusy ? Colors.grey : accentColor),
                    boxShadow: [
                      BoxShadow(
                        color: (isRecording ? Colors.red : accentColor).withValues(alpha: 0.3),
                        blurRadius: 12,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: Icon(
                    isRecording ? Icons.stop : Icons.mic,
                    color: Colors.white,
                    size: 36,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 12),
            Center(
              child: Text(
                isRecording
                    ? '録音中... タップで停止'
                    : isTranscribing
                        ? '認識中...'
                        : _isEvaluating
                            ? '評価中...'
                            : 'タップして録音開始',
                style: TextStyle(
                  color: isRecording ? Colors.red : Colors.grey,
                  fontSize: 14,
                  fontWeight: isRecording ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            ),

            // エラーメッセージ
            if (_errorMessage != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.red, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // 評価結果 or 認識テキスト
            if (result != null) ...[
              const SizedBox(height: 16),
              result,
            ] else if (_transcription != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('あなたの発話:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 4),
                    Text(_transcription!, style: const TextStyle(fontSize: 16)),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// 評価結果ウィジェット（シャドーイング・瞬間英作共通）
  Widget _buildEvaluationResult({
    required int score,
    required bool isNewBest,
    required bool isCompleted,
    required int attemptCount,
    required int bestScore,
    required List<WordMatch> matchingWords,
  }) {
    final scoreColor = score >= 80
        ? Colors.green
        : score >= 60
            ? Colors.orange
            : Colors.red;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: scoreColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: scoreColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    score >= 80
                        ? Icons.celebration
                        : score >= 60
                            ? Icons.thumb_up
                            : Icons.refresh,
                    color: scoreColor,
                    size: 28,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'スコア: $score点',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: scoreColor,
                    ),
                  ),
                ],
              ),
              if (isNewBest)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.amber,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.star, color: Colors.white, size: 14),
                      SizedBox(width: 4),
                      Text(
                        'ベスト更新!',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          // 単語ハイライト
          Wrap(
            spacing: 4,
            runSpacing: 4,
            children: matchingWords.map((wordMatch) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: wordMatch.matched ? Colors.green.shade100 : Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  wordMatch.word,
                  style: TextStyle(
                    color: wordMatch.matched ? Colors.green.shade800 : Colors.grey.shade600,
                    decoration: wordMatch.matched ? null : TextDecoration.lineThrough,
                    fontWeight: wordMatch.matched ? FontWeight.w500 : FontWeight.normal,
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 12),
          Text(
            '練習回数: $attemptCount回 / ベスト: $bestScore点',
            style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
          ),
          if (isCompleted) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.green, size: 16),
                const SizedBox(width: 4),
                Text(
                  'この問題は完了しました！',
                  style: TextStyle(
                    color: Colors.green.shade700,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────
  // ナビゲーション
  // ─────────────────────────────────────────────

  Widget _buildNavigationButtons(bool isLastQuestion) {
    final relatedScenario = _relatedScenario;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          if (isLastQuestion && relatedScenario != null) ...[
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.check),
                label: const Text('完了'),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () => _startScenarioSession(relatedScenario),
                icon: const Icon(Icons.play_arrow),
                label: const Text('シナリオを開始'),
              ),
            ),
          ] else ...[
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
                onPressed: isLastQuestion ? () => Navigator.of(context).pop() : _nextSentence,
                icon: Icon(isLastQuestion ? Icons.check : Icons.arrow_forward),
                label: Text(isLastQuestion ? '完了' : '次へ'),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────
  // アクション
  // ─────────────────────────────────────────────

  Future<void> _startScenarioSession(ScenarioSummary scenario) async {
    try {
      final sessionId = await ref
          .read(sessionControllerProvider.notifier)
          .startNewSession(
            scenarioId: scenario.id,
            difficulty: scenario.difficulty,
            mode: 'standard',
          );
      if (mounted) {
        context.push('/sessions/$sessionId');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('セッション開始に失敗しました: $e')),
        );
      }
    }
  }

  Future<void> _speakSentence(String text) async {
    try {
      await ref.read(audioControllerProvider.notifier).playTts(text);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('音声再生エラー: $e')),
        );
      }
    }
  }

  /// 録音の開始/停止を切り替え
  Future<void> _toggleRecording(ShadowingSentence sentence, QuestionType questionType) async {
    final audioController = ref.read(audioControllerProvider.notifier);
    final audioState = ref.read(audioControllerProvider);

    setState(() => _errorMessage = null);

    if (audioState.isRecording) {
      // 録音停止 → 音声認識 → 評価API呼び出し
      try {
        final transcription = await audioController.stopAndTranscribe();

        if (transcription == null || transcription.trim().isEmpty) {
          setState(() {
            _errorMessage = '音声を認識できませんでした。もう一度お試しください。';
          });
          return;
        }

        setState(() {
          _transcription = transcription;
          _isEvaluating = true;
        });

        final api = ShadowingApi(ApiClient());

        if (questionType == QuestionType.shadowing) {
          final result = await api.speakAttempt(
            sentenceId: sentence.id,
            userTranscription: transcription,
          );
          if (mounted) {
            setState(() {
              _speakResult = result;
              _isEvaluating = false;
            });
          }
        } else {
          final result = await api.instantTranslateAttempt(
            sentenceId: sentence.id,
            userTranscription: transcription,
          );
          if (mounted) {
            setState(() {
              _instantTranslateResult = result;
              _isEvaluating = false;
            });
          }
        }

        if (mounted) {
          ref.invalidate(scenarioShadowingProvider(widget.scenarioId));
        }
      } catch (e) {
        if (mounted) {
          setState(() {
            _errorMessage = 'エラー: $e';
            _isEvaluating = false;
          });
        }
      }
    } else {
      // 録音開始
      try {
        setState(() {
          _transcription = null;
          _speakResult = null;
          _instantTranslateResult = null;
        });
        await audioController.startRecording();
      } catch (e) {
        if (mounted) {
          setState(() => _errorMessage = '$e');
        }
      }
    }
  }

  void _previousSentence() {
    if (_currentIndex > 0) {
      setState(() {
        _currentIndex--;
        _showTranslation = false;
        _transcription = null;
        _speakResult = null;
        _instantTranslateResult = null;
        _errorMessage = null;
      });
    }
  }

  void _nextSentence() {
    if (_currentIndex < _questionQueue.length - 1) {
      setState(() {
        _currentIndex++;
        _showTranslation = false;
        _transcription = null;
        _speakResult = null;
        _instantTranslateResult = null;
        _errorMessage = null;
      });
    }
  }
}
