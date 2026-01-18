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
      debugPrint('RevenueCat: Attempting logIn with appUserId=$appUserId');
      final result = await Purchases.logIn(appUserId);
      debugPrint('RevenueCat: logIn success, customerInfo.originalAppUserId=${result.customerInfo.originalAppUserId}');
    } catch (e, stackTrace) {
      // エラーを詳細にログ出力
      debugPrint('RevenueCat logIn failed: $e');
      debugPrint('RevenueCat logIn stackTrace: $stackTrace');
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


