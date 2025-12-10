import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/models/review_models.dart';
import '../../shared/services/api_client.dart';
import '../../shared/services/review_api.dart';
import '../audio/audio_controller.dart';

final _reviewApiProvider = Provider<ReviewApi>(
  (ref) => ReviewApi(ApiClient()),
);

final _reviewItemsProvider =
    FutureProvider<ReviewNextResponseModel>((ref) async {
  final api = ref.watch(_reviewApiProvider);
  return api.getNextReviews();
});

class ReviewScreen extends ConsumerWidget {
  const ReviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncItems = ref.watch(_reviewItemsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('復習'),
      ),
      body: asyncItems.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (data) {
          if (data.reviewItems.isEmpty) {
            return const Center(
              child: Text('本日の復習フレーズはありません'),
            );
          }

          return ListView.builder(
            itemCount: data.reviewItems.length,
            itemBuilder: (context, index) {
              final item = data.reviewItems[index];
              return Card(
                margin: const EdgeInsets.all(12),
                child: InkWell(
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (context) => ReviewQuizScreen(
                          reviewItem: item,
                          onComplete: () {
                            ref.invalidate(_reviewItemsProvider);
                          },
                        ),
                      ),
                    );
                  },
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.phrase,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          item.explanation,
                          style: const TextStyle(fontSize: 14),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            Text(
                              'タップして問題を開始 →',
                              style: TextStyle(
                                fontSize: 12,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

/// 復習クイズ画面（スピーキング・リスニング問題）
class ReviewQuizScreen extends ConsumerStatefulWidget {
  const ReviewQuizScreen({
    super.key,
    required this.reviewItem,
    required this.onComplete,
  });

  final ReviewItemModel reviewItem;
  final VoidCallback onComplete;

  @override
  ConsumerState<ReviewQuizScreen> createState() => _ReviewQuizScreenState();
}

class _ReviewQuizScreenState extends ConsumerState<ReviewQuizScreen> {
  ReviewQuestionsResponseModel? _questions;
  bool _isLoadingQuestions = true;
  String? _errorMessage;

  // 現在の問題タイプ: 0=speaking, 1=listening, 2=完了
  int _currentStep = 0;

  // スピーキング問題の結果
  String? _transcript;
  ReviewEvaluateResponseModel? _speakingResult;

  // リスニング問題の結果
  List<String> _shuffledWords = [];
  List<String> _selectedWords = [];
  ReviewEvaluateResponseModel? _listeningResult;

  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    setState(() {
      _isLoadingQuestions = true;
      _errorMessage = null;
    });

    try {
      final api = ref.read(_reviewApiProvider);
      final questions = await api.getReviewQuestions(
        reviewId: widget.reviewItem.id,
      );

      // リスニング用の単語をシャッフル
      final words = List<String>.from(questions.listening.puzzleWords ?? []);
      words.shuffle(Random());

      setState(() {
        _questions = questions;
        _shuffledWords = words;
        _isLoadingQuestions = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoadingQuestions = false;
      });
    }
  }

  Future<void> _submitSpeakingAnswer() async {
    if (_transcript == null || _transcript!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('発話を録音してください')),
      );
      return;
    }

    try {
      final api = ref.read(_reviewApiProvider);
      final result = await api.evaluateSpeaking(
        reviewId: widget.reviewItem.id,
        userTranscription: _transcript!,
      );
      setState(() {
        _speakingResult = result;
        _currentStep = 1;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('評価の送信に失敗しました: $e')),
        );
      }
    }
  }

  Future<void> _submitListeningAnswer() async {
    if (_selectedWords.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('単語を並べてください')),
      );
      return;
    }

    try {
      final api = ref.read(_reviewApiProvider);
      final result = await api.evaluateListening(
        reviewId: widget.reviewItem.id,
        userAnswer: _selectedWords,
      );

      setState(() {
        _listeningResult = result;
        _currentStep = 2;
      });

      // 完了メッセージを表示
      if (mounted) {
        final message = result.isCompleted
            ? '復習完了！よくできました。'
            : '次回また復習しましょう。';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('評価の送信に失敗しました: $e')),
        );
      }
    }
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

  void _resetWords() {
    final words = List<String>.from(_questions!.listening.puzzleWords ?? []);
    words.shuffle(Random());
    setState(() {
      _shuffledWords = words;
      _selectedWords = [];
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('復習クイズ'),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoadingQuestions) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('問題を生成中...'),
          ],
        ),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('エラー: $_errorMessage'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadQuestions,
              child: const Text('再試行'),
            ),
          ],
        ),
      );
    }

    if (_questions == null) {
      return const Center(child: Text('問題の読み込みに失敗しました'));
    }

    switch (_currentStep) {
      case 0:
        return _buildSpeakingQuestion();
      case 1:
        return _buildListeningQuestion();
      case 2:
        return _buildCompletionScreen();
      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildSpeakingQuestion() {
    final question = _questions!.speaking;
    final audioState = ref.watch(audioControllerProvider);
    final audioController = ref.read(audioControllerProvider.notifier);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 進捗表示
          _buildProgressIndicator(0),
          const SizedBox(height: 24),

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

          // 問題説明
          Card(
            color: Colors.blue.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    question.prompt,
                    style: const TextStyle(fontSize: 14),
                  ),
                  if (question.hint != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      'ヒント: ${question.hint}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                ],
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
                    question.targetSentence ?? '',
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

          // 音声録音ボタン
          Center(
            child: Column(
              children: [
                GestureDetector(
                  onTap: audioState.isRecording || audioState.isTranscribing
                      ? null
                      : () async {
                          if (audioState.isRecording) {
                            final text =
                                await audioController.stopAndTranscribe();
                            setState(() => _transcript = text);
                          } else {
                            await audioController.startRecording();
                          }
                        },
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
                      color: audioState.isRecording
                          ? Colors.red
                          : Colors.blue,
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
                          ? '録音中... タップで停止'
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
                onPressed: _submitSpeakingAnswer,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('評価する'),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildListeningQuestion() {
    final question = _questions!.listening;
    final audioState = ref.watch(audioControllerProvider);
    final audioController = ref.read(audioControllerProvider.notifier);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 進捗表示
          _buildProgressIndicator(1),
          const SizedBox(height: 16),

          // スピーキング結果表示
          if (_speakingResult != null)
            Card(
              color: _speakingResult!.isCorrect
                  ? Colors.green.shade50
                  : Colors.orange.shade50,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    Icon(
                      _speakingResult!.isCorrect
                          ? Icons.check_circle
                          : Icons.info,
                      color: _speakingResult!.isCorrect
                          ? Colors.green
                          : Colors.orange,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Speaking: ${_speakingResult!.score}点'
                        '${_speakingResult!.isCorrect ? " ✓" : ""}',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 16),

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

          // TTS再生ボタン
          Card(
            color: Colors.green.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Text(
                    question.prompt,
                    style: const TextStyle(fontSize: 14),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: audioState.isPlaying
                        ? null
                        : () async {
                            if (question.audioText != null) {
                              await audioController.playTts(question.audioText!);
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
                  if (question.hint != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      'ヒント: ${question.hint}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

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
              onPressed: _selectedWords.isNotEmpty ? _submitListeningAnswer : null,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: Colors.green,
              ),
              child: const Text('回答を送信'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCompletionScreen() {
    final speakingScore = _speakingResult?.score ?? 0;
    final listeningScore = _listeningResult?.score ?? 0;
    final avgScore = (speakingScore + listeningScore) / 2;
    final isGood = avgScore >= 70;

    return SingleChildScrollView(
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                isGood ? Icons.check_circle : Icons.refresh,
                size: 80,
                color: isGood ? Colors.green : Colors.orange,
              ),
              const SizedBox(height: 24),
              Text(
                isGood ? '復習完了！' : 'もう少し練習しましょう',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),

              // スピーキング結果
              _buildResultCard(
                'Speaking',
                speakingScore,
                _speakingResult?.isCorrect ?? false,
                _speakingResult?.correctAnswer,
                _speakingResult?.matchingWords,
              ),
              const SizedBox(height: 16),

              // リスニング結果
              _buildResultCard(
                'Listening',
                listeningScore,
                _listeningResult?.isCorrect ?? false,
                _listeningResult?.correctAnswer,
                null,
              ),
              const SizedBox(height: 16),

              // 平均スコア
              Card(
                color: isGood ? Colors.green.shade50 : Colors.orange.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        '平均スコア: ',
                        style: TextStyle(fontSize: 18),
                      ),
                      Text(
                        '${avgScore.toInt()}点',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: isGood ? Colors.green : Colors.orange,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),

              ElevatedButton(
                onPressed: () {
                  widget.onComplete();
                  Navigator.of(context).pop();
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                ),
                child: const Text('復習リストに戻る'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResultCard(
    String title,
    int score,
    bool isCorrect,
    String? correctAnswer,
    List<WordMatchModel>? matchingWords,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: isCorrect ? Colors.green : Colors.orange,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    '$score点',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            if (matchingWords != null && matchingWords.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 4,
                runSpacing: 4,
                children: matchingWords.map((m) {
                  return Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: m.matched
                          ? Colors.green.shade100
                          : Colors.red.shade100,
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
            if (correctAnswer != null && !isCorrect) ...[
              const SizedBox(height: 12),
              Text(
                '正解: $correctAnswer',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildProgressIndicator(int step) {
    return Row(
      children: [
        _buildStepCircle(0, step, 'Speaking'),
        Expanded(
          child: Container(
            height: 2,
            color: step > 0 ? Colors.blue : Colors.grey.shade300,
          ),
        ),
        _buildStepCircle(1, step, 'Listening'),
      ],
    );
  }

  Widget _buildStepCircle(int index, int currentStep, String label) {
    final isCompleted = currentStep > index;
    final isCurrent = currentStep == index;

    return Column(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isCompleted
                ? Colors.blue
                : isCurrent
                    ? Colors.blue.shade100
                    : Colors.grey.shade300,
            border: isCurrent
                ? Border.all(color: Colors.blue, width: 2)
                : null,
          ),
          child: Center(
            child: isCompleted
                ? const Icon(Icons.check, size: 16, color: Colors.white)
                : Text(
                    '${index + 1}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: isCurrent ? Colors.blue : Colors.grey,
                    ),
                  ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: isCurrent ? Colors.blue : Colors.grey,
          ),
        ),
      ],
    );
  }
}
