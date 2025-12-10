class AppConfig {
  AppConfig._();

  /// Base URL for the FastAPI backend.
  ///
  /// In development you will typically point this to your Mac's local IP
  /// including the API prefix, e.g. http://192.168.1.10:8000/api/v1
  // static const String apiBaseUrl = String.fromEnvironment(
  //   'API_BASE_URL',
  //   defaultValue: 'http://localhost:8000/api/v1',

  // );

  // for development ios simulator
  static const String apiBaseUrl = 'http://192.168.11.7:8000/api/v1';

  /// API timeout in seconds.
  /// バックエンド側のOpenAI呼び出しタイムアウト（60秒）に合わせて少し長めに確保する。
  static const int apiTimeoutSeconds = 60;
}


