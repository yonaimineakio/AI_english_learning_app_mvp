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
    required this.transcripts,
    this.isSubmitting = false,
    this.isCompleted = false,
    this.submitResult,
  });

  final List<PlacementQuestionModel> questions;
  final int currentIndex;
  final Map<int, PlacementSpeakingEvaluateResponseModel> speakingResults;
  final Map<int, PlacementListeningEvaluateResponseModel> listeningResults;
  final Map<int, String> transcripts; // questionId -> STT text

  final bool isSubmitting;
  final bool isCompleted;
  final PlacementSubmitResponseModel? submitResult;

  PlacementState copyWith({
    List<PlacementQuestionModel>? questions,
    int? currentIndex,
    Map<int, PlacementSpeakingEvaluateResponseModel>? speakingResults,
    Map<int, PlacementListeningEvaluateResponseModel>? listeningResults,
    Map<int, String>? transcripts,
    bool? isSubmitting,
    bool? isCompleted,
    PlacementSubmitResponseModel? submitResult,
  }) {
    return PlacementState(
      questions: questions ?? this.questions,
      currentIndex: currentIndex ?? this.currentIndex,
      speakingResults: speakingResults ?? this.speakingResults,
      listeningResults: listeningResults ?? this.listeningResults,
      transcripts: transcripts ?? this.transcripts,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      isCompleted: isCompleted ?? this.isCompleted,
      submitResult: submitResult ?? this.submitResult,
    );
  }

  int get totalQuestions => questions.length;

  PlacementQuestionModel? get currentQuestion {
    if (questions.isEmpty) return null;
    if (currentIndex < 0 || currentIndex >= questions.length) return null;
    return questions[currentIndex];
  }

  bool get isLastQuestion => totalQuestions > 0 && currentIndex == totalQuestions - 1;

  /// 0.0 - 1.0 (progress bar)
  double get progress {
    if (totalQuestions == 0) return 0;
    return currentIndex / totalQuestions;
  }

  bool hasResultForQuestion(PlacementQuestionModel q) {
    if (q.type == 'speaking') return speakingResults.containsKey(q.id);
    return listeningResults.containsKey(q.id);
  }

  /// 全問題の回答リストを生成（submit用）
  List<PlacementAnswerModel> get answers {
    return questions.map((q) {
      final score = q.type == 'speaking'
          ? (speakingResults[q.id]?.score ?? 0)
          : (listeningResults[q.id]?.score ?? 0);
      return PlacementAnswerModel(questionId: q.id, score: score);
    }).toList();
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
      speakingResults: const {},
      listeningResults: const {},
      transcripts: const {},
    );
  }

  Future<PlacementSpeakingEvaluateResponseModel> evaluateSpeaking({
    required int questionId,
    required String transcript,
  }) async {
    final current = state.valueOrNull;
    if (current == null) {
      throw StateError('Placement state is not ready');
    }
    if (transcript.trim().isEmpty) {
      throw ArgumentError('transcript must not be empty');
    }

    final result = await _api.evaluateSpeaking(
      questionId: questionId,
      userTranscription: transcript,
    );

    final updatedResults = Map<int, PlacementSpeakingEvaluateResponseModel>.from(
      current.speakingResults,
    )..[questionId] = result;
    final updatedTranscripts = Map<int, String>.from(current.transcripts)
      ..[questionId] = transcript;

    state = AsyncData(
      current.copyWith(
        speakingResults: updatedResults,
        transcripts: updatedTranscripts,
      ),
    );
    return result;
  }

  Future<PlacementListeningEvaluateResponseModel> evaluateListening({
    required int questionId,
    required List<String> userAnswer,
  }) async {
    final current = state.valueOrNull;
    if (current == null) {
      throw StateError('Placement state is not ready');
    }
    if (userAnswer.isEmpty) {
      throw ArgumentError('userAnswer must not be empty');
    }

    final result = await _api.evaluateListening(
      questionId: questionId,
      userAnswer: userAnswer,
    );

    final updatedResults = Map<int, PlacementListeningEvaluateResponseModel>.from(
      current.listeningResults,
    )..[questionId] = result;

    state = AsyncData(current.copyWith(listeningResults: updatedResults));
    return result;
  }

  void retryQuestion(int questionId) {
    final current = state.valueOrNull;
    if (current == null) return;

    final updatedSpeaking = Map<int, PlacementSpeakingEvaluateResponseModel>.from(current.speakingResults)
      ..remove(questionId);
    final updatedListening = Map<int, PlacementListeningEvaluateResponseModel>.from(current.listeningResults)
      ..remove(questionId);
    final updatedTranscripts = Map<int, String>.from(current.transcripts)
      ..remove(questionId);

    state = AsyncData(
      current.copyWith(
        speakingResults: updatedSpeaking,
        listeningResults: updatedListening,
        transcripts: updatedTranscripts,
      ),
    );
  }

  void goToNextQuestion() {
    final current = state.valueOrNull;
    if (current == null) return;

    final nextIndex = current.currentIndex + 1;
    if (nextIndex >= current.questions.length) {
      state = AsyncData(current.copyWith(isCompleted: true));
      return;
    }
    state = AsyncData(current.copyWith(currentIndex: nextIndex));
  }

  Future<PlacementSubmitResponseModel> submit() async {
    final current = state.valueOrNull;
    if (current == null) {
      throw StateError('Placement state is not ready');
    }

    state = AsyncData(current.copyWith(isSubmitting: true));
    try {
      final result = await _api.submitAnswers(current.answers);
      final latest = state.valueOrNull ?? current;
      state = AsyncData(
        latest.copyWith(
          isSubmitting: false,
          isCompleted: true,
          submitResult: result,
        ),
      );
      return result;
    } catch (e) {
      final latest = state.valueOrNull ?? current;
      state = AsyncData(latest.copyWith(isSubmitting: false));
      rethrow;
    }
  }
}

final placementControllerProvider =
    AsyncNotifierProvider<PlacementController, PlacementState>(
  PlacementController.new,
);
