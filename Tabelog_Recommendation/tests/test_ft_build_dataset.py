import json
import random
from unittest.mock import MagicMock

import pytest

from scripts.ft_build_dataset import (
    MULTI_REVIEWER_MIN_FRACTION,
    allocate_by_fraction,
    build_candidate_pools,
    build_split_queues,
    derive_combination,
    fetch_seed_rows,
    passes_faithfulness_filter,
    run_split,
)

FACTS = [
    {
        "name": "らぁ麺や 嶋",
        "genres": ["ラーメン"],
        "stations": ["新宿"],
        "tabelog_rating": 4.07,
        "tabelog_review_count": 2106,
        "budget_dinner": "￥1,000～￥1,999",
        "budget_lunch": None,
        "awards": ["百名店 2024"],
        "visit_count_total": 5,
        "reviewers": [
            {"display_name": "maro-j", "reviewer_rating": 4.5, "visit_count": 3},
            {"display_name": "ひしもち", "reviewer_rating": None, "visit_count": 2},
        ],
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
            {"display_name": "maro-j", "reviewer_rating": 4.0, "visit_count": 1},
        ],
    },
]


# --- passes_faithfulness_filter ---


def test_filter_passes_faithful_text():
    text = (
        "らぁ麺や 嶋는 tabelog 4.07(리뷰 2106건)의 라멘 맛집입니다. "
        "테스트식당2는 리뷰 10건의 야키니쿠 식당입니다. "
        "총 2곳을 안내드립니다."
    )
    ok, reason = passes_faithfulness_filter(text, FACTS)
    assert ok is True
    assert reason is None


def test_filter_rejects_missing_name():
    text = "らぁ麺や 嶋만 언급하고 나머지는 생략합니다."
    ok, reason = passes_faithfulness_filter(text, FACTS)
    assert ok is False
    assert reason == "name_missing"


def test_filter_rejects_unlisted_quoted_name():
    text = (
        "らぁ麺や 嶋 테스트식당2 모두 추천하며, 「스시 지로」에서 영감을 받았습니다."
    )
    ok, reason = passes_faithfulness_filter(text, FACTS)
    assert ok is False
    assert reason == "unlisted_quoted_name"


def test_filter_allows_quoted_name_that_matches_input():
    text = "らぁ麺や 嶋 테스트식당2 모두 좋은 곳이며, 특히 「らぁ麺や 嶋」가 인상적입니다."
    ok, reason = passes_faithfulness_filter(text, FACTS)
    assert ok is True
    assert reason is None


def test_filter_rejects_hallucinated_number():
    # 9999는 입력 어디에도 없는 리뷰 수/평점/엔화 수치
    text = "らぁ麺や 嶋 테스트식당2 모두 추천하며, 리뷰가 9999건이나 됩니다."
    ok, reason = passes_faithfulness_filter(text, FACTS)
    assert ok is False
    assert reason == "number_not_traceable"


def test_filter_allows_restaurant_count_reference():
    # len(facts)==2 이하의 작은 정수는 "총 N곳" 류 목록-개수 언급으로 간주해 예외
    text = "らぁ麺や 嶋 테스트식당2 총 2곳을 안내드립니다."
    ok, reason = passes_faithfulness_filter(text, FACTS)
    assert ok is True
    assert reason is None


def test_filter_allows_budget_and_award_numbers_from_input():
    text = (
        "らぁ麺や 嶋는 ￥1,000～￥1,999 예산대이며 百名店 2024에 선정됐고 "
        "리뷰 2106건, 평점 4.07입니다. 테스트식당2는 리뷰 10건입니다."
    )
    ok, reason = passes_faithfulness_filter(text, FACTS)
    assert ok is True
    assert reason is None


def test_filter_rejects_length_exceeding_cap():
    text = ("らぁ麺や 嶋 테스트식당2 " + "가" * 700)
    ok, reason = passes_faithfulness_filter(text, FACTS)
    assert ok is False
    assert reason == "length_exceeded"


# --- derive_combination ---


def test_derive_combination_is_deterministic_given_same_seed():
    row = ("tokyo", "A1307", "ラーメン", "￥3,000～￥3,999", 1)
    combo_a = derive_combination(row, random.Random(42))
    combo_b = derive_combination(row, random.Random(42))
    assert combo_a == combo_b


def test_derive_combination_never_invents_budget_when_source_is_null():
    row = ("tokyo", "A1307", "ラーメン", None, 1)
    for seed in range(20):
        combo = derive_combination(row, random.Random(seed))
        assert combo[3] is None


def test_derive_combination_pref_and_genre_always_preserved():
    row = ("osaka", "A2701", "寿司", "￥5,000～￥5,999", 3)
    for seed in range(20):
        combo = derive_combination(row, random.Random(seed))
        assert combo[0] == "osaka"
        assert combo[2] == "寿司"
        assert combo[1] in (None, "A2701")
        assert combo[3] in (None, "￥5,000～￥5,999")


# --- allocate_by_fraction ---


def test_allocate_by_fraction_covers_all_items_disjointly():
    items = list(range(1000))
    result = allocate_by_fraction(
        items, {"train": 0.8, "val": 0.1, "test": 0.1}, random.Random(1)
    )
    all_out = result["train"] + result["val"] + result["test"]
    assert sorted(all_out) == items
    assert len(result["train"]) + len(result["val"]) + len(result["test"]) == 1000


def test_allocate_by_fraction_respects_fractions_approximately():
    items = list(range(1000))
    result = allocate_by_fraction(
        items, {"train": 0.8, "val": 0.1, "test": 0.1}, random.Random(1)
    )
    assert abs(len(result["train"]) - 800) <= 1
    assert abs(len(result["val"]) - 100) <= 1


# --- pool building against the real DB (§14 restaurants_agg / restaurant_genres) ---


def test_fetch_seed_rows_shape(real_db):
    rows = fetch_seed_rows(real_db)
    assert rows
    pref, area2, genre, budget_dinner, reviewer_count = rows[0]
    assert isinstance(pref, str)
    assert isinstance(genre, str)
    assert isinstance(reviewer_count, int)


def test_build_candidate_pools_classification_is_correct(real_db):
    rng = random.Random(7)
    seed_rows = fetch_seed_rows(real_db)
    multi_pool, single_pool = build_candidate_pools(
        real_db, seed_rows, rng, total_target=60, multi_fraction=0.30, buffer=1.2
    )
    assert multi_pool
    assert single_pool
    for combo, top5 in multi_pool.items():
        assert any(r["reviewer_count"] >= 2 for r in top5)
    for combo, top5 in single_pool.items():
        assert all(r["reviewer_count"] < 2 for r in top5)
    # 조합 키는 두 풀 사이에 겹치지 않는다 (같은 조합이 두 분류에 동시에 속할 수 없음)
    assert set(multi_pool.keys()).isdisjoint(single_pool.keys())


def test_build_split_queues_no_combo_shared_across_splits(real_db):
    rng = random.Random(7)
    seed_rows = fetch_seed_rows(real_db)
    multi_pool, single_pool = build_candidate_pools(
        real_db, seed_rows, rng, total_target=60, multi_fraction=0.30, buffer=1.2
    )
    queues = build_split_queues(
        multi_pool, single_pool, rng, {"train": 40, "val": 3, "test": 2}
    )
    train_set = set(queues["train"])
    val_set = set(queues["val"])
    test_set = set(queues["test"])
    assert train_set.isdisjoint(val_set)
    assert train_set.isdisjoint(test_set)
    assert val_set.isdisjoint(test_set)


def test_build_split_queues_meets_multi_reviewer_oversampling_target(real_db):
    rng = random.Random(7)
    seed_rows = fetch_seed_rows(real_db)
    total_target = 200
    multi_pool, single_pool = build_candidate_pools(
        real_db, seed_rows, rng, total_target=total_target, multi_fraction=0.30, buffer=1.2
    )
    all_pools = {**multi_pool, **single_pool}
    queues = build_split_queues(
        multi_pool, single_pool, rng, {"train": 140, "val": 40, "test": 20}
    )
    all_combos = queues["train"] + queues["val"] + queues["test"]
    n_multi = sum(
        1 for c in all_combos if any(r["reviewer_count"] >= 2 for r in all_pools[c])
    )
    assert n_multi / len(all_combos) >= MULTI_REVIEWER_MIN_FRACTION - 0.01


# --- run_split (incremental JSONL write) against a mocked teacher model ---

RAW_RECORDS = [
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
        ],
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
    },
]


def _mock_model_and_tokenizer_batch(batch_decode_outputs):
    """batch_decode_outputs: list of lists-of-strings, one list per
    successive tokenizer.batch_decode() call (배치 생성 시 1회 호출 = 1개
    리스트 반환이므로, 이 side_effect 순서가 곧 호출 순서와 대응)."""
    model = MagicMock()
    tokenizer = MagicMock()
    tokenizer.apply_chat_template.return_value = "PROMPT_TEXT"
    tokenizer.return_value.to.return_value = tokenizer.return_value
    tokenizer.batch_decode.side_effect = batch_decode_outputs
    return model, tokenizer


def test_run_split_writes_accepted_sample_incrementally_and_flushes(tmp_path):
    combo = ("tokyo", None, "ラーメン", None)
    all_pools = {combo: RAW_RECORDS}
    faithful_text = "らぁ麺や 嶋 테스트식당2 총 2곳을 안내드립니다."
    model, tokenizer = _mock_model_and_tokenizer_batch([[faithful_text]])
    reject_counts: dict[str, int] = {}
    out_path = tmp_path / "train.jsonl"

    accepted_combos, attempted = run_split(
        model, tokenizer, "train", [combo], 1, all_pools,
        random.Random(1), out_path, reject_counts,
    )

    assert accepted_combos == [combo]
    assert attempted == 1
    assert model.generate.call_count == 1  # greedy만으로 통과, 재생성 없음

    lines = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    saved = json.loads(lines[0])
    assert saved["completion"] == faithful_text
    assert saved["messages"][0]["role"] == "system"
    assert saved["messages"][1]["role"] == "user"


def test_run_split_stops_once_target_reached_leaving_queue_tail_unused(tmp_path):
    combo_a = ("tokyo", None, "ラーメン", None)
    combo_b = ("osaka", None, "寿司", None)
    all_pools = {combo_a: RAW_RECORDS, combo_b: RAW_RECORDS}
    faithful_text = "らぁ麺や 嶋 테스트식당2 총 2곳을 안내드립니다."
    model, tokenizer = _mock_model_and_tokenizer_batch([[faithful_text]])
    out_path = tmp_path / "train.jsonl"

    accepted_combos, attempted = run_split(
        model, tokenizer, "train", [combo_a, combo_b], 1, all_pools,
        random.Random(1), out_path, {},
    )

    assert accepted_combos == [combo_a]
    assert attempted == 1  # target(1)이 batch_size를 1로 좁혀 combo_b는 시도조차 안 됨
    lines = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


def test_run_split_discards_after_retry_still_fails_and_undershoots_target(tmp_path):
    combo = ("tokyo", None, "ラーメン", None)
    all_pools = {combo: RAW_RECORDS}
    # 두 시도 모두 이름 하나가 빠진 불충실 출력
    bad_text = "らぁ麺や 嶋만 언급합니다."
    model, tokenizer = _mock_model_and_tokenizer_batch([[bad_text], [bad_text]])
    reject_counts: dict[str, int] = {}
    out_path = tmp_path / "train.jsonl"

    accepted_combos, attempted = run_split(
        model, tokenizer, "train", [combo], 1, all_pools,
        random.Random(1), out_path, reject_counts,
    )

    assert accepted_combos == []
    assert attempted == 1
    assert model.generate.call_count == 2  # greedy 배치 + 재생성 배치 1회
    assert reject_counts["discarded_after_retry"] == 1
    assert out_path.read_text(encoding="utf-8") == ""


def test_run_split_batches_multiple_combos_into_a_single_generate_call(tmp_path):
    combo_a = ("tokyo", None, "ラーメン", None)
    combo_b = ("osaka", None, "寿司", None)
    combo_c = ("kyoto", None, "焼肉", None)
    combos = [combo_a, combo_b, combo_c]
    all_pools = {c: RAW_RECORDS for c in combos}
    texts = [f"라멘가게 らぁ麺や 嶋 그리고 테스트식당2, 총 2곳을 안내드립니다 [{c}]" for c in "ABC"]
    model, tokenizer = _mock_model_and_tokenizer_batch([texts])
    out_path = tmp_path / "train.jsonl"

    accepted_combos, attempted = run_split(
        model, tokenizer, "train", combos, 3, all_pools, random.Random(1), out_path, {},
    )

    assert set(accepted_combos) == set(combos)
    assert attempted == 3
    assert model.generate.call_count == 1  # 3건이 한 배치로 처리됨
    lines = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3


def test_generate_batch_falls_back_to_sequential_on_oom(tmp_path):
    import torch

    combo_a = ("tokyo", None, "ラーメン", None)
    combo_b = ("osaka", None, "寿司", None)
    all_pools = {combo_a: RAW_RECORDS, combo_b: RAW_RECORDS}
    faithful = "らぁ麺や 嶋 테스트식당2 총 2곳을 안내드립니다."

    model = MagicMock()
    model.generate.side_effect = [
        torch.cuda.OutOfMemoryError("simulated OOM"),
        MagicMock(),
        MagicMock(),
    ]
    tokenizer = MagicMock()
    tokenizer.apply_chat_template.return_value = "PROMPT_TEXT"
    tokenizer.return_value.to.return_value = tokenizer.return_value
    tokenizer.batch_decode.side_effect = [[faithful], [faithful]]

    out_path = tmp_path / "train.jsonl"
    accepted_combos, attempted = run_split(
        model, tokenizer, "train", [combo_a, combo_b], 2, all_pools,
        random.Random(1), out_path, {},
    )

    assert set(accepted_combos) == {combo_a, combo_b}
    assert attempted == 2
    assert model.generate.call_count == 3  # OOM 배치 1회 + 순차 폴백 2회
