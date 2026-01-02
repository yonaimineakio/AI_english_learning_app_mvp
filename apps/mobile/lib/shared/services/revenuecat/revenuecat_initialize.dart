import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import '../../../config/app_config.dart';

Future<void> initializeRevenueCat() async {
  if (kDebugMode) {
    await Purchases.setLogLevel(LogLevel.debug);
  }

  final String apiKey;
  if (Platform.isIOS) {
    apiKey = AppConfig.revenueCatIosApiKey;
  } else if (Platform.isAndroid) {
    apiKey = AppConfig.revenueCatAndroidApiKey;
  } else {
    throw UnsupportedError('RevenueCat: platform not supported');
  }

  if (apiKey.trim().isEmpty) {
    throw StateError(
      'RevenueCat API key is missing. '
      'Set REVENUECAT_IOS_API_KEY / REVENUECAT_ANDROID_API_KEY via dart_defines.json or --dart-define.',
    );
  }

  await Purchases.configure(PurchasesConfiguration(apiKey));
}


