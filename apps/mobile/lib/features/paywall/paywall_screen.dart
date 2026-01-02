import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:purchases_ui_flutter/purchases_ui_flutter.dart';

import '../../shared/services/revenuecat/revenuecat_client.dart';

class PaywallScreen extends StatefulWidget {
  const PaywallScreen({super.key});

  @override
  State<PaywallScreen> createState() => _PaywallScreenState();
}

class _PaywallScreenState extends State<PaywallScreen> {
  final _revenueCat = RevenueCatClient();
  bool _isRestoring = false;

  Future<void> _restorePurchases() async {
    if (_isRestoring) return;
    setState(() => _isRestoring = true);

    try {
      final info = await _revenueCat.restorePurchases();
      final hasPro = _revenueCat.hasPro(info);

      if (!mounted) return;

      if (hasPro) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('購入を復元しました')),
        );
        if (context.canPop()) {
          context.pop();
        } else {
          context.go('/');
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('復元できる購入が見つかりませんでした')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('購入の復元に失敗しました: $e')),
      );
    } finally {
      if (mounted) setState(() => _isRestoring = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Proにアップグレード'),
        actions: [
          TextButton(
            onPressed: _isRestoring ? null : _restorePurchases,
            child: _isRestoring
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('復元'),
          ),
        ],
      ),
      body: PaywallView(
        onDismiss: () {
          if (context.canPop()) {
            context.pop();
          } else {
            context.go('/');
          }
        },
      ),
    );
  }
}


