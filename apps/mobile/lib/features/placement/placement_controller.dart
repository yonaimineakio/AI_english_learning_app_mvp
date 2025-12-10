import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/models/placement_models.dart';
import '../../shared/services/api_client.dart';
import '../../shared/services/placement_api.dart';

class PlacementState {
  const PlacementState({
    required this.questions,
    required this.currentIndex,
    required this.speakingResults,
    required this.listeningResults,
    this.isSubmitting = false,
    this.isCompleted = false,
    this.submitResult,
  });

  final List<PlacementQuestionModel> questions;
  final int currentIndex;
  final Map<int, PlacementSpeakingEvaluateResponseModel> speakingResults;
  final Map<int, PlacementListeningEvaluateResponseModel> listeningResults;
  final bool isSubmitting;
  final bool isCompleted;
  final PlacementSubmitResponseModel? submitResult;

  PlacementState copyWith({
    List<PlacementQuestionModel>? questions,
    int? currentIndex,
    Map<int, PlacementSpeakingEvaluateResponseModel>? speakingResults,
    Map<int, PlacementListeningEvaluateResponseModel>? listeningResults,
    bool? isSubmitting,
    bool? isCompleted,
    PlacementSubmitResponseModel? submitResult,
  }) {
    return PlacementState(
      questions: questions ?? this.questions,
      currentIndex: currentIndex ?? this.currentIndex,
      speakingResults: speakingResults ?? this.speakingResults,
      listeningResults: listeningResults ?? this.listeningResults,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      isCompleted: isCompleted ?? this.isCompleted,
      submitResult: submitResult ?? this.submitResult,
    );
  }

  /// 全問題の回答リストを生成
  List<PlacementAnswerModel> get answers {
    final list = <PlacementAnswerModel>[];
    for (final q in questions) {
      int score = 0;
      if (q.type == 'speaking') {
        final result = speakingResults[q.id];
        score = result?.score ?? 0;
      } else {
        final result = listeningResults[q.id];
        score = result?.score ?? 0;
      }
      list.add(PlacementAnswerModel(questionId: q.id, score: score));
    }
    return list;
  }
}

class PlacementController extends AsyncNotifier<PlacementState> {
  late final PlacementApi _api;

  @override
  Future<PlacementState> build() async {
    _api = PlacementApi(ApiClient());
    final questions = await _api.getQuestions();
    return PlacementState(
      questions: questions,
      currentIndex: 0,
      speakingResults: {},
      listeningResults: {},
    );
  }

  /// スピーキング問題を評価
  Future<void> evaluateSpeaking(int questionId, String transcript) async {
    final current = state.valueOrNull;
    if (current == null) return;

    try {
      final result = await _api.evaluateSpeaking(
        questionId: questionId,
        userTranscription: transcript,
      );

      final updatedResults =
          Map<int, PlacementSpeakingEvaluateResponseModel>.from(
        current.speakingResults,
      )..[questionId] = result;

      state = AsyncData(current.copyWith(speakingResults: updatedResults));
    } catch (e) {
      // エラー時は状態を変更しない（UIでエラー表示）
      rethrow;
    }
  }

  /// リスニング問題を評価
  Future<void> evaluateListening(int questionId, List<String> userAnswer) async {
    final current = state.valueOrNull;
    if (current == null) return;

    try {
      final result = await _api.evaluateListening(
        questionId: questionId,
        userAnswer: userAnswer,
      );

      final updatedResults =
          Map<int, PlacementListeningEvaluateResponseModel>.from(
        current.listeningResults,
      )..[questionId] = result;

      state = AsyncData(current.copyWith(listeningResults: updatedResults));
    } catch (e) {
      // エラー時は状態を変更しない（UIでエラー表示）
      rethrow;
    }
  }

  /// 次の問題へ進む
  void goToNextQuestion() {
    final current = state.valueOrNull;
    if (current == null) return;

    final nextIndex = current.currentIndex + 1;
    if (nextIndex >= current.questions.length) {
      // 全問完了
      state = AsyncData(current.copyWith(isCompleted: true));
    } else {
      state = AsyncData(current.copyWith(currentIndex: nextIndex));
    }
  }

  /// 結果を送信
  Future<void> submit() async {
    final current = state.valueOrNull;
    if (current == null) return;

    state = AsyncData(current.copyWith(isSubmitting: true));

    try {
      final result = await _api.submitAnswers(current.answers);
      state = AsyncData(
        current.copyWith(
          isSubmitting: false,
          submitResult: result,
        ),
      );
    } catch (e) {
      state = AsyncData(current.copyWith(isSubmitting: false));
      rethrow;
    }
  }
}

final placementControllerProvider =
    AsyncNotifierProvider<PlacementController, PlacementState>(
  PlacementController.new,
);
