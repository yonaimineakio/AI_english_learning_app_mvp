import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../audio/audio_controller.dart';
import 'session_controller.dart';
import 'widgets/ai_turn_message_card.dart';
import 'widgets/session_task_checklist_card.dart';

class SessionScreen extends ConsumerStatefulWidget {
  const SessionScreen({super.key, required this.sessionId});

  final String sessionId;

  @override
  ConsumerState<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends ConsumerState<SessionScreen> {
  final _controller = TextEditingController();
  int _lastSpokenAiIndex = -1;
  ProviderSubscription<AsyncValue<SessionUiState>>? _sessionSub;
  bool _navigatingToSummary = false;
  bool _showingEndDialog = false;

  void _maybeSpeakLatestAi(AsyncValue<SessionUiState> next) {
    final current = next.valueOrNull;
    if (current == null || current.messages.isEmpty) return;

    final idx = current.messages.lastIndexWhere((m) => !m.isUser);
    if (idx == -1 || idx == _lastSpokenAiIndex) return;

    _lastSpokenAiIndex = idx;
    final text = current.messages[idx].text;
    if (text.isEmpty) return;

    ref.read(audioControllerProvider.notifier).playTts(text);
  }

  @override
  void initState() {
    super.initState();

    // セッション状態の変化を監視し、新しいAIメッセージが追加されたときに一度だけTTS再生する
    _sessionSub = ref.listenManual<AsyncValue<SessionUiState>>(
      sessionControllerProvider,
      (previous, next) {
        _maybeSpeakLatestAi(next);
      },
    );

    // 画面表示直後に現在の状態をチェックし、既に存在する初期AIメッセージも読み上げる
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _maybeSpeakLatestAi(ref.read(sessionControllerProvider));
    });
  }

  @override
  void dispose() {
    _sessionSub?.close();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(sessionControllerProvider);
    final audio = ref.watch(audioControllerProvider);
    final dataOrNull = state.valueOrNull;
    final titleText = dataOrNull?.scenario.name ?? '会話セッション';
    final roundTarget = dataOrNull?.roundTarget;
    final completedRounds = dataOrNull?.completedRounds ?? 0;
    final roundLabel = (roundTarget != null && roundTarget > 0)
        ? 'Round ${completedRounds + 1 > roundTarget ? roundTarget : completedRounds + 1} / $roundTarget'
        : null;

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 64,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              titleText,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            if (roundLabel != null)
              Text(
                roundLabel,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: const Color(0xFF6B7280), // gray-500
                      fontWeight: FontWeight.w600,
                    ),
              ),
          ],
        ),
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (data) {
          // バックエンドから「終了提案」フラグを受け取ったら、ユーザー承認のモーダルを表示する
          if (data.shouldEndSession &&
              !_navigatingToSummary &&
              !_showingEndDialog) {
            _showingEndDialog = true;
            WidgetsBinding.instance.addPostFrameCallback((_) async {
              if (!mounted || !context.mounted) return;

              final res = await showDialog<bool>(
                context: context,
                barrierDismissible: true,
                builder: (context) {
                  final isGoalsCompleted = data.endPromptReason == 'goals_completed';
                  return AlertDialog(
                    title: Text(
                      isGoalsCompleted ? 'タスクを達成しました！' : 'セッションを終了しますか？',
                    ),
                    content: Text(
                      isGoalsCompleted
                          ? 'タスクをすべて完了しました。\nセッションを終了してサマリに移動しますか？'
                          : '会話を終了してサマリに移動します。\n'
                              '（後で続けたい場合は「続ける」を選んでください）',
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        child: const Text('続ける'),
                      ),
                      ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(true),
                        child: const Text('終了する'),
                      ),
                    ],
                  );
                },
              );

              if (!mounted || !context.mounted) return;

              if (res == true) {
                _navigatingToSummary = true;
                try {
                  final end = await ref
                      .read(sessionControllerProvider.notifier)
                      .endCurrentSession();
                  if (!mounted || !context.mounted) return;
                  context.go('/summary', extra: end);
                } catch (e) {
                  if (!mounted || !context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('セッション終了処理に失敗しました: $e'),
                    ),
                  );
                } finally {
                  _navigatingToSummary = false;
                }
              } else {
                // 会話継続: フラグをクリアして再表示ループを防ぐ
                ref.read(sessionControllerProvider.notifier).dismissEndPrompt();
              }

              if (mounted) {
                setState(() {
                  _showingEndDialog = false;
                });
              } else {
                _showingEndDialog = false;
              }
            });
          }

          return Column(
            children: [
              if (data.goalsTotal != null || data.goalsStatus != null)
                SessionTaskChecklistCard(
                  scenarioId: data.scenario.id,
                  scenarioName: data.scenario.name,
                  goalsStatus: data.goalsStatus,
                  goalsTotal: data.goalsTotal,
                  goalsAchieved: data.goalsAchieved,
                ),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: data.messages.length,
                  itemBuilder: (context, index) {
                    final m = data.messages[index];
                    if (m.isUser) {
                      return Align(
                        alignment: Alignment.centerRight,
                        child: ConstrainedBox(
                          constraints: BoxConstraints(
                            maxWidth: MediaQuery.of(context).size.width * 0.82,
                          ),
                          child: Container(
                            margin: const EdgeInsets.symmetric(vertical: 6),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 14,
                              vertical: 12,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.blue[200],
                              borderRadius: BorderRadius.circular(18),
                            ),
                            child: Text(
                              m.text,
                              style: const TextStyle(
                                fontSize: 15,
                                height: 1.35,
                                color: Colors.black87,
                              ),
                            ),
                          ),
                        ),
                      );
                    }

                    return Align(
                      alignment: Alignment.centerLeft,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: AiTurnMessageCard(
                          message: m.text,
                          feedbackShort: m.feedbackShort,
                          improvedSentence: m.improvedSentence,
                        ),
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Row(
                  children: [
                    IconButton(
                      icon: audio.isTranscribing
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : Icon(
                              audio.isRecording ? Icons.stop : Icons.mic,
                            ),
                      onPressed: audio.isTranscribing
                          ? null
                          : () async {
                              final notifier = ref
                                  .read(audioControllerProvider.notifier);
                              try {
                                if (audio.isRecording) {
                                  final text =
                                      await notifier.stopAndTranscribe();
                                  if (text != null && text.isNotEmpty) {
                                    _controller.text = text;
                                  }
                                } else {
                                  await notifier.startRecording();
                                }
                              } catch (e) {
                                if (!context.mounted) return;
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      'マイク操作に失敗しました: $e',
                                    ),
                                  ),
                                );
                              }
                            },
                    ),
                    Expanded(
                      child: TextField(
                        controller: _controller,
                        decoration: const InputDecoration(
                          hintText: '英語で話しかけてみましょう',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: data.isLoadingTurn
                          ? const CircularProgressIndicator()
                          : const Icon(Icons.send),
                      onPressed: data.isLoadingTurn
                          ? null
                          : () async {
                              final text = _controller.text.trim();
                              if (text.isEmpty) return;
                              _controller.clear();
                              final notifier = ref.read(
                                sessionControllerProvider.notifier,
                              );
                              try {
                                await notifier.sendUserMessage(text);
                              } catch (e) {
                                _controller.text = text;
                                if (!context.mounted) return;
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      'メッセージ送信に失敗しました: $e',
                                    ),
                                  ),
                                );
                              }
                            },
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}



