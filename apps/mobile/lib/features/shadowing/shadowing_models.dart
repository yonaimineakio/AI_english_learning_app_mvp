/// シャドーイング機能のモデル定義

class ShadowingUserProgress {
  final int attemptCount;
  final int? bestScore;
  final bool isCompleted;
  final DateTime? lastPracticedAt;

  const ShadowingUserProgress({
    this.attemptCount = 0,
    this.bestScore,
    this.isCompleted = false,
    this.lastPracticedAt,
  });

  factory ShadowingUserProgress.fromJson(Map<String, dynamic> json) {
    return ShadowingUserProgress(
      attemptCount: json['attempt_count'] ?? 0,
      bestScore: json['best_score'],
      isCompleted: json['is_completed'] ?? false,
      lastPracticedAt: json['last_practiced_at'] != null
          ? DateTime.parse(json['last_practiced_at'])
          : null,
    );
  }
}

class ShadowingSentence {
  final int id;
  final int scenarioId;
  final String keyPhrase;
  final String sentenceEn;
  final String sentenceJa;
  final int orderIndex;
  final String difficulty;
  final String? audioUrl;
  final ShadowingUserProgress? userProgress;

  const ShadowingSentence({
    required this.id,
    required this.scenarioId,
    required this.keyPhrase,
    required this.sentenceEn,
    required this.sentenceJa,
    required this.orderIndex,
    required this.difficulty,
    this.audioUrl,
    this.userProgress,
  });

  factory ShadowingSentence.fromJson(Map<String, dynamic> json) {
    return ShadowingSentence(
      id: json['id'],
      scenarioId: json['scenario_id'],
      keyPhrase: json['key_phrase'],
      sentenceEn: json['sentence_en'],
      sentenceJa: json['sentence_ja'],
      orderIndex: json['order_index'],
      difficulty: json['difficulty'],
      audioUrl: json['audio_url'],
      userProgress: json['user_progress'] != null
          ? ShadowingUserProgress.fromJson(json['user_progress'])
          : null,
    );
  }
}

class ScenarioShadowingResponse {
  final int scenarioId;
  final String scenarioName;
  final List<ShadowingSentence> sentences;
  final int totalSentences;
  final int completedCount;

  const ScenarioShadowingResponse({
    required this.scenarioId,
    required this.scenarioName,
    required this.sentences,
    required this.totalSentences,
    required this.completedCount,
  });

  factory ScenarioShadowingResponse.fromJson(Map<String, dynamic> json) {
    return ScenarioShadowingResponse(
      scenarioId: json['scenario_id'],
      scenarioName: json['scenario_name'],
      sentences: (json['sentences'] as List)
          .map((e) => ShadowingSentence.fromJson(e))
          .toList(),
      totalSentences: json['total_sentences'],
      completedCount: json['completed_count'],
    );
  }

  double get progressPercent =>
      totalSentences > 0 ? completedCount / totalSentences * 100 : 0;
}

class ShadowingAttemptResponse {
  final int shadowingSentenceId;
  final int attemptCount;
  final int bestScore;
  final bool isCompleted;
  final bool isNewBest;

  const ShadowingAttemptResponse({
    required this.shadowingSentenceId,
    required this.attemptCount,
    required this.bestScore,
    required this.isCompleted,
    required this.isNewBest,
  });

  factory ShadowingAttemptResponse.fromJson(Map<String, dynamic> json) {
    return ShadowingAttemptResponse(
      shadowingSentenceId: json['shadowing_sentence_id'],
      attemptCount: json['attempt_count'],
      bestScore: json['best_score'],
      isCompleted: json['is_completed'],
      isNewBest: json['is_new_best'],
    );
  }
}

class ScenarioProgressSummary {
  final int scenarioId;
  final String scenarioName;
  final String category;
  final String difficulty;
  final int totalSentences;
  final int completedSentences;
  final int progressPercent;
  final DateTime? lastPracticedAt;

  const ScenarioProgressSummary({
    required this.scenarioId,
    required this.scenarioName,
    required this.category,
    required this.difficulty,
    required this.totalSentences,
    required this.completedSentences,
    required this.progressPercent,
    this.lastPracticedAt,
  });

  factory ScenarioProgressSummary.fromJson(Map<String, dynamic> json) {
    return ScenarioProgressSummary(
      scenarioId: json['scenario_id'],
      scenarioName: json['scenario_name'],
      category: json['category'],
      difficulty: json['difficulty'],
      totalSentences: json['total_sentences'],
      completedSentences: json['completed_sentences'],
      progressPercent: json['progress_percent'],
      lastPracticedAt: json['last_practiced_at'] != null
          ? DateTime.parse(json['last_practiced_at'])
          : null,
    );
  }

  String get categoryLabel {
    switch (category) {
      case 'travel':
        return '旅行';
      case 'business':
        return 'ビジネス';
      case 'daily':
        return '日常会話';
      default:
        return category;
    }
  }

  String get difficultyLabel {
    switch (difficulty) {
      case 'beginner':
        return '初級';
      case 'intermediate':
        return '中級';
      case 'advanced':
        return '上級';
      default:
        return difficulty;
    }
  }
}

class ShadowingProgressResponse {
  final int totalScenarios;
  final int practicedScenarios;
  final int totalSentences;
  final int completedSentences;
  final int todayPracticeCount;
  final List<ScenarioProgressSummary> recentScenarios;

  const ShadowingProgressResponse({
    required this.totalScenarios,
    required this.practicedScenarios,
    required this.totalSentences,
    required this.completedSentences,
    required this.todayPracticeCount,
    required this.recentScenarios,
  });

  factory ShadowingProgressResponse.fromJson(Map<String, dynamic> json) {
    return ShadowingProgressResponse(
      totalScenarios: json['total_scenarios'],
      practicedScenarios: json['practiced_scenarios'],
      totalSentences: json['total_sentences'],
      completedSentences: json['completed_sentences'],
      todayPracticeCount: json['today_practice_count'],
      recentScenarios: (json['recent_scenarios'] as List)
          .map((e) => ScenarioProgressSummary.fromJson(e))
          .toList(),
    );
  }

  double get overallProgressPercent =>
      totalSentences > 0 ? completedSentences / totalSentences * 100 : 0;
}
