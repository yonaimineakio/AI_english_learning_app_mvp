import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/services/api_client.dart';
import '../../shared/services/saved_phrases_api.dart';
import '../audio/audio_controller.dart';
import 'session_controller.dart';
import 'widgets/ai_turn_message_card.dart';
import 'widgets/session_task_checklist_card.dart';

final _savedPhrasesApiProvider = Provider<SavedPhrasesApi>(
  (ref) => SavedPhrasesApi(ApiClient()),
);

class SessionScreen extends ConsumerStatefulWidget {
  const SessionScreen({super.key, required this.sessionId});

  final String sessionId;

  @override
  ConsumerState<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends ConsumerState<SessionScreen> {
  int _lastSpokenAiIndex = -1;
  ProviderSubscription<AsyncValue<SessionUiState>>? _sessionSub;
  bool _navigatingToSummary = false;
  bool _showingEndDialog = false;
  int _redoCount = 0;
  static const int _maxRedoCount = 3;

  // 保存済みのラウンドインデックスを管理（key: roundIndex）
  final Set<int> _savedRoundIndexes = {};
  int? _savingRoundIndex;

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
    super.dispose();
  }

  Future<void> _handleTranscriptionAndSend({
    required String text,
    required bool isLoadingTurn,
  }) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('文字起こし結果が空でした。もう一度お試しください。')),
      );
      return;
    }

    final canRetry = _redoCount < _maxRedoCount;
    final remaining = (_maxRedoCount - _redoCount).clamp(0, _maxRedoCount);

    final action = await showModalBottomSheet<_TranscriptionAction>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '認識結果',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFF3F4F6),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  trimmed,
                  style: const TextStyle(fontSize: 15, height: 1.35),
                ),
              ),
              const SizedBox(height: 12),
              Text(
                canRetry ? 'やり直し: 残り $remaining 回' : 'やり直し上限に達しました',
                style: TextStyle(
                  fontSize: 12.5,
                  color: Colors.black.withOpacity(0.6),
                ),
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: canRetry
                          ? () => Navigator.of(context).pop(
                                _TranscriptionAction.retry,
                              )
                          : null,
                      child: const Text('やり直す'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: isLoadingTurn
                          ? null
                          : () => Navigator.of(context).pop(
                                _TranscriptionAction.send,
                              ),
                      child: const Text('送信'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Center(
                child: TextButton(
                  onPressed: () =>
                      Navigator.of(context).pop(_TranscriptionAction.cancel),
                  child: const Text('キャンセル'),
                ),
              ),
            ],
          ),
        );
      },
    );

    if (!mounted) return;

    switch (action) {
      case _TranscriptionAction.send:
        setState(() => _redoCount = 0);
        try {
          await ref
              .read(sessionControllerProvider.notifier)
              .sendUserMessage(trimmed);
        } catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('送信に失敗しました: $e')),
          );
        }
        break;
      case _TranscriptionAction.retry:
        setState(() => _redoCount += 1);
        try {
          await ref.read(audioControllerProvider.notifier).startRecording();
        } catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('録音を開始できませんでした: $e')),
          );
        }
        break;
      case _TranscriptionAction.cancel:
      case null:
        // keep redoCount as-is (so multiple cancels still count toward limit)
        break;
    }
  }

  Future<void> _savePhrase({
    required int sessionId,
    required int roundIndex,
    required String phrase,
    required String explanation,
    required String originalInput,
  }) async {
    if (_savedRoundIndexes.contains(roundIndex) ||
        _savingRoundIndex == roundIndex) {
      return;
    }

    setState(() {
      _savingRoundIndex = roundIndex;
    });

    try {
      final api = ref.read(_savedPhrasesApiProvider);
      await api.createSavedPhrase(
        phrase: phrase,
        explanation: explanation,
        originalInput: originalInput,
        sessionId: sessionId,
        roundIndex: roundIndex,
      );
      setState(() {
        _savedRoundIndexes.add(roundIndex);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('フレーズを保存しました'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('保存に失敗しました: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _savingRoundIndex = null;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(sessionControllerProvider);
    final audio = ref.watch(audioControllerProvider);
    final dataOrNull = state.valueOrNull;
    final titleText = dataOrNull?.scenarioName ?? '会話セッション';
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

              final isGoalsCompleted = data.endPromptReason == 'goals_completed';
              final isRoundLimit = data.endPromptReason == 'round_limit';
              final canExtend = isRoundLimit && data.canExtend;

              final res = await showDialog<_EndDialogAction>(
                context: context,
                barrierDismissible: true,
                builder: (context) {
                  return AlertDialog(
                    title: Text(
                      isGoalsCompleted
                          ? 'タスクを達成しました！'
                          : isRoundLimit
                              ? 'ラウンド上限です'
                              : 'セッションを終了しますか？',
                    ),
                    content: Text(
                      isGoalsCompleted
                          ? 'タスクをすべて完了しました。\nセッションを終了してサマリに移動しますか？'
                          : isRoundLimit
                              ? (canExtend
                                  ? '最大ラウンドに到達しました。\n+3ラウンド延長しますか？'
                                  : '最大ラウンドに到達しました。\nセッションを終了してサマリに移動しますか？')
                              : '会話を終了してサマリに移動します。\n'
                                  '（後で続けたい場合は「続ける」を選んでください）',
                    ),
                    actions: [
                      if (!isRoundLimit)
                        TextButton(
                          onPressed: () => Navigator.of(context).pop(
                            _EndDialogAction.continueSession,
                          ),
                          child: const Text('続ける'),
                        ),
                      if (canExtend)
                        TextButton(
                          onPressed: () => Navigator.of(context).pop(
                            _EndDialogAction.extend,
                          ),
                          child: const Text('+3ラウンド延長'),
                        ),
                      ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(
                          _EndDialogAction.end,
                        ),
                        child: const Text('終了する'),
                      ),
                    ],
                  );
                },
              );

              if (!mounted || !context.mounted) return;

              if (res == _EndDialogAction.end) {
                _navigatingToSummary = true;

                // 終了フラグをクリアして再表示を防ぐ
                ref.read(sessionControllerProvider.notifier).dismissEndPrompt();

                // ローディングダイアログを表示（閉じられない）
                showDialog(
                  context: context,
                  barrierDismissible: false,
                  builder: (ctx) => PopScope(
                    canPop: false,
                    child: AlertDialog(
                      content: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: const [
                          CircularProgressIndicator(),
                          SizedBox(width: 16),
                          Text('会話を分析中...'),
                        ],
                      ),
                    ),
                  ),
                );

                try {
                  final end = await ref
                      .read(sessionControllerProvider.notifier)
                      .endCurrentSession();
                  if (!mounted || !context.mounted) return;

                  // ローディングダイアログを閉じる
                  Navigator.of(context).pop();

                  context.go('/summary', extra: end);
                } catch (e) {
                  if (!mounted || !context.mounted) return;

                  // ローディングダイアログを閉じる
                  Navigator.of(context).pop();

                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('セッション終了処理に失敗しました: $e'),
                    ),
                  );
                } finally {
                  _navigatingToSummary = false;
                }
              } else if (res == _EndDialogAction.extend) {
                // +3ラウンド延長
                try {
                  await ref
                      .read(sessionControllerProvider.notifier)
                      .extendCurrentSession();
                } catch (e) {
                  if (!mounted || !context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('延長に失敗しました: $e')),
                  );
                } finally {
                  // 再表示ループを防ぐ
                  ref.read(sessionControllerProvider.notifier).dismissEndPrompt();
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
              // カスタムシナリオの場合はタスクチェックリストを表示しない
              if (!data.isCustomScenario &&
                  (data.goalsTotal != null || data.goalsStatus != null))
                SessionTaskChecklistCard(
                  scenarioId: data.scenario?.id ?? 0,
                  scenarioName: data.scenarioName,
                  goalsStatus: data.goalsStatus,
                  goalsTotal: data.goalsTotal,
                  goalsAchieved: data.goalsAchieved,
                  goalsLabels: data.goalsLabels,
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

                    final roundIndex = m.roundIndex;
                    final hasImproved = m.improvedSentence != null &&
                        m.improvedSentence!.trim().isNotEmpty;
                    final canSave = roundIndex != null && hasImproved;
                    final isSaved = roundIndex != null &&
                        _savedRoundIndexes.contains(roundIndex);
                    final isSaving = roundIndex != null &&
                        _savingRoundIndex == roundIndex;

                    return Align(
                      alignment: Alignment.centerLeft,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: AiTurnMessageCard(
                          message: m.text,
                          feedbackShort: m.feedbackShort,
                          improvedSentence: m.improvedSentence,
                          onSavePhrase: canSave
                              ? () => _savePhrase(
                                    sessionId: data.sessionId,
                                    roundIndex: roundIndex,
                                    phrase: m.improvedSentence!,
                                    explanation: m.feedbackShort ?? '',
                                    originalInput: m.userInputForRound ?? '',
                                  )
                              : null,
                          isSaved: isSaved,
                          isSaving: isSaving,
                        ),
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: SafeArea(
                  top: false,
                  child: Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            // Keep it a red "record" button, like speaking question UI.
                            color: audio.isRecording
                                ? Colors.red
                                : Colors.redAccent,
                          ),
                          child: IconButton(
                            onPressed:
                                (audio.isTranscribing || data.isLoadingTurn)
                                    ? null
                                    : () async {
                                        final notifier = ref.read(
                                          audioControllerProvider.notifier,
                                        );
                                        try {
                                          if (audio.isRecording) {
                                            final text = await notifier
                                                .stopAndTranscribe();
                                            if (!context.mounted) return;
                                            await _handleTranscriptionAndSend(
                                              text: text ?? '',
                                              isLoadingTurn: data.isLoadingTurn,
                                            );
                                          } else {
                                            await notifier.startRecording();
                                          }
                                        } catch (e) {
                                          if (!context.mounted) return;
                                          ScaffoldMessenger.of(context)
                                              .showSnackBar(
                                            SnackBar(
                                              content: Text(
                                                'マイク操作に失敗しました: $e',
                                              ),
                                            ),
                                          );
                                        }
                                      },
                            icon: (audio.isTranscribing || data.isLoadingTurn)
                                ? const SizedBox(
                                    width: 28,
                                    height: 28,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 3,
                                      color: Colors.white,
                                    ),
                                  )
                                : Icon(
                                    audio.isRecording ? Icons.stop : Icons.mic,
                                    size: 40,
                                    color: Colors.white,
                                  ),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          audio.isTranscribing
                              ? '認識中...'
                              : audio.isRecording
                                  ? '録音中…タップで停止'
                                  : (data.isLoadingTurn
                                      ? '応答生成中…'
                                      : 'マイクをタップして話してください'),
                          style: const TextStyle(fontSize: 14),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

enum _TranscriptionAction { send, retry, cancel }

enum _EndDialogAction { end, extend, continueSession }



