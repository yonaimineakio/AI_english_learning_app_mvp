import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/models/session_models.dart';
import '../../shared/services/api_client.dart';
import '../../shared/services/session_api.dart';

class MessageItem {
  const MessageItem({
    required this.isUser,
    required this.text,
    this.feedbackShort,
    this.improvedSentence,
  });

  final bool isUser;
  final String text;
  final String? feedbackShort;
  final String? improvedSentence;
}

class SessionUiState {
  const SessionUiState({
    required this.sessionId,
    required this.scenario,
    required this.messages,
    required this.goalsTotal,
    required this.goalsAchieved,
    this.isLoadingTurn = false,
    this.shouldEndSession = false,
  });

  final int sessionId;
  final ScenarioModel scenario;
  final List<MessageItem> messages;
  final int? goalsTotal;
  final int? goalsAchieved;
  final bool isLoadingTurn;
  final bool shouldEndSession;

  SessionUiState copyWith({
    List<MessageItem>? messages,
    int? goalsTotal,
    int? goalsAchieved,
    bool? isLoadingTurn,
    bool? shouldEndSession,
  }) {
    return SessionUiState(
      sessionId: sessionId,
      scenario: scenario,
      messages: messages ?? this.messages,
      goalsTotal: goalsTotal ?? this.goalsTotal,
      goalsAchieved: goalsAchieved ?? this.goalsAchieved,
      isLoadingTurn: isLoadingTurn ?? this.isLoadingTurn,
      shouldEndSession: shouldEndSession ?? this.shouldEndSession,
    );
  }
}

class SessionController extends AsyncNotifier<SessionUiState> {
  late final SessionApi _api;

  @override
  Future<SessionUiState> build() async {
    _api = SessionApi(ApiClient());
    // 初期状態では「空のセッション」を返し、実際の開始処理は
    // startNewSession で上書きする。
    final placeholderScenario = ScenarioModel(
      id: 0,
      name: 'Loading scenario',
      description: '',
      category: 'travel',
      difficulty: 'beginner',
    );
    return SessionUiState(
      sessionId: 0,
      scenario: placeholderScenario,
      messages: const [],
      goalsTotal: null,
      goalsAchieved: null,
    );
  }

  Future<int> startNewSession({
    required int scenarioId,
    required String difficulty,
    required String mode,
  }) async {
    final res = await _api.startSession(
      scenarioId: scenarioId,
      roundTarget: 6,
      difficulty: difficulty,
      mode: mode,
    );

    final messages = <MessageItem>[];
    if (res.initialAiMessage != null &&
        res.initialAiMessage!.trim().isNotEmpty) {
      messages.add(
        MessageItem(
          isUser: false,
          text: res.initialAiMessage!,
        ),
      );
    }

    state = AsyncData(
      SessionUiState(
        sessionId: res.sessionId,
        scenario: res.scenario,
        messages: messages,
        goalsTotal: null,
        goalsAchieved: null,
      ),
    );

    return res.sessionId;
  }

  Future<void> sendUserMessage(String text) async {
    final current = state.valueOrNull;
    if (current == null || text.trim().isEmpty) return;

    final updatedMessages = List<MessageItem>.from(current.messages)
      ..add(MessageItem(isUser: true, text: text));
    state = AsyncData(
      current.copyWith(
        messages: updatedMessages,
        isLoadingTurn: true,
      ),
    );

    try {
      final turn = await _api.sendTurn(
        sessionId: current.sessionId,
        userInput: text,
      );

      final aiMessage = MessageItem(
        isUser: false,
        text: turn.aiReplyText,
        feedbackShort: turn.feedbackShort,
        improvedSentence: turn.improvedSentence,
      );

      final newMessages = List<MessageItem>.from(updatedMessages)
        ..add(aiMessage);

      state = AsyncData(
        current.copyWith(
          messages: newMessages,
          isLoadingTurn: false,
          goalsTotal: turn.goalsTotal ?? current.goalsTotal,
          goalsAchieved: turn.goalsAchieved ?? current.goalsAchieved,
          shouldEndSession: turn.shouldEndSession,
        ),
      );
    } catch (error, stackTrace) {
      state = AsyncData(
        current.copyWith(
          messages: updatedMessages,
          isLoadingTurn: false,
        ),
      );
      Error.throwWithStackTrace(error, stackTrace);
    }
  }

  Future<SessionEndResponseModel> endCurrentSession() async {
    final current = state.valueOrNull;
    if (current == null) {
      throw StateError('No active session to end');
    }
    return _api.endSession(sessionId: current.sessionId);
  }
}

final sessionControllerProvider =
    AsyncNotifierProvider<SessionController, SessionUiState>(
  SessionController.new,
);


