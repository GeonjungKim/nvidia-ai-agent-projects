import sys
from unittest.mock import MagicMock, patch

import pytest

from app.generate import build_messages, generate, load_model

FIXED_RECORDS = [
    {
        "name": "らぁ麺や 嶋",
        "genres": ["ラーメン"],
        "stations": ["新宿"],
        "tabelog_rating": 4.07,
        "tabelog_review_count": 2106,
        "budget_dinner": "￥1,000～￥1,999",
        "budget_lunch": None,
        "awards": [{"label": "百名店 2024"}],
        "visit_count_total": 5,
        "reviewers": [
            {"reviewer_display_name": "maro-j", "reviewer_rating": 4.5, "visit_count": 3},
            {"reviewer_display_name": "ひしもち", "reviewer_rating": None, "visit_count": 2},
        ],
        "last_visited": "2024/05",
    },
    {
        "name": "테스트식당2",
        "genres": ["焼肉"],
        "stations": ["渋谷"],
        "tabelog_rating": None,
        "tabelog_review_count": 10,
        "budget_dinner": None,
        "budget_lunch": None,
        "awards": [],
        "visit_count_total": 1,
        "reviewers": [
            {"reviewer_display_name": "maro-j", "reviewer_rating": 4.0, "visit_count": 1},
        ],
        "last_visited": "2023/11",
    },
    {
        "name": "테스트식당3",
        "genres": ["寿司"],
        "stations": ["銀座"],
        "tabelog_rating": 3.5,
        "tabelog_review_count": 50,
        "budget_dinner": "￥10,000～￥14,999",
        "budget_lunch": "￥3,000～￥3,999",
        "awards": [],
        "visit_count_total": 2,
        "reviewers": [
            {"reviewer_display_name": "maro-j", "reviewer_rating": None, "visit_count": 2},
        ],
        "last_visited": "2025/01",
    },
]


def _make_mock_model_and_tokenizer(generated_text: str):
    model = MagicMock()
    tokenizer = MagicMock()
    tokenizer.apply_chat_template.return_value = "PROMPT_TEXT"
    tokenizer.return_value.to.return_value = tokenizer.return_value
    tokenizer.decode.return_value = generated_text
    return model, tokenizer


def test_build_messages_has_two_roles_and_facts():
    messages = build_messages(FIXED_RECORDS)
    assert len(messages) == 2
    assert [m["role"] for m in messages] == ["system", "user"]
    assert "창작" in messages[0]["content"]
    for r in FIXED_RECORDS:
        assert r["name"] in messages[1]["content"]


def test_build_messages_includes_multi_reviewer_instruction_and_breakdown():
    # §14.4: prompt tells the model to synthesize multiple reviewers' facts,
    # and each restaurant's per-reviewer (display_name, rating, visits) rides
    # along in the user message so it actually can.
    messages = build_messages(FIXED_RECORDS)
    assert "복수 리뷰어" in messages[0]["content"]
    assert "ひしもち" in messages[1]["content"]
    assert "maro-j" in messages[1]["content"]


def test_template_fallback_contains_all_restaurant_names():
    text = generate(FIXED_RECORDS, model=None, tokenizer=None)
    for r in FIXED_RECORDS:
        assert r["name"] in text


def test_generate_returns_greedy_output_when_valid():
    text = "\n".join(f"{r['name']} 추천" for r in FIXED_RECORDS)
    model, tokenizer = _make_mock_model_and_tokenizer(text)

    result = generate(FIXED_RECORDS, model=model, tokenizer=tokenizer)

    assert result == text
    assert model.generate.call_count == 1


def test_generate_retries_then_falls_back_on_invalid_names():
    bad_text = "관련 없는 추천 내용"
    model, tokenizer = _make_mock_model_and_tokenizer(bad_text)

    result = generate(FIXED_RECORDS, model=model, tokenizer=tokenizer)

    assert model.generate.call_count == 2
    for r in FIXED_RECORDS:
        assert r["name"] in result


def test_load_model_success_returns_model_and_tokenizer_no_warning():
    # patch("transformers....") must import the real package to resolve its
    # target, so this needs transformers installed — skip cleanly where it
    # isn't (e.g. a torch/transformers-free deploy environment); the
    # sys.modules-based fallback test below covers that path instead.
    pytest.importorskip("transformers")
    fake_model = MagicMock()
    fake_tokenizer = MagicMock()
    with patch(
        "transformers.AutoModelForCausalLM.from_pretrained", return_value=fake_model
    ), patch(
        "transformers.AutoTokenizer.from_pretrained", return_value=fake_tokenizer
    ):
        model, tokenizer, warning = load_model()

    assert model is fake_model
    assert tokenizer is fake_tokenizer
    assert warning is None


def test_load_model_failure_falls_back_with_warning():
    pytest.importorskip("transformers")
    with patch(
        "transformers.AutoModelForCausalLM.from_pretrained",
        side_effect=OSError("network unavailable"),
    ):
        model, tokenizer, warning = load_model()

    assert model is None
    assert tokenizer is None
    assert warning is not None


def test_load_model_falls_back_when_transformers_is_not_installed():
    # Forcing sys.modules["transformers"] = None makes the next `import
    # transformers` (or `from transformers import ...`) raise ImportError,
    # simulating an environment where the package is absent — without
    # actually uninstalling it.
    with patch.dict(sys.modules, {"transformers": None}):
        model, tokenizer, warning = load_model()

    assert model is None
    assert tokenizer is None
    assert warning is not None
