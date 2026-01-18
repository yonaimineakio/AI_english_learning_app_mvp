import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import '../../config/app_config.dart';
import '../../shared/services/revenuecat/revenuecat_client.dart';

final revenueCatClientProvider =
    Provider<RevenueCatClient>((_) => const RevenueCatClient());

class ProStatusNotifier extends AsyncNotifier<bool> {
  Future<bool> _load({bool invalidateCache = false}) async {
    // キャッシュをクリアして最新の情報を取得
    if (invalidateCache) {
      await Purchases.invalidateCustomerInfoCache();
    }
    
    final info = await Purchases.getCustomerInfo();
    final client = ref.read(revenueCatClientProvider);
    
    // デバッグ: RevenueCatの状態を詳細にログ出力
    final currentAppUserId = await Purchases.appUserID;
    debugPrint('=== ProStatusProvider Debug ===');
    debugPrint('Current AppUserId: $currentAppUserId');
    debugPrint('Original AppUserId: ${info.originalAppUserId}');
    debugPrint('Expected EntitlementId: ${AppConfig.revenueCatEntitlementId}');
    debugPrint('Active Entitlements: ${info.entitlements.active.keys.toList()}');
    debugPrint('All Entitlements: ${info.entitlements.all.keys.toList()}');
    
    final hasPro = client.hasPro(info);
    debugPrint('hasPro result: $hasPro');
    debugPrint('===============================');
    
    return hasPro;
  }

  @override
  Future<bool> build() async {
    return _load();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    // refresh時はキャッシュをクリアして最新情報を取得
    state = AsyncData(await _load(invalidateCache: true));
  }
}

final proStatusProvider =
    AsyncNotifierProvider<ProStatusNotifier, bool>(ProStatusNotifier.new);


