import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';

import '../../config/app_config.dart';

class ApiClient {
  ApiClient._internal()
      : _dio = Dio(
          BaseOptions(
            baseUrl: AppConfig.apiBaseUrl,
            connectTimeout: const Duration(seconds: AppConfig.apiTimeoutSeconds),
            receiveTimeout: const Duration(seconds: AppConfig.apiTimeoutSeconds),
            headers: const {
              HttpHeaders.contentTypeHeader: 'application/json',
            },
          ),
        );

  static final ApiClient _instance = ApiClient._internal();

  factory ApiClient() => _instance;

  final Dio _dio;

  String? _accessToken;

  void updateToken(String? token) {
    _accessToken = token;
  }

  Options _withAuth(Options? options) {
    final headers = Map<String, dynamic>.from(options?.headers ?? {});
    if (_accessToken != null) {
      headers[HttpHeaders.authorizationHeader] = 'Bearer $_accessToken';
    }
    return (options ?? Options()).copyWith(headers: headers);
  }

  Future<Response<T>> getJson<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) {
    return _dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: _withAuth(options),
    );
  }

  Object? _encodeBody(Object? data) {
    if (data == null) return null;
    if (data is FormData) return data;
    if (data is String) return data;
    return jsonEncode(data);
  }

  Future<Response<T>> postJson<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) {
    return _dio.post<T>(
      path,
      data: _encodeBody(data),
      queryParameters: queryParameters,
      options: _withAuth(options),
    );
  }

  Future<Response<T>> deleteJson<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) {
    return _dio.delete<T>(
      path,
      queryParameters: queryParameters,
      options: _withAuth(options),
    );
  }
}


