import 'package:flutter/foundation.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import '../../../config/app_config.dart';

class RevenueCatClient {
  const RevenueCatClient();

  bool hasPro(CustomerInfo info) {
    final entitlementId = AppConfig.revenueCatEntitlementId.trim();
    if (entitlementId.isEmpty) return false;
    return info.entitlements.active.containsKey(entitlementId);
  }

  Future<CustomerInfo> restorePurchases() async {
    return await Purchases.restorePurchases();
  }

  /// RevenueCat にユーザーIDを紐付ける
  Future<void> loginUser(String appUserId) async {
    try {
      await Purchases.logIn(appUserId);
    } catch (e) {
      // サイレント失敗: ログのみ
      debugPrint('RevenueCat logIn failed: $e');
    }
  }

  /// RevenueCat から匿名ユーザーに戻す
  Future<void> logoutUser() async {
    try {
      await Purchases.logOut();
    } catch (e) {
      debugPrint('RevenueCat logOut failed: $e');
    }
  }
}


