import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import '../../../config/app_config.dart';

Future<void> initializeRevenueCat() async {
  await Purchases.setLogLevel(kDebugMode ? LogLevel.verbose : LogLevel.info);

  final String apiKey;
  if (Platform.isIOS) {
    apiKey = AppConfig.revenueCatIosApiKey;
  } else if (Platform.isAndroid) {
    apiKey = AppConfig.revenueCatAndroidApiKey;
  } else {
    debugPrint('RevenueCat: platform not supported, skipping init');
    return;
  }

  if (apiKey.trim().isEmpty) {
    debugPrint(
      'RevenueCat API key is missing. '
      'Set REVENUECAT_IOS_API_KEY / REVENUECAT_ANDROID_API_KEY via dart_defines.json or --dart-define.',
    );
    return;
  }

  await Purchases.configure(PurchasesConfiguration(apiKey));
}


