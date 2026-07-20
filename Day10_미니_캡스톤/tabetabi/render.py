"""일정표 렌더링 — Streamlit UI와 CLI 데모가 같은 마크다운을 공유한다.

하루를 시간대 타임라인(오전 활동 → 점심 → 카페 → 오후 활동 → 저녁)으로 배치하고,
역좌표 거리 기반 도보/전철 이동 힌트를 붙인다.
"""
from __future__ import annotations

SLOT_KO = {"lunch": "점심", "cafe": "카페", "dinner": "저녁"}
SLOT_TIME = {"lunch": "12:00", "cafe": "15:00", "dinner": "18:30"}
SLOT_EMOJI = {"lunch": "🍜", "cafe": "☕", "dinner": "🍣"}
ACT_SLOT_EMOJI = {"morning": "🌅", "late_afternoon": "🏙️", "evening": "🌃"}


def _meal_lines(m: dict) -> list[str]:
    t = SLOT_TIME.get(m.get("slot"), "")
    emoji = SLOT_EMOJI.get(m.get("slot"), "🍽️")
    lock = "🔒 " if m.get("locked") else ""
    slot = SLOT_KO.get(m.get("slot"), m.get("slot"))
    if m.get("external"):
        note = f" · _{m['note']}_" if m.get("note") else " (사용자 지정 장소)"
        return [f"- **{t}** {emoji} {lock}**{slot}** · **{m['name']}**{note} · [📍 지도]({m['gmap']})"]
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
    if m.get("reason"):
        lines.append(f"  - _{m['reason']}_")
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

        # 타임라인: 슬롯 시각으로 활동·식사를 한 줄에 정렬 (D3 스케줄 결과 사용)
        entries: list[tuple[str, list[str]]] = []
        for a in (d.get("activities") or []):
            entries.append((a.get("time") or "10:00", _activity_lines(a)))
        for m in d.get("meals", []):
            entries.append((SLOT_TIME.get(m.get("slot"), "23:00"), _meal_lines(m)))
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
        if f.get("hint"):
            L.append(f"- 💡 {f['hint']}")
        links = [f"[Google Flights 검색]({f['google_flights']})"]
        if f.get("skyscanner"):
            links.append(f"[스카이스캐너 검색]({f['skyscanner']})")
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
        if v.get("pass"):
            L.append("✅ **@critic 검증 통과** — 추천 식당 실존·계약 준수 확인됨")
        else:
            L.append("⚠️ **@critic 지적사항** — " + "; ".join(map(str, v.get("issues", []))))
    return "\n\n".join(L)


def map_points(it: dict) -> list[dict]:
    pts, seen = [], set()
    for d in it.get("days", []):
        for p in (d.get("route") or {}).get("points", []):
            if p["name"] not in seen:
                seen.add(p["name"])
                pts.append(p)
    return pts
