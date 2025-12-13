class UserModel {
  const UserModel({
    required this.id,
    required this.sub,
    required this.name,
    required this.email,
    required this.createdAt,
    this.updatedAt,
    this.placementLevel,
    this.placementScore,
    this.placementCompletedAt,
    this.currentStreak,
    this.longestStreak,
    this.lastActivityDate,
  });

  final int id;
  final String sub;
  final String name;
  final String email;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final String? placementLevel; // beginner | intermediate | advanced
  final int? placementScore;
  final DateTime? placementCompletedAt;
  final int? currentStreak;
  final int? longestStreak;
  final DateTime? lastActivityDate;

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      sub: json['sub'] as String,
      name: json['name'] as String,
      email: json['email'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
      placementLevel: json['placement_level'] as String?,
      placementScore: json['placement_score'] as int?,
      placementCompletedAt: json['placement_completed_at'] != null
          ? DateTime.parse(json['placement_completed_at'] as String)
          : null,
      currentStreak: json['current_streak'] as int?,
      longestStreak: json['longest_streak'] as int?,
      lastActivityDate: json['last_activity_date'] != null
          ? DateTime.parse(json['last_activity_date'] as String)
          : null,
    );
  }
}

class UserStatsModel {
  const UserStatsModel({
    required this.currentStreak,
    required this.longestStreak,
    required this.totalSessions,
    required this.totalRounds,
    this.lastActivityDate,
  });

  final int currentStreak;
  final int longestStreak;
  final DateTime? lastActivityDate;
  final int totalSessions;
  final int totalRounds;

  factory UserStatsModel.fromJson(Map<String, dynamic> json) {
    return UserStatsModel(
      currentStreak: json['current_streak'] as int,
      longestStreak: json['longest_streak'] as int,
      lastActivityDate: json['last_activity_date'] != null
          ? DateTime.parse(json['last_activity_date'] as String)
          : null,
      totalSessions: json['total_sessions'] as int,
      totalRounds: json['total_rounds'] as int,
    );
  }
}


