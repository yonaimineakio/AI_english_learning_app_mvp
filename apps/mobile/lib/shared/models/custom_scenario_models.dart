/// カスタムシナリオ（オリジナルシナリオ）のモデル定義
class CustomScenario {
  final int id;
  final String userId;
  final String name;
  final String description;
  final String userRole;
  final String aiRole;
  final String difficulty;
  final bool isActive;
  final DateTime createdAt;

  CustomScenario({
    required this.id,
    required this.userId,
    required this.name,
    required this.description,
    required this.userRole,
    required this.aiRole,
    required this.difficulty,
    required this.isActive,
    required this.createdAt,
  });

  factory CustomScenario.fromJson(Map<String, dynamic> json) {
    return CustomScenario(
      id: json['id'] as int,
      userId: json['user_id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      userRole: json['user_role'] as String,
      aiRole: json['ai_role'] as String,
      difficulty: json['difficulty'] as String? ?? 'intermediate',
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class CustomScenarioCreate {
  final String name;
  final String description;
  final String userRole;
  final String aiRole;

  CustomScenarioCreate({
    required this.name,
    required this.description,
    required this.userRole,
    required this.aiRole,
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'description': description,
        'user_role': userRole,
        'ai_role': aiRole,
      };
}

class CustomScenarioListResponse {
  final List<CustomScenario> customScenarios;
  final int totalCount;

  CustomScenarioListResponse({
    required this.customScenarios,
    required this.totalCount,
  });

  factory CustomScenarioListResponse.fromJson(Map<String, dynamic> json) {
    final list = (json['custom_scenarios'] as List<dynamic>)
        .map((e) => CustomScenario.fromJson(e as Map<String, dynamic>))
        .toList();
    return CustomScenarioListResponse(
      customScenarios: list,
      totalCount: json['total_count'] as int,
    );
  }
}

class CustomScenarioLimitResponse {
  final int dailyLimit;
  final int createdToday;
  final int remaining;
  final bool isPro;

  CustomScenarioLimitResponse({
    required this.dailyLimit,
    required this.createdToday,
    required this.remaining,
    required this.isPro,
  });

  factory CustomScenarioLimitResponse.fromJson(Map<String, dynamic> json) {
    return CustomScenarioLimitResponse(
      dailyLimit: json['daily_limit'] as int,
      createdToday: json['created_today'] as int,
      remaining: json['remaining'] as int,
      isPro: json['is_pro'] as bool,
    );
  }
}
