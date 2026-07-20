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
# 웹 조인 자동 확정 하한 — 검색엔진은 의미 기반이라 "이름이 다른 관련 가게"(예: 유명 돈카츠집)를
# 상위로 줄 수 있다. 이름 유사도가 이 이상일 때만 자동 확정, 미달이면 확인 후보로 강등한다.
WEB_CONFIRM_SIMILARITY = 0.5

# 웹검색 결과에 실린 타베로그 URL에서 restaurant_id 추출용
# (예: https://tabelog.com/tokyo/A1306/A130603/13229075/)
_TABELOG_ID_RE = re.compile(r"tabelog\.com/[a-z_]+/A\d{4}/A\d{6}/(\d{6,10})")

# 웹 조인 결과 캐시 — pending 확인·파이프라인에서 같은 이름을 반복 조회하므로 필수
_web_cache: dict[tuple, list[dict]] = {}


def _resolve_via_web(pref: str, name: str, anchor_label: str) -> list[dict]:
    """2단: 웹검색 스니펫의 타베로그 URL을 자체 DB와 조인한다 (검색 상위순, 최대 2곳).

    타베로그를 긁는 게 아니라 검색엔진 결과에 노출된 URL만 쓴다 — 봇 차단 우회가 아니며,
    id가 자체 DB에 있을 때만 쓴다. Tavily 키가 없거나 실패하면 빈 목록 (fail-soft).
    """
    key = (pref, name, anchor_label)
    if key in _web_cache:
        return _web_cache[key]
    out: list[dict] = []
    try:
        from tabetabi.tools.search_server import web_search_lib
        from tabetabi.tools.tabelog_server import fetch_by_ids
        q = " ".join(x for x in (name, anchor_label, "食べログ") if x)
        results = web_search_lib(q, max_results=5)
        ids: list[str] = []
        for r in results:
            blob = (r.get("url") or "") + " " + (r.get("snippet") or "")
            ids.extend(m.group(1) for m in _TABELOG_ID_RE.finditer(blob))
        ids = list(dict.fromkeys(ids))[:5]        # 검색 상위 순서 유지 + 중복 제거
        if ids:
            rows = fetch_by_ids(ids)
            out = [rows[i] for i in ids if i in rows and rows[i].get("pref") == pref][:2]
    except Exception:
        out = []
    _web_cache[key] = out
    return out


def _tokens(name: str) -> list[str]:
    """공백·괄호·중점 등으로 토큰 분해. 너무 짧은(1글자) 토큰은 노이즈라 제외."""
    parts = re.split(r"[ 　()（）・/、,·]+", name.strip())
    return [p for p in parts if len(p) >= 2]


# 히라가나 → 가타카나 변환표 (U+3041~3096 → U+30A1~30F6). LLM이 사용자 발화를 일본어로 옮길 때
# とんかつ/トンカツ/豚カツ처럼 표기가 갈리면 원문 유사도가 0에 수렴한다 — 가나 정규화 후 비교한다.
_HIRA_TO_KATA = str.maketrans({chr(h): chr(h + 0x60) for h in range(0x3041, 0x3097)})


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.translate(_HIRA_TO_KATA), b.translate(_HIRA_TO_KATA)).ratio()


def resolve_place(pref: str, name: str, anchor_kwargs: dict | None = None) -> dict:
    """이름 → DB 매칭을 다단계로 시도한다 (실행 순서: 1 → 3 → 2 → 4).

    1) 원문 keyword 정확/단일 일치 → 자동 확정
    3) 토큰 분해 부분일치(정확/단일 일치) → 자동 확정
    2) 웹검색 조인 — 검색 결과의 타베로그 URL을 자체 DB id와 대조 → 외부 증거라 자동 확정
    4) 앵커 검색 키(station|area2) + 가나 정규화 유사도 상위 3곳 → **자동 확정 금지**, 후보만 반환
    0) 전부 실패 → 후보 없음 (external)

    반환: {"stage": 1|2|3|4|0, "hit": row|None, "candidates": [row,...]}
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

    # 2) 웹검색 조인 — 검색 결과의 타베로그 URL을 자체 DB에 대조. 이름 유사도 가드를 통과할
    #    때만 자동 확정한다 (검색 상위 ≠ 그 가게: 유명 인접 가게 오확정 방지, 실측 사례 まい泉).
    anchor_label = str((anchor_kwargs or {}).get("station") or (anchor_kwargs or {}).get("area2") or "")
    web_rows = _resolve_via_web(pref, name, anchor_label)
    strong = next((w for w in web_rows if _similarity(name, w["name"]) >= WEB_CONFIRM_SIMILARITY), None)
    if strong:
        return {"stage": 2, "hit": strong, "candidates": []}

    # 4) 확인 후보 수집 — 웹 조인 약한 매치(외부 증거 보유, 우선) + 앵커 유사도 상위. 확정 금지.
    cands: list[dict] = list(web_rows)
    if anchor_kwargs:
        arows = search_lib(pref=pref, limit=25, **anchor_kwargs)
        ranked = sorted(arows, key=lambda r: _similarity(name, r["name"]), reverse=True)
        cands += [r for r in ranked if _similarity(name, r["name"]) >= FUZZY_MIN_SIMILARITY]
    top, seen = [], set()
    for c in cands:
        if c["restaurant_id"] not in seen:
            seen.add(c["restaurant_id"])
            top.append(c)
        if len(top) == 3:
            break
    if top:
        return {"stage": 4, "hit": None, "candidates": top}

    return {"stage": 0, "hit": None, "candidates": []}
