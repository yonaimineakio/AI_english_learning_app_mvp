class PlacementQuestionModel {
  const PlacementQuestionModel({
    required this.id,
    required this.type,
    required this.prompt,
    required this.scenarioHint,
    this.targetSentence,
    this.audioText,
    this.puzzleWords,
  });

  final int id;
  final String type; // listening | speaking
  final String prompt;
  final String scenarioHint;
  final String? targetSentence; // Speaking用: ユーザーが読み上げる文
  final String? audioText; // Listening用: TTS読み上げテキスト
  final List<String>? puzzleWords; // Listening用: 並べ替え単語リスト

  factory PlacementQuestionModel.fromJson(Map<String, dynamic> json) {
    return PlacementQuestionModel(
      id: json['id'] as int,
      type: json['type'] as String,
      prompt: json['prompt'] as String,
      scenarioHint: json['scenario_hint'] as String,
      targetSentence: json['target_sentence'] as String?,
      audioText: json['audio_text'] as String?,
      puzzleWords: (json['puzzle_words'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
    );
  }
}

class PlacementSubmitResponseModel {
  const PlacementSubmitResponseModel({
    required this.score,
    required this.maxScore,
    required this.placementLevel,
    required this.placementCompletedAt,
  });

  final int score;
  final int maxScore;
  final String placementLevel;
  final DateTime placementCompletedAt;

  factory PlacementSubmitResponseModel.fromJson(Map<String, dynamic> json) {
    return PlacementSubmitResponseModel(
      score: json['score'] as int,
      maxScore: json['max_score'] as int,
      placementLevel: json['placement_level'] as String,
      placementCompletedAt:
          DateTime.parse(json['placement_completed_at'] as String),
    );
  }
}

/// 単語一致情報
class PlacementWordMatchModel {
  const PlacementWordMatchModel({
    required this.word,
    required this.matched,
    required this.index,
  });

  final String word;
  final bool matched;
  final int index;

  factory PlacementWordMatchModel.fromJson(Map<String, dynamic> json) {
    return PlacementWordMatchModel(
      word: json['word'] as String,
      matched: json['matched'] as bool,
      index: json['index'] as int,
    );
  }
}

/// スピーキング評価レスポンス
class PlacementSpeakingEvaluateResponseModel {
  const PlacementSpeakingEvaluateResponseModel({
    required this.questionId,
    required this.score,
    required this.isCorrect,
    required this.matchingWords,
    required this.targetSentence,
  });

  final int questionId;
  final int score;
  final bool isCorrect;
  final List<PlacementWordMatchModel> matchingWords;
  final String targetSentence;

  factory PlacementSpeakingEvaluateResponseModel.fromJson(
      Map<String, dynamic> json) {
    return PlacementSpeakingEvaluateResponseModel(
      questionId: json['question_id'] as int,
      score: json['score'] as int,
      isCorrect: json['is_correct'] as bool,
      matchingWords: (json['matching_words'] as List<dynamic>)
          .map((e) =>
              PlacementWordMatchModel.fromJson(Map<String, dynamic>.from(e as Map)))
          .toList(),
      targetSentence: json['target_sentence'] as String,
    );
  }
}

/// リスニング評価レスポンス
class PlacementListeningEvaluateResponseModel {
  const PlacementListeningEvaluateResponseModel({
    required this.questionId,
    required this.score,
    required this.isCorrect,
    required this.correctAnswer,
  });

  final int questionId;
  final int score;
  final bool isCorrect;
  final String correctAnswer;

  factory PlacementListeningEvaluateResponseModel.fromJson(
      Map<String, dynamic> json) {
    return PlacementListeningEvaluateResponseModel(
      questionId: json['question_id'] as int,
      score: json['score'] as int,
      isCorrect: json['is_correct'] as bool,
      correctAnswer: json['correct_answer'] as String,
    );
  }
}

/// 各問題の評価結果（提出用）
class PlacementAnswerModel {
  const PlacementAnswerModel({
    required this.questionId,
    required this.score,
  });

  final int questionId;
  final int score;

  Map<String, dynamic> toJson() {
    return {
      'question_id': questionId,
      'score': score,
    };
  }
}


