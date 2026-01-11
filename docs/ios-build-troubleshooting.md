## iOSビルド/実機起動トラブルシューティング（今日の対応まとめ）

### 対象
- Flutter iOS（`apps/mobile`）
- Xcode + CocoaPods
- 物理iPhone実機（iOS 26.x含む）

---

## 今日の取り組み内容（何が起きて、何を直したか）

### 1) Info.plist関連のビルドエラー（Local Network / Bonjour）
- **症状**: Xcodeのビルドログで `Info.plist: Could not extract value ... NSBonjourServices / NSLocalNetworkUsageDescription`
- **原因**: iOSのローカルネットワーク利用に必要なInfo.plistキーが不足
- **対応**: `apps/mobile/ios/Runner/Info.plist` に以下を追加
  - `NSLocalNetworkUsageDescription`
  - `NSBonjourServices`（例: `_http._tcp`）

### 2) 実機転送で `No space left on device`
- **症状**: `rsync ... write: No space left on device`
- **原因**: ほぼ **iPhone側の空き容量不足**（加えてMacも容量逼迫だと悪化）
- **対応**:
  - iPhoneの空き容量を確保（アプリ削除/写真整理など）
  - Macの空き容量も確保（最低でも数GB、できれば10GB以上）

### 3) `Framework 'Pods_Runner' not found` / `Linker command failed`
- **症状**:
  - `ld: framework 'Pods_Runner' not found`
  - `ld: library 'Pods-Runner' not found`
- **原因（複合）**:
  - `Runner.xcodeproj` に **存在しない `Pods_Runner.framework` をリンクする参照**が残っていた
  - `ios/Flutter/Generated.xcconfig` に **`CONFIGURATION_BUILD_DIR` の強制**が入り、
    - Runnerの出力先だけが `apps/mobile/build/ios/iphoneos` へ
    - Pods（`libPods-Runner.a`）はDerivedDataへ
    - **出力先がズレてリンクが解決できない**状態になっていた
  - `Podfile` で `use_frameworks!` が有効になっており、環境によってはCocoaPods統合を壊すことがある
- **対応**:
  - `apps/mobile/ios/Runner.xcodeproj/project.pbxproj` から `Pods_Runner.framework` の手動リンク参照を削除
  - `apps/mobile/ios/Podfile` から `use_frameworks!` を削除してPodsを再生成
  - `apps/mobile/ios/Flutter/Generated.xcconfig` から `CONFIGURATION_BUILD_DIR` を削除（ビルド出力先の強制を解除）
  - `Runner` の `IPHONEOS_DEPLOYMENT_TARGET` を 13.0 に統一（Podsの最小バージョンと整合）

### 4) Xcodeの `Product → Clean Build Folder` が失敗
- **症状**: Cleanで `Could not delete ... build/ios/iphoneos because it was not created by the build system`
- **原因**: `apps/mobile/build/ios/iphoneos` がXcode由来と認識されず、Clean対象として削除できない
- **対応**:
  - `apps/mobile/build/ios/iphoneos` を手動削除してからClean

---

## 再発した時の復旧手順（優先度順）

### 0) まず確認（最短で原因が分かるチェック）
- **空き容量**:

```bash
df -h /Users/yonamineakio
```

- **Podsがあるか**:

```bash
ls -la /Users/yonamineakio/Desktop/AI_english_learning_app_mvp/apps/mobile/ios/Pods >/dev/null && echo "Pods OK"
```

- **Workspaceを開いているか（最重要）**:
  - Xcodeで `Runner.xcworkspace` を開く
  - ナビゲータに `Pods`（`Pods.xcodeproj`）が見えればOK

---

### 1) `Clean Build Folder` が失敗する場合

```bash
rm -rf /Users/yonamineakio/Desktop/AI_english_learning_app_mvp/apps/mobile/build/ios/iphoneos
```

その後、Xcodeで `Product → Clean Build Folder` を再実行。

---

### 2) CocoaPods周り（`Pods_Runner` / linker系）の復旧
#### 2-1) CocoaPodsを作り直す
（UTF-8問題の回避も含める）

```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
cd /Users/yonamineakio/Desktop/AI_english_learning_app_mvp/apps/mobile/ios
rm -rf Pods Podfile.lock
pod install
```

#### 2-2) Flutter側もクリーン

```bash
cd /Users/yonamineakio/Desktop/AI_english_learning_app_mvp/apps/mobile
flutter clean
flutter pub get
```

#### 2-3) Xcodeで実行

```bash
open /Users/yonamineakio/Desktop/AI_english_learning_app_mvp/apps/mobile/ios/Runner.xcworkspace
```

Xcodeで `Product → Clean Build Folder` → `Run (Cmd+R)`

---

### 3) `No space left on device`（実機転送で失敗）
- **iPhoneの空き容量**を最優先で確保（最低でも数百MB、できれば1GB以上）
- 既存のデバッグアプリ（Runner）を削除してから再転送

---

### 4) iOS 26.x（ベータ）での注意点
- iOSベータは **Flutterのデバッグ接続（Dart VM Service）で詰まりやすい**ことがあります。
- まずは **シミュレータで検証**し、実機は安定版iOSで確認するのが安全です。

---

## 参考：今回の“やってはいけない/やるべき”一覧

- **やるべき**
  - `Runner.xcworkspace` を開く
  - CocoaPods実行時はUTF-8（`LANG/LC_ALL`）を設定
  - 容量（Mac/iPhone）を常に余らせる
- **避けたい**
  - `ios/Flutter/Generated.xcconfig` に `CONFIGURATION_BUILD_DIR` を固定（出力先ズレでリンクが壊れる）
  - `Runner.xcodeproj` に `Pods_Runner.framework` を手動追加（存在しない成果物を参照しがち）


