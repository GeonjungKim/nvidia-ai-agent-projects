"""@scout — 여행 리서처 (도구: 웹검색 MCP만).

권한 경계: DB 접근 불가 — 식당 추천에는 관여할 수 없다.
임무: 날짜별 주변 활동 + 날씨 + 실명 호텔 추천 + 항공권 시세 힌트.
"""
from __future__ import annotations

import json

from tabetabi.agents.loop import run_tool_agent
from tabetabi.contract import TripContract, extract_json
from tabetabi.links import city_of
from tabetabi.tools.search_server import mcp as search_mcp

SYSTEM = """너는 여행 리서처(@scout)다. web_search 도구만 쓸 수 있다.
임무 4가지:
① 날짜별 앵커 지역 주변 볼거리/활동 2~3개 (실제 장소 이름으로, 그 앵커 지역 반경 안에서)
② 여행 기간 날씨 한 줄 (기온·강수 등 수치가 검색되면 포함)
③ 숙소 앵커 지역의 '실명' 호텔 2~3곳 (지역명이 아니라 호텔 이름)
④ 항공권 — **서로 다른 검색어(다른 소스)로 최소 2회** 검색해서 왕복 가격의 하한/상한을 원화 정수로 추정한다.
   "○○원부터" 식으로 하한 하나만 제시하는 것은 금지 — 반드시 low/high 두 값을 채운다.
   두 값을 근거로 판단 기준선(baseline) 1줄도 쓴다 (예: "이 시기 20만원대 초반이면 평년 대비 저렴한 편 — 즉시 예약 권장").
   baseline도 검색 근거 기반으로 쓴다 — 시세 감이 없으면 "판단 보류, 가격 비교 사이트 확인 필요"라고 정직하게 적는다.
규칙:
- 검색 결과에 나온 내용만 쓰고, url은 검색 결과의 것을 그대로 인용한다 (창작 금지).
- 활동의 why·open_hours·last_entry는 검색 스니펫에서 확인된 것만 적는다. 불확실하면 "확인 필요"라고 쓴다(창작 금지). 이 근거는 뒤에서 @critic이 검증한다.
- 각 활동에 tip 1줄을 반드시 붙인다. 가능하면 검색에서 확인한 '지금 시점' 정보로 구체적으로 쓴다
  (예: "현재 대기 90분 — 오픈런 권장", "이번 달 특별전시 진행 중"). 그런 정보가 검색에 없으면
  일반적인 방문 팁을 쓰고 창작하지 않는다 (예: "오픈런 아니면 대기 발생 가능 — 확인 필요").
- 활동은 그 날 앵커 지역에서 벗어나지 않게 고른다 (앵커와 무관한 도쿄 일반 명소 나열 금지).
- 검색은 총 9회 이내 (활동 지역당 1회 + 날씨 1회 + 호텔 1회 + 항공 2회 + 활동 실시간 팁 보강 최대 2회). 한 턴에 여러 검색을 동시에 호출해도 된다.
- 검색어의 일본 지명은 한국어 통용 표기로 쓴다 (예: 新宿→신주쿠, 表参道→오모테산도, 駒込→고마고메).
- 마지막 답변은 JSON 하나만 출력한다 (코드펜스 금지)."""

OUTPUT_SPEC = """출력 JSON 스키마:
{"days": [{"day": 1, "items": [
   {"title": "실제 장소/활동 이름", "url": "...", "why": "한 줄(스니펫 근거)", "area": "앵커 지역",
    "open_hours": "영업시간 또는 확인 필요", "last_entry": "입장마감 또는 확인 필요",
    "dwell_min": 90, "best_time": "morning|late_afternoon|evening", "tip": "1줄 팁(필수)"}]}],
 "weather": "여행 기간 날씨 한 줄",
 "hotels": [{"name": "실명 호텔", "url": "...", "why": "위치·가격대 등 한 줄"}],
 "flight": {"low": 250000, "high": 450000, "note": "검색 근거 요약(성수기/시즌 등) 한 줄",
            "baseline": "판단 기준선 1줄(검색 근거 기반)"}}
- 각 날짜당 items 2~3개, hotels 2~3개. dwell_min은 예상 체류시간(분).
- best_time: 정원·신사·시장은 morning, 쇼핑은 late_afternoon, 전망대·야경은 evening 권장.
- flight.low/high는 반드시 숫자(원화, 콤마 없이)로 채운다. 확실한 근거가 없으면 대략치라도 검색 스니펫의
  숫자에서 뽑아 쓰되, 완전히 못 찾았을 때만 0으로 남긴다(창작 금지)."""


async def run_scout(contract: TripContract, log=None) -> dict:
    city_ko, _ = city_of(contract.pref)
    day_anchor = {str(d): a for d, a in contract.effective_day_anchors().items()}
    if not day_anchor:
        day_anchor = {"1": city_ko}
    stay = contract.hotel_anchor() or city_ko
    task = (
        f"여행: {city_ko}({contract.pref}) {contract.start_date}~{contract.end_date}, {contract.num_days}일, {contract.party}명.\n"
        f"날짜별 활동 앵커 지역(이 지역 반경에서만 활동을 고른다): {json.dumps(day_anchor, ensure_ascii=False)}\n"
        f"숙소 앵커 지역(호텔은 이 역 기준): {stay}\n"
        f"항공: {contract.origin} → {city_ko} 왕복 ({contract.start_date} ~ {contract.end_date})\n"
        f"참고 메모: {contract.notes or '없음'}\n\n{OUTPUT_SPEC}"
    )
    out, evidence = await run_tool_agent(
        name="@scout", server=search_mcp, system=SYSTEM, task=task,
        max_steps=11, log=log, max_tokens=2400,
    )
    evidence_text = "\n---\n".join(evidence)[:6000]   # @critic의 창작 탐지 근거 (D4)
    data = extract_json(out)
    if not data or not isinstance(data.get("days"), list):
        # fail-soft: 활동 없이도 일정은 완성돼야 한다
        return {"days": [], "weather": "", "hotels": [], "flight": {}, "note": (out or "")[:300],
                "_evidence": evidence_text}
    data.setdefault("hotels", [])
    if not isinstance(data.get("flight"), dict):
        data["flight"] = {}
    data["_evidence"] = evidence_text
    return data
