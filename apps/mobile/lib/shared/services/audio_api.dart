import 'dart:typed_data';

import 'package:dio/dio.dart';

import 'api_client.dart';

class AudioApi {
  AudioApi(this._client);

  final ApiClient _client;

  /// Upload an audio file for transcription.
  ///
  /// Returns the raw JSON response from the backend for now.
  Future<Map<String, dynamic>> transcribe({
    required Uint8List bytes,
    required String filename,
    String? language,
  }) async {
    final formData = FormData.fromMap({
      'audio_file': MultipartFile.fromBytes(bytes, filename: filename),
      if (language != null) 'language': language,
    });

    final Response<dynamic> res = await _client.postJson(
      '/audio/transcribe',
      data: formData,
    );

    return Map<String, dynamic>.from(res.data as Map);
  }

  /// Request TTS audio (MP3) for given text.
  Future<Uint8List> tts({
    required String text,
    String? voiceProfile,
  }) async {
    final Response<List<int>> res = await _client.postJson(
      '/audio/tts',
      data: {
        'text': text,
        if (voiceProfile != null) 'voice_profile': voiceProfile,
      },
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(res.data ?? []);
  }
}


