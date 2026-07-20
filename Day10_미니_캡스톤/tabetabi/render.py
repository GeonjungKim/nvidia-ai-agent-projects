"""일정표 렌더링 — Streamlit UI와 CLI 데모가 같은 마크다운을 공유한다.

하루를 시간대 타임라인(오전 활동 → 점심 → 카페 → 오후 활동 → 저녁)으로 배치하고,
역좌표 거리 기반 도보/전철 이동 힌트를 붙인다.
"""
from __future__ import annotations

SLOT_KO = {"lunch": "점심", "cafe": "카페", "dinner": "저녁"}
SLOT_TIME = {"lunch": "12:00", "cafe": "15:00", "dinner": "18:30"}
SLOT_EMOJI = {"lunch": "🍜", "cafe": "☕", "dinner": "🍣"}
ACT_TIMES = ["10:00", "16:30", "20:30"]


def _meal_lines(m: dict) -> list[str]:
    t = SLOT_TIME.get(m.get("slot"), "")
    emoji = SLOT_EMOJI.get(m.get("slot"), "🍽️")
    lock = "🔒 " if m.get("locked") else ""
    slot = SLOT_KO.get(m.get("slot"), m.get("slot"))
    if m.get("external"):
        return [f"- **{t}** {emoji} {lock}**{slot}** · **{m['name']}** (사용자 지정 장소) · [📍 지도]({m['gmap']})"]
    rating = f"★{m['rating']}" if m.get("rating") else "★-"
    reviews = f"{m['reviews']:,}" if m.get("reviews") else "0"
    bayes = f" · 신뢰점수 {m['bayes']}" if m.get("bayes") else ""
    budget = f" · {m['budget']}" if m.get("budget") else ""
    station = f" · {m['station']}역" if m.get("station") else ""
    lines = [
        f"- **{t}** {emoji} {lock}**{slot}** · [{m['name']}]({m['tabelog_url']}) — {m.get('genres', '')}"
        f" · {rating}({reviews}){bayes}{budget}{station} · [📍 지도]({m['gmap']})"
    ]
    if m.get("reason"):
        lines.append(f"  - _{m['reason']}_")
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
        L.append(f"### Day {d['day']} · {d.get('date', '')}")

        # 타임라인: 오전 활동 → 점심 → 카페 → 오후 활동 → 저녁 → (야간 활동)
        acts = list(d.get("activities") or [])
        meals = {m.get("slot"): m for m in d.get("meals", [])}
        entries: list[tuple[str, list[str]]] = []
        for i, a in enumerate(acts[:3]):
            t = ACT_TIMES[i] if i < len(ACT_TIMES) else "21:00"
            why = f" — {a['why']}" if a.get("why") else ""
            entries.append((t, [f"- **{t}** 🎡 [{a.get('title', '활동')}]({a.get('url', '')}){why}"]))
        for slot, m in meals.items():
            entries.append((SLOT_TIME.get(slot, "23:00"), _meal_lines(m)))
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
