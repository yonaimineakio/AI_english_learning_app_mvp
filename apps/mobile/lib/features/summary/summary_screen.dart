import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../shared/models/session_models.dart';

class SummaryScreen extends StatelessWidget {
  const SummaryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = GoRouterState.of(context);
    final end = state.extra as SessionEndResponseModel?;

    return Scaffold(
      appBar: AppBar(
        title: const Text('セッションサマリ'),
      ),
      body: end == null
          ? const Center(child: Text('No session data'))
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    end.scenarioName ?? 'セッション ${end.sessionId}',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'ラウンド数: ${end.completedRounds}\n'
                    'レベル: ${end.difficulty} / モード: ${end.mode}',
                  ),
                  if (end.goalsTotal != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      'ゴール達成: ${end.goalsAchieved}/${end.goalsTotal}',
                    ),
                  ],
                  const SizedBox(height: 16),
                  const Text(
                    '改善トップ3フレーズ',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: ListView.builder(
                      itemCount: end.topPhrases.length,
                      itemBuilder: (context, index) {
                        final p = end.topPhrases[index];
                        return ListTile(
                          leading: Text('${index + 1}.'),
                          title: Text(p.phrase),
                          subtitle: Text(p.explanation),
                        );
                      },
                    ),
                  ),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            context.go('/review');
                          },
                          child: const Text('復習へ進む'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            context.go('/');
                          },
                          child: const Text('新規セッションを開始'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
    );
  }
}



