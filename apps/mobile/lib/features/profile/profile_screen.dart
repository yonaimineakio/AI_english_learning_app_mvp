import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../auth/auth_providers.dart';
import '../home/streak_widget.dart';

/// プロフィール画面
class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  Future<void> _showEditProfileDialog(
    BuildContext context,
    WidgetRef ref,
    AuthState state,
  ) async {
    final controller = TextEditingController(text: state.userName ?? '');
    bool saving = false;

    await showDialog<void>(
      context: context,
      barrierDismissible: !saving,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setState) {
            return AlertDialog(
              title: const Text('プロフィール編集'),
              content: TextField(
                controller: controller,
                decoration: const InputDecoration(
                  labelText: '表示名',
                  hintText: '例: Akio',
                ),
              ),
              actions: [
                TextButton(
                  onPressed: saving ? null : () => Navigator.of(ctx).pop(),
                  child: const Text('キャンセル'),
                ),
                ElevatedButton(
                  onPressed: saving
                      ? null
                      : () async {
                          final name = controller.text.trim();
                          if (name.isEmpty) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('表示名を入力してください')),
                            );
                            return;
                          }
                          setState(() => saving = true);
                          try {
                            await ref
                                .read(authStateProvider.notifier)
                                .updateProfileName(name);
                            if (context.mounted) {
                              Navigator.of(ctx).pop();
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('プロフィールを更新しました')),
                              );
                            }
                          } catch (e) {
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('更新に失敗しました: $e')),
                              );
                            }
                          } finally {
                            if (ctx.mounted) setState(() => saving = false);
                          }
                        },
                  child: saving
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('保存'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _showDeleteAccountDialog(
    BuildContext context,
    WidgetRef ref,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        bool deleting = false;
        return StatefulBuilder(
          builder: (ctx, setState) {
            return AlertDialog(
              title: const Text('アカウント削除'),
              content: const Text(
                'この操作は取り消せません。\n\n'
                '学習履歴・保存フレーズ・アカウント情報など、'
                'すべてのデータが完全に削除されます。',
              ),
              actions: [
                TextButton(
                  onPressed: deleting ? null : () => Navigator.of(ctx).pop(false),
                  child: const Text('キャンセル'),
                ),
                TextButton(
                  onPressed: deleting
                      ? null
                      : () async {
                          setState(() => deleting = true);
                          try {
                            await ref.read(authStateProvider.notifier).deleteAccount();
                            if (ctx.mounted) Navigator.of(ctx).pop(true);
                          } catch (e) {
                            if (ctx.mounted) {
                              setState(() => deleting = false);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('削除に失敗しました: $e')),
                              );
                              Navigator.of(ctx).pop(false);
                            }
                          }
                        },
                  child: deleting
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text(
                          '削除する',
                          style: TextStyle(color: Colors.red),
                        ),
                ),
              ],
            );
          },
        );
      },
    );

    if (confirmed == true && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('アカウントを削除しました')),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        centerTitle: true,
      ),
      body: authState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (state) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // プロフィールヘッダー
              _ProfileHeader(
                name: state.userName ?? 'ユーザー',
                email: state.email,
              ),
              const SizedBox(height: 24),

              // ストリーク情報
              const StreakWidget(),
              const SizedBox(height: 16),

              // 設定メニュー
              _SettingsSection(
                title: '学習設定',
                items: [
                  _SettingsItem(
                    icon: Icons.translate,
                    label: '学習言語',
                    value: '英語',
                    onTap: () {},
                  ),
                  _SettingsItem(
                    icon: Icons.speed,
                    label: '難易度',
                    value: '中級',
                    onTap: () {},
                  ),
                  _SettingsItem(
                    icon: Icons.notifications_outlined,
                    label: '復習リマインダー',
                    value: 'ON',
                    onTap: () {},
                  ),
                ],
              ),
              const SizedBox(height: 16),

              _SettingsSection(
                title: 'アカウント',
                items: [
                  _SettingsItem(
                    icon: Icons.workspace_premium,
                    label: 'Proにアップグレード',
                    value: '7日間無料トライアル',
                    onTap: () => context.push('/paywall'),
                  ),
                  _SettingsItem(
                    icon: Icons.person_outline,
                    label: 'プロフィール編集',
                    onTap: () => _showEditProfileDialog(context, ref, state),
                  ),
                  _SettingsItem(
                    icon: Icons.help_outline,
                    label: 'ヘルプ・お問い合わせ',
                    onTap: () {},
                  ),
                  _SettingsItem(
                    icon: Icons.info_outline,
                    label: 'アプリについて',
                    value: 'v1.0.0',
                    onTap: () {},
                  ),
                  _SettingsItem(
                    icon: Icons.delete_outline,
                    label: 'アカウント削除',
                    onTap: () => _showDeleteAccountDialog(context, ref),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // ログアウトボタン
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () async {
                    await ref.read(authStateProvider.notifier).logout();
                  },
                  icon: const Icon(Icons.logout, color: Colors.red),
                  label: const Text(
                    'ログアウト',
                    style: TextStyle(color: Colors.red),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Colors.red),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// プロフィールヘッダー
class _ProfileHeader extends StatelessWidget {
  const _ProfileHeader({
    required this.name,
    this.email,
  });

  final String name;
  final String? email;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // アバター
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: const Color(0xFF4169E1),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              name.isNotEmpty ? name[0].toUpperCase() : '?',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          name,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        if (email != null) ...[
          const SizedBox(height: 4),
          Text(
            email!,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ],
    );
  }
}

/// 設定セクション
class _SettingsSection extends StatelessWidget {
  const _SettingsSection({
    required this.title,
    required this.items,
  });

  final String title;
  final List<_SettingsItem> items;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 8),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: Colors.grey.shade600,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: items
                .asMap()
                .entries
                .map(
                  (entry) => Column(
                    children: [
                      entry.value,
                      if (entry.key < items.length - 1)
                        Divider(
                          height: 1,
                          indent: 56,
                          color: Colors.grey.shade200,
                        ),
                    ],
                  ),
                )
                .toList(),
          ),
        ),
      ],
    );
  }
}

/// 設定項目
class _SettingsItem extends StatelessWidget {
  const _SettingsItem({
    required this.icon,
    required this.label,
    this.value,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final String? value;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon,
                size: 20,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                label,
                style: const TextStyle(fontSize: 16),
              ),
            ),
            if (value != null)
              Text(
                value!,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade500,
                ),
              ),
            const SizedBox(width: 8),
            Icon(
              Icons.chevron_right,
              size: 20,
              color: Colors.grey.shade400,
            ),
          ],
        ),
      ),
    );
  }
}

