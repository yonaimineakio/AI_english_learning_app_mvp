import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import 'auth_providers.dart';
import '../../config/app_config.dart';

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
                final url = Uri.parse('${AppConfig.apiBaseUrl}/auth/login');
                final ok = await launchUrl(
                  url,
                  mode: LaunchMode.externalApplication,
                );
                if (!ok && context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Failed to open: $url')),
                  );
                }
              },
              child: const Text('Login with Google'),
            );
          },
          loading: () => const CircularProgressIndicator(),
          error: (e, st) => Text('Error: $e'),
        ),
      ),
    );
  }
}


