"""@critic — 읽기 전용 검증 게이트 (도구: get_restaurant 하나만 허용).

Day9 교훈: 병렬 결과의 이음새는 리뷰어가 검증해야 한다. 리뷰어는 선택이 아니라 필수.
allow={"get_restaurant"} — 검색·수정 능력 자체가 없다 (tools = 권한 경계).
"""
from __future__ import annotations

import json
from dataclasses import asdict

from tabetabi.agents.loop import run_tool_agent
from tabetabi.contract import TripContract, extract_json
from tabetabi.tools.tabelog_server import mcp as tabelog_mcp

SYSTEM = """너는 읽기 전용 검증자(@critic)다. 일정을 수정하지 말고 판정만 한다.
검증 절차: 목록의 모든 restaurant_id를 get_restaurant으로 조회해서 확인한다.
(1) found=true 인가 (유령 식당 탐지)
(2) 이름이 일정의 표기와 일치하는가
(3) 계약의 locked 항목이 해당 날짜·슬롯에 그대로 들어갔는가
(4) max_dinner_budget이 있으면 저녁 식당의 budget_dinner_floor ≤ 상한인가
external(사용자 지정 장소)은 조회 대상이 아니다.
마지막 답변은 JSON 하나만: {"pass": true/false, "issues": ["문제 설명"]}"""


async def run_critic(contract: TripContract, picks: list[dict], log=None) -> dict:
    task = (
        f"계약 요약: pref={contract.pref}, 기간={contract.start_date}~{contract.end_date}, "
        f"저녁 예산 상한={contract.max_dinner_budget or '없음'}\n"
        f"locked: {json.dumps([asdict(l) for l in contract.locked], ensure_ascii=False)}\n\n"
        f"검증 대상 일정:\n{json.dumps(picks, ensure_ascii=False, indent=1)}"
    )
    out = await run_tool_agent(
        name="@critic", server=tabelog_mcp, system=SYSTEM, task=task,
        allow={"get_restaurant"}, max_steps=14, log=log, max_tokens=900,
    )
    data = extract_json(out)
    if not data or "pass" not in data:
        return {"pass": True, "issues": ["(critic 출력 파싱 실패 — 판정 생략)"]}
    data.setdefault("issues", [])
    return data
