import 'package:dio/dio.dart';

import '../models/session_models.dart';
import 'api_client.dart';

class SessionApi {
  SessionApi(this._client);

  final ApiClient _client;

  Future<SessionStartResponseModel> startSession({
    int? scenarioId,
    int? customScenarioId,
    required int roundTarget,
    required String difficulty,
    required String mode,
  }) async {
    final Map<String, dynamic> data = {
      'round_target': roundTarget,
      'difficulty': difficulty,
      'mode': mode,
    };
    if (scenarioId != null) {
      data['scenario_id'] = scenarioId;
    }
    if (customScenarioId != null) {
      data['custom_scenario_id'] = customScenarioId;
    }
    final Response<dynamic> res = await _client.postJson(
      '/sessions/start',
      data: data,
    );
    return SessionStartResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  Future<TurnResponseModel> sendTurn({
    required int sessionId,
    required String userInput,
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/sessions/$sessionId/turn',
      data: {
        'user_input': userInput,
      },
    );
    return TurnResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  Future<SessionStatusResponseModel> extendSession({
    required int sessionId,
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/sessions/$sessionId/extend',
    );
    return SessionStatusResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  Future<SessionEndResponseModel> endSession({
    required int sessionId,
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/sessions/$sessionId/end',
    );
    return SessionEndResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  Future<SessionStatusResponseModel> getStatus({
    required int sessionId,
  }) async {
    final Response<dynamic> res = await _client.getJson(
      '/sessions/$sessionId/status',
    );
    return SessionStatusResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }
}


