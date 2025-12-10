import 'package:flutter/material.dart';

/// アプリ共通のテーマ定義。
///
/// Web版のTailwind設定（primary/secondaryカラー, Interフォント）を参考に、
/// モバイル向けに少しだけトーンを調整している。
class AppTheme {
  AppTheme._();

  static ThemeData light() {
    const primary = Color(0xFF2563EB); // tailwind primary-600
    const secondary = Color(0xFF475569); // tailwind secondary-600

    final colorScheme = ColorScheme.fromSeed(
      seedColor: primary,
      primary: primary,
      secondary: secondary,
      brightness: Brightness.light,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: const Color(0xFFF8FAFC), // secondary-50
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.white,
        foregroundColor: colorScheme.onSurface,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.1,
        ),
      ),
      textTheme: const TextTheme(
        bodyLarge: TextStyle(fontSize: 16, height: 1.5),
        bodyMedium: TextStyle(fontSize: 14, height: 1.5),
        titleMedium: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          textStyle: const TextStyle(
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          textStyle: const TextStyle(
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      cardTheme: const CardThemeData(
        color: Colors.white,
        elevation: 0,
        margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(999),
        ),
        backgroundColor: colorScheme.primary.withValues(alpha: 0.08),
        labelStyle: TextStyle(
          color: colorScheme.primary,
          fontWeight: FontWeight.w600,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(999),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(999),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(999),
          borderSide: BorderSide(color: primary),
        ),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
    );
  }
}


