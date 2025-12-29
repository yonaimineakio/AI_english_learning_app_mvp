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
    this.roundIndex,
    this.userInputForRound,
  });

  final bool isUser;
  final String text;
  final String? feedbackShort;
  final String? improvedSentence;
  final int? roundIndex;
  final String? userInputForRound; // AI応答に対応するユーザー入力
}

class SessionUiState {
  const SessionUiState({
    required this.sessionId,
    required this.scenario,
    required this.messages,
    required this.roundTarget,
    required this.completedRounds,
    required this.goalsTotal,
    required this.goalsAchieved,
    required this.goalsStatus,
    required this.goalsLabels,
    required this.endPromptReason,
    required this.dismissedGoalsCompletedPrompt,
    required this.canExtend,
    required this.extensionOffered,
    this.isLoadingTurn = false,
    this.shouldEndSession = false,
  });

  final int sessionId;
  final ScenarioModel scenario;
  final List<MessageItem> messages;
  final int? roundTarget;
  final int? completedRounds;
  final int? goalsTotal;
  final int? goalsAchieved;
  final List<int>? goalsStatus;
  final List<String>? goalsLabels; // 各ゴールのラベル（テキスト）
  final String? endPromptReason; // user_intent | goals_completed
  final bool dismissedGoalsCompletedPrompt;
  final bool canExtend;
  final bool extensionOffered;
  final bool isLoadingTurn;
  final bool shouldEndSession;

  SessionUiState copyWith({
    List<MessageItem>? messages,
    int? roundTarget,
    int? completedRounds,
    int? goalsTotal,
    int? goalsAchieved,
    List<int>? goalsStatus,
    List<String>? goalsLabels,
    String? endPromptReason,
    bool? dismissedGoalsCompletedPrompt,
    bool? canExtend,
    bool? extensionOffered,
    bool? isLoadingTurn,
    bool? shouldEndSession,
  }) {
    return SessionUiState(
      sessionId: sessionId,
      scenario: scenario,
      messages: messages ?? this.messages,
      roundTarget: roundTarget ?? this.roundTarget,
      completedRounds: completedRounds ?? this.completedRounds,
      goalsTotal: goalsTotal ?? this.goalsTotal,
      goalsAchieved: goalsAchieved ?? this.goalsAchieved,
      goalsStatus: goalsStatus ?? this.goalsStatus,
      goalsLabels: goalsLabels ?? this.goalsLabels,
      endPromptReason: endPromptReason ?? this.endPromptReason,
      dismissedGoalsCompletedPrompt:
          dismissedGoalsCompletedPrompt ?? this.dismissedGoalsCompletedPrompt,
      canExtend: canExtend ?? this.canExtend,
      extensionOffered: extensionOffered ?? this.extensionOffered,
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
      roundTarget: null,
      completedRounds: null,
      goalsTotal: null,
      goalsAchieved: null,
      goalsStatus: null,
      goalsLabels: null,
      endPromptReason: null,
      dismissedGoalsCompletedPrompt: false,
      canExtend: false,
      extensionOffered: false,
    );
  }

  int? _defaultGoalsTotalForScenario(int scenarioId) {
    // Backend defines up to 3 goals per scenario id (1..21). Keep this list in sync
    // with the UI task labels mapping in `SessionTaskChecklistCard`.
    if (scenarioId <= 0) return null;
    return 3;
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

    final goalsLabels = res.goalsLabels;
    final goalsTotal =
        (goalsLabels != null && goalsLabels.isNotEmpty) ? goalsLabels.length : _defaultGoalsTotalForScenario(res.scenario.id);

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
        roundTarget: res.roundTarget,
        completedRounds: 0,
        goalsTotal: goalsTotal,
        goalsAchieved: 0,
        goalsStatus: goalsTotal == null
            ? null
            : List<int>.filled(
                goalsTotal,
                0,
              ),
        goalsLabels: goalsLabels, // start時点でAPIから取得
        endPromptReason: null,
        dismissedGoalsCompletedPrompt: false,
        canExtend: false,
        extensionOffered: false,
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
        roundIndex: turn.roundIndex,
        userInputForRound: text,
      );

      final newMessages = List<MessageItem>.from(updatedMessages)
        ..add(aiMessage);

      final nextReason = turn.endPromptReason;
      final isGoalsCompletedReason = nextReason == 'goals_completed';
      final shouldPrompt = turn.shouldEndSession &&
          !(isGoalsCompletedReason && current.dismissedGoalsCompletedPrompt);

      // Keep goals monotonic: once achieved, never revert to 0 during the session UI.
      List<int>? mergedGoalsStatus;
      if (turn.goalsStatus != null && current.goalsStatus != null) {
        final a = current.goalsStatus!;
        final b = turn.goalsStatus!;
        final n = a.length > b.length ? a.length : b.length;
        mergedGoalsStatus = List<int>.generate(n, (i) {
          final av = i < a.length ? a[i] : 0;
          final bv = i < b.length ? b[i] : 0;
          return (av == 1 || bv == 1) ? 1 : 0;
        });
      } else {
        mergedGoalsStatus = turn.goalsStatus ?? current.goalsStatus;
      }
      final mergedGoalsAchieved = mergedGoalsStatus == null
          ? (turn.goalsAchieved ?? current.goalsAchieved)
          : mergedGoalsStatus.where((v) => v == 1).length;

      state = AsyncData(
        current.copyWith(
          messages: newMessages,
          isLoadingTurn: false,
          roundTarget: turn.sessionStatus?.roundTarget ?? current.roundTarget,
          completedRounds: turn.sessionStatus?.completedRounds ??
              current.completedRounds ??
              turn.roundIndex,
          goalsTotal: turn.goalsTotal ?? current.goalsTotal,
          goalsAchieved: mergedGoalsAchieved,
          goalsStatus: mergedGoalsStatus,
          goalsLabels: turn.goalsLabels ?? current.goalsLabels,
          canExtend: turn.sessionStatus?.canExtend ?? current.canExtend,
          extensionOffered:
              turn.sessionStatus?.extensionOffered ?? current.extensionOffered,
          shouldEndSession: shouldPrompt,
          endPromptReason: nextReason,
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

  Future<void> extendCurrentSession() async {
    final current = state.valueOrNull;
    if (current == null) {
      throw StateError('No active session to extend');
    }
    final status = await _api.extendSession(sessionId: current.sessionId);
    state = AsyncData(
      current.copyWith(
        roundTarget: status.roundTarget,
        completedRounds: status.completedRounds,
        canExtend: status.canExtend,
        extensionOffered: status.extensionOffered,
        shouldEndSession: false,
        endPromptReason: null,
      ),
    );
  }

  /// 「終了提案」モーダルを閉じて会話を継続したいときに呼ぶ。
  /// shouldEndSession をクリアし、再表示ループを防ぐ。
  void dismissEndPrompt() {
    final current = state.valueOrNull;
    if (current == null) return;
    if (!current.shouldEndSession) return;
    final dismissedGoals = current.endPromptReason == 'goals_completed'
        ? true
        : current.dismissedGoalsCompletedPrompt;
    state = AsyncData(
      current.copyWith(
        shouldEndSession: false,
        endPromptReason: null,
        dismissedGoalsCompletedPrompt: dismissedGoals,
      ),
    );
  }
}

final sessionControllerProvider =
    AsyncNotifierProvider<SessionController, SessionUiState>(
  SessionController.new,
);


