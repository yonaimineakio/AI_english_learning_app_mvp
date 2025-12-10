import 'package:dio/dio.dart';

import '../models/review_models.dart';
import 'api_client.dart';

class ReviewApi {
  ReviewApi(this._client);

  final ApiClient _client;

  Future<ReviewNextResponseModel> getNextReviews() async {
    final Response<dynamic> res = await _client.getJson('/reviews/next');
    return ReviewNextResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  Future<ReviewItemModel> completeReview({
    required int reviewId,
    required String result, // "correct" | "incorrect"
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/reviews/$reviewId/complete',
      data: {
        'result': result,
      },
    );
    return ReviewItemModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// 復習アイテムに対するスピーキング・リスニング問題を取得
  Future<ReviewQuestionsResponseModel> getReviewQuestions({
    required int reviewId,
  }) async {
    final Response<dynamic> res = await _client.getJson(
      '/reviews/$reviewId/questions',
    );
    return ReviewQuestionsResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// スピーキング問題の評価を送信（発話内容とターゲット文の一致率で評価）
  Future<ReviewEvaluateResponseModel> evaluateSpeaking({
    required int reviewId,
    required String userTranscription, // 音声認識結果
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/reviews/$reviewId/evaluate',
      data: {
        'question_type': 'speaking',
        'user_transcription': userTranscription,
      },
    );
    return ReviewEvaluateResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// リスニング問題の評価を送信（単語パズルの完全一致で評価）
  Future<ReviewEvaluateResponseModel> evaluateListening({
    required int reviewId,
    required List<String> userAnswer, // ユーザーが並べた単語リスト
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/reviews/$reviewId/evaluate',
      data: {
        'question_type': 'listening',
        'user_answer': userAnswer,
      },
    );
    return ReviewEvaluateResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }
}
