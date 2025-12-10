import 'package:dio/dio.dart';

import '../models/placement_models.dart';
import 'api_client.dart';

class PlacementApi {
  PlacementApi(this._client);

  final ApiClient _client;

  Future<List<PlacementQuestionModel>> getQuestions() async {
    final Response<dynamic> res = await _client.getJson('/placement/questions');
    final data = Map<String, dynamic>.from(res.data as Map);
    final questions = (data['questions'] as List<dynamic>)
        .map(
          (e) => PlacementQuestionModel.fromJson(
            Map<String, dynamic>.from(e as Map),
          ),
        )
        .toList();
    return questions;
  }

  /// スピーキング問題を評価
  Future<PlacementSpeakingEvaluateResponseModel> evaluateSpeaking({
    required int questionId,
    required String userTranscription,
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/placement/evaluate-speaking',
      data: {
        'question_id': questionId,
        'user_transcription': userTranscription,
      },
    );
    return PlacementSpeakingEvaluateResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// リスニング問題を評価
  Future<PlacementListeningEvaluateResponseModel> evaluateListening({
    required int questionId,
    required List<String> userAnswer,
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/placement/evaluate-listening',
      data: {
        'question_id': questionId,
        'user_answer': userAnswer,
      },
    );
    return PlacementListeningEvaluateResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// 全問題の回答を送信してレベルを決定
  Future<PlacementSubmitResponseModel> submitAnswers(
    List<PlacementAnswerModel> answers,
  ) async {
    final Response<dynamic> res = await _client.postJson(
      '/placement/submit',
      data: {
        'answers': answers.map((a) => a.toJson()).toList(),
      },
    );
    return PlacementSubmitResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }
}


