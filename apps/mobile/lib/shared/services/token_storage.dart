import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Secure storage service for authentication tokens.
class TokenStorage {
  TokenStorage() : _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  final FlutterSecureStorage _storage;

  /// Save tokens to secure storage.
  Future<void> saveTokens({
    required String accessToken,
    String? refreshToken,
  }) async {
    await _storage.write(key: _accessTokenKey, value: accessToken);
    if (refreshToken != null) {
      await _storage.write(key: _refreshTokenKey, value: refreshToken);
    }
  }

  /// Load tokens from secure storage.
  /// Returns a record of (accessToken, refreshToken).
  Future<({String? accessToken, String? refreshToken})> loadTokens() async {
    final accessToken = await _storage.read(key: _accessTokenKey);
    final refreshToken = await _storage.read(key: _refreshTokenKey);
    return (accessToken: accessToken, refreshToken: refreshToken);
  }

  /// Clear all tokens from secure storage.
  Future<void> clearTokens() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }
}
