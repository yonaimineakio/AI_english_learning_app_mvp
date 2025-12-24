import 'package:dio/dio.dart';

import '../models/review_models.dart';
import 'api_client.dart';

class SavedPhrasesApi {
  SavedPhrasesApi(this._client);

  final ApiClient _client;

  /// 改善文を保存する
  Future<SavedPhraseModel> createSavedPhrase({
    required String phrase,
    required String explanation,
    String? originalInput,
    int? sessionId,
    int? roundIndex,
  }) async {
    final Response<dynamic> res = await _client.postJson(
      '/saved-phrases',
      data: {
        'phrase': phrase,
        'explanation': explanation,
        if (originalInput != null) 'original_input': originalInput,
        if (sessionId != null) 'session_id': sessionId,
        if (roundIndex != null) 'round_index': roundIndex,
      },
    );
    return SavedPhraseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// 保存した表現一覧を取得する
  Future<SavedPhrasesListResponseModel> getSavedPhrases() async {
    final Response<dynamic> res = await _client.getJson('/saved-phrases');
    return SavedPhrasesListResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }

  /// 保存した表現を削除する
  Future<void> deleteSavedPhrase({required int phraseId}) async {
    await _client.deleteJson('/saved-phrases/$phraseId');
  }

  /// 特定のセッションラウンドの改善文が保存済みかチェックする
  Future<SavedPhraseCheckResponseModel> checkSavedPhrase({
    required int sessionId,
    required int roundIndex,
  }) async {
    final Response<dynamic> res = await _client.getJson(
      '/saved-phrases/check/$sessionId/$roundIndex',
    );
    return SavedPhraseCheckResponseModel.fromJson(
      Map<String, dynamic>.from(res.data as Map),
    );
  }
}

