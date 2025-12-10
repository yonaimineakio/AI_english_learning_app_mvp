import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/models/placement_models.dart';
import '../auth/auth_providers.dart';
import 'placement_controller.dart';
import 'widgets/listening_question_card.dart';
import 'widgets/speaking_question_card.dart';

class PlacementScreen extends ConsumerWidget {
  const PlacementScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(placementControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('レベル判定テスト'),
        actions: [
          // 進捗表示
          state.maybeWhen(
            data: (data) => Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Center(
                child: Text(
                  '${data.currentIndex + 1} / ${data.questions.length}',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            orElse: () => const SizedBox.shrink(),
          ),
        ],
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (data) {
          // 全問完了時
          if (data.isCompleted) {
            return _buildCompletionScreen(context, ref, data);
          }

          // 現在の問題を表示
          final currentQuestion = data.questions[data.currentIndex];
          final speakingResult = data.speakingResults[currentQuestion.id];
          final listeningResult = data.listeningResults[currentQuestion.id];

          return Column(
            children: [
              // 進捗バー
              LinearProgressIndicator(
                value: data.currentIndex / data.questions.length,
                backgroundColor: Colors.grey.shade200,
              ),
              Expanded(
                child: currentQuestion.type == 'speaking'
                    ? SpeakingQuestionCard(
                        key: ValueKey(currentQuestion.id),
                        question: currentQuestion,
                        evaluationResult: speakingResult,
                        onEvaluate: (transcript) async {
                          await ref
                              .read(placementControllerProvider.notifier)
                              .evaluateSpeaking(
                                currentQuestion.id,
                                transcript,
                              );
                        },
                      )
                    : ListeningQuestionCard(
                        key: ValueKey(currentQuestion.id),
                        question: currentQuestion,
                        evaluationResult: listeningResult,
                        onEvaluate: (userAnswer) async {
                          await ref
                              .read(placementControllerProvider.notifier)
                              .evaluateListening(
                                currentQuestion.id,
                                userAnswer,
                              );
                        },
                      ),
              ),
              // 次へボタン（評価後に表示）
              if (_hasResult(currentQuestion, speakingResult, listeningResult))
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        ref
                            .read(placementControllerProvider.notifier)
                            .goToNextQuestion();
                      },
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: Text(
                        data.currentIndex < data.questions.length - 1
                            ? '次の問題へ'
                            : '結果を見る',
                      ),
                    ),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }

  bool _hasResult(
    PlacementQuestionModel question,
    PlacementSpeakingEvaluateResponseModel? speakingResult,
    PlacementListeningEvaluateResponseModel? listeningResult,
  ) {
    if (question.type == 'speaking') {
      return speakingResult != null;
    } else {
      return listeningResult != null;
    }
  }

  Widget _buildCompletionScreen(
    BuildContext context,
    WidgetRef ref,
    PlacementState data,
  ) {
    final result = data.submitResult;

    if (result == null) {
      // 提出中
      if (data.isSubmitting) {
        return const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('結果を送信中...'),
            ],
          ),
        );
      }

      // 提出ボタン
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.check_circle_outline,
                size: 80,
                color: Colors.blue,
              ),
              const SizedBox(height: 24),
              const Text(
                '全問回答完了！',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                '${data.questions.length}問すべての問題に回答しました。',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () async {
                    await ref
                        .read(placementControllerProvider.notifier)
                        .submit();
                  },
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('結果を送信'),
                ),
              ),
            ],
          ),
        ),
      );
    }

    // 結果表示
    final levelLabel = _getLevelLabel(result.placementLevel);
    final levelColor = _getLevelColor(result.placementLevel);

    return SingleChildScrollView(
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.emoji_events,
                size: 80,
                color: levelColor,
              ),
              const SizedBox(height: 24),
              const Text(
                'レベル判定完了！',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),

              // レベル表示
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                decoration: BoxDecoration(
                  color: levelColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: levelColor, width: 2),
                ),
                child: Column(
                  children: [
                    const Text(
                      'あなたのレベル',
                      style: TextStyle(fontSize: 14, color: Colors.grey),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      levelLabel,
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: levelColor,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // スコア表示
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const Text(
                        '平均スコア',
                        style: TextStyle(fontSize: 14, color: Colors.grey),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${result.score} / ${result.maxScore}',
                        style: const TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // シナリオ選択へ
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    // 認証状態にレベルテスト完了を反映
                    ref
                        .read(authStateProvider.notifier)
                        .applyPlacementResult(result);
                    context.go('/');
                  },
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('シナリオ選択へ'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getLevelLabel(String level) {
    switch (level.toLowerCase()) {
      case 'beginner':
        return '初級';
      case 'intermediate':
        return '中級';
      case 'advanced':
        return '上級';
      default:
        return level;
    }
  }

  Color _getLevelColor(String level) {
    switch (level.toLowerCase()) {
      case 'beginner':
        return Colors.green;
      case 'intermediate':
        return Colors.orange;
      case 'advanced':
        return Colors.purple;
      default:
        return Colors.blue;
    }
  }
}
