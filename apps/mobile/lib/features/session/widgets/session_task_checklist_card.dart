import 'package:flutter/material.dart';

class SessionTaskChecklistCard extends StatefulWidget {
  const SessionTaskChecklistCard({
    super.key,
    required this.scenarioId,
    required this.scenarioName,
    required this.goalsStatus,
    required this.goalsTotal,
    required this.goalsAchieved,
    this.goalsLabels,
  });

  final int scenarioId;
  final String scenarioName;
  final List<int>? goalsStatus; // 0/1 per task
  final int? goalsTotal;
  final int? goalsAchieved;
  final List<String>? goalsLabels; // APIから取得したゴールラベル

  @override
  State<SessionTaskChecklistCard> createState() =>
      _SessionTaskChecklistCardState();
}

class _SessionTaskChecklistCardState extends State<SessionTaskChecklistCard> {
  bool _expanded = true;

  List<String> _getLabels() {
    // APIから取得したラベルを優先的に使用
    if (widget.goalsLabels != null && widget.goalsLabels!.isNotEmpty) {
      return widget.goalsLabels!;
    }

    // フォールバック: ゴール数に基づいて汎用ラベルを生成
    final total = widget.goalsTotal ?? widget.goalsStatus?.length ?? 0;
    if (total <= 0) return const [];
    return List<String>.generate(total, (i) => 'タスク ${i + 1}');
  }

  @override
  Widget build(BuildContext context) {
    final labels = _getLabels();
    final total = labels.isNotEmpty
        ? labels.length
        : (widget.goalsTotal ?? widget.goalsStatus?.length ?? 0);
    if (total <= 0) return const SizedBox.shrink();

    final status = widget.goalsStatus ?? List<int>.filled(total, 0);
    final achieved = widget.goalsAchieved ??
        status.where((v) => v == 1).length.clamp(0, total);

    final baseTextColor = Colors.white.withOpacity(0.92);
    final secondaryTextColor = Colors.white.withOpacity(0.75);

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 10, 16, 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            const Color(0xFF0D1B2A),
            const Color(0xFF0B1A3A).withOpacity(0.95),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.10),
            blurRadius: 16,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Material(
        type: MaterialType.transparency,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () => setState(() => _expanded = !_expanded),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 14, 12, 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'タスク ($achieved/$total 完了)',
                        style: TextStyle(
                          color: baseTextColor,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    Icon(
                      _expanded ? Icons.expand_less : Icons.expand_more,
                      color: secondaryTextColor,
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                AnimatedCrossFade(
                  duration: const Duration(milliseconds: 180),
                  crossFadeState: _expanded
                      ? CrossFadeState.showFirst
                      : CrossFadeState.showSecond,
                  firstChild: Column(
                    children: List<Widget>.generate(total, (idx) {
                      final label =
                          idx < labels.length ? labels[idx] : 'タスク ${idx + 1}';
                      final done = idx < status.length && status[idx] == 1;
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          children: [
                            Icon(
                              done
                                  ? Icons.check_circle
                                  : Icons.radio_button_unchecked,
                              size: 18,
                              color: done
                                  ? const Color(0xFF32D583)
                                  : Colors.white.withOpacity(0.60),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                label,
                                style: TextStyle(
                                  color: done
                                      ? Colors.white.withOpacity(0.65)
                                      : baseTextColor,
                                  fontSize: 14.5,
                                  height: 1.25,
                                  decoration: done
                                      ? TextDecoration.lineThrough
                                      : TextDecoration.none,
                                  decorationColor:
                                      Colors.white.withOpacity(0.55),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                  ),
                  secondChild: const SizedBox.shrink(),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
