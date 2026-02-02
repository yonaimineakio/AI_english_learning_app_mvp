import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/models/scenario_static.dart';
import '../../shared/models/custom_scenario_models.dart';
import '../../shared/services/api_client.dart';
import '../../shared/services/custom_scenario_api.dart';
import '../auth/auth_providers.dart';
import '../paywall/pro_status_provider.dart';
import '../session/session_controller.dart';
import '../home/streak_widget.dart';

// カスタムシナリオ一覧のプロバイダー
final customScenariosProvider = FutureProvider<CustomScenarioListResponse>((ref) async {
  final api = CustomScenarioApi(ApiClient());
  return api.fetchCustomScenarios();
});

// 作成制限のプロバイダー
final customScenarioLimitProvider = FutureProvider<CustomScenarioLimitResponse>((ref) async {
  final api = CustomScenarioApi(ApiClient());
  return api.fetchLimit();
});

class ScenarioSelectionScreen extends ConsumerWidget {
  const ScenarioSelectionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authStateProvider);
    final pro = ref.watch(proStatusProvider);
    final customScenariosAsync = ref.watch(customScenariosProvider);

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

          final customScenarios = customScenariosAsync.valueOrNull?.customScenarios ?? [];

          return Column(
            children: [
              const StreakWidget(),
              // オリジナルシナリオ作成ボタン
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _showCreateCustomScenarioDialog(context, ref),
                    icon: const Icon(Icons.auto_awesome),
                    label: const Text('オリジナルシナリオを作成'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.purple.shade600,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ),
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
                child: ListView(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  children: [
                    // カスタムシナリオセクション
                    if (customScenarios.isNotEmpty) ...[
                      Padding(
                        padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                        child: Row(
                          children: [
                            Icon(Icons.auto_awesome, size: 18, color: Colors.purple.shade600),
                            const SizedBox(width: 6),
                            Text(
                              'あなたのオリジナルシナリオ',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                color: Colors.purple.shade700,
                              ),
                            ),
                          ],
                        ),
                      ),
                      ...customScenarios.map((cs) => _buildCustomScenarioCard(context, ref, cs)),
                      const SizedBox(height: 16),
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16),
                        child: Divider(),
                      ),
                      const SizedBox(height: 8),
                      Padding(
                        padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                        child: Text(
                          'すべてのシナリオ',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: Colors.grey.shade700,
                          ),
                        ),
                      ),
                    ],
                    // 通常シナリオ
                    ...scenarios.map((s) => _buildScenarioCard(context, ref, s)),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildCustomScenarioCard(BuildContext context, WidgetRef ref, CustomScenario cs) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.purple.shade200, width: 1),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () async {
          final sessionId = await ref
              .read(sessionControllerProvider.notifier)
              .startNewSession(
                customScenarioId: cs.id,
                difficulty: 'intermediate',
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
                  Expanded(
                    child: Row(
                      children: [
                        Icon(Icons.auto_awesome, size: 16, color: Colors.purple.shade400),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            cs.name,
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(fontWeight: FontWeight.w600),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.delete_outline, color: Colors.grey.shade400, size: 20),
                    onPressed: () => _confirmDeleteCustomScenario(context, ref, cs),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                cs.description,
                style: Theme.of(context)
                    .textTheme
                    .bodyMedium
                    ?.copyWith(color: Colors.grey[800]),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  _buildRoleChip('あなた: ${cs.userRole}'),
                  const SizedBox(width: 8),
                  _buildRoleChip('AI: ${cs.aiRole}'),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRoleChip(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.purple.shade50,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          color: Colors.purple.shade700,
        ),
        overflow: TextOverflow.ellipsis,
      ),
    );
  }

  Widget _buildScenarioCard(BuildContext context, WidgetRef ref, ScenarioSummary s) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () async {
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
                  Expanded(
                    child: Text(
                      s.name,
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.w600),
                    ),
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
                    label: Text(s.categoryLabel),
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
  }

  Future<void> _confirmDeleteCustomScenario(BuildContext context, WidgetRef ref, CustomScenario cs) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('シナリオを削除'),
        content: Text('「${cs.name}」を削除しますか？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('キャンセル'),
          ),
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('削除'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final api = CustomScenarioApi(ApiClient());
      await api.deleteCustomScenario(cs.id);
      ref.invalidate(customScenariosProvider);
    }
  }

  Future<void> _showCreateCustomScenarioDialog(BuildContext context, WidgetRef ref) async {
    final limitAsync = ref.read(customScenarioLimitProvider);
    final limit = limitAsync.valueOrNull;

    if (limit != null && limit.remaining <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            limit.isPro
                ? '本日の作成上限（${limit.dailyLimit}件）に達しました'
                : '無料プランでは1日1件まで作成できます',
          ),
          backgroundColor: Colors.orange.shade700,
        ),
      );
      return;
    }

    final result = await showDialog<CustomScenarioCreate>(
      context: context,
      builder: (ctx) => const _CreateCustomScenarioDialog(),
    );

    if (result != null) {
      try {
        final api = CustomScenarioApi(ApiClient());
        await api.createCustomScenario(result);
        ref.invalidate(customScenariosProvider);
        ref.invalidate(customScenarioLimitProvider);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('オリジナルシナリオを作成しました'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } catch (e) {
        if (context.mounted) {
          String errorMessage = '作成に失敗しました';
          
          // DioExceptionの場合、詳細なエラーメッセージを取得
          if (e.toString().contains('DioException')) {
            final dioError = e as DioException;
            if (dioError.response?.data != null) {
              final data = dioError.response!.data;
              if (data is Map && data.containsKey('detail')) {
                errorMessage = data['detail'].toString();
              } else if (data is String) {
                errorMessage = data;
              } else {
                errorMessage = '$errorMessage (${dioError.response?.statusCode})';
              }
            } else {
              errorMessage = '$errorMessage: ${dioError.message}';
            }
          } else {
            errorMessage = '$errorMessage: $e';
          }
          
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMessage),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      }
    }
  }
}

class _CreateCustomScenarioDialog extends StatefulWidget {
  const _CreateCustomScenarioDialog();

  @override
  State<_CreateCustomScenarioDialog> createState() => _CreateCustomScenarioDialogState();
}

class _CreateCustomScenarioDialogState extends State<_CreateCustomScenarioDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _userRoleController = TextEditingController();
  final _aiRoleController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _userRoleController.dispose();
    _aiRoleController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.auto_awesome, color: Colors.purple.shade600),
          const SizedBox(width: 8),
          const Text('オリジナルシナリオ作成'),
        ],
      ),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'シナリオ名',
                  hintText: '例: カフェで注文',
                ),
                validator: (v) => (v == null || v.isEmpty) ? '必須です' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'シナリオの説明',
                  hintText: '例: カフェでコーヒーを注文するシチュエーション',
                ),
                maxLines: 2,
                validator: (v) => (v == null || v.isEmpty) ? '必須です' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _userRoleController,
                decoration: const InputDecoration(
                  labelText: 'あなたの役割',
                  hintText: '例: カフェの客',
                ),
                validator: (v) => (v == null || v.isEmpty) ? '必須です' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _aiRoleController,
                decoration: const InputDecoration(
                  labelText: 'AIの役割',
                  hintText: '例: カフェの店員',
                ),
                validator: (v) => (v == null || v.isEmpty) ? '必須です' : null,
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('キャンセル'),
        ),
        ElevatedButton(
          onPressed: () {
            if (_formKey.currentState?.validate() ?? false) {
              Navigator.of(context).pop(
                CustomScenarioCreate(
                  name: _nameController.text.trim(),
                  description: _descriptionController.text.trim(),
                  userRole: _userRoleController.text.trim(),
                  aiRole: _aiRoleController.text.trim(),
                ),
              );
            }
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.purple.shade600,
            foregroundColor: Colors.white,
          ),
          child: const Text('作成'),
        ),
      ],
    );
  }
}



