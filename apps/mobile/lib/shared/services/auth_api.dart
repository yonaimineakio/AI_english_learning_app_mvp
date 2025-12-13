import 'package:dio/dio.dart';

import '../models/user_model.dart';
import 'api_client.dart';

class AuthTokenResponse {
  const AuthTokenResponse({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  final String accessToken;
  final String tokenType;
  final int expiresIn;
  final Map<String, dynamic> user;

  factory AuthTokenResponse.fromJson(Map<String, dynamic> json) {
    return AuthTokenResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
      expiresIn: json['expires_in'] as int? ?? 0,
      user: Map<String, dynamic>.from(json['user'] as Map),
    );
  }
}

class AuthApi {
  AuthApi(this._client);

  final ApiClient _client;

  Future<UserModel> getMe() async {
    final Response<dynamic> res = await _client.getJson('/auth/me');
    return UserModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  Future<UserStatsModel> getUserStats() async {
    final Response<dynamic> res = await _client.getJson('/auth/me/stats');
    return UserStatsModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// Exchange authorization code for app JWT.
  ///
  /// In mock mode, `code` can be any string starting with `mock_auth_code_`.
  Future<AuthTokenResponse> exchangeCodeForToken(String code) async {
    final Response<dynamic> res = await _client.postJson(
      '/auth/token',
      data: {
        'code': code,
      },
    );
    return AuthTokenResponse.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }
}


