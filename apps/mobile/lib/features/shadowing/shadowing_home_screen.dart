import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/services/api_client.dart';
import '../auth/auth_providers.dart';
import '../home/streak_widget.dart';
import 'shadowing_api.dart';
import 'shadowing_models.dart';

/// シャドーイング進捗プロバイダー
final shadowingProgressProvider = FutureProvider<ShadowingProgressResponse>((ref) async {
  final auth = ref.watch(authStateProvider);
  if (auth.valueOrNull?.isLoggedIn != true) {
    throw StateError('Not logged in');
  }
  final api = ShadowingApi(ApiClient());
  return api.getProgress();
});

/// 全シナリオ進捗プロバイダー
final shadowingScenariosProvider = FutureProvider.family<List<ScenarioProgressSummary>, String?>((ref, category) async {
  final auth = ref.watch(authStateProvider);
  if (auth.valueOrNull?.isLoggedIn != true) {
    throw StateError('Not logged in');
  }
  final api = ShadowingApi(ApiClient());
  return api.getAllScenariosProgress(category: category);
});

/// シャドーイングホーム画面
class ShadowingHomeScreen extends ConsumerStatefulWidget {
  const ShadowingHomeScreen({super.key});

  @override
  ConsumerState<ShadowingHomeScreen> createState() => _ShadowingHomeScreenState();
}

class _ShadowingHomeScreenState extends ConsumerState<ShadowingHomeScreen> {
  String? _selectedCategory;

  @override
  Widget build(BuildContext context) {
    final progressAsync = ref.watch(shadowingProgressProvider);
    final scenariosAsync = ref.watch(shadowingScenariosProvider(_selectedCategory));

    return Scaffold(
      appBar: AppBar(
        title: const Text('シャドーイング'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(shadowingProgressProvider);
              ref.invalidate(shadowingScenariosProvider(_selectedCategory));
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(shadowingProgressProvider);
          ref.invalidate(shadowingScenariosProvider(_selectedCategory));
        },
        child: ListView(
          padding: const EdgeInsets.only(bottom: 24),
          children: [
            const StreakWidget(),

            // 進捗サマリーカード
            progressAsync.when(
              loading: () => const Padding(
                padding: EdgeInsets.all(16),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (e, _) => Padding(
                padding: const EdgeInsets.all(16),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text('エラー: $e', style: const TextStyle(color: Colors.red)),
                  ),
                ),
              ),
              data: (progress) => _buildProgressCard(progress),
            ),

            // カテゴリフィルター
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  const Text(
                    'シナリオを選択',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  DropdownButton<String?>(
                    value: _selectedCategory,
                    hint: const Text('全て'),
                    items: const [
                      DropdownMenuItem(value: null, child: Text('全て')),
                      DropdownMenuItem(value: 'travel', child: Text('旅行')),
                      DropdownMenuItem(value: 'daily', child: Text('日常会話')),
                      DropdownMenuItem(value: 'business', child: Text('ビジネス')),
                    ],
                    onChanged: (value) {
                      setState(() => _selectedCategory = value);
                    },
                  ),
                ],
              ),
            ),

            // シナリオ一覧
            scenariosAsync.when(
              loading: () => const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (e, _) => Padding(
                padding: const EdgeInsets.all(16),
                child: Text('エラー: $e', style: const TextStyle(color: Colors.red)),
              ),
              data: (scenarios) => _buildScenarioList(scenarios),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressCard(ShadowingProgressResponse progress) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.record_voice_over, color: Colors.blue, size: 28),
                const SizedBox(width: 8),
                const Text(
                  '今日のシャドーイング',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // 今日の練習回数
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    icon: Icons.today,
                    label: '今日の練習',
                    value: '${progress.todayPracticeCount}文',
                    color: Colors.orange,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    icon: Icons.check_circle,
                    label: '完了した文',
                    value: '${progress.completedSentences}/${progress.totalSentences}',
                    color: Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // 全体進捗バー
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress.overallProgressPercent / 100,
                minHeight: 10,
                backgroundColor: Colors.grey.shade200,
                valueColor: const AlwaysStoppedAnimation(Colors.blue),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '全体進捗: ${progress.overallProgressPercent.toStringAsFixed(1)}%',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 12,
              ),
            ),
            // 最近練習したシナリオ
            if (progress.recentScenarios.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                '最近練習したシナリオ',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              ...progress.recentScenarios.take(3).map((scenario) => InkWell(
                onTap: () => _navigateToScenario(scenario.scenarioId, scenario.scenarioName),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          scenario.scenarioName,
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                      Text(
                        '${scenario.progressPercent}%',
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Icon(Icons.chevron_right, size: 20),
                    ],
                  ),
                ),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }

  Widget _buildScenarioList(List<ScenarioProgressSummary> scenarios) {
    if (scenarios.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(32),
        child: Center(
          child: Text('シナリオがありません'),
        ),
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: scenarios.length,
      itemBuilder: (context, index) {
        final scenario = scenarios[index];
        return _buildScenarioCard(scenario);
      },
    );
  }

  Widget _buildScenarioCard(ScenarioProgressSummary scenario) {
    final hasProgress = scenario.completedSentences > 0;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _navigateToScenario(scenario.scenarioId, scenario.scenarioName),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      scenario.scenarioName,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  if (hasProgress)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: scenario.progressPercent >= 100
                            ? Colors.green.shade100
                            : Colors.blue.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '${scenario.progressPercent}%',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: scenario.progressPercent >= 100
                              ? Colors.green.shade700
                              : Colors.blue.shade700,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  _buildChip(scenario.categoryLabel, Colors.purple),
                  const SizedBox(width: 8),
                  _buildChip(scenario.difficultyLabel, _getDifficultyColor(scenario.difficulty)),
                  const Spacer(),
                  Text(
                    '${scenario.totalSentences}文',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              if (hasProgress) ...[
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: scenario.progressPercent / 100,
                    minHeight: 6,
                    backgroundColor: Colors.grey.shade200,
                    valueColor: AlwaysStoppedAnimation(
                      scenario.progressPercent >= 100 ? Colors.green : Colors.blue,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildChip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          color: color,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Color _getDifficultyColor(String difficulty) {
    switch (difficulty) {
      case 'beginner':
        return Colors.green;
      case 'intermediate':
        return Colors.orange;
      case 'advanced':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  void _navigateToScenario(int scenarioId, String scenarioName) {
    context.push('/shadowing/$scenarioId', extra: scenarioName);
  }
}
