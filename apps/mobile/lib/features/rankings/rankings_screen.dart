import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/models/points_models.dart';
import '../../shared/services/rankings_api.dart';
import '../../shared/services/api_client.dart';
import '../auth/auth_providers.dart';

final rankingsApiProvider = Provider<RankingsApi>((ref) {
  final apiClient = ApiClient();
  return RankingsApi(apiClient);
});

final userPointsProvider = FutureProvider<UserPointsModel>((ref) async {
  // 認証状態を監視してログアウト時に自動的にリフレッシュ
  final auth = ref.watch(authStateProvider);
  if (auth.valueOrNull?.isLoggedIn != true) {
    throw StateError('Not logged in');
  }
  final api = ref.watch(rankingsApiProvider);
  return api.getUserPoints();
});

final rankingsProvider = FutureProvider.family<RankingsModel, String>((ref, period) async {
  // 認証状態を監視してログアウト時に自動的にリフレッシュ
  final auth = ref.watch(authStateProvider);
  if (auth.valueOrNull?.isLoggedIn != true) {
    throw StateError('Not logged in');
  }
  final api = ref.watch(rankingsApiProvider);
  return api.getRankings(limit: 20, period: period);
});

final myRankingProvider = FutureProvider<MyRankingModel>((ref) async {
  // 認証状態を監視してログアウト時に自動的にリフレッシュ
  final auth = ref.watch(authStateProvider);
  if (auth.valueOrNull?.isLoggedIn != true) {
    throw StateError('Not logged in');
  }
  final api = ref.watch(rankingsApiProvider);
  return api.getMyRanking();
});

class RankingsScreen extends ConsumerWidget {
  const RankingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedPeriod = ref.watch(_selectedPeriodProvider);
    final rankingsAsync = ref.watch(rankingsProvider(selectedPeriod));
    final myRankingAsync = ref.watch(myRankingProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('ランキング'),
      ),
      body: Column(
        children: [
          // 自分のランキング表示
          myRankingAsync.when(
            loading: () => const Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
            error: (error, stack) => Padding(
              padding: const EdgeInsets.all(16),
              child: Text('エラー: $error'),
            ),
            data: (myRanking) => Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Row(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'あなたの順位',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${myRanking.rank}位',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${myRanking.totalPoints}ポイント',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey[700],
                        ),
                      ),
                      if (myRanking.pointsToNextRank != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          '次まであと${myRanking.pointsToNextRank}ポイント',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ],
                  ),
                  const Spacer(),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '総ユーザー数',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                      Text(
                        '${myRanking.totalUsers}人',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // 期間選択タブ
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _PeriodTab(
                  label: '全期間',
                  period: 'all_time',
                  selectedPeriod: selectedPeriod,
                  onTap: () => ref.read(_selectedPeriodProvider.notifier).state = 'all_time',
                ),
                const SizedBox(width: 8),
                _PeriodTab(
                  label: '週間',
                  period: 'weekly',
                  selectedPeriod: selectedPeriod,
                  onTap: () => ref.read(_selectedPeriodProvider.notifier).state = 'weekly',
                ),
                const SizedBox(width: 8),
                _PeriodTab(
                  label: '月間',
                  period: 'monthly',
                  selectedPeriod: selectedPeriod,
                  onTap: () => ref.read(_selectedPeriodProvider.notifier).state = 'monthly',
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ランキング一覧
          Expanded(
            child: rankingsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => Center(child: Text('エラー: $error')),
              data: (rankings) => rankings.rankings.isEmpty
                  ? const Center(child: Text('ランキングデータがありません'))
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: rankings.rankings.length,
                      itemBuilder: (context, index) {
                        final entry = rankings.rankings[index];
                        final isTopThree = entry.rank <= 3;

                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          color: isTopThree ? Colors.amber.shade50 : null,
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: isTopThree
                                  ? Colors.amber.shade300
                                  : Colors.grey.shade300,
                              child: Text(
                                '${entry.rank}',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: isTopThree ? Colors.amber.shade900 : Colors.grey.shade700,
                                ),
                              ),
                            ),
                            title: Text(
                              entry.userName,
                              style: const TextStyle(fontWeight: FontWeight.w600),
                            ),
                            subtitle: Row(
                              children: [
                                Text('${entry.totalPoints}ポイント'),
                                const SizedBox(width: 16),
                                if (entry.currentStreak > 0)
                                  Row(
                                    children: [
                                      const Icon(Icons.local_fire_department, size: 16, color: Colors.orange),
                                      const SizedBox(width: 4),
                                      Text('${entry.currentStreak}日'),
                                    ],
                                  ),
                              ],
                            ),
                            trailing: isTopThree
                                ? Icon(Icons.star, color: Colors.amber.shade700)
                                : null,
                          ),
                        );
                      },
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

final _selectedPeriodProvider = StateProvider<String>((ref) => 'all_time');

class _PeriodTab extends StatelessWidget {
  const _PeriodTab({
    required this.label,
    required this.period,
    required this.selectedPeriod,
    required this.onTap,
  });

  final String label;
  final String period;
  final String selectedPeriod;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isSelected = period == selectedPeriod;
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? Colors.blue.shade100 : Colors.grey.shade200,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected ? Colors.blue.shade900 : Colors.grey.shade700,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

