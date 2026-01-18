#!/bin/bash
set -euo pipefail

# Xcode Cloud: ensure Flutter + CocoaPods deps exist before xcodebuild.
# Fixes errors like:
# - could not find included file 'Pods/...Pods-Runner.release.xcconfig'
# - could not find included file 'Generated.xcconfig'
# - Unable to load contents of file list: '/Target Support Files/Pods-Runner/...xcfilelist'

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

REPO_ROOT="${CI_PRIMARY_REPOSITORY_PATH:-$(pwd)}"
cd "$REPO_ROOT"

MOBILE_DIR="$REPO_ROOT/apps/mobile"
IOS_DIR="$MOBILE_DIR/ios"

if [ ! -d "$IOS_DIR" ]; then
  echo "Expected iOS directory not found: $IOS_DIR" >&2
  exit 1
fi

# Read Flutter version from .flutter-version file.
FLUTTER_VERSION_FILE="$MOBILE_DIR/.flutter-version"
if [ ! -f "$FLUTTER_VERSION_FILE" ]; then
  echo "Flutter version file not found: $FLUTTER_VERSION_FILE" >&2
  exit 1
fi

FLUTTER_VERSION="$(cat "$FLUTTER_VERSION_FILE" | tr -d '[:space:]')"

if [ -z "$FLUTTER_VERSION" ]; then
  echo "Failed to read Flutter version from $FLUTTER_VERSION_FILE" >&2
  exit 1
fi

echo "Using Flutter version: $FLUTTER_VERSION"

FLUTTER_DIR="$REPO_ROOT/.flutter"

# Clone Flutter SDK using tag (--branch works with tags).
# This ensures Flutter can detect its version correctly via git describe.
if [ ! -d "$FLUTTER_DIR/.git" ]; then
  rm -rf "$FLUTTER_DIR"
  echo "Cloning Flutter SDK (tag: $FLUTTER_VERSION)..."
  git clone --branch "$FLUTTER_VERSION" --depth 1 https://github.com/flutter/flutter.git "$FLUTTER_DIR"
else
  # If already cloned, fetch and checkout the correct tag.
  echo "Flutter SDK directory exists, checking out tag: $FLUTTER_VERSION..."
  cd "$FLUTTER_DIR"
  git fetch --depth 1 origin "refs/tags/$FLUTTER_VERSION:refs/tags/$FLUTTER_VERSION" || true
  git checkout --force "$FLUTTER_VERSION"
  cd "$REPO_ROOT"
fi

export PATH="$FLUTTER_DIR/bin:$PATH"

echo "Flutter version:"
flutter --version

cd "$MOBILE_DIR"
echo "Running flutter pub get..."
flutter pub get

# Precache iOS artifacts (Flutter.xcframework is required by Podfile post_install hook).
echo "Running flutter precache --ios..."
flutter precache --ios

# Ensure iOS Pods exist (Podfile requires Flutter/Generated.xcconfig from flutter pub get).
cd "$IOS_DIR"
if ! command -v pod >/dev/null 2>&1; then
  echo "CocoaPods (pod) is not available in this environment." >&2
  exit 1
fi

echo "Running pod install..."
pod install

echo "ci_post_clone.sh completed successfully."
