import 'package:flutter/material.dart';

class AiTurnMessageCard extends StatelessWidget {
  const AiTurnMessageCard({
    super.key,
    required this.message,
    required this.feedbackShort,
    required this.improvedSentence,
    this.onSavePhrase,
    this.isSaved = false,
    this.isSaving = false,
  });

  final String message;
  final String? feedbackShort;
  final String? improvedSentence;
  final VoidCallback? onSavePhrase;
  final bool isSaved;
  final bool isSaving;

  @override
  Widget build(BuildContext context) {
    final maxWidth = MediaQuery.of(context).size.width * 0.86;

    final tip = feedbackShort?.trim();
    final improved = improvedSentence?.trim();
    final hasTip = tip != null && tip.isNotEmpty;
    final hasImproved = improved != null && improved.isNotEmpty;
    final hasAnyFeedback = hasTip || hasImproved;

    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: maxWidth),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI reply bubble
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFFF3F4F6), // light gray
              borderRadius: BorderRadius.circular(18),
            ),
            child: Text(
              message,
              style: const TextStyle(
                fontSize: 15,
                height: 1.35,
                color: Color(0xFF111827),
              ),
            ),
          ),

          // Feedback + improved sentence as a single cohesive card (like the reference UI)
          if (hasAnyFeedback) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                border: Border.all(color: const Color(0xFFE5E7EB)), // gray-200
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x14000000),
                    blurRadius: 10,
                    offset: Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (hasTip) ...[
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Padding(
                          padding: EdgeInsets.only(top: 1),
                          child: Icon(
                            Icons.lightbulb_outline,
                            size: 18,
                            color: Color(0xFFF97316), // orange-500
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            tip,
                            style: const TextStyle(
                              fontSize: 13,
                              height: 1.35,
                              color: Color(0xFFEA580C), // orange-600
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                  if (hasTip && hasImproved) ...[
                    const SizedBox(height: 12),
                    const Divider(height: 1, color: Color(0xFFE5E7EB)),
                    const SizedBox(height: 12),
                  ],
                  if (hasImproved) ...[
                    Row(
                      children: const [
                        Icon(
                          Icons.chat_bubble_outline,
                          size: 18,
                          color: Color(0xFF2563EB), // blue-600
                        ),
                        SizedBox(width: 8),
                        Text(
                          'BETTER WAY TO SAY IT:',
                          style: TextStyle(
                            fontSize: 12,
                            letterSpacing: 0.4,
                            color: Color(0xFF2563EB),
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF), // blue-50
                        border: Border.all(
                          color: const Color(0xFFBFDBFE), // blue-200
                        ),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Text(
                        '"$improved"',
                        style: const TextStyle(
                          fontSize: 18,
                          height: 1.3,
                          color: Color(0xFF1D4ED8), // blue-700
                          fontStyle: FontStyle.italic,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    // 保存ボタン
                    if (onSavePhrase != null) ...[
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          if (isSaved)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 12,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: const Color(0xFFDCFCE7), // green-100
                                borderRadius: BorderRadius.circular(16),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.check_circle,
                                    size: 16,
                                    color: Color(0xFF16A34A), // green-600
                                  ),
                                  SizedBox(width: 4),
                                  Text(
                                    '保存済み',
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w600,
                                      color: Color(0xFF16A34A),
                                    ),
                                  ),
                                ],
                              ),
                            )
                          else
                            ElevatedButton.icon(
                              onPressed: isSaving ? null : onSavePhrase,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF3B82F6),
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 8,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                ),
                              ),
                              icon: isSaving
                                  ? const SizedBox(
                                      width: 14,
                                      height: 14,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: Colors.white,
                                      ),
                                    )
                                  : const Icon(Icons.bookmark_border, size: 16),
                              label: Text(
                                isSaving ? '保存中...' : '保存する',
                                style: const TextStyle(fontSize: 12),
                              ),
                            ),
                        ],
                      ),
                    ],
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

