import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'auth_providers.dart';

class CallbackScreen extends ConsumerStatefulWidget {
  const CallbackScreen({
    super.key,
    required this.code,
  });

  final String? code;

  @override
  ConsumerState<CallbackScreen> createState() => _CallbackScreenState();
}

class _CallbackScreenState extends ConsumerState<CallbackScreen> {
  Object? _error;

  @override
  void initState() {
    super.initState();
    // Avoid modifying providers while the widget tree is building.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _run();
    });
  }

  Future<void> _run() async {
    final code = widget.code?.trim() ?? '';
    if (code.isEmpty) {
      setState(() {
        _error = 'Missing authorization code.';
      });
      return;
    }

    try {
      final newState =
          await ref.read(authStateProvider.notifier).loginWithAuthCode(code);

      if (!mounted) return;
      if (newState.placementCompletedAt == null) {
        context.go('/placement');
      } else {
        context.go('/');
      }
    } catch (e) {
      // Extra logging to surface FastAPI `detail` on 400s.
      if (e is DioException) {
        // ignore: avoid_print
        print(
          'Auth callback failed: status=${e.response?.statusCode} data=${e.response?.data}',
        );
      }
      if (!mounted) return;
      setState(() {
        _error = e;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final error = _error;
    return Scaffold(
      appBar: AppBar(title: const Text('Signing in...')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: error == null
              ? const Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 12),
                    Text('Completing sign-in…'),
                  ],
                )
              : Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('Login failed'),
                    const SizedBox(height: 8),
                    Text(
                      error.toString(),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => context.go('/login'),
                      child: const Text('Back to login'),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}


