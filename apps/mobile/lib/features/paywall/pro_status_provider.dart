import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import '../../shared/services/revenuecat/revenuecat_client.dart';

final revenueCatClientProvider =
    Provider<RevenueCatClient>((_) => const RevenueCatClient());

class ProStatusNotifier extends AsyncNotifier<bool> {
  Future<bool> _load() async {
    final info = await Purchases.getCustomerInfo();
    final client = ref.read(revenueCatClientProvider);
    return client.hasPro(info);
  }

  @override
  Future<bool> build() async {
    return _load();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = AsyncData(await _load());
  }
}

final proStatusProvider =
    AsyncNotifierProvider<ProStatusNotifier, bool>(ProStatusNotifier.new);


