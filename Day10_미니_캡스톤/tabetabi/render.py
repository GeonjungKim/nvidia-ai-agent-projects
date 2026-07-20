"""일정표 렌더링 — Streamlit UI와 CLI 데모가 같은 마크다운을 공유한다.

하루를 시간대 타임라인(오전 활동 → 점심 → 카페 → 오후 활동 → 저녁)으로 배치하고,
역좌표 거리 기반 도보/전철 이동 힌트를 붙인다.
"""
from __future__ import annotations

SLOT_KO = {"lunch": "점심", "cafe": "카페", "dinner": "저녁"}
SLOT_TIME = {"lunch": "12:00", "cafe": "15:00", "dinner": "18:30"}
SLOT_EMOJI = {"lunch": "🍜", "cafe": "☕", "dinner": "🍣"}
ACT_SLOT_EMOJI = {"morning": "🌅", "late_afternoon": "🏙️", "evening": "🌃"}


def _alt_line(alts: list[dict]) -> str:
    """대안 후보 1줄 — 카드 안에서 바로 갈아탈 수 있게 (별도 섹션으로 숨기지 않는다)."""
    parts = []
    for a in alts[:3]:
        station = f" · {a['station']}역" if a.get("station") else ""
        rating = f" ★{a['rating']}" if a.get("rating") else ""
        parts.append(f"[{a['name']}]({a.get('tabelog_url') or a.get('gmap', '')}){rating}{station}")
    return "  - 🔀 다른 후보: " + " / ".join(parts)


def _meal_lines(m: dict) -> list[str]:
    t = m.get("time") or SLOT_TIME.get(m.get("slot"), "")   # 시간창 기반 동적 시각 우선
    emoji = SLOT_EMOJI.get(m.get("slot"), "🍽️")
    lock = "🔒 " if m.get("locked") else ""
    slot = SLOT_KO.get(m.get("slot"), m.get("slot"))
    if m.get("external"):
        web = f" · [🔎 웹 검색]({m['web']})" if m.get("web") else ""
        map_label = "📍 지도" if m.get("pin_verified") else "📍 지도 검색"
        lines = [f"- **{t}** {emoji} {lock}**{slot}** · **{m['name']}** · [{map_label}]({m['gmap']}){web}"]
        if m.get("pin_verified"):     # Places 확인됨 — 정확한 핀. 주소·정식 표기를 근거로 제시
            detail = " · ".join(x for x in (
                f"지도 표기: {m['canonical']}" if m.get("canonical") else "",
                m.get("address") or "") if x)
            lines.append(f"  - ✅ 구글 지도에서 위치 확인됨{(' — ' + detail) if detail else ''} "
                         "(타베로그 DB 미등록 — 평점·휴무는 검증 불가)")
        else:
            lines.append("  - ⚠️ 타베로그 DB 미등록 — 평점·휴무 검증 불가. 이름 표기가 다르면 지도 검색이 "
                         "엉뚱한 곳을 보여줄 수 있으니 웹 검색으로 교차 확인하세요.")
        for s in (m.get("suggestions") or [])[:2]:   # 4단계 매칭의 근접 후보 — "혹시 이 곳?"
            rating = f"★{s['rating']}" if s.get("rating") else "★-"
            station = f" · {s['station']}역" if s.get("station") else ""
            gmap = f" · [📍 지도]({s['gmap']})" if s.get("gmap") else ""
            lines.append(f"  - 🔍 혹시 이 곳 아닌가요? [{s['name']}]({s.get('tabelog_url', '')}) — "
                         f"{rating}{station}{gmap} · 맞다면 채팅에 \"고정 식당을 {s['name']}(으)로 바꿔줘\"라고 말씀해 주세요")
        return lines
    rating = f"★{m['rating']}" if m.get("rating") else "★-"
    reviews = f"{m['reviews']:,}" if m.get("reviews") else "0"
    bayes = f" · 신뢰점수 {m['bayes']}" if m.get("bayes") else ""
    budget = f" · {m['budget']}" if m.get("budget") else ""
    station = f" · {m['station']}역" if m.get("station") else ""
    lines = [
        f"- **{t}** {emoji} {lock}**{slot}** · [{m['name']}]({m['tabelog_url']}) — {m.get('genres', '')}"
        f" · {rating}({reviews}){bayes}{budget}{station} · [📍 지도]({m['gmap']})"
    ]
    if m.get("off_anchor"):                       # 앵커 이탈 라벨 강제 표기 (D2, 조용한 이탈 금지)
        lines.append(f"  - {m['off_anchor']}")
    if m.get("relaxed"):                          # 품질 하한 완화 사유 라벨 (D5)
        lines.append("  - ⚠️ 데이터 희소 지역 — 품질 기준 완화 적용")
    closed = m.get("closed")
    if closed and "無休" not in closed:           # 정기휴무 표기 + 방문일 겹침 경고 (결정론 대조)
        if m.get("closed_warn"):
            lines.append(f"  - 🚨 **정기휴무 {closed} — 방문일과 겹칠 수 있어요!** 예약·방문 전 꼭 확인하세요")
        else:
            lines.append(f"  - 🗓️ 정기휴무: {closed}")
    if m.get("reason"):
        lines.append(f"  - _{m['reason']}_")
    if m.get("alternatives"):                     # 대안을 카드 안에 인라인 — 클릭 한 번 거리로 (UX)
        lines.append(_alt_line(m["alternatives"]))
    return lines


def _activity_lines(a: dict) -> list[str]:
    """활동 카드 — 슬롯 시각·why + tip 1줄(필수)·영업시간/입장마감(있으면) (D3)."""
    t = a.get("time") or "10:00"
    emoji = ACT_SLOT_EMOJI.get(a.get("slot"), "🎡")
    why = f" — {a['why']}" if a.get("why") else ""
    title = a.get("title", "활동")
    head = f"- **{t}** {emoji} [{title}]({a.get('url', '')}){why}" if a.get("url") \
        else f"- **{t}** {emoji} **{title}**{why}"
    lines = [head]
    hours = []
    if a.get("open_hours"):
        hours.append(f"영업 {a['open_hours']}")
    if a.get("last_entry"):
        hours.append(f"입장마감 {a['last_entry']}")
    if a.get("dwell_min"):
        hours.append(f"체류 ~{a['dwell_min']}분")
    if hours:
        lines.append("  - 🕒 " + " · ".join(hours))
    if a.get("tip"):                              # tip 1줄 필수 (D3 수용 기준)
        lines.append(f"  - 💡 {a['tip']}")
    return lines


def _walk_hint(km) -> str:
    if km is None:
        return ""
    if km <= 2.2:
        return f"도보 ~{max(round(km * 13), 3)}분"
    return f"전철 권장 (~{km}km)"


def itinerary_md(it: dict) -> str:
    L = ["## 🗾 TabeTabi 여행 일정"]
    s = it.get("stats") or {}
    if s:
        gate = "통과 ✅" if s.get("critic_pass") else "지적 ⚠️"
        L.append(
            f"`🤖 에이전트 작업 요약`  @foodie 후보 **{s.get('foodie_candidates', 0)}곳** 검토 → 식사 **{s.get('meals', 0)}슬롯** 확정"
            f" · @scout 활동 **{s.get('activities', 0)}건** + 호텔 **{s.get('hotel_picks', 0)}곳** 조사"
            f" · @critic 식당 **{s.get('verified', 0)}곳** 실존 검증 {gate}"
        )
    if it.get("comment"):
        L.append(f"> {it['comment']}")
    if it.get("weather"):
        L.append(f"**🌤️ 날씨** — {it['weather']}")

    for d in it.get("days", []):
        anchor = f" · 🧭 {d['anchor']}" if d.get("anchor") else ""
        L.append(f"### Day {d['day']} · {d.get('date', '')}{anchor}")
        if d.get("banner"):                       # 항공 시간 가정/반영 배너 (조용한 가정 금지)
            L.append(f"> {d['banner']}")

        # 타임라인: 슬롯 시각으로 활동·식사를 한 줄에 정렬 (D3 스케줄 결과 사용)
        entries: list[tuple[str, list[str]]] = []
        for a in (d.get("activities") or []):
            entries.append((a.get("time") or "10:00", _activity_lines(a)))
        for m in d.get("meals", []):
            entries.append((m.get("time") or SLOT_TIME.get(m.get("slot"), "23:00"), _meal_lines(m)))
        entries.sort(key=lambda e: e[0])
        for _, lines in entries:
            L.extend(lines)

        r = d.get("route") or {}
        legs = r.get("legs") or []
        if legs:
            parts = [f"{leg['from']} → {leg['to']} ({_walk_hint(leg.get('approx_km'))})" for leg in legs]
            link = f" · [🗺️ 경로 열기]({r['route_url']})" if r.get("route_url") else ""
            L.append("- 🚶 **동선(최근접 정렬)** — " + "  ·  ".join(parts) + link)
        elif r.get("route_url"):
            L.append(f"- 🚶 [하루 동선 경로 열기]({r['route_url']})")

    # 종일형 POI는 슬롯에 넣지 않고 별도 섹션으로만 노출한다 (D3, 예약·오픈런 팁 동반)
    allday = it.get("allday_options") or []
    if allday:
        L.append("### 🎢 하루를 통째로 쓰는 옵션 (테마파크 등 — 슬롯 배정 제외)")
        for a in allday:
            why = f" — {a['why']}" if a.get("why") else ""
            title = a.get("title", "옵션")
            head = f"- [{title}]({a['url']}){why}" if a.get("url") else f"- **{title}**{why}"
            L.append(head)
            tip = a.get("tip") or "예약·오픈런 필수 — 이 일정은 하루 전체를 씁니다."
            L.append(f"  - 💡 {tip}")

    f = it.get("flights") or {}
    if f.get("google_flights"):
        L.append(f"### ✈️ 항공 — {f.get('label', '')}")
        if f.get("range_krw"):        # D7: 단일 '부터'가 아니라 2소스 기반 범위 (부터 표기 금지)
            note = f" ({f['note']})" if f.get("note") else ""
            L.append(f"- 💰 **왕복 시세** {f['range_krw']}{note}")
        if f.get("baseline"):         # D7: 판단 기준선 1줄
            L.append(f"- 💡 {f['baseline']}")
        if f.get("airport_tip"):
            L.append(f"- {f['airport_tip']}")
        if f.get("price_alert"):
            L.append(f"- {f['price_alert']}")
        links = [f"[Google Flights(특정일)]({f['google_flights']})"]
        if f.get("skyscanner"):
            links.append(f"[스카이스캐너(특정일)]({f['skyscanner']})")
        if f.get("skyscanner_month"):
            links.append(f"[스카이스캐너(월 캘린더)]({f['skyscanner_month']})")
        if f.get("naver"):
            links.append(f"[네이버 항공권]({f['naver']})")
        if f.get("trip_com"):
            links.append(f"[트립닷컴]({f['trip_com']})")
        if f.get("myrealtrip"):
            links.append(f"[마이리얼트립]({f['myrealtrip']})")
        L.append(" · ".join(links))

    h = it.get("hotels") or {}
    if h.get("booking"):
        L.append(f"### 🏨 숙소 — {h.get('label', '')}")
        for p in h.get("picks") or []:
            why = f" — {p['why']}" if p.get("why") else ""
            L.append(f"- 🏷️ [{p.get('name', '호텔')}]({p.get('url', '')}){why}")
        L.append(f"[Booking.com 검색]({h['booking']}) · [Google Hotels 검색]({h['google_hotels']})")

    v = it.get("critic") or {}
    if v:
        checked = f"식당 {v.get('restaurants_checked', 0)}곳 + 활동 {v.get('activities_checked', 0)}건 판정"
        if v.get("pass"):
            L.append(f"✅ **@critic 검증 통과** ({checked}) — 실존·계약 준수·활동 근거 확인됨")
        else:
            L.append(f"⚠️ **@critic 지적사항** ({checked}) — " + "; ".join(map(str, v.get("issues", []))))
    return "\n\n".join(L)


def map_points(it: dict) -> list[dict]:
    pts, seen = [], set()
    for d in it.get("days", []):
        for p in (d.get("route") or {}).get("points", []):
            if p["name"] not in seen:
                seen.add(p["name"])
                pts.append(p)
    return pts
