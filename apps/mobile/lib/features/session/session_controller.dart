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
    this.scenario,
    this.customScenario,
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
  final ScenarioModel? scenario; // 通常シナリオ用
  final CustomScenarioResponseModel? customScenario; // カスタムシナリオ用
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

  /// シナリオ名（通常シナリオまたはカスタムシナリオの名前）
  String get scenarioName =>
      scenario?.name ?? customScenario?.name ?? 'Unknown Scenario';

  /// カスタムシナリオかどうか
  bool get isCustomScenario => customScenario != null;

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
      customScenario: customScenario,
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
      customScenario: null,
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

  int? _defaultGoalsTotalForScenario(int? scenarioId, {bool isCustomScenario = false}) {
    // カスタムシナリオの場合はゴールを無効化
    if (isCustomScenario) return null;
    // Backend defines up to 3 goals per scenario id (1..21). Keep this list in sync
    // with the UI task labels mapping in `SessionTaskChecklistCard`.
    if (scenarioId == null || scenarioId <= 0) return null;
    return 3;
  }

  Future<int> startNewSession({
    int? scenarioId,
    int? customScenarioId,
    required String difficulty,
    required String mode,
  }) async {
    final res = await _api.startSession(
      scenarioId: scenarioId,
      customScenarioId: customScenarioId,
      roundTarget: 6,
      difficulty: difficulty,
      mode: mode,
    );

    final goalsLabels = res.goalsLabels;
    final isCustomScenario = customScenarioId != null || res.customScenario != null;
    // カスタムシナリオの場合はゴールを無効化
    final int? goalsTotal;
    if (isCustomScenario) {
      goalsTotal = null;
    } else if (goalsLabels != null && goalsLabels.isNotEmpty) {
      goalsTotal = goalsLabels.length;
    } else {
      goalsTotal = _defaultGoalsTotalForScenario(scenarioId, isCustomScenario: false);
    }

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
        customScenario: res.customScenario,
        messages: messages,
        roundTarget: res.roundTarget,
        completedRounds: 0,
        goalsTotal: goalsTotal,
        goalsAchieved: isCustomScenario ? null : 0,
        goalsStatus: goalsTotal == null
            ? null
            : List<int>.filled(
                goalsTotal,
                0,
              ),
        goalsLabels: isCustomScenario ? null : goalsLabels, // カスタムシナリオの場合はnull
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
      // カスタムシナリオではgoals_completedの終了提案を無視
      final shouldPrompt = turn.shouldEndSession &&
          !(isGoalsCompletedReason && current.dismissedGoalsCompletedPrompt) &&
          !(isGoalsCompletedReason && current.isCustomScenario);

      // カスタムシナリオの場合はゴールを常にnullに保つ
      int? mergedGoalsTotal;
      int? mergedGoalsAchieved;
      List<int>? mergedGoalsStatus;
      List<String>? mergedGoalsLabels;

      if (current.isCustomScenario) {
        // カスタムシナリオの場合はゴールを無効化
        mergedGoalsTotal = null;
        mergedGoalsAchieved = null;
        mergedGoalsStatus = null;
        mergedGoalsLabels = null;
      } else {
        // Keep goals monotonic: once achieved, never revert to 0 during the session UI.
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
        mergedGoalsAchieved = mergedGoalsStatus == null
            ? (turn.goalsAchieved ?? current.goalsAchieved)
            : mergedGoalsStatus.where((v) => v == 1).length;
        mergedGoalsTotal = turn.goalsTotal ?? current.goalsTotal;
        mergedGoalsLabels = turn.goalsLabels ?? current.goalsLabels;
      }

      state = AsyncData(
        current.copyWith(
          messages: newMessages,
          isLoadingTurn: false,
          roundTarget: turn.sessionStatus?.roundTarget ?? current.roundTarget,
          completedRounds: turn.sessionStatus?.completedRounds ??
              current.completedRounds ??
              turn.roundIndex,
          goalsTotal: mergedGoalsTotal,
          goalsAchieved: mergedGoalsAchieved,
          goalsStatus: mergedGoalsStatus,
          goalsLabels: mergedGoalsLabels,
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


