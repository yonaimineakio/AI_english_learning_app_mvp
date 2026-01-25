import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../shadowing/shadowing_home_screen.dart';
import '../scenario_selection/scenario_selection_screen.dart';
import '../review/review_screen.dart';
import '../profile/profile_screen.dart';
import 'main_tab_state.dart';

/// メインのボトムナビゲーション付きシェル画面
/// 4タブ: Home(シャドーイング) / Scenarios / Review / Profile
class MainShellScreen extends ConsumerWidget {
  const MainShellScreen({super.key});

  final List<Widget> _screens = const [
    ShadowingHomeScreen(),
    ScenarioSelectionScreen(),
    ReviewScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentIndex = ref.watch(mainTabIndexProvider);

    return Scaffold(
      body: IndexedStack(
        index: currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A2E),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 10,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _NavItem(
                  icon: Icons.record_voice_over,
                  label: 'Home',
                  isSelected: currentIndex == 0,
                  onTap: () => ref.read(mainTabIndexProvider.notifier).state = 0,
                ),
                _NavItem(
                  icon: Icons.chat_bubble_outline,
                  label: 'Scenarios',
                  isSelected: currentIndex == 1,
                  onTap: () => ref.read(mainTabIndexProvider.notifier).state = 1,
                ),
                _NavItem(
                  icon: Icons.bolt,
                  label: 'Review',
                  isSelected: currentIndex == 2,
                  onTap: () => ref.read(mainTabIndexProvider.notifier).state = 2,
                ),
                _NavItem(
                  icon: Icons.person_outline,
                  label: 'Profile',
                  isSelected: currentIndex == 3,
                  onTap: () => ref.read(mainTabIndexProvider.notifier).state = 3,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// ナビゲーションアイテム
class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = isSelected ? const Color(0xFF4169E1) : Colors.grey.shade400;

    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: SizedBox(
        width: 64,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: color,
              size: 28,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

