import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/models/user_model.dart';
import '../../shared/models/placement_models.dart';
import '../../shared/services/api_client.dart';
import '../../shared/services/auth_api.dart';
import '../../shared/services/revenuecat/revenuecat_client.dart';

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
  final int? userId;
  final String? token;
  final String? userName;
  final String? email;
  final DateTime? placementCompletedAt;

  AuthState copyWith({
    bool? isLoggedIn,
    int? userId,
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

  @override
  Future<AuthState> build() async {
    _authApi = AuthApi(ApiClient());
    ref.onDispose(_controller.close);
    // 初期状態では未ログイン。将来的にSecureStorageからトークン復元する余地を残す。
    const initial = AuthState(isLoggedIn: false);
    _controller.add(initial);
    return initial;
  }

  Future<AuthState> loginWithMock() async {
    // 開発用: モックコードで /auth/token を叩いてJWTを取得
    state = const AsyncLoading();
    try {
      const mockCode = 'mock_auth_code_flutter_app';
      final tokenRes = await _authApi.exchangeCodeForToken(mockCode);

      final accessToken = tokenRes.accessToken;
      ApiClient().updateToken(accessToken);

      // /auth/me でユーザー情報を取得
      final UserModel me = await _authApi.getMe();

      // RevenueCat にユーザーIDを紐付ける
      await const RevenueCatClient().loginUser(me.id.toString());

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
      ApiClient().updateToken(accessToken);

      // /auth/me でユーザー情報を取得
      final UserModel me = await _authApi.getMe();

      // RevenueCat にユーザーIDを紐付ける
      await const RevenueCatClient().loginUser(me.id.toString());

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
    ApiClient().updateToken(null);
    // RevenueCat から匿名ユーザーに戻す
    await const RevenueCatClient().logoutUser();
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


