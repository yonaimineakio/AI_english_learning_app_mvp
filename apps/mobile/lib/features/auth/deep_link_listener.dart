import 'dart:async';

import 'package:app_links/app_links.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../router/app_router.dart';

class DeepLinkListener extends ConsumerStatefulWidget {
  const DeepLinkListener({
    super.key,
    required this.child,
  });

  final Widget child;

  @override
  ConsumerState<DeepLinkListener> createState() => _DeepLinkListenerState();
}

class _DeepLinkListenerState extends ConsumerState<DeepLinkListener> {
  late final AppLinks _appLinks;
  StreamSubscription<Uri>? _sub;

  @override
  void initState() {
    super.initState();
    _appLinks = AppLinks();

    // Cold start deep link
    _appLinks.getInitialLink().then((uri) {
      if (uri == null) return;
      _handle(uri);
    });

    // Warm deep links
    _sub = _appLinks.uriLinkStream.listen(
      _handle,
      onError: (err) {
        // ignore: avoid_print
        print('Deep link error: $err');
      },
    );
  }

  void _handle(Uri uri) {
    // We only accept: ai-english-learning://app/callback?code=...
    if (uri.scheme != 'ai-english-learning') return;
    if (uri.host != 'app') return;
    if (uri.path != '/callback') return;

    final code = uri.queryParameters['code'];
    if (code == null || code.trim().isEmpty) return;

    // Avoid navigation while widget tree is building.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final router = ref.read(appRouterProvider);
      router.go(
        Uri(path: '/callback', queryParameters: {'code': code}).toString(),
      );
    });
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.child;
}


