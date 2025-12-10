import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/models/scenario_static.dart';
import '../auth/auth_providers.dart';
import '../session/session_controller.dart';

class ScenarioSelectionScreen extends ConsumerWidget {
  const ScenarioSelectionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('シナリオ選択'),
      ),
      body: auth.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (authState) {
          final level = authState.placementCompletedAt == null
              ? null
              : 'intermediate'; // TODO: 実際のplacement_levelをUserModelから保持

          final scenarios = kScenarioList.where((s) {
            if (level == null) return true;
            if (level == 'beginner') {
              return s.difficulty == 'beginner';
            }
            if (level == 'intermediate') {
              return s.difficulty == 'beginner' ||
                  s.difficulty == 'intermediate';
            }
            return true;
          }).toList();

          return ListView.builder(
            padding: const EdgeInsets.symmetric(vertical: 16),
            itemCount: scenarios.length,
            itemBuilder: (context, index) {
              final s = scenarios[index];
              return Card(
                child: InkWell(
                  borderRadius: BorderRadius.circular(16),
                  onTap: () async {
                  // シナリオIDから新しいセッションを開始してから会話画面へ遷移
                  // 難易度はシナリオ定義の値をそのまま使用、モードはとりあえずstandard固定
                  // TODO: ユーザー設定でmodeを選べるように拡張
                    final sessionId = await ref
                        .read(sessionControllerProvider.notifier)
                        .startNewSession(
                          scenarioId: s.id,
                          difficulty: s.difficulty,
                          mode: 'standard',
                        );
                    if (context.mounted) {
                      context.go('/sessions/$sessionId');
                    }
                  },
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              s.name,
                              style: Theme.of(context)
                                  .textTheme
                                  .titleMedium
                                  ?.copyWith(fontWeight: FontWeight.w600),
                            ),
                            Text(
                              '${s.estimatedMinutes}分',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(color: Colors.grey[600]),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          s.description,
                          style: Theme.of(context)
                              .textTheme
                              .bodyMedium
                              ?.copyWith(color: Colors.grey[800]),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Chip(
                              label: Text(
                                s.categoryLabel,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Chip(
                              label: Text('Lv: ${s.difficulty}'),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}



