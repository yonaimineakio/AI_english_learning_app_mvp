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
}


