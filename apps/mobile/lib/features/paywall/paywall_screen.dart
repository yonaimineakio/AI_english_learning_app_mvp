import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import '../../shared/services/revenuecat/revenuecat_client.dart';

enum BillingPlan {
  monthly,
  yearly,
}

class _FeatureItem {
  const _FeatureItem(this.title, this.description);

  final String title;
  final String description;
}

const _monthlyFallbackPrice = 1580;
const _yearlyFallbackPrice = 15800;

const _features = [
  _FeatureItem('無制限のAI英会話', '時間を気にせず好きなだけ話せます'),
  _FeatureItem('高度なリアルタイム添削', '文法・発音を即座に分析'),
  _FeatureItem('会話に基づく復習問題', '苦手箇所を重点的に克服'),
  _FeatureItem('レベル診断とシナリオ最適化', 'あなたに最適な難易度を提供'),
  _FeatureItem('フレーズ保存・復習', '気になった表現をすぐ保存'),
  _FeatureItem('全シナリオ解放', '50以上の実践的シチュエーション'),
];

class PaywallScreen extends StatefulWidget {
  const PaywallScreen({super.key});

  @override
  State<PaywallScreen> createState() => _PaywallScreenState();
}

class _PaywallScreenState extends State<PaywallScreen> {
  final _revenueCat = RevenueCatClient();
  bool _isRestoring = false;
  bool _isLoading = true;
  bool _isPurchasing = false;
  String? _loadError;
  BillingPlan _selectedPlan = BillingPlan.monthly;
  Package? _monthlyPackage;
  Package? _yearlyPackage;

  @override
  void initState() {
    super.initState();
    _loadOfferings();
  }

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

  Future<void> _loadOfferings() async {
    setState(() {
      _isLoading = true;
      _loadError = null;
    });

    try {
      final offerings = await Purchases.getOfferings();
      final current = offerings.current;
      if (current == null) {
        throw StateError('現在のオファリングが見つかりませんでした');
      }

      _monthlyPackage = _findPackage(current, PackageType.monthly);
      _yearlyPackage = _findPackage(current, PackageType.annual);

      if (_monthlyPackage == null && _yearlyPackage == null) {
        throw StateError('購入可能なプランが見つかりませんでした');
      }

      if (_selectedPlan == BillingPlan.monthly && _monthlyPackage == null) {
        _selectedPlan = BillingPlan.yearly;
      } else if (_selectedPlan == BillingPlan.yearly && _yearlyPackage == null) {
        _selectedPlan = BillingPlan.monthly;
      }
    } catch (e) {
      _loadError = e.toString();
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Package? _findPackage(Offering offering, PackageType type) {
    for (final package in offering.availablePackages) {
      if (package.packageType == type) {
        return package;
      }
    }
    return null;
  }

  Package? get _selectedPackage {
    return _selectedPlan == BillingPlan.monthly
        ? _monthlyPackage
        : _yearlyPackage;
  }

  Future<void> _purchaseSelected() async {
    if (_isPurchasing) return;
    final package = _selectedPackage;
    if (package == null) return;

    setState(() => _isPurchasing = true);
    try {
      final result = await Purchases.purchasePackage(package);
      final hasPro = _revenueCat.hasPro(result.customerInfo);
      if (!mounted) return;
      if (hasPro) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Proプランにアップグレードしました')),
        );
        if (context.canPop()) {
          context.pop();
        } else {
          context.go('/');
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('購入は完了しましたがProが確認できませんでした')),
        );
      }
    } on PlatformException catch (e) {
      if (!mounted) return;
      final code = PurchasesErrorHelper.getErrorCode(e);
      if (code != PurchasesErrorCode.purchaseCancelledError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('購入に失敗しました: ${e.message ?? e.code}')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('購入に失敗しました: $e')),
      );
    } finally {
      if (mounted) setState(() => _isPurchasing = false);
    }
  }

  String _formatYen(int amount) {
    final buffer = StringBuffer();
    final digits = amount.toString();
    for (var i = 0; i < digits.length; i++) {
      final positionFromEnd = digits.length - i;
      buffer.write(digits[i]);
      if (positionFromEnd > 1 && positionFromEnd % 3 == 1) {
        buffer.write(',');
      }
    }
    return buffer.toString();
  }

  String _priceText(Package? package, int fallback) {
    if (package == null) {
      return '¥${_formatYen(fallback)}';
    }
    return package.storeProduct.priceString;
  }

  double _priceValue(Package? package, int fallback) {
    if (package == null) return fallback.toDouble();
    return package.storeProduct.price;
  }

  Widget _buildPlanCard({
    required BillingPlan plan,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color accent,
    required String priceText,
    required String unitText,
    required String footnote,
    String? topBadge,
    String? cornerBadge,
  }) {
    final isSelected = _selectedPlan == plan;
    final isAvailable = plan == BillingPlan.monthly
        ? _monthlyPackage != null
        : _yearlyPackage != null;

    return Opacity(
      opacity: isAvailable ? 1 : 0.55,
      child: GestureDetector(
        onTap: isAvailable ? () => setState(() => _selectedPlan = plan) : null,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: isSelected ? accent.withValues(alpha: 0.08) : Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isSelected ? accent : const Color(0xFFE2E8F0),
              width: 2,
            ),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: accent.withValues(alpha: 0.18),
                      blurRadius: 16,
                      offset: const Offset(0, 6),
                    ),
                  ]
                : const [
                    BoxShadow(
                      color: Color(0x0F0F172A),
                      blurRadius: 12,
                      offset: Offset(0, 6),
                    ),
                  ],
          ),
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              if (topBadge != null)
                Positioned(
                  top: -26,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: accent,
                        borderRadius: BorderRadius.circular(999),
                        boxShadow: [
                          BoxShadow(
                            color: accent.withValues(alpha: 0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Text(
                        topBadge,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ),
              if (cornerBadge != null)
                Positioned(
                  top: -4,
                  right: -4,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE0F2FE),
                      borderRadius: const BorderRadius.only(
                        topRight: Radius.circular(16),
                        bottomLeft: Radius.circular(16),
                      ),
                    ),
                    child: Text(
                      cornerBadge,
                      style: const TextStyle(
                        color: Color(0xFF0F766E),
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? accent.withValues(alpha: 0.12)
                              : const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(icon, color: accent, size: 24),
                      ),
                      if (isSelected)
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: accent.withValues(alpha: 0.12),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.check, color: accent, size: 18),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 13,
                      color: Color(0xFF64748B),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        priceText,
                        style: const TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        unitText,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Color(0xFF64748B),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    footnote,
                    style: const TextStyle(
                      fontSize: 12,
                      color: Color(0xFF94A3B8),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureTile(_FeatureItem item) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Icon(Icons.check_circle, color: Color(0xFF22C55E), size: 20),
        const SizedBox(width: 10),
        Expanded(
          child: Text.rich(
            TextSpan(
              text: item.title,
              style: const TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 13,
                color: Color(0xFF0F172A),
              ),
              children: [
                TextSpan(
                  text: '\n${item.description}',
                  style: const TextStyle(
                    fontWeight: FontWeight.w500,
                    fontSize: 12,
                    color: Color(0xFF64748B),
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final monthlyPriceText = _priceText(_monthlyPackage, _monthlyFallbackPrice);
    final yearlyPriceText = _priceText(_yearlyPackage, _yearlyFallbackPrice);
    final yearlyMonthlyEquivalent =
        ( _priceValue(_yearlyPackage, _yearlyFallbackPrice) / 12).floor();
    final selectedPriceText = _selectedPlan == BillingPlan.monthly
        ? monthlyPriceText
        : yearlyPriceText;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Proにアップグレード'),
        leading: IconButton(
          icon: const Icon(Icons.close_rounded),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/');
            }
          },
        ),
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
      body: Stack(
        children: [
          Positioned(
            top: -80,
            right: -40,
            child: Container(
              width: 180,
              height: 180,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Color(0x1A2563EB),
              ),
            ),
          ),
          Positioned(
            bottom: 60,
            left: -70,
            child: Container(
              width: 220,
              height: 220,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Color(0x14F97316),
              ),
            ),
          ),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 1000),
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final isWide = constraints.maxWidth >= 900;
                      final twoColumnCards = constraints.maxWidth >= 600;

                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Column(
                            children: [
                              const Text(
                                'Proプランにアップグレード',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  fontSize: 28,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.2,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                '無制限のAI会話と高度なフィードバックを解放しましょう。',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Color(0xFF64748B),
                                ),
                              ),
                              const SizedBox(height: 16),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 16,
                                  vertical: 8,
                                ),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFE0F2FE),
                                  borderRadius: BorderRadius.circular(999),
                                ),
                                child: const Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      Icons.schedule_rounded,
                                      size: 18,
                                      color: Color(0xFF2563EB),
                                    ),
                                    SizedBox(width: 8),
                                    Text(
                                      '最初の7日間は無料でお試しいただけます',
                                      style: TextStyle(
                                        color: Color(0xFF2563EB),
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),
                          if (_loadError != null)
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFEE2E2),
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: const Color(0xFFFECACA)),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'プラン情報の取得に失敗しました',
                                    style: TextStyle(
                                      fontWeight: FontWeight.w700,
                                      color: Color(0xFF991B1B),
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    _loadError ?? '',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: Color(0xFFB91C1C),
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                  OutlinedButton(
                                    onPressed: _loadOfferings,
                                    child: const Text('再読み込み'),
                                  ),
                                ],
                              ),
                            ),
                          if (_loadError != null) const SizedBox(height: 24),
                          if (_isLoading)
                            const LinearProgressIndicator(minHeight: 2),
                          if (_isLoading) const SizedBox(height: 16),
                          if (isWide)
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(
                                  flex: 7,
                                  child: _buildLeftColumn(twoColumnCards,
                                      monthlyPriceText, yearlyPriceText, yearlyMonthlyEquivalent),
                                ),
                                const SizedBox(width: 24),
                                Expanded(
                                  flex: 5,
                                  child: _buildRightColumn(selectedPriceText),
                                ),
                              ],
                            )
                          else
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                _buildLeftColumn(twoColumnCards, monthlyPriceText,
                                    yearlyPriceText, yearlyMonthlyEquivalent),
                                const SizedBox(height: 24),
                                _buildRightColumn(selectedPriceText),
                              ],
                            ),
                        ],
                      );
                    },
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLeftColumn(
    bool twoColumnCards,
    String monthlyPriceText,
    String yearlyPriceText,
    int yearlyMonthlyEquivalent,
  ) {
    final double cardSpacing = twoColumnCards ? 0.0 : 16.0;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (twoColumnCards)
          Row(
            children: [
              Expanded(
                child: _buildPlanCard(
                  plan: BillingPlan.monthly,
                  title: '月額払い',
                  subtitle: 'まずはここからスタート',
                  icon: Icons.star_rounded,
                  accent: const Color(0xFF2563EB),
                  priceText: monthlyPriceText,
                  unitText: '/月',
                  footnote: '月々のお支払い',
                  topBadge: '一番人気',
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildPlanCard(
                  plan: BillingPlan.yearly,
                  title: '年額払い',
                  subtitle: '長期学習コミット',
                  icon: Icons.bolt_rounded,
                  accent: const Color(0xFF7C3AED),
                  priceText: yearlyPriceText,
                  unitText: '/年',
                  footnote: '実質 ¥${_formatYen(yearlyMonthlyEquivalent)}/月',
                  cornerBadge: '2ヶ月分お得',
                ),
              ),
            ],
          )
        else
          Column(
            children: [
              _buildPlanCard(
                plan: BillingPlan.monthly,
                title: '月額払い',
                subtitle: 'まずはここからスタート',
                icon: Icons.star_rounded,
                accent: const Color(0xFF2563EB),
                priceText: monthlyPriceText,
                unitText: '/月',
                footnote: '月々のお支払い',
                topBadge: '一番人気',
              ),
              SizedBox(height: cardSpacing),
              _buildPlanCard(
                plan: BillingPlan.yearly,
                title: '年額払い',
                subtitle: '長期学習コミット',
                icon: Icons.bolt_rounded,
                accent: const Color(0xFF7C3AED),
                priceText: yearlyPriceText,
                unitText: '/年',
                footnote: '実質 ¥${_formatYen(yearlyMonthlyEquivalent)}/月',
                cornerBadge: '2ヶ月分お得',
              ),
            ],
          ),
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.auto_awesome, color: Color(0xFFF59E0B)),
                  SizedBox(width: 8),
                  Text(
                    'Proプランの全機能:',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              GridView.count(
                crossAxisCount: twoColumnCards ? 2 : 1,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                childAspectRatio: twoColumnCards ? 3.4 : 4.2,
                children: _features.map(_buildFeatureTile).toList(),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRightColumn(String selectedPriceText) {
    final selectedLabel = _selectedPlan == BillingPlan.monthly
        ? 'Proプラン (月額)'
        : 'Proプラン (年額)';
    final selectedShort =
        _selectedPlan == BillingPlan.monthly ? '月額プラン' : '年額プラン';

    return Card(
      elevation: 0,
      color: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'お支払い情報',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: Color(0xFF0F172A),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              '$selectedShortの申し込み',
              style: const TextStyle(
                fontSize: 13,
                color: Color(0xFF64748B),
              ),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFDBEAFE),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFBFDBFE)),
              ),
              child: Text(
                'まずは7日間無料でお試し\n'
                'トライアル期間終了後に $selectedPriceText が請求されます。'
                '期間中にキャンセルすれば料金は発生しません。',
                style: const TextStyle(
                  fontSize: 12,
                  color: Color(0xFF1D4ED8),
                  height: 1.5,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'プラン',
                  style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                ),
                Text(
                  selectedLabel,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '料金',
                  style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                ),
                Text(
                  selectedPriceText,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                Text(
                  '本日の請求額',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                ),
                Text(
                  '¥0',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              '7日後に $selectedPriceText (${_selectedPlan == BillingPlan.monthly ? '月額' : '年額'}) が請求されます',
              textAlign: TextAlign.right,
              style: const TextStyle(
                fontSize: 11,
                color: Color(0xFF94A3B8),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _isPurchasing || _selectedPackage == null
                    ? null
                    : _purchaseSelected,
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  backgroundColor: const Color(0xFF2563EB),
                  disabledBackgroundColor: const Color(0xFFCBD5F5),
                ),
                child: _isPurchasing
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text(
                        '7日間の無料トライアルを開始',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                      ),
              ),
            ),
            const SizedBox(height: 12),
            const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.shield_rounded, size: 14, color: Color(0xFF94A3B8)),
                SizedBox(width: 6),
                Text(
                  'お支払いは安全に暗号化されます',
                  style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
