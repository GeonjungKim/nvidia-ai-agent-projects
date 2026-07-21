import json
import re
import sqlite3
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "reviewer_id",
    "reviewer_display_name",
    "restaurant_id",
    "name",
    "url",
    "pref",
    "area2",
    "area3",
    "genres",
    "stations",
    "tabelog_rating",
    "tabelog_review_count",
    "budget_dinner",
    "budget_lunch",
    "closed_days",
    "awards",
    "reviewer_rating",
    "visited_month",
    "visit_count",
    "review_url",
    "bookmark_id",
    "source_node",
)
REQUIRED_FIELDS_SET = frozenset(REQUIRED_FIELDS)

DDL_STATEMENTS = (
    """
    CREATE TABLE restaurants (
      reviewer_id TEXT NOT NULL,
      restaurant_id TEXT NOT NULL,
      name TEXT NOT NULL,
      url TEXT NOT NULL,
      pref TEXT NOT NULL,
      area2 TEXT NOT NULL,
      area3 TEXT NOT NULL,
      tabelog_rating REAL,
      tabelog_review_count INTEGER NOT NULL,
      reviewer_rating REAL,
      visit_count INTEGER NOT NULL,
      visited_month TEXT,    -- nullable since §14: 2 of 3 reviewer files have a handful of nulls (10/47703)
      budget_dinner TEXT,
      budget_lunch TEXT,
      budget_dinner_floor INTEGER,
      budget_lunch_floor INTEGER,
      closed_days TEXT,
      stations_json TEXT NOT NULL,
      awards_json TEXT NOT NULL,
      award_count INTEGER NOT NULL,
      bayes_score REAL,
      PRIMARY KEY (reviewer_id, restaurant_id)
    )
    """,
    """
    CREATE TABLE restaurant_genres (
      restaurant_id TEXT NOT NULL,
      genre TEXT NOT NULL,
      PRIMARY KEY (restaurant_id, genre)
    )
    """,
    "CREATE INDEX idx_r_region ON restaurants(pref, area2, area3)",
    "CREATE INDEX idx_r_bayes ON restaurants(bayes_score)",
    "CREATE INDEX idx_g_genre ON restaurant_genres(genre)",
    "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)",
)

# §14.2 — restaurant-level aggregation, one row per restaurant_id, built only
# by load_reviewers() (the multi-file path). restaurant_genres is reused as-is:
# it was already restaurant_id-keyed with INSERT OR IGNORE, so it naturally
# unions genres across reviewer files with no separate table needed.
AGG_DDL_STATEMENTS = (
    """
    CREATE TABLE restaurants_agg (
      restaurant_id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      url TEXT NOT NULL,
      pref TEXT NOT NULL,
      area2 TEXT NOT NULL,
      area3 TEXT NOT NULL,
      tabelog_rating REAL,
      tabelog_review_count INTEGER NOT NULL,
      budget_dinner TEXT,
      budget_lunch TEXT,
      budget_dinner_floor INTEGER,
      budget_lunch_floor INTEGER,
      closed_days TEXT,
      stations_json TEXT NOT NULL,
      awards_json TEXT NOT NULL,
      award_count INTEGER NOT NULL,
      bayes_score REAL,
      reviewer_count INTEGER NOT NULL,
      reviewers_json TEXT NOT NULL,
      visit_count_total INTEGER NOT NULL,
      reviewer_rating_mean REAL,
      last_visited TEXT
    )
    """,
    "CREATE INDEX idx_agg_region ON restaurants_agg(pref, area2, area3)",
    "CREATE INDEX idx_agg_bayes ON restaurants_agg(bayes_score)",
)

# Restaurant-level facts that may differ across reviewer files for the same
# restaurant_id; resolved by "most recent visited_month wins" (§14.2).
AGG_MOST_RECENT_FIELDS = (
    "name",
    "url",
    "pref",
    "area2",
    "area3",
    "tabelog_rating",
    "tabelog_review_count",
    "budget_dinner",
    "budget_lunch",
    "closed_days",
    "stations",
    "awards",
)

INSERT_RESTAURANT_SQL = """
    INSERT INTO restaurants (
      reviewer_id, restaurant_id, name, url, pref, area2, area3,
      tabelog_rating, tabelog_review_count, reviewer_rating,
      visit_count, visited_month, budget_dinner, budget_lunch,
      budget_dinner_floor, budget_lunch_floor, closed_days, stations_json,
      awards_json, award_count, bayes_score
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

INSERT_GENRE_SQL = (
    "INSERT OR IGNORE INTO restaurant_genres (restaurant_id, genre) VALUES (?, ?)"
)

INSERT_META_SQL = "INSERT INTO meta (key, value) VALUES (?, ?)"

INSERT_AGG_SQL = """
    INSERT INTO restaurants_agg (
      restaurant_id, name, url, pref, area2, area3,
      tabelog_rating, tabelog_review_count, budget_dinner, budget_lunch,
      budget_dinner_floor, budget_lunch_floor, closed_days, stations_json,
      awards_json, award_count, bayes_score, reviewer_count, reviewers_json,
      visit_count_total, reviewer_rating_mean, last_visited
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def _load_records(json_path: Path) -> list[dict[str, Any]]:
    with open(json_path, encoding="utf-8") as f:
        payload = json.load(f)

    records = payload["records"]
    expected_count = payload["meta"].get("record_count")
    if expected_count is not None and len(records) != expected_count:
        raise ValueError(
            f"{json_path}: record count mismatch: meta.record_count={expected_count} "
            f"but len(records)={len(records)}"
        )

    for i, record in enumerate(records):
        fields = set(record.keys())
        if fields != REQUIRED_FIELDS_SET:
            missing = sorted(REQUIRED_FIELDS_SET - fields)
            extra = sorted(fields - REQUIRED_FIELDS_SET)
            raise ValueError(
                f"{json_path}: records[{i}] schema mismatch vs required 22 fields "
                f"— missing={missing} extra={extra}"
            )

    return records


def _parse_budget_floor(value: str | None) -> int | None:
    if value is None:
        return None
    if value.startswith("～"):
        # e.g. "～￥999" has no lower bound — floor is 0, not the 999 upper bound.
        return 0
    match = re.search(r"\d[\d,]*", value)
    if match is None:
        raise ValueError(f"budget bucket has no digit group: {value!r}")
    return int(match.group(0).replace(",", ""))


def _compute_prior(records: list[dict[str, Any]]) -> tuple[float, int]:
    rated = [r for r in records if r["tabelog_rating"] is not None]
    global_mean_c = statistics.mean(r["tabelog_rating"] for r in rated)
    prior_m = int(statistics.median(r["tabelog_review_count"] for r in rated))
    return global_mean_c, prior_m


def _bayes_score(
    v: int, rating: float | None, m: int, c: float
) -> float | None:
    if rating is None:
        return None
    return (v * rating + m * c) / (v + m)


def _build_rows(
    records: list[dict[str, Any]], global_mean_c: float, prior_m: int
) -> tuple[list[tuple], list[tuple]]:
    restaurant_rows = []
    genre_rows = []
    for r in records:
        dinner_floor = _parse_budget_floor(r["budget_dinner"])
        lunch_floor = _parse_budget_floor(r["budget_lunch"])
        score = _bayes_score(
            r["tabelog_review_count"], r["tabelog_rating"], prior_m, global_mean_c
        )
        restaurant_rows.append(
            (
                r["reviewer_id"],
                r["restaurant_id"],
                r["name"],
                r["url"],
                r["pref"],
                r["area2"],
                r["area3"],
                r["tabelog_rating"],
                r["tabelog_review_count"],
                r["reviewer_rating"],
                r["visit_count"],
                r["visited_month"],
                r["budget_dinner"],
                r["budget_lunch"],
                dinner_floor,
                lunch_floor,
                r["closed_days"],
                json.dumps(r["stations"], ensure_ascii=False),
                json.dumps(r["awards"], ensure_ascii=False),
                len(r["awards"]),
                score,
            )
        )
        for genre in r["genres"]:
            genre_rows.append((r["restaurant_id"], genre))
    return restaurant_rows, genre_rows


def load(json_path: Path, db_path: Path) -> None:
    """M1 single-file loader — unchanged since v1.0. Kept as the 'records
    table verification' regression path per §14.3; production loading now
    goes through load_reviewers() below."""
    json_path = Path(json_path)
    db_path = Path(db_path)

    records = _load_records(json_path)
    global_mean_c, prior_m = _compute_prior(records)
    restaurant_rows, genre_rows = _build_rows(records, global_mean_c, prior_m)
    meta_rows = [
        ("global_mean_C", str(global_mean_c)),
        ("prior_m", str(prior_m)),
        ("source_file", str(json_path)),
        ("record_count", str(len(records))),
        ("loaded_at", datetime.now(timezone.utc).isoformat()),
    ]

    conn = sqlite3.connect(db_path)
    try:
        # DDL auto-commits immediately in sqlite3's legacy transaction mode,
        # so it sits outside the `with conn:` block below on purpose.
        conn.execute("DROP TABLE IF EXISTS restaurants")
        conn.execute("DROP TABLE IF EXISTS restaurant_genres")
        conn.execute("DROP TABLE IF EXISTS meta")
        for statement in DDL_STATEMENTS:
            conn.execute(statement)

        with conn:
            conn.executemany(INSERT_RESTAURANT_SQL, restaurant_rows)
            conn.executemany(INSERT_GENRE_SQL, genre_rows)
            conn.executemany(INSERT_META_SQL, meta_rows)
    finally:
        conn.close()


def _load_reviewer_files(
    reviewers_dir: Path,
) -> tuple[list[dict[str, Any]], list[tuple[str, int]]]:
    reviewers_dir = Path(reviewers_dir)
    json_files = sorted(reviewers_dir.glob("*.json"))
    if not json_files:
        raise ValueError(f"no .json files found in {reviewers_dir}")

    all_records: list[dict[str, Any]] = []
    file_counts: list[tuple[str, int]] = []
    for path in json_files:
        records = _load_records(path)
        all_records.extend(records)
        file_counts.append((path.name, len(records)))

    seen: set[tuple[str, str]] = set()
    for r in all_records:
        pk = (r["reviewer_id"], r["restaurant_id"])
        if pk in seen:
            raise ValueError(f"duplicate (reviewer_id, restaurant_id) across files: {pk}")
        seen.add(pk)

    return all_records, file_counts


def _pick_latest_record(records_for_restaurant: list[dict[str, Any]]) -> dict[str, Any]:
    """§14.2: most-recent visited_month wins; null sorts as oldest (never
    wins over a real value); ties (incl. all-null) broken by reviewer_id asc."""
    with_month = [r for r in records_for_restaurant if r["visited_month"] is not None]
    if with_month:
        max_month = max(r["visited_month"] for r in with_month)
        pool = [r for r in with_month if r["visited_month"] == max_month]
    else:
        pool = records_for_restaurant
    return min(pool, key=lambda r: r["reviewer_id"])


def _comparable(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return value


def _count_attribute_discrepancies(groups: dict[str, list[dict[str, Any]]]) -> int:
    """Restaurants with 2+ reviewers where at least one §14.2 attribute
    genuinely differs across their records (anomaly-detection signal)."""
    count = 0
    for records_for_restaurant in groups.values():
        if len(records_for_restaurant) < 2:
            continue
        for field in AGG_MOST_RECENT_FIELDS:
            values = {_comparable(r[field]) for r in records_for_restaurant}
            if len(values) > 1:
                count += 1
                break
    return count


def _build_agg_row(
    restaurant_id: str,
    records_for_restaurant: list[dict[str, Any]],
    agg_c: float,
    agg_m: int,
) -> tuple:
    winner = _pick_latest_record(records_for_restaurant)
    dinner_floor = _parse_budget_floor(winner["budget_dinner"])
    lunch_floor = _parse_budget_floor(winner["budget_lunch"])
    score = _bayes_score(
        winner["tabelog_review_count"], winner["tabelog_rating"], agg_m, agg_c
    )

    reviewers = [
        {
            "reviewer_id": r["reviewer_id"],
            "reviewer_display_name": r["reviewer_display_name"],
            "reviewer_rating": r["reviewer_rating"],
            "visit_count": r["visit_count"],
        }
        for r in sorted(records_for_restaurant, key=lambda r: r["reviewer_id"])
    ]
    visit_count_total = sum(r["visit_count"] for r in records_for_restaurant)
    rated = [
        r["reviewer_rating"] for r in records_for_restaurant if r["reviewer_rating"] is not None
    ]
    reviewer_rating_mean = statistics.mean(rated) if rated else None
    months = [
        r["visited_month"] for r in records_for_restaurant if r["visited_month"] is not None
    ]
    last_visited = max(months) if months else None

    return (
        restaurant_id,
        winner["name"],
        winner["url"],
        winner["pref"],
        winner["area2"],
        winner["area3"],
        winner["tabelog_rating"],
        winner["tabelog_review_count"],
        winner["budget_dinner"],
        winner["budget_lunch"],
        dinner_floor,
        lunch_floor,
        winner["closed_days"],
        json.dumps(winner["stations"], ensure_ascii=False),
        json.dumps(winner["awards"], ensure_ascii=False),
        len(winner["awards"]),
        score,
        len(records_for_restaurant),
        json.dumps(reviewers, ensure_ascii=False),
        visit_count_total,
        reviewer_rating_mean,
        last_visited,
    )


def load_reviewers(reviewers_dir: Path, db_path: Path) -> dict[str, Any]:
    """§14.1/§14.2 production loader: every .json in reviewers_dir is
    schema-validated and unioned into `restaurants` (unchanged per-record
    shape), then deduplicated by restaurant_id into `restaurants_agg` with
    its own bayes prior (C, m recomputed on the deduped set, not records).
    Returns a report dict consumed by scripts/measure_constants.py."""
    reviewers_dir = Path(reviewers_dir)
    db_path = Path(db_path)

    all_records, file_counts = _load_reviewer_files(reviewers_dir)

    records_c, records_m = _compute_prior(all_records)
    restaurant_rows, genre_rows = _build_rows(all_records, records_c, records_m)

    groups: dict[str, list[dict[str, Any]]] = {}
    for r in all_records:
        groups.setdefault(r["restaurant_id"], []).append(r)

    agg_source_records = [_pick_latest_record(recs) for recs in groups.values()]
    agg_c, agg_m = _compute_prior(agg_source_records)

    agg_rows = [
        _build_agg_row(rid, recs, agg_c, agg_m) for rid, recs in groups.items()
    ]
    discrepancy_count = _count_attribute_discrepancies(groups)

    meta_rows = [
        ("global_mean_C", str(records_c)),
        ("prior_m", str(records_m)),
        ("source_file", ",".join(name for name, _ in file_counts)),
        ("record_count", str(len(all_records))),
        ("loaded_at", datetime.now(timezone.utc).isoformat()),
        ("agg_global_mean_C", str(agg_c)),
        ("agg_prior_m", str(agg_m)),
        ("restaurant_count", str(len(groups))),
    ]

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DROP TABLE IF EXISTS restaurants")
        conn.execute("DROP TABLE IF EXISTS restaurant_genres")
        conn.execute("DROP TABLE IF EXISTS meta")
        conn.execute("DROP TABLE IF EXISTS restaurants_agg")
        for statement in DDL_STATEMENTS:
            conn.execute(statement)
        for statement in AGG_DDL_STATEMENTS:
            conn.execute(statement)

        with conn:
            conn.executemany(INSERT_RESTAURANT_SQL, restaurant_rows)
            conn.executemany(INSERT_GENRE_SQL, genre_rows)
            conn.executemany(INSERT_META_SQL, meta_rows)
            conn.executemany(INSERT_AGG_SQL, agg_rows)
    finally:
        conn.close()

    return {
        "file_counts": file_counts,
        "total_records": len(all_records),
        "total_restaurants": len(groups),
        "attribute_discrepancy_count": discrepancy_count,
        "records_c": records_c,
        "records_m": records_m,
        "agg_c": agg_c,
        "agg_m": agg_m,
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m app.load <reviewers_dir> <db_path>")
    reviewers_dir, db_path = sys.argv[1], sys.argv[2]
    report = load_reviewers(Path(reviewers_dir), Path(db_path))
    print(f"loaded {len(report['file_counts'])} reviewer file(s) -> {db_path}")
    for name, count in report["file_counts"]:
        print(f"  {name}: {count} records")
    print(f"total records: {report['total_records']}")
    print(f"total restaurants (agg): {report['total_restaurants']}")
    print(f"attribute discrepancies (multi-reviewer restaurants): "
          f"{report['attribute_discrepancy_count']}")


if __name__ == "__main__":
    main()
