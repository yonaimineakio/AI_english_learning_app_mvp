import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'auth_providers.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI English Learning - Login'),
      ),
      body: Center(
        child: auth.when(
          data: (state) {
            if (state.isLoggedIn) {
              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Welcome, ${state.userName ?? 'User'}'),
                  const SizedBox(height: 16),
                  const Text('You are logged in.'),
                ],
              );
            }
            return ElevatedButton(
              onPressed: () async {
                final notifier =
                    ref.read(authStateProvider.notifier);
                final newState = await notifier.loginWithMock();

                // placement_completed_at が無い場合はレベルテストへ、
                // ある場合はシナリオ選択へ遷移
                if (!context.mounted) return;
                if (newState.placementCompletedAt == null) {
                  context.go('/placement');
                } else {
                  context.go('/');
                }
              },
              child: const Text('Login as demo user'),
            );
          },
          loading: () => const CircularProgressIndicator(),
          error: (e, st) => Text('Error: $e'),
        ),
      ),
    );
  }
}


