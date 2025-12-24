import 'dart:convert';

import 'package:flutter/services.dart';

class AppConfig {
  AppConfig._();

  /// Base URL for the FastAPI backend.
  ///
  /// In development you will typically point this to your Mac's local IP
  /// including the API prefix, e.g. http://192.168.1.10:8000/api/v1
  ///
  /// - iOS Simulator: `http://localhost:8000/api/v1` (FastAPIをMacで起動している場合)
  /// - iPhone実機: `http://<MacのLAN IP>:8000/api/v1` (例: http://172.20.10.10:8000/api/v1)
  /// `dart_defines.json` の `API_BASE_URL` を起動時に読み込みます。
  ///
  /// 例: `apps/mobile/dart_defines.json`
  /// {
  ///   "API_BASE_URL": "http://172.20.10.10:8000/api/v1"
  /// }
  static late final String apiBaseUrl;

  static Future<void> load() async {
    // 1) JSON (assets) → 2) dart-define → 3) fallback
    String? fromJson;
    try {
      final raw = await rootBundle.loadString('dart_defines.json');
      final decoded = jsonDecode(raw);
      if (decoded is Map && decoded['API_BASE_URL'] is String) {
        fromJson = (decoded['API_BASE_URL'] as String).trim();
      }
    } catch (_) {
      // ignore: fallback below
    }

    const fromDefine = String.fromEnvironment('API_BASE_URL', defaultValue: '');

    apiBaseUrl = (fromJson != null && fromJson.isNotEmpty)
        ? fromJson
        : (fromDefine.isNotEmpty ? fromDefine : 'http://localhost:8000/api/v1');
  }

  /// API timeout in seconds.
  /// バックエンド側のOpenAI呼び出しタイムアウト（60秒）に合わせて少し長めに確保する。
  static const int apiTimeoutSeconds = 60;
}


