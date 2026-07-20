"""앵커 해석기 — 앵커 문자열을 '검증된 DB 검색 키'로 바꾸는 결정론 유틸 (D2, 원인 R2).

핵심 관측(실측): restaurants_agg의 area2에는 동네 단위 지명(表参道·青山·原宿·駒込)이 없다.
동네 앵커는 area2가 아니라 '역 검색(stations_json LIKE)'이 정답이다.
그래서 LLM(@foodie)에게 area2를 지어내게 두지 않고, 코드가 검색 키를 확정해 task 데이터로 주입한다.

계산은 코드로, 판단은 LLM으로 (Day7 교훈).
"""
from __future__ import annotations

from functools import lru_cache

from tabetabi.geo import haversine_km, station_latlng, _coords
from tabetabi.tools.tabelog_server import _db

CLUSTER_RADIUS_KM = 4.0   # 이탈 게이트 임계 — 앵커 역에서 이 거리 초과면 '이탈'


def _count(pref: str, col_sql: str, value: str) -> int:
    conn = _db()
    try:
        return conn.execute(
            f"SELECT COUNT(*) FROM restaurants_agg WHERE pref = ? AND {col_sql} LIKE ?",
            (pref.strip().lower(), f"%{value}%"),
        ).fetchone()[0]
    finally:
        conn.close()


def _nearby_station_names(anchor: str, limit: int = 5) -> list[str]:
    """앵커와 문자열이 부분일치하거나, 좌표가 가까운 역 후보를 station_coords에서 찾는다."""
    coords = _coords()
    # 1) 이름 부분일치
    partial = [name for name in coords if anchor and (anchor in name or name in anchor)]
    if partial:
        return partial[:limit]
    return []


@lru_cache(maxsize=256)
def resolve_anchor(pref: str, anchor: str) -> dict:
    """앵커 문자열 → 검색 키 결정 (결정론).

    반환: {
      "anchor": 원문, "key_type": "area2"|"station"|"fuzzy"|"none",
      "search_kwargs": {검증된 검색 키} (예: {"station": "表参道"}),
      "count": 매칭 식당 수, "suggestions": [인접 역 후보] (fuzzy일 때),
      "log": 로그 한 줄
    }
    """
    anchor = (anchor or "").strip()
    if not anchor:
        return {"anchor": anchor, "key_type": "none", "search_kwargs": {}, "count": 0,
                "suggestions": [], "log": "[앵커] (빈 앵커)"}

    # 1) area2 정확/LIKE 매치
    n_area2 = _count(pref, "area2", anchor)
    if n_area2 > 0:
        return {"anchor": anchor, "key_type": "area2", "search_kwargs": {"area2": anchor},
                "count": n_area2, "suggestions": [],
                "log": f"[앵커] {anchor} → area2 검색 {n_area2:,}곳"}

    # 2) station LIKE (실측상 동네 단위는 대부분 이 경로)
    n_station = _count(pref, "stations_json", anchor)
    if n_station > 0:
        return {"anchor": anchor, "key_type": "station", "search_kwargs": {"station": anchor},
                "count": n_station, "suggestions": [],
                "log": f"[앵커] {anchor} → station 검색 {n_station:,}곳"}

    # 3) 둘 다 실패 → 인접 역 후보 제시 (부분일치)
    sugg = _nearby_station_names(anchor)
    if sugg:
        return {"anchor": anchor, "key_type": "fuzzy", "search_kwargs": {"station": sugg[0]},
                "count": 0, "suggestions": sugg,
                "log": f"[앵커] {anchor} → 직접 매칭 실패, 인접 역 후보 {sugg[:3]}"}
    return {"anchor": anchor, "key_type": "none", "search_kwargs": {}, "count": 0,
            "suggestions": [], "log": f"[앵커] {anchor} → 매칭 실패 (전 지역 검색으로 폴백)"}


def anchor_latlng(pref: str, anchor: str) -> tuple[float, float] | None:
    """앵커의 대표 좌표 = 앵커 역 좌표 (external 장소 좌표 근사·이탈 판정에 사용)."""
    ll = station_latlng(anchor)
    if ll:
        return ll
    r = resolve_anchor(pref, anchor)
    for s in r.get("suggestions") or []:
        ll = station_latlng(s)
        if ll:
            return ll
    return None


def deviation_km(pref: str, anchor: str, station: str) -> float | None:
    """픽의 최기역이 앵커 역에서 몇 km 떨어졌는지 (직선거리). 좌표 없으면 None."""
    a = anchor_latlng(pref, anchor)
    b = station_latlng(station) if station else None
    if not a or not b:
        return None
    return round(haversine_km(a, b), 1)


def off_anchor_label(km: float | None) -> str:
    """이탈 거리 → 카드 라벨. 임계 이내면 빈 문자열."""
    if km is None or km <= CLUSTER_RADIUS_KM:
        return ""
    mins = max(round(km * 3), 5)   # 대략 전철 3분/km 추정 (환승 포함 보수적)
    return f"⚠️ 앵커에서 벗어남 (전철 ~{mins}분, 직선 {km}km)"
