import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../audio/audio_controller.dart';
import 'session_controller.dart';

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

    return Scaffold(
      appBar: AppBar(
        title: const Text('会話セッション'),
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (data) {
          // バックエンドから終了判定フラグを受け取ったらサマリ画面へ遷移
          if (data.shouldEndSession && !_navigatingToSummary) {
            _navigatingToSummary = true;
            Future.microtask(() async {
              try {
                final end = await ref
                    .read(sessionControllerProvider.notifier)
                    .endCurrentSession();
                if (!mounted) return;
                if (!context.mounted) return;
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
            });
          }

          return Column(
            children: [
              if (data.goalsTotal != null)
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: Chip(
                    label: Text(
                      '${data.goalsAchieved ?? 0}/${data.goalsTotal} goals',
                    ),
                  ),
                ),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: data.messages.length,
                  itemBuilder: (context, index) {
                    final m = data.messages[index];
                    final align = m.isUser
                        ? Alignment.centerRight
                        : Alignment.centerLeft;
                    final color = m.isUser
                        ? Colors.blue[200]
                        : Colors.grey[300];
                    return Align(
                      alignment: align,
                      child: Container(
                        margin: const EdgeInsets.symmetric(vertical: 4),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: color,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(m.text),
                            if (m.feedbackShort != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                m.feedbackShort!,
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: Colors.black87,
                                ),
                              ),
                            ],
                            if (m.improvedSentence != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                '改善例: ${m.improvedSentence!}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontStyle: FontStyle.italic,
                                ),
                              ),
                            ],
                          ],
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



