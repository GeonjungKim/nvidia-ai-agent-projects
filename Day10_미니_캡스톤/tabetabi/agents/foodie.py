"""@foodie — 타베로그 미식 큐레이터 (도구: Tabelog DB MCP만).

권한 경계: 웹검색·지도 도구 없음. 도구 결과 밖의 식당은 말할 수 없다 → 환각을 구조로 차단.
고정(locked) 슬롯은 파이프라인이 코드로 확정하므로, @foodie는 '열린 슬롯'만 담당한다.
"""
from __future__ import annotations

import json

from tabetabi.agents.loop import run_tool_agent
from tabetabi.contract import TripContract, extract_json
from tabetabi.tools.tabelog_server import mcp as tabelog_mcp

SYSTEM = """너는 타베로그 고신뢰 리뷰어 데이터 기반 미식 큐레이터(@foodie)다.
규칙:
1. 반드시 도구 결과에 실제로 나온 식당만 후보로 쓴다. restaurant_id가 없는 식당 언급 금지(창작 금지).
2. pref는 계약에 이미 확정돼 있다 — 바로 search_restaurants부터 시작하라.
3. 왕복을 아끼기 위해 한 턴에 여러 search_restaurants를 '동시에' 호출하라 (병렬 tool call).
   권장 절차: 1턴) 요청된 슬롯별 지역×장르 검색을 한꺼번에 → 2턴) 부족한 것만 보충 → 즉시 최종 JSON.
4. 검색 결과에 상세(역·예산·평점·링크)가 이미 있으니 재조회하지 마라.
5. **앵커 검색 키**: 아래 '날짜별 검증된 검색 키'를 그대로 써라. area2를 스스로 지어내지 마라 —
   동네 지명(表参道 등)은 area2에 없어서 station 검색으로만 잡힌다. 지정된 키(station=... 또는 area2=...)로 검색하라.
6. 같은 날은 그 날 앵커의 검색 키로 후보를 모으고, 일정 전체에서 식당이 중복되지 않게 한다.
   '이미 확정된 식당' 목록의 식당은 후보로 다시 쓰지 마라.
7. 품질 하한: 가능하면 min_reviews=50, min_bayes=3.4 인자를 넣어 신뢰도 낮은 곳을 애초에 거른다.
8. 저녁 후보는 max_dinner_budget으로 예산 상한을 지키고, 弁当·惣菜·コロッケ 같은 테이크아웃 업태는 저녁에 넣지 마라.
9. bayes_score(신뢰도 보정 랭킹)가 높은 곳을 우선하되, 선호 장르를 반영한다.
10. 마지막 답변은 JSON 하나만 출력한다 (설명·코드펜스 금지)."""

OUTPUT_SPEC = """출력 JSON 스키마:
{"slots": [
  {"day": 1, "slot": "lunch",
   "candidates": [{"restaurant_id": "...", "name": "...", "reason": "한 줄 이유"}]}
 ],
 "note": "전체 코멘트 한 줄"}
- 요청된 '열린 슬롯' 전부를 빠짐없이 포함한다. 슬롯당 candidates 정확히 2개.
- cafe 슬롯은 カフェ·スイーツ·パン 계열 장르에서 고른다 (그날 점심·저녁과 같은/인접 지역 우선).
- lunch·dinner 슬롯에는 カフェ·パン·スイーツ 계열을 넣지 않는다 — 제대로 된 식사 장르만 (그건 cafe 슬롯 전용).
- reason은 자연스러운 한국어 문장으로 쓴다 (식당명·장르의 일본어 표기는 유지)."""


async def run_foodie(
    contract: TripContract,
    open_slots: list[tuple[int, str]],
    fixed: list[dict],
    anchor_keys: dict[int, dict] | None = None,
    log=None,
) -> dict:
    slot_list = ", ".join(f"{d}일차 {s}" for d, s in open_slots)
    # 날짜별 '검증된 검색 키'를 task 데이터로 주입 (프롬프트 지시가 아니라 데이터 — D2)
    keys_view = {}
    for day, info in (anchor_keys or {}).items():
        kw = info.get("search_kwargs") or {}
        keys_view[str(day)] = {"anchor": info.get("anchor"), **kw} if kw else {"anchor": info.get("anchor")}
    task = (
        f"여행 계약(SHARED CONTRACT):\n{contract.to_json()}\n\n"
        f"이미 확정된 식당(변경·중복 금지): {json.dumps(fixed, ensure_ascii=False) if fixed else '없음'}\n"
        f"채워야 할 열린 슬롯: {slot_list or '없음'}\n"
        f"날짜별 검증된 검색 키(이 키로 검색하라 — area2 창작 금지): "
        f"{json.dumps(keys_view, ensure_ascii=False) if keys_view else '없음 (전 지역 bayes 상위)'}\n\n{OUTPUT_SPEC}"
    )
    out, _evidence = await run_tool_agent(
        name="@foodie", server=tabelog_mcp, system=SYSTEM, task=task,
        allow={"list_areas", "list_genres", "search_restaurants"},   # 검색 결과에 상세가 다 있다 — 도구 다이어트
        max_steps=10, log=log, max_tokens=2400,
    )
    data = extract_json(out)
    if not data or not isinstance(data.get("slots"), list):
        raise RuntimeError("@foodie 출력 파싱 실패: " + (out or "")[:200])
    return data
