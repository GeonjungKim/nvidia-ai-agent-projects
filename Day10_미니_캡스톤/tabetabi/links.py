"""외부 링크 생성 — Tabelog_Recommendation의 검증된 maplinks를 재사용하고,
항공/숙소 검색 딥링크(예약 아님)를 추가한다.
"""
from __future__ import annotations

import urllib.parse

try:
    # 재사용: Tabelog_Recommendation/app/maplinks.py (pytest 검증 완료, sys.path는 config가 준비)
    from app.maplinks import build_route_url, google_search_url  # type: ignore
except ImportError:  # 폴백 최소 구현 (원본과 동일 포맷)
    def google_search_url(name: str, station: str) -> str:
        q = urllib.parse.quote(f"{name} {station}駅")
        return "https://www.google.com/maps/search/?api=1&query=" + q

    def build_route_url(records, n: int = 5, travelmode: str = "walking") -> str:
        places = [f"{r['name']} {r['stations'][0]}駅" for r in records if r.get("stations")][:n]
        if not places:
            return ""
        parts = ["api=1", f"destination={urllib.parse.quote(places[-1])}"]
        if places[:-1]:
            parts.append(f"waypoints={urllib.parse.quote('|'.join(places[:-1]))}")
        parts.append(f"travelmode={travelmode}")
        return "https://www.google.com/maps/dir/?" + "&".join(parts)


# pref 코드 → (한국어, 영어) 도시명. 링크 텍스트/검색어용.
CITY_BY_PREF: dict[str, tuple[str, str]] = {
    "tokyo": ("도쿄", "Tokyo"), "osaka": ("오사카", "Osaka"), "kyoto": ("교토", "Kyoto"),
    "fukuoka": ("후쿠오카", "Fukuoka"), "hokkaido": ("삿포로", "Sapporo"), "okinawa": ("오키나와", "Okinawa"),
    "nagano": ("나가노", "Nagano"), "aichi": ("나고야", "Nagoya"), "hiroshima": ("히로시마", "Hiroshima"),
    "kanagawa": ("요코하마", "Yokohama"), "hyogo": ("고베", "Kobe"), "chiba": ("지바", "Chiba"),
}

# 스카이스캐너 도시/공항 코드 (소문자). 없는 도시는 구글 플라이트만 제공.
_SKY_CODE = {
    "서울": "icn", "인천": "icn", "김포": "gmp", "부산": "pus", "제주": "cju",
    "도쿄": "tyoa", "오사카": "osaa", "교토": "osaa", "후쿠오카": "fuk", "삿포로": "spk",
    "오키나와": "oka", "나고야": "ngo", "요코하마": "tyoa", "고베": "osaa", "히로시마": "hij",
}


def city_of(pref: str) -> tuple[str, str]:
    return CITY_BY_PREF.get(pref, (pref, pref))


def flight_links(origin: str, pref: str, depart: str, ret: str) -> dict:
    """항공권 '검색' 딥링크 — 날짜·구간이 반영된 검색 결과 페이지로 이동한다."""
    city_ko, city_en = city_of(pref)
    q = f"Flights from {origin} to {city_en} on {depart} through {ret}"
    out = {
        "google_flights": "https://www.google.com/travel/flights?q=" + urllib.parse.quote(q),
        "label": f"{origin} → {city_ko} ({depart} ~ {ret})",
    }
    o, d = _SKY_CODE.get(origin), _SKY_CODE.get(city_ko)
    if o and d:
        d1 = depart.replace("-", "")[2:]   # YYMMDD
        d2 = ret.replace("-", "")[2:]
        out["skyscanner"] = f"https://www.skyscanner.co.kr/transport/flights/{o}/{d}/{d1}/{d2}/"
    return out


def hotel_links(area: str, pref: str, checkin: str, checkout: str, adults: int = 2) -> dict:
    """숙소 '검색' 딥링크 — 지역·날짜·인원이 반영된 검색 결과 페이지로 이동한다."""
    city_ko, city_en = city_of(pref)
    ss = f"{area} {city_en}".strip() if area else city_en
    booking = (
        "https://www.booking.com/searchresults.ko.html?"
        + urllib.parse.urlencode({"ss": ss, "checkin": checkin, "checkout": checkout,
                                  "group_adults": adults, "no_rooms": 1, "group_children": 0})
    )
    ghotels = "https://www.google.com/travel/search?q=" + urllib.parse.quote(f"{ss} hotels")
    return {"booking": booking, "google_hotels": ghotels,
            "label": f"{area or city_ko} 숙소 ({checkin} ~ {checkout}, 성인 {adults})"}


def external_place_link(name: str, pref: str) -> str:
    """DB에 없는(사용자 지정) 장소용 구글지도 검색 링크."""
    _, city_en = city_of(pref)
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f"{name} {city_en}")
