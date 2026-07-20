"""Google Places 연동 (선택 기능) — DB 미등록 장소의 정식 명칭·주소·정확한 지도 핀.

문제: 쿼리 문자열 지도 검색(`maps/search/?query=이름`)은 표기가 조금만 달라도 엉뚱한
다수 결과를 보여준다 (실측: '豚カツナナイド Tokyo' 핀 실패). Places Text Search는
정식 명칭과 googleMapsUri(핀 확정 링크)를 돌려줘 이 문제를 근본 해결한다.

GOOGLE_MAPS_API_KEY 미설정이면 모든 함수가 None — 기존 링크 폴백이 그대로 동작한다
(fail-soft). 결과는 메모리 캐시로 반복 과금을 막는다.
"""
from __future__ import annotations

import os

_cache: dict[str, dict | None] = {}

_ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
_FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.location,places.googleMapsUri"


def places_enabled() -> bool:
    return bool(os.getenv("GOOGLE_MAPS_API_KEY"))


def places_resolve(name: str, area: str = "", city: str = "") -> dict | None:
    """장소 이름 → Places Text Search 1건. 실패·키 없음·결과 없음은 전부 None (fail-soft).

    반환: {"name", "address", "lat", "lng", "maps_url", "place_id"}
    """
    key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    name = (name or "").strip()
    if not key or not name:
        return None
    q = " ".join(x for x in (name, area, city) if x)
    if q in _cache:
        return _cache[q]
    out: dict | None = None
    try:
        import httpx
        resp = httpx.post(
            _ENDPOINT,
            headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": _FIELD_MASK,
                     "Content-Type": "application/json"},
            json={"textQuery": q, "languageCode": "ja", "pageSize": 1},
            timeout=8.0,
        )
        resp.raise_for_status()
        places = resp.json().get("places") or []
        if places:
            p = places[0]
            loc = p.get("location") or {}
            out = {
                "name": (p.get("displayName") or {}).get("text", ""),
                "address": p.get("formattedAddress", ""),
                "lat": loc.get("latitude"), "lng": loc.get("longitude"),
                "maps_url": p.get("googleMapsUri", ""),
                "place_id": p.get("id", ""),
            }
    except Exception:
        out = None                     # 네트워크·쿼터·권한 오류 → 조용히 폴백 (일정 생성은 계속)
    _cache[q] = out
    return out
