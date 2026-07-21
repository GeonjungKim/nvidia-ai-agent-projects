"""역 좌표·거리·하루 동선 — 결정론 유틸.

계산은 코드로, 판단은 LLM으로 (Day7 Lab7 교훈).
좌표 출처: Tabelog_Recommendation/data/station_coords.json (1,142역, 사전 검증).
"""
from __future__ import annotations

import json
import math
from functools import lru_cache

from tabetabi.config import STATION_COORDS_PATH
from tabetabi.links import build_route_url


@lru_cache(maxsize=1)
def _coords() -> dict[str, dict]:
    if not STATION_COORDS_PATH.exists():
        return {}
    return json.loads(STATION_COORDS_PATH.read_text(encoding="utf-8"))


def station_latlng(station: str) -> tuple[float, float] | None:
    """역 이름(일본어) → (lat, lng). 정확 일치 → 안전한 접두/접미 변형만 허용.

    느슨한 부분일치(station in name)는 현(縣)을 건너뛰는 오매칭을 낳는다 — 실측: 深川(도쿄,
    좌표 없음)이 上深川(히로시마)에 매칭돼 665km 오차. 그래서 '○○駅'·'○○前' 같은 접미 변형과
    'query로 시작하는' 후보까지만 허용하고, query가 다른 역명의 '뒷부분'인 경우(上深川)는 배제한다.
    """
    table = _coords()
    hit = table.get(station)
    if hit is None and station:
        # 1) query 자체의 접미 변형 (深川駅·新宿前 등)이 테이블에 있으면 사용
        for suffix in ("駅", "前", "駅前"):
            hit = table.get(station + suffix)
            if hit:
                break
    if hit is None and station and len(station) >= 2:
        # 2) query로 '시작하는' 역만 허용 (표참도→表参道○). 뒷부분 일치(上深川)는 다른 역이라 배제
        cand = [(name, v) for name, v in table.items() if name.startswith(station)]
        if cand:
            hit = min(cand, key=lambda kv: len(kv[0]))[1]   # 가장 짧은 = 가장 근접한 역명
    if hit is None:
        return None
    return float(hit["lat"]), float(hit["lng"])


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def order_day_route(places: list[dict], keep_order: bool = False) -> dict:
    """하루 방문지들의 동선을 만든다 (구글지도 경유지 URL 포함).

    places: [{"name": str, "station": str}] — 시간 순서 후보(첫 항목이 출발점).
    keep_order=True면 주어진 순서(식사 시간순)를 유지하고 거리만 계산한다.
    False면 최근접 이웃(NN)으로 재정렬한다 (시간 제약 없는 방문지용).
    좌표가 없는 곳은 원래 순서를 유지한 채 뒤에 붙인다(fail-soft).
    """
    with_c, without_c = [], []
    for p in places:
        ll = station_latlng(p.get("station") or "")
        (with_c if ll else without_c).append({**p, "latlng": ll})

    if keep_order or len(with_c) <= 2:
        ordered = list(with_c)
    else:
        rest = with_c[1:]
        cur = with_c[0]
        ordered = [cur]
        while rest:
            nxt = min(rest, key=lambda q: haversine_km(cur["latlng"], q["latlng"]))
            rest.remove(nxt)
            ordered.append(nxt)
            cur = nxt
    ordered += without_c

    legs = []
    for a, b in zip(ordered, ordered[1:]):
        km = round(haversine_km(a["latlng"], b["latlng"]), 1) if a.get("latlng") and b.get("latlng") else None
        legs.append({"from": a["name"], "to": b["name"], "approx_km": km})

    url = build_route_url(
        [{"name": p["name"], "stations": [p["station"]]} for p in ordered if p.get("station")],
        n=max(len(ordered), 1),
    )
    return {
        "order": [p["name"] for p in ordered],
        "route_url": url,
        "legs": legs,
        "points": [{"name": p["name"], "lat": p["latlng"][0], "lon": p["latlng"][1]}
                   for p in ordered if p.get("latlng")],
    }
