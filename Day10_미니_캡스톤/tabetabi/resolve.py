"""고정 장소 resolve v2 — 다단 매칭 + 사용자 확인 루프 (D6, 원인 R6).

증상(S8): '돈카츠 나나이도' DB 매칭 실패 → 1회 검색뿐이라 조용히 external 처리됨(=근접 후보를
확인 없이 자동 채택하거나, 아예 못 찾으면 통보 없이 넘어감).

이 모듈은 순수 결정론 코드다 (LLM 아님). 4단계로 재시도하고, 마지막 단계(유사도 후보)는
자동 확정하지 않는다 — 호출부(@concierge 대화 루프)가 사용자 확인을 받아야 한다.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher

from tabetabi.tools.tabelog_server import search_lib

# 유사도 하한 — 이 밑이면 후보로도 제시하지 않는다 (완전히 무관한 결과 배제)
FUZZY_MIN_SIMILARITY = 0.25


def _tokens(name: str) -> list[str]:
    """공백·괄호·중점 등으로 토큰 분해. 너무 짧은(1글자) 토큰은 노이즈라 제외."""
    parts = re.split(r"[ 　()（）・/、,·]+", name.strip())
    return [p for p in parts if len(p) >= 2]


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def resolve_place(pref: str, name: str, anchor_kwargs: dict | None = None) -> dict:
    """이름 → DB 매칭을 4단계로 시도한다.

    1) 원문 keyword 정확/단일 일치 → 자동 확정
    3) 토큰 분해 부분일치(정확/단일 일치) → 자동 확정
    4) 앵커 검색 키(station|area2) + 이름 유사도 상위 3곳 → **자동 확정 금지**, 후보만 반환
    0) 전부 실패 → 후보 없음 (external)

    반환: {"stage": 1|3|4|0, "hit": row|None, "candidates": [row,...]}
    """
    name = (name or "").strip()
    if not name:
        return {"stage": 0, "hit": None, "candidates": []}

    # 1) 원문 keyword
    rows = search_lib(pref=pref, keyword=name, limit=5)
    exact = next((r for r in rows if r["name"] == name), None)
    if exact:
        return {"stage": 1, "hit": exact, "candidates": []}
    if len(rows) == 1:
        return {"stage": 1, "hit": rows[0], "candidates": []}

    # 3) 토큰 분해 부분일치 (예: "돈카츠 나나이도" → "ナナイド" 단독 검색)
    for tok in _tokens(name):
        trows = search_lib(pref=pref, keyword=tok, limit=5)
        texact = next((r for r in trows if r["name"] == name), None)
        if texact:
            return {"stage": 3, "hit": texact, "candidates": []}
        if len(trows) == 1:
            return {"stage": 3, "hit": trows[0], "candidates": []}

    # 4) 앵커 역/지역 + 이름 유사도 상위 3곳 — 확정 금지, 확인 필요
    if anchor_kwargs:
        arows = search_lib(pref=pref, limit=25, **anchor_kwargs)
        ranked = sorted(arows, key=lambda r: _similarity(name, r["name"]), reverse=True)
        top = [r for r in ranked if _similarity(name, r["name"]) >= FUZZY_MIN_SIMILARITY][:3]
        if top:
            return {"stage": 4, "hit": None, "candidates": top}

    return {"stage": 0, "hit": None, "candidates": []}
