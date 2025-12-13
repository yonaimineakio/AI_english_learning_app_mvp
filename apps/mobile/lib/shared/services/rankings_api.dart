import 'package:dio/dio.dart';

import '../models/points_models.dart';
import 'api_client.dart';

class RankingsApi {
  RankingsApi(this._client);

  final ApiClient _client;

  Future<UserPointsModel> getUserPoints() async {
    final Response<dynamic> res = await _client.getJson('/users/me/points');
    return UserPointsModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  Future<RankingsModel> getRankings({
    int limit = 20,
    String period = 'all_time',
  }) async {
    final Response<dynamic> res = await _client.getJson(
      '/rankings',
      queryParameters: {
        'limit': limit,
        'period': period,
      },
    );
    return RankingsModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  Future<MyRankingModel> getMyRanking() async {
    final Response<dynamic> res = await _client.getJson('/rankings/me');
    return MyRankingModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }
}

