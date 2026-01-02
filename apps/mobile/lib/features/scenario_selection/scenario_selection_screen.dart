import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/models/scenario_static.dart';
import '../auth/auth_providers.dart';
import '../paywall/pro_status_provider.dart';
import '../session/session_controller.dart';
import '../home/streak_widget.dart';

class ScenarioSelectionScreen extends ConsumerWidget {
  const ScenarioSelectionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authStateProvider);
    final pro = ref.watch(proStatusProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('シナリオ選択'),
      ),
      body: auth.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (authState) {
          final isPro = pro.valueOrNull ?? false;

          // Free: 固定3シナリオのみ（placementなし）
          // Pro : placement結果に応じて難易度フィルタ（現状は仮実装）
          final level = (!isPro || authState.placementCompletedAt == null)
              ? null
              : 'intermediate'; // TODO: 実際のplacement_levelをUserModelから保持

          final scenarios = kScenarioList.where((s) {
            if (!isPro) {
              return kFreeScenarioIds.contains(s.id);
            }
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

          return Column(
            children: [
              const StreakWidget(),
              if (!isPro)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                  child: Card(
                    color: Colors.blue.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          Icon(Icons.lock_outline, color: Colors.blue.shade600),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Freeプランでは利用できるシナリオは3つのみです。Proで全シナリオ・復習機能が解放されます。',
                              style: TextStyle(color: Colors.blue.shade800),
                            ),
                          ),
                          TextButton(
                            onPressed: () => context.push('/paywall'),
                            child: const Text('Proへ'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              Expanded(
                child: ListView.builder(
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
              ),
            ),
          ],
        );
        },
      ),
    );
  }
}



