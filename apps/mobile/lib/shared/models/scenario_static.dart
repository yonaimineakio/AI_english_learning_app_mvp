class ScenarioSummary {
  const ScenarioSummary({
    required this.id,
    required this.name,
    required this.description,
    required this.category,
    required this.difficulty,
    required this.estimatedMinutes,
  });

  final int id;
  final String name;
  final String description;
  final String category; // travel | business | daily
  final String difficulty; // beginner | intermediate | advanced
  final int estimatedMinutes;

  String get categoryLabel {
    switch (category) {
      case 'travel':
        return '旅行';
      case 'business':
        return 'ビジネス';
      case 'daily':
        return '日常会話';
      default:
        return category;
    }
  }
}

/// Next.js 側の `SCENARIO_LIST` をベースにした静的定義。
const List<ScenarioSummary> kScenarioList = [
  ScenarioSummary(
    id: 1,
    name: '空港チェックイン',
    description: 'チェックインから搭乗までの一連の流れを練習',
    category: 'travel',
    difficulty: 'beginner',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 2,
    name: 'ビジネスミーティング',
    description: '会議での発言や合意形成に必要な表現を学習',
    category: 'business',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 3,
    name: 'レストランでの注文',
    description: '予約から注文、会計までの会話パターンを習得',
    category: 'daily',
    difficulty: 'beginner',
    estimatedMinutes: 12,
  ),
  ScenarioSummary(
    id: 4,
    name: 'オンライン商談',
    description: 'リモートミーティングでの説明や質問に対応',
    category: 'business',
    difficulty: 'advanced',
    estimatedMinutes: 30,
  ),
  ScenarioSummary(
    id: 5,
    name: 'ホテルチェックイン',
    description: '予約確認から要望の伝え方までを網羅',
    category: 'travel',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 6,
    name: '最高のバケーション',
    description: '理想の休暇プランを説明しながら旅行英会話を練習',
    category: 'travel',
    difficulty: 'beginner',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 7,
    name: '日本を案内する',
    description: '海外の友人に日本の観光地や文化を英語で紹介',
    category: 'travel',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 8,
    name: '入国審査・税関で',
    description: '入国審査と税関のやり取りを想定した実践的な会話',
    category: 'travel',
    difficulty: 'advanced',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 9,
    name: '旅行計画を友達と相談',
    description: '友人と旅行計画を立てながら提案・調整の表現を学ぶ',
    category: 'travel',
    difficulty: 'beginner',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 10,
    name: '財布を無くして警察に相談',
    description: 'トラブル時に状況を説明して助けを求める表現を練習',
    category: 'daily',
    difficulty: 'beginner',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 11,
    name: 'カスタマーサービスに相談',
    description: '商品の不具合やトラブルをカスタマーサービスに伝える',
    category: 'daily',
    difficulty: 'beginner',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 12,
    name: 'おしゃれカフェで店員と雑談',
    description: '注文に加えて軽い雑談を交えたカジュアルな会話',
    category: 'daily',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 13,
    name: 'ショーチケットを入手',
    description: 'チケットの種類や席を確認しながら購入する会話',
    category: 'daily',
    difficulty: 'beginner',
    estimatedMinutes: 15,
  ),
  ScenarioSummary(
    id: 14,
    name: '公園で雑談',
    description: '初対面の人と趣味や天気について気軽に話す練習',
    category: 'daily',
    difficulty: 'intermediate',
    estimatedMinutes: 15,
  ),
  ScenarioSummary(
    id: 15,
    name: 'ミーティングをリスケする',
    description: '予定変更の依頼と代替案の提案を丁寧に伝える',
    category: 'business',
    difficulty: 'beginner',
    estimatedMinutes: 15,
  ),
  ScenarioSummary(
    id: 16,
    name: 'ミーティングを立てる',
    description: '関係者に日程候補を提示しながら会議を設定する',
    category: 'business',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 17,
    name: '会議を進行する',
    description: '議題の提示から議論の整理まで会議進行の英語表現',
    category: 'business',
    difficulty: 'advanced',
    estimatedMinutes: 24,
  ),
  ScenarioSummary(
    id: 18,
    name: '契約条件の交渉',
    description: '価格や条件の違いを整理しながら合意点を探る',
    category: 'business',
    difficulty: 'advanced',
    estimatedMinutes: 24,
  ),
  ScenarioSummary(
    id: 19,
    name: '顧客満足度の調査結果をプレゼン',
    description: '調査結果を分かりやすく説明し示唆を伝えるプレゼン',
    category: 'business',
    difficulty: 'advanced',
    estimatedMinutes: 24,
  ),
  ScenarioSummary(
    id: 20,
    name: 'プロジェクトの遅延を謝罪する',
    description: '遅延の理由と今後の対策を誠実に説明する表現を練習',
    category: 'business',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
  ),
  ScenarioSummary(
    id: 21,
    name: '体調不良で休む',
    description: '体調不良を丁寧に伝え、代替対応を相談する会話',
    category: 'business',
    difficulty: 'intermediate',
    estimatedMinutes: 12,
  ),
];

/// Freeプランで解放する固定シナリオ（3つ）
///
/// - travel / business / daily を1つずつにして、体験の偏りを防ぐ
const Set<int> kFreeScenarioIds = {1, 2, 3};


