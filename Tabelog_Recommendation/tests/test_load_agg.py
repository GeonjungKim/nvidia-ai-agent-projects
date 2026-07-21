import json

import pytest

from app import load

FIELD_DEFAULTS = {
    "reviewer_id": "r1",
    "reviewer_display_name": "Reviewer One",
    "restaurant_id": "1",
    "name": "테스트식당",
    "url": "https://tabelog.com/tokyo/A1301/A130101/1/",
    "pref": "tokyo",
    "area2": "A1301",
    "area3": "A130101",
    "genres": ["ラーメン"],
    "stations": ["銀座"],
    "tabelog_rating": 4.0,
    "tabelog_review_count": 100,
    "budget_dinner": "￥1,000～￥1,999",
    "budget_lunch": None,
    "closed_days": None,
    "awards": [],
    "reviewer_rating": 4.5,
    "visited_month": "2024/01",
    "visit_count": 1,
    "review_url": "https://tabelog.com/rvwr/r1/rvwdtl/1/",
    "bookmark_id": "1",
    "source_node": "pal=tokyo",
}


def _record(**overrides):
    r = dict(FIELD_DEFAULTS)
    r.update(overrides)
    return r


def _write_reviewer_file(dir_path, filename, reviewer_id, records):
    payload = {
        "meta": {"reviewer": reviewer_id, "record_count": len(records)},
        "records": records,
    }
    (dir_path / filename).write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def test_load_reviewers_rejects_file_with_missing_field(tmp_path):
    reviewers_dir = tmp_path / "reviewers"
    reviewers_dir.mkdir()
    bad_record = _record()
    del bad_record["closed_days"]
    _write_reviewer_file(reviewers_dir, "bad.json", "r1", [bad_record])

    with pytest.raises(ValueError, match="missing"):
        load.load_reviewers(reviewers_dir, tmp_path / "app.db")


def test_load_reviewers_rejects_file_with_extra_field(tmp_path):
    reviewers_dir = tmp_path / "reviewers"
    reviewers_dir.mkdir()
    bad_record = _record(unexpected_field="surprise")
    _write_reviewer_file(reviewers_dir, "bad.json", "r1", [bad_record])

    with pytest.raises(ValueError, match="extra"):
        load.load_reviewers(reviewers_dir, tmp_path / "app.db")


def test_pick_latest_record_prefers_newer_visited_month():
    older = _record(reviewer_id="a", name="Old Name", visited_month="2023/01")
    newer = _record(reviewer_id="b", name="New Name", visited_month="2024/06")

    winner = load._pick_latest_record([older, newer])

    assert winner["name"] == "New Name"


def test_pick_latest_record_ties_broken_by_reviewer_id_ascending():
    a = _record(reviewer_id="zzz", name="Z Name", visited_month="2024/06")
    b = _record(reviewer_id="aaa", name="A Name", visited_month="2024/06")

    winner = load._pick_latest_record([a, b])

    assert winner["name"] == "A Name"


def test_pick_latest_record_null_visited_month_loses_to_any_real_value():
    null_month = _record(reviewer_id="a", name="Null Month", visited_month=None)
    real_month = _record(reviewer_id="z", name="Real Month", visited_month="2020/01")

    winner = load._pick_latest_record([null_month, real_month])

    assert winner["name"] == "Real Month"


def test_pick_latest_record_all_null_falls_back_to_reviewer_id():
    a = _record(reviewer_id="zzz", name="Z Name", visited_month=None)
    b = _record(reviewer_id="aaa", name="A Name", visited_month=None)

    winner = load._pick_latest_record([a, b])

    assert winner["name"] == "A Name"


def test_load_reviewers_builds_agg_aggregate_columns(tmp_path):
    reviewers_dir = tmp_path / "reviewers"
    reviewers_dir.mkdir()
    r1 = _record(
        reviewer_id="r1",
        reviewer_display_name="Alice",
        visited_month="2023/05",
        visit_count=2,
        reviewer_rating=4.0,
    )
    r2 = _record(
        reviewer_id="r2",
        reviewer_display_name="Bob",
        visited_month="2024/08",
        visit_count=3,
        reviewer_rating=None,
    )
    _write_reviewer_file(reviewers_dir, "a.json", "r1", [r1])
    _write_reviewer_file(reviewers_dir, "b.json", "r2", [r2])

    report = load.load_reviewers(reviewers_dir, tmp_path / "app.db")

    assert report["total_records"] == 2
    assert report["total_restaurants"] == 1

    import sqlite3

    conn = sqlite3.connect(tmp_path / "app.db")
    try:
        row = conn.execute(
            "SELECT reviewer_count, visit_count_total, reviewer_rating_mean, "
            "last_visited FROM restaurants_agg WHERE restaurant_id = '1'"
        ).fetchone()
    finally:
        conn.close()

    reviewer_count, visit_count_total, reviewer_rating_mean, last_visited = row
    assert reviewer_count == 2
    assert visit_count_total == 5
    assert reviewer_rating_mean == 4.0  # only r1's non-null 4.0 averaged
    assert last_visited == "2024/08"


def test_load_reviewers_counts_attribute_discrepancy_when_values_differ(tmp_path):
    reviewers_dir = tmp_path / "reviewers"
    reviewers_dir.mkdir()
    r1 = _record(reviewer_id="r1", tabelog_rating=4.0, visited_month="2023/01")
    r2 = _record(reviewer_id="r2", tabelog_rating=4.2, visited_month="2024/01")
    _write_reviewer_file(reviewers_dir, "a.json", "r1", [r1])
    _write_reviewer_file(reviewers_dir, "b.json", "r2", [r2])

    report = load.load_reviewers(reviewers_dir, tmp_path / "app.db")

    assert report["attribute_discrepancy_count"] == 1


def test_load_reviewers_no_discrepancy_when_values_identical(tmp_path):
    reviewers_dir = tmp_path / "reviewers"
    reviewers_dir.mkdir()
    r1 = _record(reviewer_id="r1", visited_month="2023/01")
    r2 = _record(reviewer_id="r2", visited_month="2024/01")
    _write_reviewer_file(reviewers_dir, "a.json", "r1", [r1])
    _write_reviewer_file(reviewers_dir, "b.json", "r2", [r2])

    report = load.load_reviewers(reviewers_dir, tmp_path / "app.db")

    assert report["attribute_discrepancy_count"] == 0
