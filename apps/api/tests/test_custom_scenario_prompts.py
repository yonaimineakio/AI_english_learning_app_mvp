"""
カスタムシナリオプロンプトのテスト
"""

import pytest
from app.prompts.common_rules import get_common_conversation_rules
from app.prompts.custom_scenario import (
    get_custom_scenario_prompt,
    get_custom_scenario_initial_message,
    get_custom_scenario_goals,
)
from app.prompts.conversation_system import get_conversation_system_prompt


class TestCommonConversationRules:
    """共通会話ルールのテスト"""

    def test_contains_difficulty(self):
        """難易度が含まれることを確認"""
        result = get_common_conversation_rules("intermediate", "Hello")
        assert "intermediate" in result

    def test_contains_user_input(self):
        """ユーザー入力が含まれることを確認"""
        user_input = "I would like to order a coffee"
        result = get_common_conversation_rules("beginner", user_input)
        assert user_input in result

    def test_contains_end_session_marker(self):
        """終了マーカーの説明が含まれることを確認"""
        result = get_common_conversation_rules("intermediate", "test")
        assert "[END_SESSION]" in result

    def test_contains_termination_rules(self):
        """終了判定ルールが含まれることを確認"""
        result = get_common_conversation_rules("intermediate", "test")
        assert "会話終了判定ルール" in result
        assert "Goodbye" in result
        assert "Bye" in result
        assert "That's all" in result

    def test_contains_non_termination_examples(self):
        """終了とみなさない例が含まれることを確認"""
        result = get_common_conversation_rules("intermediate", "test")
        assert "終了とみなさない例" in result
        assert "Thanks for the information" in result

    def test_contains_output_format(self):
        """出力フォーマットが含まれることを確認"""
        result = get_common_conversation_rules("intermediate", "test")
        assert "AI:" in result
        assert "Feedback:" in result
        assert "Improved:" in result


class TestCustomScenarioPrompt:
    """カスタムシナリオプロンプトのテスト"""

    def test_contains_scenario_name(self):
        """シナリオ名が含まれることを確認"""
        result = get_custom_scenario_prompt(
            user_role="客",
            ai_role="店員",
            description="カフェでの注文",
            scenario_name="カフェ注文シナリオ",
        )
        assert "カフェ注文シナリオ" in result

    def test_contains_user_role(self):
        """ユーザーの役割が含まれることを確認"""
        result = get_custom_scenario_prompt(
            user_role="旅行者",
            ai_role="ホテルスタッフ",
            description="ホテルチェックイン",
        )
        assert "旅行者" in result

    def test_contains_ai_role(self):
        """AIの役割が含まれることを確認"""
        result = get_custom_scenario_prompt(
            user_role="旅行者",
            ai_role="ホテルスタッフ",
            description="ホテルチェックイン",
        )
        assert "ホテルスタッフ" in result

    def test_contains_description(self):
        """シナリオの説明が含まれることを確認"""
        result = get_custom_scenario_prompt(
            user_role="客",
            ai_role="店員",
            description="高級レストランでのディナー予約",
        )
        assert "高級レストランでのディナー予約" in result

    def test_difficulty_is_intermediate(self):
        """難易度がintermediateであることを確認"""
        result = get_custom_scenario_prompt(
            user_role="客",
            ai_role="店員",
            description="テスト",
        )
        assert "中級" in result or "intermediate" in result

    def test_does_not_contain_always_question(self):
        """常に疑問形を含めるという矛盾した指示がないことを確認"""
        result = get_custom_scenario_prompt(
            user_role="客",
            ai_role="店員",
            description="テスト",
        )
        # 矛盾する指示が削除されていることを確認
        assert "必ず疑問形を含めて会話を継続" not in result


class TestCustomScenarioInitialMessage:
    """カスタムシナリオ初期メッセージのテスト"""

    def test_contains_ai_role(self):
        """AIの役割が含まれることを確認"""
        result = get_custom_scenario_initial_message(
            ai_role="カフェの店員",
            description="コーヒーを注文する場面",
        )
        assert "カフェの店員" in result

    def test_contains_description(self):
        """シナリオの説明が含まれることを確認"""
        result = get_custom_scenario_initial_message(
            ai_role="店員",
            description="空港のチェックインカウンター",
        )
        assert "空港のチェックインカウンター" in result

    def test_is_in_english(self):
        """英語で記述されていることを確認"""
        result = get_custom_scenario_initial_message(
            ai_role="staff",
            description="coffee shop",
        )
        assert "Hello" in result
        assert "How can I help" in result


class TestCustomScenarioGoals:
    """カスタムシナリオゴールのテスト"""

    def test_returns_list(self):
        """リストが返されることを確認"""
        result = get_custom_scenario_goals()
        assert isinstance(result, list)

    def test_has_goals(self):
        """ゴールが設定されていることを確認"""
        result = get_custom_scenario_goals()
        assert len(result) > 0

    def test_returns_copy(self):
        """コピーが返されることを確認（元のリストを変更しない）"""
        result1 = get_custom_scenario_goals()
        result1.append("新しいゴール")
        result2 = get_custom_scenario_goals()
        assert "新しいゴール" not in result2


class TestConversationSystemPrompt:
    """会話システムプロンプトのテスト"""

    def test_contains_common_rules(self):
        """共通ルールが含まれることを確認"""
        result = get_conversation_system_prompt("intermediate", "test input")
        assert "[END_SESSION]" in result
        assert "会話終了判定ルール" in result

    def test_has_ai_intro(self):
        """AI紹介文が含まれることを確認"""
        result = get_conversation_system_prompt("beginner", "hello")
        assert "英会話学習用AI" in result

    def test_difficulty_in_output(self):
        """難易度が出力に含まれることを確認"""
        result = get_conversation_system_prompt("advanced", "test")
        assert "advanced" in result
