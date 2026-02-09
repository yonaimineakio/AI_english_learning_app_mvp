import pytest

from app.services.ai import review_top_phrases


class _MockResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _MockClient:
    def __init__(self, payload):
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def post(self, *_args, **_kwargs):
        return _MockResponse(self._payload)


@pytest.mark.asyncio
async def test_select_top_review_phrases_success(monkeypatch):
    output_payload = {
        "output": [
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": (
                            '{"top_phrases":['
                            '{"round_index":1,"phrase":"I go to airport.","explanation":"冠詞を補いましょう","reason":"文法の基本ミス","score":70},'
                            '{"round_index":2,"phrase":"I go to airport.","explanation":"重複候補","reason":"重複","score":68},'
                            '{"round_index":3,"phrase":"Could you help me check in?","explanation":"丁寧表現を定着","reason":"実用頻度が高い","score":88},'
                            '{"round_index":4,"phrase":"My booking reference is here.","explanation":"語順を安定させる","reason":"空港で頻出","score":82}'
                            "]}"
                        ),
                    }
                ]
            }
        ]
    }

    monkeypatch.setattr(review_top_phrases.settings, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(review_top_phrases.settings, "OPENAI_MODEL_NAME", "gpt-5-mini")
    monkeypatch.setattr(
        review_top_phrases.settings,
        "OPENAI_CHAT_COMPLETIONS_URL",
        "https://example.invalid",
    )
    monkeypatch.setattr(
        review_top_phrases.httpx,
        "AsyncClient",
        lambda **_kwargs: _MockClient(output_payload),
    )

    result = await review_top_phrases.select_top_review_phrases(
        [
            {"round_index": 1, "user_input": "I go to airport"},
            {"round_index": 3, "user_input": "Could you help me check in"},
        ]
    )

    assert result is not None
    assert len(result) == 3
    assert result[0]["score"] >= result[1]["score"] >= result[2]["score"]
    assert len({item["phrase"] for item in result}) == 3


@pytest.mark.asyncio
async def test_select_top_review_phrases_invalid_json_returns_none(monkeypatch):
    output_payload = {
        "output": [
            {"content": [{"type": "output_text", "text": "this-is-not-json"}]}
        ]
    }

    monkeypatch.setattr(review_top_phrases.settings, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(review_top_phrases.settings, "OPENAI_MODEL_NAME", "gpt-5-mini")
    monkeypatch.setattr(
        review_top_phrases.settings,
        "OPENAI_CHAT_COMPLETIONS_URL",
        "https://example.invalid",
    )
    monkeypatch.setattr(
        review_top_phrases.httpx,
        "AsyncClient",
        lambda **_kwargs: _MockClient(output_payload),
    )

    result = await review_top_phrases.select_top_review_phrases(
        [{"round_index": 1, "user_input": "hello"}]
    )
    assert result is None


@pytest.mark.asyncio
async def test_select_top_review_phrases_no_api_key_returns_none(monkeypatch):
    monkeypatch.setattr(review_top_phrases.settings, "OPENAI_API_KEY", "")
    result = await review_top_phrases.select_top_review_phrases(
        [{"round_index": 1, "user_input": "hello"}]
    )
    assert result is None
