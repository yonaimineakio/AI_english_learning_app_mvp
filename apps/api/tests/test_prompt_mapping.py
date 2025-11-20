from app.prompts import get_prompt_by_scenario_id


def test_get_prompt_by_scenario_id_existing_range() -> None:
    # 既存および Issue #27 で追加したシナリオID (1-21) でプロンプトが取得できることを確認
    for scenario_id in range(1, 22):
        prompt = get_prompt_by_scenario_id(scenario_id)
        assert prompt is not None, f"scenario_id={scenario_id} のプロンプトが見つかりません"
        assert isinstance(prompt, str)
        assert len(prompt) > 0



