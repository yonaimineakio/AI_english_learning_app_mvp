class ReviewItemModel {
  const ReviewItemModel({
    required this.id,
    required this.userId,
    required this.phrase,
    required this.explanation,
    required this.dueAt,
    required this.isCompleted,
    required this.createdAt,
    this.completedAt,
  });

  final int id;
  final int userId;
  final String phrase;
  final String explanation;
  final DateTime dueAt;
  final bool isCompleted;
  final DateTime createdAt;
  final DateTime? completedAt;

  factory ReviewItemModel.fromJson(Map<String, dynamic> json) {
    return ReviewItemModel(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      phrase: json['phrase'] as String,
      explanation: json['explanation'] as String,
      dueAt: DateTime.parse(json['due_at'] as String),
      isCompleted: json['is_completed'] as bool,
      createdAt: DateTime.parse(json['created_at'] as String),
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String)
          : null,
    );
  }
}

/// 保存した表現
class SavedPhraseModel {
  const SavedPhraseModel({
    required this.id,
    required this.userId,
    required this.phrase,
    required this.explanation,
    this.originalInput,
    this.sessionId,
    this.roundIndex,
    this.convertedToReviewId,
    required this.createdAt,
  });

  final int id;
  final int userId;
  final String phrase;
  final String explanation;
  final String? originalInput;
  final int? sessionId;
  final int? roundIndex;
  final int? convertedToReviewId;
  final DateTime createdAt;

  factory SavedPhraseModel.fromJson(Map<String, dynamic> json) {
    return SavedPhraseModel(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      phrase: json['phrase'] as String,
      explanation: json['explanation'] as String,
      originalInput: json['original_input'] as String?,
      sessionId: json['session_id'] as int?,
      roundIndex: json['round_index'] as int?,
      convertedToReviewId: json['converted_to_review_id'] as int?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

/// 保存した表現一覧レスポンス
class SavedPhrasesListResponseModel {
  const SavedPhrasesListResponseModel({
    required this.savedPhrases,
  });

  final List<SavedPhraseModel> savedPhrases;

  factory SavedPhrasesListResponseModel.fromJson(Map<String, dynamic> json) {
    return SavedPhrasesListResponseModel(
      savedPhrases: (json['saved_phrases'] as List<dynamic>)
          .map(
            (e) => SavedPhraseModel.fromJson(
              Map<String, dynamic>.from(e as Map),
            ),
          )
          .toList(),
    );
  }
}

/// 保存済みチェックのレスポンス
class SavedPhraseCheckResponseModel {
  const SavedPhraseCheckResponseModel({
    required this.isSaved,
    this.savedPhraseId,
  });

  final bool isSaved;
  final int? savedPhraseId;

  factory SavedPhraseCheckResponseModel.fromJson(Map<String, dynamic> json) {
    return SavedPhraseCheckResponseModel(
      isSaved: json['is_saved'] as bool,
      savedPhraseId: json['saved_phrase_id'] as int?,
    );
  }
}

/// 復習統計
class ReviewStatsModel {
  const ReviewStatsModel({
    required this.totalReviewItems,
    required this.completedReviewItems,
    required this.completionRate,
  });

  final int totalReviewItems;
  final int completedReviewItems;
  final double completionRate;

  factory ReviewStatsModel.fromJson(Map<String, dynamic> json) {
    return ReviewStatsModel(
      totalReviewItems: json['total_items'] as int,
      completedReviewItems: json['completed_items'] as int,
      completionRate: (json['completion_rate'] as num).toDouble(),
    );
  }
}

class ReviewNextResponseModel {
  const ReviewNextResponseModel({
    required this.reviewItems,
    required this.totalCount,
  });

  final List<ReviewItemModel> reviewItems;
  final int totalCount;

  factory ReviewNextResponseModel.fromJson(Map<String, dynamic> json) {
    return ReviewNextResponseModel(
      reviewItems: (json['review_items'] as List<dynamic>)
          .map(
            (e) => ReviewItemModel.fromJson(
              Map<String, dynamic>.from(e as Map),
            ),
          )
          .toList(),
      totalCount: json['total_count'] as int,
    );
  }
}

/// 復習用の問題（スピーキング/リスニング）
class ReviewQuestionModel {
  const ReviewQuestionModel({
    required this.questionType,
    required this.prompt,
    this.hint,
    this.targetSentence,
    this.audioText,
    this.puzzleWords,
  });

  final String questionType; // "speaking" or "listening"
  final String prompt;
  final String? hint;
  // スピーキング用: ユーザーが読み上げるターゲット文
  final String? targetSentence;
  // リスニング用: TTS読み上げテキスト
  final String? audioText;
  // リスニング用: 単語パズル（正解順の単語リスト）
  final List<String>? puzzleWords;

  factory ReviewQuestionModel.fromJson(Map<String, dynamic> json) {
    return ReviewQuestionModel(
      questionType: json['question_type'] as String,
      prompt: json['prompt'] as String,
      hint: json['hint'] as String?,
      targetSentence: json['target_sentence'] as String?,
      audioText: json['audio_text'] as String?,
      puzzleWords: json['puzzle_words'] != null
          ? (json['puzzle_words'] as List<dynamic>)
              .map((e) => e as String)
              .toList()
          : null,
    );
  }
}

/// 復習アイテムに対する問題一式
class ReviewQuestionsResponseModel {
  const ReviewQuestionsResponseModel({
    required this.reviewItemId,
    required this.phrase,
    required this.explanation,
    required this.speaking,
    required this.listening,
  });

  final int reviewItemId;
  final String phrase;
  final String explanation;
  final ReviewQuestionModel speaking;
  final ReviewQuestionModel listening;

  factory ReviewQuestionsResponseModel.fromJson(Map<String, dynamic> json) {
    return ReviewQuestionsResponseModel(
      reviewItemId: json['review_item_id'] as int,
      phrase: json['phrase'] as String,
      explanation: json['explanation'] as String,
      speaking: ReviewQuestionModel.fromJson(
        Map<String, dynamic>.from(json['speaking'] as Map),
      ),
      listening: ReviewQuestionModel.fromJson(
        Map<String, dynamic>.from(json['listening'] as Map),
      ),
    );
  }
}

/// 単語の一致情報
class WordMatchModel {
  const WordMatchModel({
    required this.word,
    required this.matched,
    required this.index,
  });

  final String word;
  final bool matched;
  final int index;

  factory WordMatchModel.fromJson(Map<String, dynamic> json) {
    return WordMatchModel(
      word: json['word'] as String,
      matched: json['matched'] as bool,
      index: json['index'] as int,
    );
  }
}

/// 復習の評価結果レスポンス
class ReviewEvaluateResponseModel {
  const ReviewEvaluateResponseModel({
    required this.reviewItemId,
    required this.questionType,
    required this.score,
    required this.isCorrect,
    required this.isCompleted,
    this.nextDueAt,
    this.matchingWords,
    this.correctAnswer,
  });

  final int reviewItemId;
  final String questionType;
  final int score; // 0-100
  final bool isCorrect;
  final bool isCompleted;
  final DateTime? nextDueAt;
  // スピーキング用: 単語ごとの一致情報
  final List<WordMatchModel>? matchingWords;
  // 正解文（フィードバック用）
  final String? correctAnswer;

  factory ReviewEvaluateResponseModel.fromJson(Map<String, dynamic> json) {
    return ReviewEvaluateResponseModel(
      reviewItemId: json['review_item_id'] as int,
      questionType: json['question_type'] as String,
      score: json['score'] as int,
      isCorrect: json['is_correct'] as bool,
      isCompleted: json['is_completed'] as bool,
      nextDueAt: json['next_due_at'] != null
          ? DateTime.parse(json['next_due_at'] as String)
          : null,
      matchingWords: json['matching_words'] != null
          ? (json['matching_words'] as List<dynamic>)
              .map(
                (e) => WordMatchModel.fromJson(
                  Map<String, dynamic>.from(e as Map),
                ),
              )
              .toList()
          : null,
      correctAnswer: json['correct_answer'] as String?,
    );
  }
}
