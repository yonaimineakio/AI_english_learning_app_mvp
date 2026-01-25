import 'package:dio/dio.dart';

import '../../shared/services/api_client.dart';
import 'shadowing_models.dart';

/// シャドーイング機能のAPIサービス
class ShadowingApi {
  ShadowingApi(this._client);

  final ApiClient _client;

  /// シナリオのシャドーイング文一覧を取得
  Future<ScenarioShadowingResponse> getScenarioShadowing({
    required int scenarioId,
  }) async {
    final Response<dynamic> res = await _client.getJson(
      '/shadowing/scenarios/$scenarioId',
    );
    return ScenarioShadowingResponse.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// シャドーイング練習結果を記録
  Future<ShadowingAttemptResponse> recordAttempt({
    required int sentenceId,
    required int score,
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/shadowing/$sentenceId/attempt',
      data: {'score': score},
    );
    return ShadowingAttemptResponse.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// シャドーイング全体進捗を取得（ホーム画面用）
  Future<ShadowingProgressResponse> getProgress() async {
    final Response<dynamic> res = await _client.getJson(
      '/shadowing/progress',
    );
    return ShadowingProgressResponse.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// 全シナリオの進捗一覧を取得
  Future<List<ScenarioProgressSummary>> getAllScenariosProgress({
    String? category,
  }) async {
    final Map<String, dynamic> queryParams = {};
    if (category != null) {
      queryParams['category'] = category;
    }
    final Response<dynamic> res = await _client.getJson(
      '/shadowing/scenarios',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );
    return (res.data as List)
        .map((e) => ScenarioProgressSummary.fromJson(Map<String, dynamic>.from(e)))
        .toList();
  }
}
