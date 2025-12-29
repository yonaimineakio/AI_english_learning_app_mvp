import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/login_screen.dart';
import '../features/auth/callback_screen.dart';
import '../features/auth/auth_providers.dart';
import '../features/placement/placement_screen.dart';
import '../features/main/main_shell_screen.dart';
import '../features/session/session_screen.dart';
import '../features/summary/summary_screen.dart';
import '../features/review/review_screen.dart';
import '../features/rankings/rankings_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/callback',
        builder: (context, state) {
          final code = state.uri.queryParameters['code'];
          return CallbackScreen(code: code);
        },
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const MainShellScreen(),
      ),
      GoRoute(
        path: '/placement',
        builder: (context, state) => const PlacementScreen(),
      ),
      GoRoute(
        path: '/sessions/:sessionId',
        builder: (context, state) {
          final id = state.pathParameters['sessionId']!;
          return SessionScreen(sessionId: id);
        },
      ),
      GoRoute(
        path: '/summary',
        builder: (context, state) => const SummaryScreen(),
      ),
      GoRoute(
        path: '/review',
        builder: (context, state) => const ReviewScreen(),
      ),
      GoRoute(
        path: '/rankings',
        builder: (context, state) => const RankingsScreen(),
      ),
    ],
    redirect: (context, state) {
      final authState = auth.valueOrNull;
      final isLoggedIn = authState?.isLoggedIn ?? false;
      final hasPlacement =
          authState?.placementCompletedAt != null;

      final loggingIn = state.matchedLocation == '/login';
      final inCallback = state.matchedLocation == '/callback';
      final goingPlacement = state.matchedLocation == '/placement';

      // 未ログイン → /login へ
      if (!isLoggedIn && !loggingIn && !inCallback) {
        return '/login';
      }

      // ログイン済みかつ placement 未完了 → /placement へ
      if (isLoggedIn && !hasPlacement && !goingPlacement) {
        return '/placement';
      }

      // ログイン済みかつ placement 済みで /login or /placement に来た場合 → ホームへ
      if (isLoggedIn && hasPlacement && (loggingIn || goingPlacement)) {
        return '/';
      }

      return null;
    },
  );
});


