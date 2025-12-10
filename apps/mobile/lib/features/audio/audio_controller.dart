import 'dart:io';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';

import '../../shared/services/api_client.dart';
import '../../shared/services/audio_api.dart';

class AudioState {
  const AudioState({
    this.isRecording = false,
    this.isPlaying = false,
    this.isTranscribing = false,
  });

  final bool isRecording;
  final bool isPlaying;
  final bool isTranscribing;

  AudioState copyWith({
    bool? isRecording,
    bool? isPlaying,
    bool? isTranscribing,
  }) {
    return AudioState(
      isRecording: isRecording ?? this.isRecording,
      isPlaying: isPlaying ?? this.isPlaying,
      isTranscribing: isTranscribing ?? this.isTranscribing,
    );
  }
}

class AudioController extends Notifier<AudioState> {
  late final AudioApi _api;
  late final AudioRecorder _recorder;
  late final AudioPlayer _player;
  String? _currentFilePath;
  String? _currentTtsPath;

  @override
  AudioState build() {
    _api = AudioApi(ApiClient());
    _recorder = AudioRecorder();
    _player = AudioPlayer();
    ref.onDispose(() {
      _recorder.dispose();
      _player.dispose();
    });
    return const AudioState();
  }

  Future<void> startRecording() async {
    if (state.isRecording) return;

    final hasPermission = await _recorder.hasPermission();
    if (!hasPermission) {
      throw Exception('マイク録音へのアクセスが許可されていません。設定で権限を許可してください。');
    }

    final dir = await getTemporaryDirectory();
    final filePath =
        '${dir.path}/speech_${DateTime.now().millisecondsSinceEpoch}.wav';
    _currentFilePath = filePath;

    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: 16000,
        numChannels: 1,
      ),
      path: filePath,
    );
    state = state.copyWith(isRecording: true);
  }

  Future<String?> stopAndTranscribe() async {
    if (!state.isRecording) return null;

    final recordedPath = await _recorder.stop();
    final path = recordedPath ?? _currentFilePath;
    _currentFilePath = null;
    state = state.copyWith(isRecording: false, isTranscribing: true);

    try {
      if (path == null) return null;
      final file = File(path);
      if (!await file.exists()) return null;

      final bytes = await file.readAsBytes();
      if (bytes.lengthInBytes < 1024) {
        throw Exception('録音が短すぎて認識できませんでした。1秒以上録音してください。');
      }
      final filename = file.uri.pathSegments.isNotEmpty
          ? file.uri.pathSegments.last
          : 'speech.wav';

      final response = await _api.transcribe(
        bytes: bytes,
        filename: filename,
        language: 'en-US',
      );

      return response['text'] as String?;
    } finally {
      state = state.copyWith(isTranscribing: false);
      await _deleteTempFile(path);
    }
  }

  Future<void> _deleteTempFile(String? path) async {
    if (path == null) return;
    final file = File(path);
    if (!await file.exists()) return;
    try {
      await file.delete();
    } catch (_) {
      // ignore cleanup errors
    }
  }

  Future<void> playTts(String text, {String? profile}) async {
    if (text.trim().isEmpty) return;

    // 既存の再生を止める
    await _player.stop();

    state = state.copyWith(isPlaying: true);
    try {
      // バックエンドからMP3バイト列を取得
      final bytes = await _api.tts(
        text: text,
        voiceProfile: profile,
      );
      if (bytes.isEmpty) {
        throw Exception('TTS音声の取得に失敗しました。');
      }

      // 一時ファイルに保存
      final dir = await getTemporaryDirectory();
      final filePath =
          '${dir.path}/tts_${DateTime.now().millisecondsSinceEpoch}.mp3';
      final file = File(filePath);
      await file.writeAsBytes(bytes, flush: true);

      _currentTtsPath = filePath;

      // 再生
      await _player.play(DeviceFileSource(filePath));
    } finally {
      state = state.copyWith(isPlaying: false);

      // TTS一時ファイルはベストエフォートで削除
      final path = _currentTtsPath;
      _currentTtsPath = null;
      if (path != null) {
        final file = File(path);
        if (await file.exists()) {
          try {
            await file.delete();
          } catch (_) {
            // ignore
          }
        }
      }
    }
  }
}

final audioControllerProvider =
    NotifierProvider<AudioController, AudioState>(AudioController.new);


