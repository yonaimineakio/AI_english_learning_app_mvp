import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Bottom navigation tab index for `MainShellScreen`.
///
/// 0: Home (ScenarioSelection)
/// 1: Review
/// 2: Profile
final mainTabIndexProvider = StateProvider<int>((ref) => 0);


