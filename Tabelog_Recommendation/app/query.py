import json
import sqlite3
from pathlib import Path
from typing import Any

SORT_COLUMNS = {
    "bayes": "bayes_score",
    "rating": "tabelog_rating",
    "reviews": "tabelog_review_count",
    "reviewer": "reviewer_rating_mean",
}


def _as_list(value: str | list[str] | None) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    return list(value)


def _station_condition(
    station: str, station_exact: bool, station_primary_only: bool
) -> tuple[str, Any]:
    """§M12: 4 combinations of (exact|partial) x (any element|primary only).

    stations_json is stored as `json.dumps(list, ensure_ascii=False)` (raw
    text, verified empirically — no \\uXXXX escaping), so an exact match of
    a full array element can be expressed as a portable LIKE on the
    quote-wrapped substring, with no SQLite JSON1 dependency: `"駒込"` can
    only appear in the serialized text as the literal content of some
    element (JSON syntax guarantees a bare `"` never appears mid-string for
    plain place names), so it can't false-positive match inside a longer
    name like `"本駒込"`. "Primary only" (first element specifically) has no
    such simple LIKE form without risking false positives across element
    boundaries in multi-station arrays, so it uses json_extract($[0])
    instead — SQLite's JSON1 extension is confirmed available here.
    """
    if station_primary_only:
        column = "json_extract(stations_json, '$[0]')"
        if station_exact:
            return f"{column} = ?", station
        return f"{column} LIKE ?", f"%{station}%"
    if station_exact:
        return "stations_json LIKE ?", f'%"{station}"%'
    return "stations_json LIKE ?", f"%{station}%"


def _validate_and_build_where(
    pref_list: list[str] | None,
    area2: str | None,
    area3: str | None,
    station: str | None,
    station_exact: bool,
    station_primary_only: bool,
    budget_dinner: str | None,
    budget_lunch: str | None,
    genre_list: list[str] | None,
) -> tuple[str, list[Any]]:
    """Shared by search() and count() so their filter semantics never drift."""
    if area2 is not None and (pref_list is None or len(pref_list) != 1):
        raise ValueError("area2 requires exactly one pref to be specified")
    if area3 is not None and area2 is None:
        raise ValueError("area3 requires area2 to be specified")

    conditions = []
    params: list[Any] = []

    if pref_list is not None:
        placeholders = ",".join("?" for _ in pref_list)
        conditions.append(f"pref IN ({placeholders})")
        params.extend(pref_list)
    if area2 is not None:
        conditions.append("area2 = ?")
        params.append(area2)
    if area3 is not None:
        conditions.append("area3 = ?")
        params.append(area3)
    if station is not None:
        condition, param = _station_condition(station, station_exact, station_primary_only)
        conditions.append(condition)
        params.append(param)
    if budget_dinner is not None:
        conditions.append("budget_dinner = ?")
        params.append(budget_dinner)
    if budget_lunch is not None:
        conditions.append("budget_lunch = ?")
        params.append(budget_lunch)
    if genre_list is not None:
        placeholders = ",".join("?" for _ in genre_list)
        conditions.append(
            "EXISTS (SELECT 1 FROM restaurant_genres g "
            "WHERE g.restaurant_id = restaurants_agg.restaurant_id "
            f"AND g.genre IN ({placeholders}))"
        )
        params.extend(genre_list)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_clause, params


def search(
    db: str | Path,
    pref: str | list[str] | None = None,
    area2: str | None = None,
    area3: str | None = None,
    genre: str | list[str] | None = None,
    station: str | None = None,
    station_exact: bool = True,
    station_primary_only: bool = False,
    budget_dinner: str | None = None,
    budget_lunch: str | None = None,
    sort: str = "bayes",
    limit: int = 30,
    offset: int = 0,
) -> list[dict[str, Any]]:
    pref_list = _as_list(pref)
    genre_list = _as_list(genre)
    if sort not in SORT_COLUMNS:
        raise ValueError(f"unknown sort option: {sort!r}")

    where_clause, params = _validate_and_build_where(
        pref_list, area2, area3, station, station_exact, station_primary_only,
        budget_dinner, budget_lunch, genre_list,
    )

    sort_column = SORT_COLUMNS[sort]
    # NULLS LAST is SQLite 3.30+ only; this portable form works on any version.
    # §14.2: search() reads restaurants_agg (one card = one restaurant),
    # not the record-level restaurants table.
    query = (
        f"SELECT * FROM restaurants_agg {where_clause} "
        f"ORDER BY ({sort_column} IS NULL) ASC, {sort_column} DESC "
        f"LIMIT ? OFFSET ?"
    )
    params = [*params, limit, offset]

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(query, params).fetchall()
        results = [dict(row) for row in rows]
        _attach_genres(conn, results)
    finally:
        conn.close()

    for r in results:
        r["stations"] = json.loads(r.pop("stations_json"))
        r["awards"] = json.loads(r.pop("awards_json"))
        r["reviewers"] = json.loads(r.pop("reviewers_json"))

    return results


def count(
    db: str | Path,
    pref: str | list[str] | None = None,
    area2: str | None = None,
    area3: str | None = None,
    genre: str | list[str] | None = None,
    station: str | None = None,
    station_exact: bool = True,
    station_primary_only: bool = False,
    budget_dinner: str | None = None,
    budget_lunch: str | None = None,
) -> int:
    """§15.1: total matches for the same filters search() would use, ignoring
    limit/offset/sort — powers the "전체 X곳 중 a–b" pagination caption."""
    pref_list = _as_list(pref)
    genre_list = _as_list(genre)

    where_clause, params = _validate_and_build_where(
        pref_list, area2, area3, station, station_exact, station_primary_only,
        budget_dinner, budget_lunch, genre_list,
    )
    query = f"SELECT COUNT(*) FROM restaurants_agg {where_clause}"

    conn = sqlite3.connect(db)
    try:
        return conn.execute(query, params).fetchone()[0]
    finally:
        conn.close()


def _attach_genres(conn: sqlite3.Connection, results: list[dict[str, Any]]) -> None:
    for r in results:
        r["genres"] = []
    if not results:
        return
    ids = [r["restaurant_id"] for r in results]
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(
        f"SELECT restaurant_id, genre FROM restaurant_genres "
        f"WHERE restaurant_id IN ({placeholders})",
        ids,
    ).fetchall()
    by_id: dict[str, list[str]] = {}
    for restaurant_id, genre in rows:
        by_id.setdefault(restaurant_id, []).append(genre)
    for r in results:
        r["genres"] = by_id.get(r["restaurant_id"], [])
