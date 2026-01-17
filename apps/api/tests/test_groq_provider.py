"""Groqプロバイダーのテスト"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

from app.services.ai.groq_provider import GroqConversationProvider


class TestParseResponse:
    """_parse_response メソッドのテスト"""

    def setup_method(self):
        """各テスト前にプロバイダーをモック初期化"""
        with patch.object(GroqConversationProvider, "__init__", lambda x: None):
            self.provider = GroqConversationProvider()

    def test_parse_standard_response(self):
        """標準的なレスポンスのパース"""
        content = """AI: Hello! How can I help you today?
Feedback: 良い挨拶です。もう少しカジュアルにしても良いでしょう。
Improved: Hi there! What can I do for you?"""

        ai_reply, feedback, improved, should_end = self.provider._parse_response(
            content
        )

        assert ai_reply == "Hello! How can I help you today?"
        assert feedback == "良い挨拶です。もう少しカジュアルにしても良いでしょう。"
        assert improved == "Hi there! What can I do for you?"
        assert should_end is False

    def test_parse_response_with_end_session(self):
        """[END_SESSION]マーカーを含むレスポンスのパース"""
        content = """AI: Goodbye! Have a nice day! [END_SESSION]
Feedback: 丁寧なお別れの挨拶ができています。"""

        ai_reply, feedback, improved, should_end = self.provider._parse_response(
            content
        )

        assert ai_reply == "Goodbye! Have a nice day!"
        assert feedback == "丁寧なお別れの挨拶ができています。"
        assert should_end is True

    def test_parse_response_missing_fields(self):
        """フィールドが欠けているレスポンスのパース"""
        content = "Just a plain response without structure"

        ai_reply, feedback, improved, should_end = self.provider._parse_response(
            content
        )

        assert ai_reply == "Just a plain response without structure"
        assert feedback == "改善点を120字以内で記述してください。"
        assert improved == "Please provide an improved sentence."
        assert should_end is False

    def test_parse_response_case_insensitive(self):
        """大文字小文字を区別しないパース"""
        content = """ai: Hello!
FEEDBACK: Good job!
IMPROVED: Great work!"""

        ai_reply, feedback, improved, should_end = self.provider._parse_response(
            content
        )

        assert ai_reply == "Hello!"
        assert feedback == "Good job!"
        assert improved == "Great work!"


class TestBuildRequestPayload:
    """_build_request_payload メソッドのテスト"""

    def setup_method(self):
        """各テスト前にプロバイダーをモック初期化"""
        with patch.object(GroqConversationProvider, "__init__", lambda x: None):
            self.provider = GroqConversationProvider()

    @patch("app.services.ai.groq_provider.get_prompt_by_scenario_id")
    @patch("app.services.ai.groq_provider.get_conversation_system_prompt")
    @patch("app.services.ai.groq_provider.settings")
    def test_build_payload_with_scenario_id(
        self, mock_settings, mock_conv_prompt, mock_scenario_prompt
    ):
        """シナリオIDを使ったペイロード構築"""
        mock_settings.GROQ_MODEL_NAME = "openai/gpt-oss-120b"
        mock_scenario_prompt.return_value = "You are at an airport..."
        mock_conv_prompt.return_value = "Conversation prompt..."

        payload = self.provider._build_request_payload(
            user_input="Hello",
            difficulty="intermediate",
            scenario_category="travel",
            context=[],
            scenario_id=1,
        )

        assert payload["model"] == "openai/gpt-oss-120b"
        assert "messages" in payload
        # OpenAI互換形式: system, user メッセージ
        messages = payload["messages"]
        assert messages[0]["role"] == "system"
        assert "You are at an airport..." in messages[0]["content"]
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Hello"
        mock_scenario_prompt.assert_called_once_with(1)

    @patch("app.services.ai.groq_provider.get_prompt_by_scenario_id")
    @patch("app.services.ai.groq_provider.get_prompt_by_category_difficulty")
    @patch("app.services.ai.groq_provider.get_conversation_system_prompt")
    @patch("app.services.ai.groq_provider.settings")
    def test_build_payload_fallback_to_category(
        self,
        mock_settings,
        mock_conv_prompt,
        mock_category_prompt,
        mock_scenario_prompt,
    ):
        """シナリオIDがない場合のカテゴリフォールバック"""
        mock_settings.GROQ_MODEL_NAME = "openai/gpt-oss-120b"
        mock_scenario_prompt.return_value = None
        mock_category_prompt.return_value = "Category prompt..."
        mock_conv_prompt.return_value = "Conversation prompt..."

        payload = self.provider._build_request_payload(
            user_input="Hello",
            difficulty="beginner",
            scenario_category="business",
            context=[],
            scenario_id=999,  # 存在しないID
        )

        mock_category_prompt.assert_called_once_with("business", "beginner")

    @patch("app.services.ai.groq_provider.get_prompt_by_scenario_id")
    @patch("app.services.ai.groq_provider.get_conversation_system_prompt")
    @patch("app.services.ai.groq_provider.settings")
    def test_build_payload_with_context(
        self, mock_settings, mock_conv_prompt, mock_scenario_prompt
    ):
        """コンテキストを含むペイロード構築"""
        mock_settings.GROQ_MODEL_NAME = "openai/gpt-oss-120b"
        mock_scenario_prompt.return_value = "System prompt"
        mock_conv_prompt.return_value = "Conv prompt"

        context = [
            {"user_input": "Hi", "ai_reply": "Hello!"},
            {"user_input": "How are you?", "ai_reply": "I'm fine!"},
        ]

        payload = self.provider._build_request_payload(
            user_input="Great!",
            difficulty="intermediate",
            scenario_category="daily",
            context=context,
            scenario_id=1,
        )

        # コンテキストがペイロードに含まれていることを確認
        assert "messages" in payload
        messages = payload["messages"]
        # system + コンテキスト(2ターン×2) + ユーザー入力 = 6メッセージ
        assert len(messages) == 6
        assert messages[0]["role"] == "system"
        assert messages[1]["content"] == "Hi"  # コンテキストのユーザー入力
        assert messages[2]["content"] == "Hello!"  # コンテキストのAI応答
        assert messages[-1]["content"] == "Great!"  # 最新のユーザー入力


class TestGroqProviderInit:
    """GroqConversationProvider 初期化のテスト"""

    @patch("app.services.ai.groq_provider.settings")
    def test_init_without_api_key_raises_error(self, mock_settings):
        """APIキーがない場合にValueErrorが発生"""
        mock_settings.GROQ_API_KEY = None

        with pytest.raises(ValueError, match="GROQ_API_KEY is not configured"):
            GroqConversationProvider()


class TestGenerateResponse:
    """generate_response メソッドのテスト"""

    @pytest.mark.asyncio
    @patch("app.services.ai.groq_provider.settings")
    @patch("app.services.ai.groq_provider.calculate_groq_cost")
    async def test_generate_response_success(self, mock_cost, mock_settings):
        """正常なレスポンス生成"""
        mock_settings.GROQ_API_KEY = "test-api-key"
        mock_settings.GROQ_MODEL_NAME = "openai/gpt-oss-120b"
        mock_settings.GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/v1/chat"

        # HTTPレスポンスをモック（OpenAI互換形式）
        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "content": "AI: Hello!\nFeedback: Good!\nImproved: Hi there!",
                    }
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }

        with patch.object(GroqConversationProvider, "__init__", lambda x: None):
            provider = GroqConversationProvider()
            provider._client = AsyncMock()

            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            provider._client.post = AsyncMock(return_value=mock_response)

            response = await provider.generate_response(
                user_input="Hello",
                difficulty="intermediate",
                scenario_category="daily",
                round_index=1,
                context=[],
                scenario_id=1,
            )

            assert response.ai_reply == "Hello!"
            assert response.feedback_short == "Good!"
            assert response.improved_sentence == "Hi there!"
            assert response.provider == "groq"
            mock_cost.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.ai.groq_provider.settings")
    async def test_generate_response_timeout(self, mock_settings):
        """タイムアウト時のエラー処理"""
        mock_settings.GROQ_API_KEY = "test-api-key"
        mock_settings.GROQ_MODEL_NAME = "openai/gpt-oss-120b"
        mock_settings.GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/v1/chat"

        with patch.object(GroqConversationProvider, "__init__", lambda x: None):
            provider = GroqConversationProvider()
            provider._client = AsyncMock()
            provider._client.post = AsyncMock(side_effect=httpx.ReadTimeout("Timeout"))

            with pytest.raises(TimeoutError, match="Groq request timed out"):
                await provider.generate_response(
                    user_input="Hello",
                    difficulty="intermediate",
                    scenario_category="daily",
                    round_index=1,
                    context=[],
                    scenario_id=1,
                )


class TestCostCalculation:
    """料金計算のテスト"""

    @pytest.mark.asyncio
    @patch("app.services.ai.groq_provider.settings")
    @patch("app.services.ai.groq_provider.calculate_groq_cost")
    async def test_cost_calculation_called_with_usage(self, mock_cost, mock_settings):
        """usageデータがある場合に料金計算が呼ばれる"""
        mock_settings.GROQ_API_KEY = "test-api-key"
        mock_settings.GROQ_MODEL_NAME = "openai/gpt-oss-120b"
        mock_settings.GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/v1/chat"

        mock_response_data = {
            "choices": [{"message": {"content": "AI: Hi!"}}],
            "usage": {"prompt_tokens": 150, "completion_tokens": 75},
        }

        with patch.object(GroqConversationProvider, "__init__", lambda x: None):
            provider = GroqConversationProvider()
            provider._client = AsyncMock()

            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            provider._client.post = AsyncMock(return_value=mock_response)

            await provider.generate_response(
                user_input="Hello",
                difficulty="beginner",
                scenario_category="travel",
                round_index=1,
                context=[],
                scenario_id=1,
            )

            mock_cost.assert_called_once()
            call_args = mock_cost.call_args
            assert call_args.kwargs["model"] == "openai/gpt-oss-120b"
            assert call_args.kwargs["input_tokens"] == 150
            assert call_args.kwargs["output_tokens"] == 75

    @pytest.mark.asyncio
    @patch("app.services.ai.groq_provider.settings")
    @patch("app.services.ai.groq_provider.calculate_groq_cost")
    async def test_cost_calculation_not_called_without_usage(
        self, mock_cost, mock_settings
    ):
        """usageデータがない場合に料金計算が呼ばれない"""
        mock_settings.GROQ_API_KEY = "test-api-key"
        mock_settings.GROQ_MODEL_NAME = "openai/gpt-oss-120b"
        mock_settings.GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/v1/chat"

        mock_response_data = {
            "choices": [{"message": {"content": "AI: Hi!"}}],
            "usage": {},  # 空のusage
        }

        with patch.object(GroqConversationProvider, "__init__", lambda x: None):
            provider = GroqConversationProvider()
            provider._client = AsyncMock()

            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            provider._client.post = AsyncMock(return_value=mock_response)

            await provider.generate_response(
                user_input="Hello",
                difficulty="beginner",
                scenario_category="travel",
                round_index=1,
                context=[],
                scenario_id=1,
            )

            mock_cost.assert_not_called()
