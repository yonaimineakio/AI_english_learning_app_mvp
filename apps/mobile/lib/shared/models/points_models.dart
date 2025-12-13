class UserPointsModel {
  const UserPointsModel({
    required this.totalPoints,
    required this.pointsThisWeek,
    required this.pointsToday,
  });

  final int totalPoints;
  final int pointsThisWeek;
  final int pointsToday;

  factory UserPointsModel.fromJson(Map<String, dynamic> json) {
    return UserPointsModel(
      totalPoints: json['total_points'] as int,
      pointsThisWeek: json['points_this_week'] as int,
      pointsToday: json['points_today'] as int,
    );
  }
}

class RankingEntryModel {
  const RankingEntryModel({
    required this.rank,
    required this.userId,
    required this.userName,
    required this.totalPoints,
    required this.currentStreak,
  });

  final int rank;
  final int userId;
  final String userName;
  final int totalPoints;
  final int currentStreak;

  factory RankingEntryModel.fromJson(Map<String, dynamic> json) {
    return RankingEntryModel(
      rank: json['rank'] as int,
      userId: json['user_id'] as int,
      userName: json['user_name'] as String,
      totalPoints: json['total_points'] as int,
      currentStreak: json['current_streak'] as int,
    );
  }
}

class RankingsModel {
  const RankingsModel({
    required this.rankings,
    required this.totalUsers,
  });

  final List<RankingEntryModel> rankings;
  final int totalUsers;

  factory RankingsModel.fromJson(Map<String, dynamic> json) {
    return RankingsModel(
      rankings: (json['rankings'] as List<dynamic>)
          .map((e) => RankingEntryModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalUsers: json['total_users'] as int,
    );
  }
}

class MyRankingModel {
  const MyRankingModel({
    required this.rank,
    required this.totalPoints,
    this.pointsToNextRank,
    required this.totalUsers,
  });

  final int rank;
  final int totalPoints;
  final int? pointsToNextRank;
  final int totalUsers;

  factory MyRankingModel.fromJson(Map<String, dynamic> json) {
    return MyRankingModel(
      rank: json['rank'] as int,
      totalPoints: json['total_points'] as int,
      pointsToNextRank: json['points_to_next_rank'] as int?,
      totalUsers: json['total_users'] as int,
    );
  }
}

