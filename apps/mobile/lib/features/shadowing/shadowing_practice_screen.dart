import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_tts/flutter_tts.dart';

import '../../shared/services/api_client.dart';
import '../audio/audio_controller.dart';
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
  
  // 音声録音・評価用の状態
  String? _transcription;
  ShadowingSpeakResponse? _speakResult;
  bool _isEvaluating = false;
  String? _errorMessage;

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

                  // 音声録音セクション
                  _buildRecordingSection(sentence),
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

  /// 音声録音セクションを構築
  Widget _buildRecordingSection(ShadowingSentence sentence) {
    final audioState = ref.watch(audioControllerProvider);
    final isRecording = audioState.isRecording;
    final isTranscribing = audioState.isTranscribing;
    // 録音中は停止可能、認識中・評価中は操作不可
    final isBusy = isTranscribing || _isEvaluating;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.mic, color: Colors.deepPurple),
                const SizedBox(width: 8),
                const Text(
                  '発話して評価',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              'マイクボタンを押して、文章を声に出して読んでください',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 16),

            // 録音ボタン
            Center(
              child: GestureDetector(
                onTap: isBusy ? null : () => _toggleRecording(sentence),
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isRecording
                        ? Colors.red
                        : (isBusy ? Colors.grey : Colors.deepPurple),
                    boxShadow: [
                      BoxShadow(
                        color: (isRecording ? Colors.red : Colors.deepPurple)
                            .withOpacity(0.3),
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

            // 状態表示
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

            // 認識結果と評価結果
            if (_speakResult != null) ...[
              const SizedBox(height: 16),
              _buildEvaluationResult(),
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
                    const Text(
                      'あなたの発話:',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _transcription!,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// 評価結果を表示するウィジェット
  Widget _buildEvaluationResult() {
    final result = _speakResult!;
    final scoreColor = result.score >= 80
        ? Colors.green
        : result.score >= 60
            ? Colors.orange
            : Colors.red;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: scoreColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: scoreColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // スコア表示
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    result.score >= 80
                        ? Icons.celebration
                        : result.score >= 60
                            ? Icons.thumb_up
                            : Icons.refresh,
                    color: scoreColor,
                    size: 28,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'スコア: ${result.score}点',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: scoreColor,
                    ),
                  ),
                ],
              ),
              if (result.isNewBest)
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

          // 単語ハイライト表示
          Wrap(
            spacing: 4,
            runSpacing: 4,
            children: result.matchingWords.map((wordMatch) {
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

          // 進捗情報
          Text(
            '練習回数: ${result.attemptCount}回 / ベスト: ${result.bestScore}点',
            style: TextStyle(
              color: Colors.grey.shade600,
              fontSize: 12,
            ),
          ),

          if (result.isCompleted) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.green, size: 16),
                const SizedBox(width: 4),
                Text(
                  'この文は完了しました！',
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

  Future<void> _speakSentence(String text) async {
    setState(() => _isPlaying = true);
    await _tts.speak(text);
  }

  /// 録音の開始/停止を切り替え
  Future<void> _toggleRecording(ShadowingSentence sentence) async {
    final audioController = ref.read(audioControllerProvider.notifier);
    final audioState = ref.read(audioControllerProvider);

    setState(() {
      _errorMessage = null;
    });

    if (audioState.isRecording) {
      // 録音停止 → 認識 → 評価
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

        // 評価APIを呼び出し
        final api = ShadowingApi(ApiClient());
        final result = await api.speakAttempt(
          sentenceId: sentence.id,
          userTranscription: transcription,
        );

        if (mounted) {
          setState(() {
            _speakResult = result;
            _isEvaluating = false;
          });

          // 進捗を更新
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
        // 前回の結果をクリア
        setState(() {
          _transcription = null;
          _speakResult = null;
        });
        await audioController.startRecording();
      } catch (e) {
        if (mounted) {
          setState(() {
            _errorMessage = '$e';
          });
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
        _errorMessage = null;
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
        _showTranslation = false;
        _transcription = null;
        _speakResult = null;
        _errorMessage = null;
      });
    }
  }
}
