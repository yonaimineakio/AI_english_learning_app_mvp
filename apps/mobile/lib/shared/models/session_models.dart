class ScenarioModel {
  const ScenarioModel({
    required this.id,
    required this.name,
    required this.description,
    required this.category,
    required this.difficulty,
  });

  final int id;
  final String name;
  final String? description;
  final String category; // travel | business | daily
  final String difficulty; // beginner | intermediate | advanced

  factory ScenarioModel.fromJson(Map<String, dynamic> json) {
    return ScenarioModel(
      id: json['id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
      category: json['category'] as String,
      difficulty: json['difficulty'] as String,
    );
  }
}

class SessionStartResponseModel {
  const SessionStartResponseModel({
    required this.sessionId,
    required this.scenario,
    required this.roundTarget,
    required this.difficulty,
    required this.mode,
    this.initialAiMessage,
  });

  final int sessionId;
  final ScenarioModel scenario;
  final int roundTarget;
  final String difficulty;
  final String mode;
  final String? initialAiMessage;

  factory SessionStartResponseModel.fromJson(Map<String, dynamic> json) {
    return SessionStartResponseModel(
      sessionId: json['session_id'] as int,
      scenario: ScenarioModel.fromJson(json['scenario'] as Map<String, dynamic>),
      roundTarget: json['round_target'] as int,
      difficulty: json['difficulty'] as String,
      mode: json['mode'] as String,
      initialAiMessage: json['initial_ai_message'] as String?,
    );
  }
}

class SessionStatusResponseModel {
  const SessionStatusResponseModel({
    required this.sessionId,
    required this.scenarioId,
    required this.roundTarget,
    required this.completedRounds,
    required this.difficulty,
    required this.mode,
    required this.isActive,
    this.difficultyLabel,
    this.modeLabel,
    this.extensionOffered = false,
    this.scenarioName,
    this.canExtend = false,
    this.initialAiMessage,
  });

  final int sessionId;
  final int scenarioId;
  final int roundTarget;
  final int completedRounds;
  final String difficulty;
  final String mode;
  final bool isActive;
  final String? difficultyLabel;
  final String? modeLabel;
  final bool extensionOffered;
  final String? scenarioName;
  final bool canExtend;
  final String? initialAiMessage;

  factory SessionStatusResponseModel.fromJson(Map<String, dynamic> json) {
    return SessionStatusResponseModel(
      sessionId: json['session_id'] as int,
      scenarioId: json['scenario_id'] as int,
      roundTarget: json['round_target'] as int,
      completedRounds: json['completed_rounds'] as int,
      difficulty: json['difficulty'] as String,
      mode: json['mode'] as String,
      isActive: json['is_active'] as bool,
      difficultyLabel: json['difficulty_label'] as String?,
      modeLabel: json['mode_label'] as String?,
      extensionOffered: (json['extension_offered'] as bool?) ?? false,
      scenarioName: json['scenario_name'] as String?,
      canExtend: (json['can_extend'] as bool?) ?? false,
      initialAiMessage: json['initial_ai_message'] as String?,
    );
  }
}

class ConversationAiReplyModel {
  const ConversationAiReplyModel({
    required this.message,
    required this.feedbackShort,
    required this.improvedSentence,
    this.tags,
    this.details,
    this.scores,
  });

  final String message;
  final String feedbackShort;
  final String improvedSentence;
  final List<String>? tags;
  final Map<String, dynamic>? details;
  final Map<String, int?>? scores;

  factory ConversationAiReplyModel.fromJson(Map<String, dynamic> json) {
    return ConversationAiReplyModel(
      message: json['message'] as String,
      feedbackShort: json['feedback_short'] as String,
      improvedSentence: json['improved_sentence'] as String,
      tags: (json['tags'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList(),
      details: json['details'] != null
          ? Map<String, dynamic>.from(json['details'] as Map)
          : null,
      scores: json['scores'] != null
          ? (json['scores'] as Map<String, dynamic>).map(
              (key, value) => MapEntry(key, value as int?),
            )
          : null,
    );
  }
}

class TurnResponseModel {
  const TurnResponseModel({
    required this.roundIndex,
    required this.aiReplyText,
    required this.feedbackShort,
    required this.improvedSentence,
    this.tags,
    this.responseTimeMs,
    this.provider,
    this.sessionStatus,
    this.shouldEndSession = false,
    this.endPromptReason,
    this.goalsTotal,
    this.goalsAchieved,
    this.goalsStatus,
  });

  final int roundIndex;
  final String aiReplyText;
  final String feedbackShort;
  final String improvedSentence;
  final List<String>? tags;
  final int? responseTimeMs;
  final String? provider;
  final SessionStatusResponseModel? sessionStatus;
  final bool shouldEndSession;
  final String? endPromptReason; // user_intent | goals_completed
  final int? goalsTotal;
  final int? goalsAchieved;
  final List<int>? goalsStatus;

  factory TurnResponseModel.fromJson(Map<String, dynamic> json) {
    final aiReply = json['ai_reply'];
    String aiText;
    if (aiReply is String) {
      aiText = aiReply;
    } else if (aiReply is Map<String, dynamic>) {
      aiText = (aiReply['message'] ?? '').toString();
    } else {
      aiText = '';
    }

    return TurnResponseModel(
      roundIndex: json['round_index'] as int,
      aiReplyText: aiText,
      feedbackShort: json['feedback_short'] as String,
      improvedSentence: json['improved_sentence'] as String,
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e.toString()).toList(),
      responseTimeMs: json['response_time_ms'] as int?,
      provider: json['provider'] as String?,
      sessionStatus: json['session_status'] != null
          ? SessionStatusResponseModel.fromJson(
              json['session_status'] as Map<String, dynamic>,
            )
          : null,
      shouldEndSession: (json['should_end_session'] as bool?) ?? false,
      endPromptReason: json['end_prompt_reason'] as String?,
      goalsTotal: json['goals_total'] as int?,
      goalsAchieved: json['goals_achieved'] as int?,
      goalsStatus: (json['goals_status'] as List<dynamic>?)
          ?.map((e) => e as int)
          .toList(),
    );
  }
}

class TopPhraseModel {
  const TopPhraseModel({
    required this.phrase,
    required this.explanation,
    this.extra,
  });

  final String phrase;
  final String explanation;
  final Map<String, dynamic>? extra;

  factory TopPhraseModel.fromJson(Map<String, dynamic> json) {
    return TopPhraseModel(
      phrase: json['phrase'] as String? ?? '',
      explanation: json['explanation'] as String? ?? '',
      extra: Map<String, dynamic>.from(json),
    );
  }
}

class SessionEndResponseModel {
  const SessionEndResponseModel({
    required this.sessionId,
    required this.completedRounds,
    required this.topPhrases,
    required this.difficulty,
    required this.mode,
    this.nextReviewAt,
    this.scenarioName,
    this.goalsTotal,
    this.goalsAchieved,
    this.goalsStatus,
  });

  final int sessionId;
  final int completedRounds;
  final List<TopPhraseModel> topPhrases;
  final DateTime? nextReviewAt;
  final String? scenarioName;
  final String difficulty;
  final String mode;
  final int? goalsTotal;
  final int? goalsAchieved;
  final List<int>? goalsStatus;

  factory SessionEndResponseModel.fromJson(Map<String, dynamic> json) {
    return SessionEndResponseModel(
      sessionId: json['session_id'] as int,
      completedRounds: json['completed_rounds'] as int,
      topPhrases: (json['top_phrases'] as List<dynamic>)
          .map(
            (e) => TopPhraseModel.fromJson(
              Map<String, dynamic>.from(e as Map),
            ),
          )
          .toList(),
      nextReviewAt: json['next_review_at'] != null
          ? DateTime.parse(json['next_review_at'] as String)
          : null,
      scenarioName: json['scenario_name'] as String?,
      difficulty: json['difficulty'] as String,
      mode: json['mode'] as String,
      goalsTotal: json['goals_total'] as int?,
      goalsAchieved: json['goals_achieved'] as int?,
      goalsStatus: (json['goals_status'] as List<dynamic>?)
          ?.map((e) => e as int)
          .toList(),
    );
  }
}


