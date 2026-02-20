import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import 'package:sign_in_with_apple/sign_in_with_apple.dart';

import 'auth_providers.dart';
import '../../config/app_config.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  bool _isGoogleLoading = false;
  bool _isAppleLoading = false;

  bool get _isLoading => _isGoogleLoading || _isAppleLoading;

  Future<void> _loginWithGoogle() async {
    if (_isLoading) return;
    setState(() => _isGoogleLoading = true);

    try {
      final authUrl = '${AppConfig.apiBaseUrl}/auth/login';
      const callbackScheme = 'ai-english-learning';

      final resultUrl = await FlutterWebAuth2.authenticate(
        url: authUrl,
        callbackUrlScheme: callbackScheme,
      );

      final uri = Uri.parse(resultUrl);
      final code = uri.queryParameters['code'];
      if (code == null || code.isEmpty) {
        throw Exception('認証コードを取得できませんでした');
      }

      await ref.read(authStateProvider.notifier).loginWithAuthCode(code);
    } catch (e) {
      if (!mounted) return;
      final msg = e.toString().contains('CANCELED')
          ? null
          : 'ログインに失敗しました: $e';
      if (msg != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg)),
        );
      }
    } finally {
      if (mounted) setState(() => _isGoogleLoading = false);
    }
  }

  Future<void> _loginWithApple() async {
    if (_isLoading) return;
    setState(() => _isAppleLoading = true);

    try {
      final credential = await SignInWithApple.getAppleIDCredential(
        scopes: [
          AppleIDAuthorizationScopes.email,
          AppleIDAuthorizationScopes.fullName,
        ],
      );

      final identityToken = credential.identityToken;
      if (identityToken == null) {
        throw Exception('Apple identity token が取得できませんでした');
      }

      String? fullName;
      final given = credential.givenName ?? '';
      final family = credential.familyName ?? '';
      if (given.isNotEmpty || family.isNotEmpty) {
        fullName = [given, family]
            .where((s) => s.isNotEmpty)
            .join(' ');
      }

      await ref.read(authStateProvider.notifier).loginWithAppleToken(
            identityToken: identityToken,
            fullName: fullName,
          );
    } on SignInWithAppleAuthorizationException catch (e) {
      if (!mounted) return;
      if (e.code != AuthorizationErrorCode.canceled) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Appleサインインに失敗しました: ${e.message}')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('ログインに失敗しました: $e')),
      );
    } finally {
      if (mounted) setState(() => _isAppleLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authStateProvider);

    return Scaffold(
      body: SafeArea(
        child: auth.when(
          data: (state) {
            if (state.isLoggedIn) {
              return Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('ようこそ、${state.userName ?? 'ユーザー'}さん'),
                    const SizedBox(height: 16),
                    const Text('ログイン済みです。'),
                  ],
                ),
              );
            }
            return _buildLoginBody();
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, st) => _buildLoginBody(),
        ),
      ),
    );
  }

  Widget _buildLoginBody() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        children: [
          const Spacer(flex: 3),
          ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: Image.asset(
              'assets/icon/app_icon.png',
              width: 80,
              height: 80,
              fit: BoxFit.cover,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'YuruEigo',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0F172A),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'AIと楽しく英会話を練習しよう',
            style: TextStyle(
              fontSize: 15,
              color: Color(0xFF64748B),
            ),
          ),
          const Spacer(flex: 2),

          if (Platform.isIOS) ...[
            SizedBox(
              width: double.infinity,
              height: 52,
              child: _AppleSignInButton(
                onPressed: _isLoading ? null : _loginWithApple,
                isLoading: _isAppleLoading,
              ),
            ),
            const SizedBox(height: 12),
          ],

          SizedBox(
            width: double.infinity,
            height: 52,
            child: _GoogleSignInButton(
              onPressed: _isLoading ? null : _loginWithGoogle,
              isLoading: _isGoogleLoading,
            ),
          ),
          const Spacer(flex: 3),
          const Text(
            'ログインすることで利用規約とプライバシーポリシーに同意したものとみなされます。',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 11,
              color: Color(0xFF94A3B8),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}

class _AppleSignInButton extends StatelessWidget {
  const _AppleSignInButton({required this.onPressed, required this.isLoading});

  final VoidCallback? onPressed;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        elevation: 0,
      ),
      child: isLoading
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Colors.white,
              ),
            )
          : const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.apple, size: 22),
                SizedBox(width: 10),
                Text(
                  'Appleでサインイン',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ],
            ),
    );
  }
}

class _GoogleSignInButton extends StatelessWidget {
  const _GoogleSignInButton({required this.onPressed, required this.isLoading});

  final VoidCallback? onPressed;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        foregroundColor: const Color(0xFF0F172A),
        side: const BorderSide(color: Color(0xFFE2E8F0)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: isLoading
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'G',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF4285F4),
                  ),
                ),
                SizedBox(width: 10),
                Text(
                  'Googleでログイン',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ],
            ),
    );
  }
}
