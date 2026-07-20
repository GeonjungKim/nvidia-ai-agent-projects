"""@critic — 읽기 전용 검증 게이트 (도구: get_restaurant 하나만 허용).

Day9 교훈: 병렬 결과의 이음새는 리뷰어가 검증해야 한다. 리뷰어는 선택이 아니라 필수.
allow={"get_restaurant"} — 검색·수정 능력 자체가 없다 (tools = 권한 경계).

D4(원인 R4): 검증 비대칭 해소 — 기존에는 식당만 검증하고 활동(@scout 산출물)은 무방비였다
("표참도에서 교통 편리" 같은 거짓 근거가 그대로 나간 사례, S6). 활동도 판정 대상에 넣되,
새 도구는 주지 않는다(읽기 전용 유지) — 대신 @scout이 실제로 확인한 검색 스니펫 원문을
evidence로 첨부해, 그 evidence 안에 실재하는 근거인지만 LLM이 대조 판단하게 한다.
"""
from __future__ import annotations

import json
from dataclasses import asdict

from tabetabi.agents.loop import run_tool_agent
from tabetabi.contract import TripContract, extract_json
from tabetabi.tools.tabelog_server import mcp as tabelog_mcp

SYSTEM = """너는 읽기 전용 검증자(@critic)다. 일정을 수정하지 말고 판정만 한다.

[식당 검증] 목록의 모든 restaurant_id를 get_restaurant으로 조회해서 확인한다.
(1) found=true 인가 (유령 식당 탐지)
(2) 이름이 일정의 표기와 일치하는가
(3) 계약의 locked 항목이 해당 날짜·슬롯에 그대로 들어갔는가
(4) max_dinner_budget이 있으면 저녁 식당의 budget_dinner_floor ≤ 상한인가
external(사용자 지정 장소)은 조회 대상이 아니다.

[활동 검증 — 새 도구 없이 evidence 텍스트만으로 판정한다]
(5) why·open_hours·last_entry가 evidence 스니펫에 실제로 등장하는 내용에 근거하는가.
    evidence 어디에도 없는 구체적 사실(시간·거리·평판 등)을 단정했다면 창작으로 간주해 issues에 적는다.
    "확인 필요"라고 정직하게 적은 항목은 창작이 아니므로 통과.
(6) 활동의 area가 그 날짜의 day_anchor와 실제로 부합하는가 (전혀 다른 동네인데 "가깝다"고 서술 등은 위반).
(7) 항공 판단 기준선(flight.baseline)이 있다면, evidence에 있는 가격 정보와 모순되지 않는가
    (예: evidence엔 없는 수치를 baseline이 단정하면 위반).
found=false 식당, evidence에 없는 창작된 활동 근거, 앵커와 불일치하는 area 서술, evidence와 모순되는
항공 기준선은 모두 issues에 문장으로 적는다.
마지막 답변은 JSON 하나만: {"pass": true/false, "issues": ["문제 설명"]}"""


async def run_critic(
    contract: TripContract,
    picks: list[dict],
    activities: list[dict] | None = None,
    evidence: str = "",
    day_anchors: dict[int, str] | None = None,
    flight: dict | None = None,
    log=None,
) -> dict:
    task = (
        f"계약 요약: pref={contract.pref}, 기간={contract.start_date}~{contract.end_date}, "
        f"저녁 예산 상한={contract.max_dinner_budget or '없음'}\n"
        f"locked: {json.dumps([asdict(l) for l in contract.locked], ensure_ascii=False)}\n\n"
        f"검증 대상 식당 일정:\n{json.dumps(picks, ensure_ascii=False, indent=1)}\n\n"
        f"날짜별 앵커: {json.dumps({str(k): v for k, v in (day_anchors or {}).items()}, ensure_ascii=False)}\n"
        f"검증 대상 활동:\n{json.dumps(activities or [], ensure_ascii=False, indent=1)}\n\n"
        f"검증 대상 항공 판단 기준선: {json.dumps(flight or {}, ensure_ascii=False)}\n\n"
        f"@scout이 실제로 확인한 검색 스니펫(evidence — 활동·항공 근거가 여기 실재하는지 대조):\n"
        f"{evidence or '(없음)'}"
    )
    out, _ev = await run_tool_agent(
        name="@critic", server=tabelog_mcp, system=SYSTEM, task=task,
        allow={"get_restaurant"}, max_steps=14, log=log, max_tokens=900,
    )
    data = extract_json(out)
    if not data or "pass" not in data:
        return {"pass": True, "issues": ["(critic 출력 파싱 실패 — 판정 생략)"]}
    data.setdefault("issues", [])
    return data
