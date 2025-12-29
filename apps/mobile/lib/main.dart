import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'config/app_config.dart';
import 'config/app_theme.dart';
import 'features/auth/deep_link_listener.dart';
import 'router/app_router.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppConfig.load();
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
      builder: (context, child) => DeepLinkListener(
        child: child ?? const SizedBox.shrink(),
      ),
    );
  }
}


