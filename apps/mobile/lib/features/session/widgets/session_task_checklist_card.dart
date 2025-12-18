import 'package:flutter/material.dart';

class SessionTaskChecklistCard extends StatefulWidget {
  const SessionTaskChecklistCard({
    super.key,
    required this.scenarioId,
    required this.scenarioName,
    required this.goalsStatus,
    required this.goalsTotal,
    required this.goalsAchieved,
  });

  final int scenarioId;
  final String scenarioName;
  final List<int>? goalsStatus; // 0/1 per task
  final int? goalsTotal;
  final int? goalsAchieved;

  @override
  State<SessionTaskChecklistCard> createState() =>
      _SessionTaskChecklistCardState();
}

class _SessionTaskChecklistCardState extends State<SessionTaskChecklistCard> {
  bool _expanded = true;

  List<String> _labelsForScenario(int id) {
    // NOTE: Backend stores goals in Japanese (SCENARIO_GOALS). The mobile UI shows
    // short English task labels (like the screenshot). Keep these aligned by index.
    // Fallback: generic "Task n" when unknown.
    const m = <int, List<String>>{
      1: [
        'Start check-in with your reservation name',
        'State your seat preference (window/aisle)',
        'Ask about checking in baggage',
      ],
      2: [
        'Share your opinion at the start of the meeting',
        'Agree or disagree with a proposal',
        'Confirm the next action items',
      ],
      3: [
        'Call the waiter and ask for the menu',
        'Ask about recommendations / sides',
        'Mention any allergies or restrictions',
      ],
      4: [
        'Introduce yourself and break the ice',
        'Explain your proposal briefly',
        'Answer questions and address concerns',
      ],
      5: [
        'Start check-in with your reservation name',
        'Request an upgrade or extra needs',
        'Ask about hotel facilities/services',
      ],
      6: [
        'Explain your destination and why',
        'Share your dates and budget',
        'Ask about recommended activities',
      ],
      7: [
        'Suggest a place to visit and explain why',
        'Explain transport options and time',
        'Adjust the plan based on preferences',
      ],
      8: [
        'Answer purpose of visit and duration',
        'Share your hotel name and address',
        'Respond to extra questions honestly',
      ],
      9: [
        'Suggest dates and a destination',
        'Ask their availability and adjust',
        'Share budget and activities you want',
      ],
      10: [
        'Explain when/where you lost your wallet',
        'Describe the wallet (color/contents)',
        'Ask about the lost-item report process',
      ],
      11: [
        'Describe the problem clearly',
        'Request refund/exchange/return',
        'Confirm options and decide next steps',
      ],
      12: [
        "Ask about recommended drinks (seasonal too)",
        'Comment on the atmosphere',
        'Make light small talk (weather, etc.)',
      ],
      13: [
        'Tell the date/time and number of tickets',
        'Ask about seat types and prices',
        'Discuss other dates if sold out',
      ],
      14: [
        'Comment on the weather/park',
        'Ask about hobbies and how often they come',
        'Say goodbye politely (“See you again!”)',
      ],
      15: [
        'Explain the reason briefly',
        'Offer 2–3 alternative times',
        'Apologize and confirm their availability',
      ],
      16: [
        'Share the purpose and expected duration',
        'Propose multiple candidate times',
        "Confirm everyone's availability",
      ],
      17: [
        'Share the agenda at the beginning',
        "Invite opinions on each topic",
        'Confirm decisions and action items',
      ],
      18: [
        'Ask about price/delivery/payment terms',
        'Share your preferred terms and flexibility',
        'Offer an alternative proposal',
      ],
      19: [
        'Explain the survey overview',
        'Share key numbers and changes',
        'Propose improvements based on results',
      ],
      20: [
        'Explain the delay and its cause',
        'Apologize and clarify responsibility',
        'Share a new plan and prevention steps',
      ],
      21: [
        'Describe your symptoms',
        'Share expected leave duration and return',
        'Discuss handover/coverage',
      ],
    };

    final labels = m[id];
    if (labels != null && labels.isNotEmpty) return labels;

    final total = widget.goalsTotal ?? widget.goalsStatus?.length ?? 0;
    if (total <= 0) return const [];
    return List<String>.generate(total, (i) => 'Task ${i + 1}');
  }

  @override
  Widget build(BuildContext context) {
    final labels = _labelsForScenario(widget.scenarioId);
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
                        'Tasks ($achieved/$total completed)',
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
                          idx < labels.length ? labels[idx] : 'Task ${idx + 1}';
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

