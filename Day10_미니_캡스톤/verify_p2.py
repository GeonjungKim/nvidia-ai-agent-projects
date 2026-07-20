"""P2 수용 기준 검증 하니스 (DESIGN_V2_SPEC D7 결정론 부분).

D7의 '부터 단일가 금지'·'링크 4종'은 코드(links.py·_sanitize_flight)가 결정론으로 보장하는
부분만 이 하니스로 검증한다. @scout이 실제로 2회 검색해 좋은 범위·기준선을 만드는지는 LLM
경유라 이 하니스로 검증 불가 — run_demo.py E2E로 확인해야 한다 (P0/P1과 동일한 한계).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("NVIDIA_API_KEY", "dummy-key-for-import-only")
sys.path.insert(0, str(Path(__file__).resolve().parent))

results: list[tuple[str, str, bool, str]] = []


def check(dcode: str, crit: str, cond: bool, detail: str = "") -> None:
    results.append((dcode, crit, bool(cond), detail))


from tabetabi.agents.concierge import _sanitize_flight
from tabetabi.links import flight_links

# ---- _sanitize_flight: '부터' 단일가 유출 차단 ----
only_low = _sanitize_flight({"low": 250000, "high": 0, "baseline": "가짜기준선"})
check("D7", "low만 있고 high가 없으면 range_krw를 비운다 (단일가 유출 차단)",
      only_low["range_krw"] == "" and only_low["low"] is None, str(only_low))

both = _sanitize_flight({"low": 250000, "high": 450000, "baseline": "20만 초반이면 저렴", "note": "성수기"})
check("D7", "low·high 둘 다 있으면 '약 N~M원' 범위 문자열을 만든다",
      both["range_krw"] == "약 250,000~450,000원", str(both))

swapped = _sanitize_flight({"low": 450000, "high": 250000})
check("D7", "low>high로 뒤바뀌어 와도 정렬해서 바로잡는다", swapped["low"] == 250000 and swapped["high"] == 450000, str(swapped))

garbage = _sanitize_flight({"low": "모름", "high": None})
check("D7", "숫자가 아닌 값은 안전하게 빈 범위로 처리 (예외 없이 fail-soft)", garbage["range_krw"] == "", str(garbage))

# ---- flight_links: 링크 4종 + 공항 팁 ----
fl = flight_links("서울", "tokyo", "2026-08-22", "2026-08-24", 2)
check("D7", "특정일 링크(Google Flights) 존재", bool(fl.get("google_flights")), "")
check("D7", "스카이스캐너 월 캘린더 링크 존재 (YYMM 포맷)", bool(fl.get("skyscanner_month")), fl.get("skyscanner_month", ""))
check("D7", "비교 링크 2종 이상 (네이버·트립닷컴·마이리얼트립)",
      sum(bool(fl.get(k)) for k in ("naver", "trip_com", "myrealtrip")) >= 2, str(fl))
check("D7", "가격 알림 안내 문구 존재", bool(fl.get("price_alert")), "")
check("D7", "도쿄 노선 → 공항 선택 팁(김포~하네다/인천~나리타) 존재",
      "하네다" in fl.get("airport_tip", "") and "나리타" in fl.get("airport_tip", ""), fl.get("airport_tip", ""))

fl_osaka = flight_links("서울", "osaka", "2026-08-22", "2026-08-24", 2)
check("D7", "도쿄가 아닌 노선엔 공항 팁을 억지로 안 붙인다 (거짓 정밀도 방지)", "airport_tip" not in fl_osaka, "")

# ---- render.py가 범위·기준선·링크를 실제로 렌더하는지 (구조 확인) ----
from tabetabi.render import itinerary_md

fake_it = {"days": [], "stats": {}, "flights": {**fl, "range_krw": "약 250,000~450,000원",
                                                 "baseline": "20만원대 초반이면 저렴", "note": "성수기"}}
md = itinerary_md(fake_it)
check("D7", "렌더 결과에 '부터'가 없다 (단일가 표기 금지 수용 기준)", "부터" not in md, "")
check("D7", "렌더 결과에 범위·기준선이 포함된다", "250,000~450,000원" in md and "20만원대 초반" in md, "")
check("D7", "렌더 결과에 링크 4종 텍스트가 포함된다 (특정일/월캘린더/네이버/트립닷컴 등)",
      all(x in md for x in ("특정일", "월 캘린더", "네이버 항공권")), "")

print("\n" + "=" * 72)
print("  P2 수용 기준 검증 체크리스트 (D7 결정론 부분)")
print("=" * 72)
cur = None
npass = 0
for dcode, crit, ok, detail in results:
    if dcode != cur:
        print(f"\n[{dcode}]")
        cur = dcode
    print(f"  {'v' if ok else 'x FAIL'}  {crit}")
    if not ok and detail:
        print(f"        L {detail}")
    npass += ok
print("\n" + "-" * 72)
print(f"  통과 {npass}/{len(results)}")
print("-" * 72)
sys.exit(0 if npass == len(results) else 1)
