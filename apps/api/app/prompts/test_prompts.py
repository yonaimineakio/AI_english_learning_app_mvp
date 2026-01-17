"""プロンプトシステムのテストファイル

このファイルは、作成したプロンプトシステムが正しく動作するかを確認するためのテストです。
"""

from . import (
    get_prompt_by_scenario_id,
    get_prompt_by_category_difficulty,
    get_prompts_by_category,
    get_prompts_by_difficulty,
    get_all_prompts,
    get_available_combinations,
    SCENARIO_PROMPTS,
    CATEGORY_DIFFICULTY_PROMPTS,
)


def test_scenario_prompts():
    """シナリオIDでプロンプトを取得するテスト"""
    print("=== シナリオIDでプロンプトを取得するテスト ===")

    for scenario_id in range(1, 6):
        prompt = get_prompt_by_scenario_id(scenario_id)
        if prompt:
            print(f"シナリオID {scenario_id}: プロンプト取得成功 ({len(prompt)} 文字)")
        else:
            print(f"シナリオID {scenario_id}: プロンプトが見つかりません")


def test_category_difficulty_prompts():
    """カテゴリと難易度でプロンプトを取得するテスト"""
    print("\n=== カテゴリと難易度でプロンプトを取得するテスト ===")

    test_cases = [
        ("travel", "beginner"),
        ("travel", "intermediate"),
        ("business", "intermediate"),
        ("business", "advanced"),
        ("daily", "beginner"),
        ("travel", "advanced"),  # 存在しない組み合わせ
    ]

    for category, difficulty in test_cases:
        prompt = get_prompt_by_category_difficulty(category, difficulty)
        if prompt:
            print(
                f"({category}, {difficulty}): プロンプト取得成功 ({len(prompt)} 文字)"
            )
        else:
            print(f"({category}, {difficulty}): プロンプトが見つかりません")


def test_category_prompts():
    """カテゴリでプロンプト一覧を取得するテスト"""
    print("\n=== カテゴリでプロンプト一覧を取得するテスト ===")

    categories = ["travel", "business", "daily"]

    for category in categories:
        prompts = get_prompts_by_category(category)
        print(f"{category} カテゴリ: {len(prompts)} 個のプロンプト")
        for difficulty, prompt in prompts.items():
            print(f"  - {difficulty}: {len(prompt)} 文字")


def test_difficulty_prompts():
    """難易度でプロンプト一覧を取得するテスト"""
    print("\n=== 難易度でプロンプト一覧を取得するテスト ===")

    difficulties = ["beginner", "intermediate", "advanced"]

    for difficulty in difficulties:
        prompts = get_prompts_by_difficulty(difficulty)
        print(f"{difficulty} 難易度: {len(prompts)} 個のプロンプト")
        for category, prompt in prompts.items():
            print(f"  - {category}: {len(prompt)} 文字")


def test_available_combinations():
    """利用可能な組み合わせを取得するテスト"""
    print("\n=== 利用可能な組み合わせを取得するテスト ===")

    combinations = get_available_combinations()
    print(f"利用可能な組み合わせ: {len(combinations)} 個")
    for category, difficulty in combinations:
        print(f"  - ({category}, {difficulty})")


def test_all_prompts():
    """全てのプロンプトを取得するテスト"""
    print("\n=== 全てのプロンプトを取得するテスト ===")

    all_prompts = get_all_prompts()
    print(f"総プロンプト数: {len(all_prompts)} 個")

    for scenario_id, prompt in all_prompts.items():
        print(f"シナリオID {scenario_id}: {len(prompt)} 文字")


def main():
    """メイン関数"""
    print("プロンプトシステムのテストを開始します...\n")

    test_scenario_prompts()
    test_category_difficulty_prompts()
    test_category_prompts()
    test_difficulty_prompts()
    test_available_combinations()
    test_all_prompts()

    print("\nプロンプトシステムのテストが完了しました。")


if __name__ == "__main__":
    main()
