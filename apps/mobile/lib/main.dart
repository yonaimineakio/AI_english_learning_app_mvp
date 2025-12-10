import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'config/app_theme.dart';
import 'router/app_router.dart';

void main() {
  runApp(const ProviderScope(child: AiEnglishLearningApp()));
}

class AiEnglishLearningApp extends ConsumerWidget {
  const AiEnglishLearningApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'AI English Learning',
      theme: AppTheme.light(),
      routerConfig: router,
    );
  }
}


