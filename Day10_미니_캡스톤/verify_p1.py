"""P1 수용 기준 검증 하니스 (DESIGN_V2_SPEC D8 / D4 / D6).

verify_p0.py와 같은 방식: 실 DB(app.db)·NVIDIA 키 없이도 '결정론 코드'는 픽스처 DB로
실제 함수를 그대로 호출해 검증한다. @critic의 LLM 판정 자체(창작 탐지 등)와 @concierge
대화 LLM 응답은 실 키가 있는 사용자 머신에서 E2E로 확인해야 한다(P0와 동일한 한계).
이 하니스가 다루는 것: D6 다단 매칭(전부 결정론), D8 랭킹 조회 배선(전부 결정론),
D4의 comment 코드 템플릿·critic 판정 건수 강제·evidence 배선(코드 경로).
"""
from __future__ import annotations

import atexit
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

FIX = Path(tempfile.mkdtemp(prefix="tabetabi_fix_p1_"))
atexit.register(lambda: shutil.rmtree(FIX, ignore_errors=True))
(FIX / "data").mkdir()
os.environ["NVIDIA_API_KEY"] = "dummy-key-for-import-only"
os.environ["TABELOG_DIR"] = str(FIX)
os.environ["TABELOG_DB"] = str(FIX / "app.db")

conn = sqlite3.connect(FIX / "app.db")
conn.executescript(
    """
    CREATE TABLE restaurants_agg (
      restaurant_id TEXT PRIMARY KEY, name TEXT, url TEXT, pref TEXT,
      area2 TEXT, area3 TEXT, tabelog_rating REAL, tabelog_review_count INTEGER,
      budget_lunch TEXT, budget_dinner TEXT, budget_dinner_floor INTEGER,
      closed_days TEXT, stations_json TEXT, award_count INTEGER,
      bayes_score REAL, reviewer_count INTEGER);
    CREATE TABLE restaurant_genres (restaurant_id TEXT, genre TEXT);
    """
)
rows = [
    # id, name, url, pref, area2, area3, rating, reviews, b_lunch, b_dinner, floor, closed, stations, award, bayes, rc
    ("r1", "鮨 おもて", "http://t/r1", "tokyo", "神宮前", "", 3.8, 180, "￥3,000", "￥12,000", 8000, "", '["表参道","明治神宮前"]', 1, 3.72, 5),
    ("r2", "焼肉 こまごめ", "http://t/r2", "tokyo", "駒込", "", 3.6, 90, "￥2,000", "￥6,000", 5000, "", '["駒込"]', 0, 3.55, 4),
    ("r3", "新宿ラーメン横丁", "http://t/r3", "tokyo", "新宿", "", 3.55, 200, "￥1,000", "￥3,000", 2500, "", '["新宿"]', 0, 3.5, 6),
    ("r4", "コロッケ肉店", "http://t/r4", "tokyo", "神宮前", "", 3.04, 6, "～￥999", "～￥999", 800, "", '["表参道"]', 0, 3.04, 2),
    ("r5", "中野二郎", "http://t/r5", "tokyo", "中野", "", 3.5, 100, "￥1,000", "￥2,000", 1500, "", '["中野"]', 0, 3.5, 5),
    ("r6", "表参道カフェ", "http://t/r6", "tokyo", "神宮前", "", 3.5, 120, "￥1,500", "-", None, "", '["表参道"]', 0, 3.5, 4),
    # D6 픽스처: 토큰 분해 매칭용 (사용자가 여러 단어로 부르지만 DB엔 짧은 이름만 있음, S8 재현)
    ("r7", "ナナイド", "http://t/r7", "tokyo", "神宮前", "", 3.6, 70, "￥1,200", "￥2,800", 2000, "", '["表参道"]', 0, 3.6, 4),
    # D6 픽스처: 라멘 후보 다수 (앵커 랭킹 뷰용)
    ("r8", "麺屋 表参道", "http://t/r8", "tokyo", "神宮前", "", 3.65, 140, "￥1,300", "￥2,900", 2200, "", '["表参道"]', 0, 3.6, 5),
]
conn.executemany("INSERT INTO restaurants_agg VALUES (%s)" % ",".join("?" * 16), rows)
conn.executemany("INSERT INTO restaurant_genres VALUES (?,?)", [
    ("r1", "寿司"), ("r2", "焼肉"), ("r3", "ラーメン"), ("r4", "コロッケ"),
    ("r5", "ラーメン"), ("r6", "カフェ"), ("r6", "スイーツ"), ("r7", "とんかつ"), ("r8", "ラーメン"),
])
conn.commit()
conn.close()

(FIX / "data" / "station_coords.json").write_text(json.dumps({
    "表参道": {"lat": 35.6652, "lng": 139.7126},
    "明治神宮前": {"lat": 35.6702, "lng": 139.7057},
    "駒込": {"lat": 35.7365, "lng": 139.7480},
    "中野": {"lat": 35.7076, "lng": 139.6659},
    "新宿": {"lat": 35.6896, "lng": 139.7006},
}, ensure_ascii=False), encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))

results: list[tuple[str, str, bool, str]] = []


def check(dcode: str, crit: str, cond: bool, detail: str = "") -> None:
    results.append((dcode, crit, bool(cond), detail))


# ========== D6: 고정 장소 resolve v2 (다단 매칭) ==========
from tabetabi.resolve import resolve_place

r_exact = resolve_place("tokyo", "鮨 おもて")
check("D6", "1단계 원문 정확 일치 → 자동 확정", r_exact["stage"] == 1 and r_exact["hit"]["restaurant_id"] == "r1",
      json.dumps(r_exact, ensure_ascii=False, default=str))

r_token = resolve_place("tokyo", "とんかつ屋 ナナイド")
check("D6", "3단계 토큰 분해 부분일치 → 자동 확정 (S8 재현: 여러 단어 중 상호만 DB에 있음)",
      r_token["stage"] == 3 and r_token["hit"] is not None and r_token["hit"]["restaurant_id"] == "r7",
      json.dumps(r_token, ensure_ascii=False, default=str))

r_fuzzy = resolve_place("tokyo", "二郎渋谷店", anchor_kwargs={"station": "中野"})
check("D6", "4단계 앵커+유사도 후보는 자동 확정하지 않는다 (hit=None)",
      r_fuzzy["stage"] == 4 and r_fuzzy["hit"] is None and len(r_fuzzy["candidates"]) >= 1,
      json.dumps(r_fuzzy, ensure_ascii=False, default=str))

r_none = resolve_place("tokyo", "완전히 무관한 이름 xyz123")
check("D6", "전부 실패 시 stage 0 (external 후보)", r_none["stage"] == 0 and not r_none["candidates"], "")

from tabetabi.agents.concierge import _apply_lock_confirm_reply, pending_lock_confirmations

draft_fuzzy = {
    "pref": "tokyo", "start_date": "2026-08-22", "end_date": "2026-08-23", "stay_area": "駒込",
    "day_anchors": {"1": "中野"},
    "locked": [{"day": 1, "slot": "lunch", "name": "二郎渋谷店", "note": "사용자 고정"}],
}
pend = pending_lock_confirmations(draft_fuzzy)
check("D6", "매칭 실패(4단계) 시 채팅에 낼 확인 후보가 잡힌다", len(pend) == 1 and len(pend[0]["candidates"]) >= 1,
      json.dumps(pend, ensure_ascii=False, default=str)[:200])

if pend:
    picked_name = pend[0]["candidates"][0]["name"]
    confirmed_draft = _apply_lock_confirm_reply(draft_fuzzy, "1", pend)
    check("D6", "번호 확인 응답 → locked.name이 DB 정식 표기로 치환됨",
          confirmed_draft["locked"][0]["name"] == picked_name, confirmed_draft["locked"][0]["name"])
    check("D6", "확인 완료 후 재조회 시 pending 목록에서 빠짐 (재질문 금지)",
          pending_lock_confirmations(confirmed_draft) == [], "")

    literal_draft = _apply_lock_confirm_reply(draft_fuzzy, "그대로", pend)
    check("D6", "'그대로' 응답 → 원래 이름 유지 + 확인 마커만 추가 (external 그대로 반영)",
          literal_draft["locked"][0]["name"] == "二郎渋谷店"
          and "[사용자 확인" in literal_draft["locked"][0]["note"], literal_draft["locked"][0])

# 파이프라인 최종 확정 단계(_resolve_locked)도 새 다단 매칭을 쓰는지 (토큰 케이스로 재확인)
from tabetabi.agents.concierge import _resolve_locked
from tabetabi.anchors import resolve_anchor
from tabetabi.contract import LockedItem, TripContract

c_lock = TripContract(pref="tokyo", start_date="2026-08-22", end_date="2026-08-22", stay_area="表参道",
                      locked=[LockedItem(day=1, slot="lunch", name="とんかつ屋 ナナイド")])
anchor_keys = {1: resolve_anchor("tokyo", "表参道")}
locked_map = _resolve_locked(c_lock, anchor_keys, log=lambda s: None)
check("D6", "_resolve_locked이 토큰분해 매칭 결과를 그대로 채택(id r7)",
      locked_map.get((1, "lunch"), {}).get("restaurant_id") == "r7", str(locked_map))

# ========== D4: comment 코드 템플릿 · critic 판정 건수 강제 · evidence 배선 ==========
from tabetabi.agents.concierge import _build_comment

fake_picks = [
    {"day": 1, "slot": "lunch", "locked": True, "genres": "寿司"},
    {"day": 1, "slot": "dinner", "locked": False, "genres": "ラーメン", "relaxed": True},
    {"day": 2, "slot": "lunch", "locked": False, "genres": "焼肉"},
]
comment = _build_comment(c_lock, fake_picks, {1: "表参道", 2: "駒込"})
check("D4", "comment은 LLM 자유서술이 아니라 코드 템플릿 — 고정 개수 포함", "고정 1곳" in comment, comment)
check("D4", "comment에 앵커(Day1/Day2) 포함", "Day1 表参道" in comment and "Day2 駒込" in comment, comment)
check("D4", "comment에 희소 완화 사유 포함", "희소 지역 1곳" in comment, comment)
check("D4", "comment은 순수 문자열이며 '표참도에서 교통 편리' 류의 근거 창작 문구가 없다 (템플릿 어휘 외 없음)",
      all(w not in comment for w in ("교통", "편리", "정정")), comment)

import inspect

from tabetabi.agents.critic import run_critic

sig = inspect.signature(run_critic)
check("D4", "run_critic이 활동(activities)·evidence·day_anchors를 인자로 받는다 (검증 비대칭 해소)",
      {"activities", "evidence", "day_anchors"} <= set(sig.parameters), str(sig))

loop_sig = inspect.signature(__import__("tabetabi.agents.loop", fromlist=["run_tool_agent"]).run_tool_agent)
check("D4", "run_tool_agent은 이제 (text, evidence) 튜플을 반환한다 (스니펫 원문 배선)",
      str(loop_sig.return_annotation) == "tuple[str, list[str]]", str(loop_sig.return_annotation))

# render.py가 판정 건수를 출력에 강제 포함하는지
from tabetabi.render import itinerary_md

fake_it = {
    "days": [], "stats": {}, "critic": {"pass": True, "issues": [], "restaurants_checked": 5, "activities_checked": 3},
}
md = itinerary_md(fake_it)
check("D4", "@critic 리포트가 '식당 N곳 + 활동 M건 판정'을 렌더에 포함", "식당 5곳" in md and "활동 3건" in md, md)

# ========== D8: 랭킹 리스트 뷰 배선 (전부 결정론 — LLM 호출 0회) ==========
from tabetabi.tools.tabelog_server import list_genres, search_lib

anchor_info = resolve_anchor("tokyo", "表参道")
check("D8", "앵커 선택 → resolve_anchor가 검색 키를 준다 (D2 재사용)",
      anchor_info["search_kwargs"] == {"station": "表参道"}, str(anchor_info))

rank_rows = search_lib(pref="tokyo", genre="ラーメン", sort="bayes", limit=30, **anchor_info["search_kwargs"])
check("D8", "랭킹 조회 결과가 즉시 반환된다 (r8 麺屋 表参道 포함)",
      any(r["restaurant_id"] == "r8" for r in rank_rows), str([r["restaurant_id"] for r in rank_rows]))

genre_rows = list_genres("tokyo", "神宮前")
check("D8", "지역 장르 목록도 즉시 조회된다 (동적 로드)", len(genre_rows) > 0, str(genre_rows))

# _picks_from / _backfill이 대안 후보(alt_ids)를 남기는지 (슬롯 카드 '다른 후보 보기'용)
from tabetabi.agents.concierge import _picks_from, _backfill

foodie_data = {"slots": [
    {"day": 1, "slot": "dinner", "candidates": [
        {"restaurant_id": "r1", "name": "鮨 おもて", "genres": "寿司"},
        {"restaurant_id": "r8", "name": "麺屋 表参道", "genres": "ラーメン"},
    ]},
]}
merged = {"days": [{"day": 1, "dinner": "r1"}]}
c_alt = TripContract(pref="tokyo", start_date="2026-08-22", end_date="2026-08-22", areas=["表参道"])
picks_alt = _picks_from(merged, foodie_data, c_alt, {}, log=lambda s: None)
p_dinner = next(p for p in picks_alt if p["slot"] == "dinner")
check("D8", "_picks_from이 선택 안 된 후보를 alt_ids로 남긴다", p_dinner.get("alt_ids") == ["r8"], str(p_dinner))

backfilled = _backfill([], c_alt, {1: anchor_info}, log=lambda s: None)
has_alt = any("alt_ids" in p for p in backfilled)
check("D8", "_backfill 픽에도 alt_ids 필드가 존재한다", has_alt, str(backfilled)[:300])

# ---- 리포트 ----
print("\n" + "=" * 72)
print("  P1 수용 기준 검증 체크리스트 (결정론 코드 · 픽스처 DB)")
print("=" * 72)
cur = None
npass = 0
for dcode, crit, ok, detail in results:
    if dcode != cur:
        print(f"\n[{dcode}]")
        cur = dcode
    print(f"  {'✔' if ok else '✗ FAIL'}  {crit}")
    if not ok and detail:
        print(f"        └ {detail}")
    npass += ok
print("\n" + "-" * 72)
print(f"  통과 {npass}/{len(results)}")
print("-" * 72)
print("\n(참고) @critic의 실제 창작-탐지 판정·@concierge 대화 LLM 응답은 결정론 코드가 아니므로")
print("       이 하니스로는 검증 불가 — 실 NVIDIA_API_KEY가 있는 환경에서 run_demo.py로 E2E 확인 필요.")
sys.exit(0 if npass == len(results) else 1)
