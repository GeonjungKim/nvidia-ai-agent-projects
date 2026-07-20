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


# 도쿄 노선 한정 — 공항 선택 팁 (D7 메타서치 벤치마킹: 캐치프로그류의 판단 보조 가치)
_AIRPORT_TIP = "✈️ 공항 선택 팁 — 김포~하네다: 도심 접근 우위(하네다는 도쿄 시내와 가까움) · 인천~나리타: 대체로 가격 우위 경향."


def flight_links(origin: str, pref: str, depart: str, ret: str, party: int = 2) -> dict:
    """항공권 '검색' 딥링크 — 날짜·구간이 반영된 검색 결과 페이지로 이동한다 (D7 v2: 4종 링크).

    ①특정일 Google Flights ②스카이스캐너 월 전체 가격 캘린더(YYMM만 넘기면 달력 뷰) ③가격 알림 안내
    ④네이버 항공권·트립닷컴·마이리얼트립 — 이 3곳은 각 사이트의 정확한 파라미터 스키마를 보증할 수
    없어(운영 중 자주 바뀜) 그 사이트로 바로 들어가는 '검색' 링크로 둔다 — 존재하지 않는 파라미터로
    빈 화면이 뜨는 것보다, 사이트 진입 후 사용자가 직접 검색하는 편이 더 정직하다.
    """
    city_ko, city_en = city_of(pref)
    q = f"Flights from {origin} to {city_en} on {depart} through {ret}"
    out = {
        "google_flights": "https://www.google.com/travel/flights?q=" + urllib.parse.quote(q),
        "label": f"{origin} → {city_ko} ({depart} ~ {ret})",
        "price_alert": "🔔 가격 알림 — Google Flights 결과 페이지에서 '가격 추적'을 켜면 이 노선의 가격 변동을 이메일로 받아볼 수 있어요.",
        "naver": "https://search.naver.com/search.naver?query=" + urllib.parse.quote(f"네이버항공권 {origin} {city_ko} {depart} {ret}"),
        "trip_com": "https://www.google.com/search?q=" + urllib.parse.quote(f"site:trip.com {origin} {city_en} flights {depart}"),
        "myrealtrip": "https://www.google.com/search?q=" + urllib.parse.quote(f"site:myrealtrip.com {origin} {city_ko} 항공권 {depart}"),
    }
    if city_ko == "도쿄":
        out["airport_tip"] = _AIRPORT_TIP
    o, d = _SKY_CODE.get(origin), _SKY_CODE.get(city_ko)
    if o and d:
        d1 = depart.replace("-", "")[2:]   # YYMMDD
        d2 = ret.replace("-", "")[2:]
        out["skyscanner"] = f"https://www.skyscanner.co.kr/transport/flights/{o}/{d}/{d1}/{d2}/"
        m1, m2 = depart.replace("-", "")[2:6], ret.replace("-", "")[2:6]   # YYMM — 월 단위만 주면 캘린더 뷰
        out["skyscanner_month"] = f"https://www.skyscanner.co.kr/transport/flights/{o}/{d}/{m1}/{m2}/"
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
