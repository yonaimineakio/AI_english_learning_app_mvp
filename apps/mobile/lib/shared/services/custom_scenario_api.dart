import 'package:dio/dio.dart';

import 'api_client.dart';
import '../models/custom_scenario_models.dart';

/// カスタムシナリオAPIサービス
class CustomScenarioApi {
  final ApiClient _client;

  CustomScenarioApi(this._client);

  /// カスタムシナリオ一覧を取得
  Future<CustomScenarioListResponse> fetchCustomScenarios() async {
    final Response<dynamic> res = await _client.getJson('/custom-scenarios');
    return CustomScenarioListResponse.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// カスタムシナリオを作成
  Future<CustomScenario> createCustomScenario(CustomScenarioCreate data) async {
    final Response<dynamic> res = await _client.postJson(
      '/custom-scenarios',
      data: data.toJson(),
    );
    return CustomScenario.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// カスタムシナリオを取得
  Future<CustomScenario> fetchCustomScenario(int id) async {
    final Response<dynamic> res = await _client.getJson('/custom-scenarios/$id');
    return CustomScenario.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// カスタムシナリオを削除（論理削除）
  Future<void> deleteCustomScenario(int id) async {
    await _client.deleteJson('/custom-scenarios/$id');
  }

  /// 本日の作成制限を取得
  Future<CustomScenarioLimitResponse> fetchLimit() async {
    final Response<dynamic> res = await _client.getJson('/custom-scenarios/limit');
    return CustomScenarioLimitResponse.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }
}
