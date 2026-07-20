"""Tabelog DB MCP 서버 — 읽기 전용.

- 유니크 식당 테이블(restaurants_agg, 45,725곳)만 노출한다.
- 리뷰어 내부 필드(reviewers_json, reviewer_rating 등)는 절대 반환하지 않는다 (C-2).
- DB는 읽기 전용 URI로만 연다 (C-1). Tabelog에 대한 네트워크 요청 없음 — 로컬 DB만.
- 이 모듈은 MCP 서버이자 라이브러리다: LLM 에이전트는 MCP 도구로,
  파이프라인의 결정론 코드는 아래 일반 함수(fetch_by_ids 등)로 같은 로직을 쓴다.
"""
from __future__ import annotations

import json
import sqlite3

from fastmcp import FastMCP

from tabetabi.config import DB_PATH
from tabetabi.links import google_search_url

mcp = FastMCP("TabelogDB")

# C-2 안전 컬럼만. r = restaurants_agg
_SAFE_COLS = (
    "r.restaurant_id, r.name, r.url, r.pref, r.area2, r.area3, r.tabelog_rating, "
    "r.tabelog_review_count, r.budget_lunch, r.budget_dinner, r.budget_dinner_floor, "
    "r.closed_days, r.stations_json, r.award_count, r.bayes_score, r.reviewer_count"
)
_GENRES_SUB = (
    "(SELECT group_concat(g.genre, ', ') FROM restaurant_genres g "
    "WHERE g.restaurant_id = r.restaurant_id) AS genres"
)
_SORTS = {
    "bayes": "(r.bayes_score IS NULL) ASC, r.bayes_score DESC",
    "rating": "(r.tabelog_rating IS NULL) ASC, r.tabelog_rating DESC",
    "reviews": "r.tabelog_review_count DESC",
}


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _row(r: sqlite3.Row) -> dict:
    d = dict(r)
    stations = json.loads(d.pop("stations_json") or "[]")
    d["stations"] = stations[:3]
    if d.get("bayes_score") is not None:
        d["bayes_score"] = round(d["bayes_score"], 3)
    d["tabelog_url"] = d.pop("url")
    d["gmap"] = google_search_url(d["name"], stations[0]) if stations else ""
    return d


@mcp.tool
def list_prefs() -> list[dict]:
    """식당 데이터가 있는 지역(pref) 코드 목록과 식당 수. pref는 로마자 소문자 (예: tokyo, osaka, kyoto)."""
    conn = _db()
    try:
        rows = conn.execute(
            "SELECT pref, COUNT(*) AS restaurants FROM restaurants_agg GROUP BY pref ORDER BY restaurants DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@mcp.tool
def list_areas(pref: str) -> list[dict]:
    """해당 pref 안의 세부지역(area2) 목록과 식당 수 상위 30. area2는 일본어 지명."""
    conn = _db()
    try:
        rows = conn.execute(
            "SELECT area2, COUNT(*) AS restaurants FROM restaurants_agg "
            "WHERE pref = ? AND area2 IS NOT NULL GROUP BY area2 ORDER BY restaurants DESC LIMIT 30",
            (pref.strip().lower(),),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@mcp.tool
def list_genres(pref: str, area2: str | None = None) -> list[dict]:
    """해당 지역의 장르 목록(식당 수 상위 30). 장르는 일본어 (예: ラーメン, 寿司, 焼肉, イタリアン)."""
    q = (
        "SELECT g.genre, COUNT(DISTINCT r.restaurant_id) AS restaurants "
        "FROM restaurants_agg r JOIN restaurant_genres g ON g.restaurant_id = r.restaurant_id "
        "WHERE r.pref = ?"
    )
    params: list = [pref.strip().lower()]
    if area2:
        q += " AND r.area2 LIKE ?"
        params.append(f"%{area2}%")
    q += " GROUP BY g.genre ORDER BY restaurants DESC LIMIT 30"
    conn = _db()
    try:
        return [dict(r) for r in conn.execute(q, params).fetchall()]
    finally:
        conn.close()


@mcp.tool
def search_restaurants(
    pref: str,
    area2: str | None = None,
    area3: str | None = None,
    genre: str | None = None,
    station: str | None = None,
    keyword: str | None = None,
    max_dinner_budget: int | None = None,
    min_reviews: int | None = None,
    min_bayes: float | None = None,
    sort: str = "bayes",
    limit: int = 8,
) -> list[dict]:
    """타베로그 고신뢰 리뷰어 데이터(유니크 45,725곳)에서 식당을 검색한다.

    추천할 식당은 반드시 이 도구의 결과에서만 골라야 한다.
    - pref: 지역 코드(필수, 예: tokyo). area2/area3: 세부지역 부분일치(일본어).
    - genre: 장르 부분일치(일본어, 예: ラーメン). station: 역 이름 부분일치(예: 新宿).
    - keyword: 식당 이름 부분일치 — 사용자가 지정한 특정 식당을 찾을 때 사용.
    - max_dinner_budget: 저녁 1인 예산 상한(엔).
    - min_reviews: 리뷰 수 하한. min_bayes: 신뢰점수 하한 (품질 하한 게이트, 예: 50 / 3.4).
    - sort: bayes(기본, 신뢰도 보정 랭킹)|rating|reviews.
    """
    q = f"SELECT {_SAFE_COLS}, {_GENRES_SUB} FROM restaurants_agg r WHERE 1=1"
    params: list = []
    if pref:
        q += " AND r.pref = ?"
        params.append(pref.strip().lower())
    for col, val in (("r.area2", area2), ("r.area3", area3), ("r.name", keyword)):
        if val:
            q += f" AND {col} LIKE ?"
            params.append(f"%{val}%")
    if genre:
        q += (" AND EXISTS (SELECT 1 FROM restaurant_genres g "
              "WHERE g.restaurant_id = r.restaurant_id AND g.genre LIKE ?)")
        params.append(f"%{genre}%")
    if station:
        q += " AND r.stations_json LIKE ?"
        params.append(f"%{station}%")
    if max_dinner_budget:
        q += " AND r.budget_dinner_floor IS NOT NULL AND r.budget_dinner_floor <= ?"
        params.append(int(max_dinner_budget))
    if min_reviews:
        q += " AND r.tabelog_review_count >= ?"
        params.append(int(min_reviews))
    if min_bayes:
        q += " AND r.bayes_score IS NOT NULL AND r.bayes_score >= ?"
        params.append(float(min_bayes))
    q += f" ORDER BY {_SORTS.get(sort, _SORTS['bayes'])} LIMIT ?"
    params.append(max(1, min(int(limit), 20)))
    conn = _db()
    try:
        return [_row(r) for r in conn.execute(q, params).fetchall()]
    finally:
        conn.close()


@mcp.tool
def get_restaurant(restaurant_id: str) -> dict:
    """restaurant_id로 식당 1곳을 조회한다 (존재 검증 + 상세 + 링크). 없으면 found=false."""
    conn = _db()
    try:
        r = conn.execute(
            f"SELECT {_SAFE_COLS}, {_GENRES_SUB} FROM restaurants_agg r WHERE r.restaurant_id = ?",
            (restaurant_id,),
        ).fetchone()
        return {"found": True, **_row(r)} if r else {"found": False, "restaurant_id": restaurant_id}
    finally:
        conn.close()


# ---------- 라이브러리 함수 (파이프라인 결정론 코드용, LLM 비경유) ----------

# 이 fastmcp 버전의 @mcp.tool은 원본 함수를 그대로 반환한다 — 결정론 백필에서 직접 호출
search_lib = search_restaurants

def fetch_by_ids(ids: list[str]) -> dict[str, dict]:
    """restaurant_id → 안전 필드 dict. 화면 표시 데이터는 전부 여기서 조인한다(LLM 전사 금지)."""
    ids = [i for i in dict.fromkeys(ids) if i]
    if not ids:
        return {}
    qmarks = ",".join("?" * len(ids))
    conn = _db()
    try:
        rows = conn.execute(
            f"SELECT {_SAFE_COLS}, {_GENRES_SUB} FROM restaurants_agg r WHERE r.restaurant_id IN ({qmarks})",
            ids,
        ).fetchall()
        return {r["restaurant_id"]: _row(r) for r in rows}
    finally:
        conn.close()


def pref_codes() -> list[tuple[str, int]]:
    conn = _db()
    try:
        return [
            (r["pref"], r["restaurants"])
            for r in conn.execute(
                "SELECT pref, COUNT(*) AS restaurants FROM restaurants_agg GROUP BY pref ORDER BY restaurants DESC"
            ).fetchall()
        ]
    finally:
        conn.close()


def db_stats() -> dict:
    conn = _db()
    try:
        n = conn.execute("SELECT COUNT(*) FROM restaurants_agg").fetchone()[0]
        p = conn.execute("SELECT COUNT(DISTINCT pref) FROM restaurants_agg").fetchone()[0]
        return {"restaurants": n, "prefs": p}
    finally:
        conn.close()
