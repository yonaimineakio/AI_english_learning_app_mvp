import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/models/user_model.dart';
import '../../shared/models/placement_models.dart';
import '../../shared/services/api_client.dart';
import '../../shared/services/auth_api.dart';
import '../../shared/services/token_storage.dart';
import '../../shared/services/revenuecat/revenuecat_client.dart';
import '../paywall/pro_status_provider.dart';

class AuthState {
  const AuthState({
    required this.isLoggedIn,
    this.userId,
    this.token,
    this.userName,
    this.email,
    this.placementCompletedAt,
  });

  final bool isLoggedIn;
  final String? userId; // UUID
  final String? token;
  final String? userName;
  final String? email;
  final DateTime? placementCompletedAt;

  AuthState copyWith({
    bool? isLoggedIn,
    String? userId,
    String? token,
    String? userName,
    String? email,
    DateTime? placementCompletedAt,
  }) {
    return AuthState(
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      userId: userId ?? this.userId,
      token: token ?? this.token,
      userName: userName ?? this.userName,
      email: email ?? this.email,
      placementCompletedAt: placementCompletedAt ?? this.placementCompletedAt,
    );
  }
}

class AuthNotifier extends AsyncNotifier<AuthState> {
  final _controller = StreamController<AuthState>.broadcast();

  Stream<AuthState> get stream => _controller.stream;

  late final AuthApi _authApi;
  late final TokenStorage _tokenStorage;

  @override
  Future<AuthState> build() async {
    _authApi = AuthApi(ApiClient());
    _tokenStorage = TokenStorage();
    ref.onDispose(_controller.close);

    // Try to restore session from stored tokens
    try {
      final tokens = await _tokenStorage.loadTokens();
      if (tokens.accessToken != null) {
        final restoredState = await _tryRestoreSession(
          tokens.accessToken!,
          tokens.refreshToken,
        );
        if (restoredState != null) {
          _controller.add(restoredState);
          return restoredState;
        }
      }
    } catch (e) {
      // If restoration fails, clear invalid tokens and proceed to login
      await _tokenStorage.clearTokens();
    }

    const initial = AuthState(isLoggedIn: false);
    _controller.add(initial);
    return initial;
  }

  /// Try to restore session using stored tokens.
  /// Returns AuthState if successful, null if failed.
  Future<AuthState?> _tryRestoreSession(
    String accessToken,
    String? refreshToken,
  ) async {
    ApiClient().updateToken(accessToken);

    try {
      // Try to get user info with current access token
      final UserModel me = await _authApi.getMe();
      
      // Login successful with existing token
      await const RevenueCatClient().loginUser(me.id);
      await ref.read(proStatusProvider.notifier).refresh();

      return AuthState(
        isLoggedIn: true,
        userId: me.id,
        token: accessToken,
        userName: me.name,
        email: me.email,
        placementCompletedAt: me.placementCompletedAt,
      );
    } on DioException catch (e) {
      // If 401, try to refresh the token
      if (e.response?.statusCode == 401 && refreshToken != null) {
        try {
          final refreshRes = await _authApi.refreshToken(refreshToken);
          final newAccessToken = refreshRes.accessToken;
          
          // Save new access token
          await _tokenStorage.saveTokens(
            accessToken: newAccessToken,
            refreshToken: refreshToken,
          );
          ApiClient().updateToken(newAccessToken);

          // Retry getting user info
          final UserModel me = await _authApi.getMe();
          
          await const RevenueCatClient().loginUser(me.id);
          await ref.read(proStatusProvider.notifier).refresh();

          return AuthState(
            isLoggedIn: true,
            userId: me.id,
            token: newAccessToken,
            userName: me.name,
            email: me.email,
            placementCompletedAt: me.placementCompletedAt,
          );
        } catch (_) {
          // Refresh failed, clear tokens
          await _tokenStorage.clearTokens();
          ApiClient().updateToken(null);
          return null;
        }
      }
      // Other errors or no refresh token
      await _tokenStorage.clearTokens();
      ApiClient().updateToken(null);
      return null;
    }
  }

  Future<AuthState> loginWithMock() async {
    // 開発用: モックコードで /auth/token を叩いてJWTを取得
    state = const AsyncLoading();
    try {
      const mockCode = 'mock_auth_code_flutter_app';
      final tokenRes = await _authApi.exchangeCodeForToken(mockCode);

      final accessToken = tokenRes.accessToken;
      final refreshToken = tokenRes.refreshToken;

      // Save tokens to secure storage
      await _tokenStorage.saveTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
      );
      ApiClient().updateToken(accessToken);

      // /auth/me でユーザー情報を取得
      final UserModel me = await _authApi.getMe();

      // RevenueCat にユーザーID(UUID)を紐付ける
      await const RevenueCatClient().loginUser(me.id);

      // RevenueCatログイン後にPro状態を更新
      await ref.read(proStatusProvider.notifier).refresh();

      final newState = AuthState(
        isLoggedIn: true,
        userId: me.id,
        token: accessToken,
        userName: me.name,
        email: me.email,
        placementCompletedAt: me.placementCompletedAt,
      );
      state = AsyncData(newState);
      _controller.add(newState);
      return newState;
    } catch (e, st) {
      state = AsyncError(e, st);
      rethrow;
    }
  }

  Future<AuthState> loginWithAuthCode(String code) async {
    state = const AsyncLoading();
    try {
      final tokenRes = await _authApi.exchangeCodeForToken(code);

      final accessToken = tokenRes.accessToken;
      final refreshToken = tokenRes.refreshToken;

      // Save tokens to secure storage
      await _tokenStorage.saveTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
      );
      ApiClient().updateToken(accessToken);

      // /auth/me でユーザー情報を取得
      final UserModel me = await _authApi.getMe();

      // RevenueCat にユーザーID(UUID)を紐付ける
      await const RevenueCatClient().loginUser(me.id);

      // RevenueCatログイン後にPro状態を更新
      await ref.read(proStatusProvider.notifier).refresh();

      final newState = AuthState(
        isLoggedIn: true,
        userId: me.id,
        token: accessToken,
        userName: me.name,
        email: me.email,
        placementCompletedAt: me.placementCompletedAt,
      );
      state = AsyncData(newState);
      _controller.add(newState);
      return newState;
    } catch (e, st) {
      // Surface FastAPI error detail for 400s.
      if (e is DioException) {
        // ignore: avoid_print
        print(
          'loginWithAuthCode failed: status=${e.response?.statusCode} data=${e.response?.data}',
        );
      }
      state = AsyncError(e, st);
      rethrow;
    }
  }

  void applyPlacementResult(PlacementSubmitResponseModel result) {
    final current = state.valueOrNull;
    if (current == null) return;
    final updated = current.copyWith(
      placementCompletedAt: result.placementCompletedAt,
    );
    state = AsyncData(updated);
    _controller.add(updated);
  }

  Future<void> logout() async {
    // Clear tokens from secure storage
    await _tokenStorage.clearTokens();
    ApiClient().updateToken(null);
    // RevenueCat から匿名ユーザーに戻す
    await const RevenueCatClient().logoutUser();
    // Pro状態のキャッシュをクリア
    ref.invalidate(proStatusProvider);
    const newState = AuthState(isLoggedIn: false);
    state = const AsyncData(newState);
    _controller.add(newState);
  }

  Future<void> updateProfileName(String name) async {
    final current = state.valueOrNull;
    if (current == null || !current.isLoggedIn) {
      throw StateError('Not logged in');
    }
    state = const AsyncLoading();
    try {
      final me = await _authApi.updateMe(name: name);
      final updated = current.copyWith(
        userName: me.name,
        email: me.email,
        placementCompletedAt: me.placementCompletedAt,
      );
      state = AsyncData(updated);
      _controller.add(updated);
    } catch (e, st) {
      state = AsyncError(e, st);
      rethrow;
    }
  }
}

final authStateProvider =
    AsyncNotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);


