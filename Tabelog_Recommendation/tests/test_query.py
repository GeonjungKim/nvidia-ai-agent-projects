import pytest

from app.query import count, search

# NOTE (§14.3, v2.0): search() now reads restaurants_agg (one row per
# restaurant, deduplicated across all reviewer files in data/reviewers/).
# All cell-size/top1 fixture values below were re-measured via
# scripts/measure_constants.py against that agg basis — they are NOT the
# same numbers as the pre-M9 single-reviewer (maro-only) era.


def test_tokyo_ramen_cell_size_and_top1(real_db):
    results = search(real_db, pref="tokyo", genre="ラーメン", limit=20000)
    assert len(results) == 6231
    assert results[0]["name"] == "らぁ麺や 嶋"


def test_nagano_ramen_cell_size(real_db):
    results = search(real_db, pref="nagano", genre="ラーメン", limit=20000)
    assert len(results) == 104


def test_aomori_french_empty(real_db):
    # okinawa x フレンチ is no longer empty post-M9 (2 restaurants from the
    # new reviewers) — aomori x フレンチ is a still-empty cell instead.
    results = search(real_db, pref="aomori", genre="フレンチ", limit=20000)
    assert results == []


def test_okinawa_french_now_has_two_restaurants_from_new_reviewers(real_db):
    results = search(real_db, pref="okinawa", genre="フレンチ", limit=20000)
    assert len(results) == 2


def test_budget_filter_matches_bucket_exactly(real_db):
    bucket = "￥1,000～￥1,999"
    results = search(
        real_db, pref="tokyo", genre="ラーメン", budget_dinner=bucket, limit=20000
    )
    assert results
    assert all(r["budget_dinner"] == bucket for r in results)


def test_region_cascade_violation_raises_value_error(real_db):
    with pytest.raises(ValueError):
        search(real_db, area2="A1307")
    with pytest.raises(ValueError):
        search(real_db, pref="tokyo", area3="A130704")


def test_all_sort_options_run_and_order_correctly(real_db):
    for sort in ("bayes", "rating", "reviews", "reviewer"):
        results = search(real_db, pref="tokyo", genre="ラーメン", sort=sort, limit=50)
        assert results

    by_reviews = search(
        real_db, pref="tokyo", genre="ラーメン", sort="reviews", limit=20000
    )
    counts = [r["tabelog_review_count"] for r in by_reviews]
    assert counts == sorted(counts, reverse=True)

    by_rating = search(
        real_db, pref="tokyo", genre="ラーメン", sort="rating", limit=20000
    )
    rated = [r["tabelog_rating"] for r in by_rating if r["tabelog_rating"] is not None]
    assert rated == sorted(rated, reverse=True)
    assert all(r["tabelog_rating"] is None for r in by_rating[len(rated):])


# --- M5 (§9.4): multi-select pref/genre, station search, revised cascade ---


def test_multi_pref_list_union(real_db):
    results = search(real_db, pref=["tokyo", "kanagawa"], genre="ラーメン", limit=20000)
    assert len(results) == 6720


def test_multi_genre_list_union_no_duplicates(real_db):
    results = search(real_db, pref="tokyo", genre=["ラーメン", "つけ麺"], limit=20000)
    assert len(results) == 6334
    ids = [r["restaurant_id"] for r in results]
    assert len(ids) == len(set(ids))


def test_single_pref_via_list_matches_single_pref_via_str(real_db):
    by_str = search(real_db, pref="kanagawa", genre="ラーメン", limit=20000)
    by_list = search(real_db, pref=["kanagawa"], genre="ラーメン", limit=20000)
    assert len(by_str) == 489
    assert len(by_list) == 489


def test_station_partial_match_ginza(real_db):
    # station_exact now defaults to True (§M12) — explicitly opt into the
    # old substring-match behavior to keep testing that path.
    results = search(real_db, station="銀座", station_exact=False, limit=20000)
    assert len(results) == 959


def test_station_partial_match_shinjuku(real_db):
    results = search(real_db, station="新宿", station_exact=False, limit=20000)
    assert len(results) == 1461


def test_multi_pref_with_area2_raises_value_error(real_db):
    with pytest.raises(ValueError):
        search(real_db, pref=["tokyo", "kanagawa"], area2="A1307")


def test_single_pref_str_with_area2_still_works(real_db):
    results = search(real_db, pref="tokyo", area2="A1307", limit=20000)
    assert results
    assert all(r["pref"] == "tokyo" and r["area2"] == "A1307" for r in results)


def test_single_pref_as_list_still_allows_area2(real_db):
    results = search(real_db, pref=["tokyo"], area2="A1307", limit=20000)
    assert results
    assert all(r["pref"] == "tokyo" and r["area2"] == "A1307" for r in results)


# --- M9 (§14.2): restaurant-level aggregation ---


def test_search_results_include_aggregate_fields(real_db):
    results = search(real_db, pref="tokyo", genre="ラーメン", limit=5)
    for r in results:
        assert r["reviewer_count"] >= 1
        assert r["visit_count_total"] >= 1
        assert isinstance(r["reviewers"], list)
        assert len(r["reviewers"]) == r["reviewer_count"]


def test_sort_by_reviewer_uses_reviewer_rating_mean(real_db):
    results = search(real_db, pref="tokyo", genre="ラーメン", sort="reviewer", limit=20000)
    rated = [
        r["reviewer_rating_mean"] for r in results if r["reviewer_rating_mean"] is not None
    ]
    assert rated == sorted(rated, reverse=True)


# --- M10 (§15.1): pagination ---


def test_count_matches_full_search_length(real_db):
    total = count(real_db, pref="nagano", genre="ラーメン")
    full = search(real_db, pref="nagano", genre="ラーメン", limit=20000)
    assert total == len(full) == 104


def test_offset_pages_cover_the_same_results_as_one_unpaged_call(real_db):
    unpaged = search(real_db, pref="tokyo", genre="ラーメン", limit=20, offset=0)
    page1 = search(real_db, pref="tokyo", genre="ラーメン", limit=10, offset=0)
    page2 = search(real_db, pref="tokyo", genre="ラーメン", limit=10, offset=10)
    assert [r["restaurant_id"] for r in page1 + page2] == [
        r["restaurant_id"] for r in unpaged
    ]


def test_offset_beyond_total_returns_empty_list(real_db):
    results = search(real_db, pref="okinawa", genre="フレンチ", limit=30, offset=1000)
    assert results == []


def test_count_respects_region_cascade_validation(real_db):
    with pytest.raises(ValueError):
        count(real_db, area2="A1307")


# --- M12: station exact/partial x primary-only, budget_lunch ---


def test_station_exact_is_the_default_and_excludes_longer_variants(real_db):
    default_results = search(real_db, station="駒込", limit=20000)
    explicit_exact = search(real_db, station="駒込", station_exact=True, limit=20000)
    assert len(default_results) == len(explicit_exact) == 64
    for r in default_results:
        assert "駒込" in r["stations"]  # the exact element is present ...
    assert not any(
        set(r["stations"]) == {"本駒込"} for r in default_results
    )  # ... 本駒込-only restaurants never sneak in


def test_station_partial_includes_longer_variants_like_motokomagome(real_db):
    partial_results = search(real_db, station="駒込", station_exact=False, limit=20000)
    assert len(partial_results) == 78
    assert any("本駒込" in r["stations"] for r in partial_results)


def test_station_primary_only_restricts_to_first_station(real_db):
    results = search(
        real_db, station="駒込", station_exact=True, station_primary_only=True, limit=20000
    )
    assert len(results) == 37
    for r in results:
        assert r["stations"][0] == "駒込"


def test_station_primary_only_partial_mode(real_db):
    results = search(
        real_db, station="駒込", station_exact=False, station_primary_only=True, limit=20000
    )
    for r in results:
        assert "駒込" in r["stations"][0]


def test_budget_lunch_filter_matches_bucket_exactly(real_db):
    bucket = "￥1,000～￥1,999"
    results = search(
        real_db, pref="tokyo", genre="ラーメン", budget_lunch=bucket, limit=20000
    )
    assert results
    assert all(r["budget_lunch"] == bucket for r in results)


def test_budget_lunch_distinct_bucket_count(real_db):
    results = search(real_db, limit=20000)
    buckets = {r["budget_lunch"] for r in results if r["budget_lunch"] is not None}
    assert len(buckets) == 16
