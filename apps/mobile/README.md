# ai_english_learning_mobile

A new Flutter project.

## Backend URL (API_BASE_URL)

This app reads the backend base URL from Dart defines.

- `AppConfig.apiBaseUrl` uses `String.fromEnvironment('API_BASE_URL')`
- Recommended: provide it from an external file with `--dart-define-from-file`

### Example

1) Copy `dart_defines.example.json` to your own file (do NOT commit it), e.g. `dart_defines.dev.json`

2) Run with the defines file:

```bash
flutter run --dart-define-from-file=dart_defines.dev.json
```

For device testing, set it to your Mac's LAN IP (must include `/api/v1`):

```json
{
  "API_BASE_URL": "http://<YOUR_MAC_LAN_IP>:8000/api/v1"
}
```

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
