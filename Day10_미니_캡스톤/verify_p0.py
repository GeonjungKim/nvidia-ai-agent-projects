"""P0 수용 기준 검증 하니스 (DESIGN_V2_SPEC D1/D2/D3+D4게이트/D5).

이 환경엔 실 DB(app.db)·NVIDIA 키가 없으므로, 스펙의 핵심 사실을 재현한
소형 픽스처 DB + 역좌표로 '결정론 게이트의 실제 코드'를 그대로 호출해 검증한다.
(LLM 경유 경로 @foodie/@scout/@critic/merge 는 실 DB+키가 있는 사용자 머신에서 E2E로 확인.)
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

FIX = Path(tempfile.mkdtemp(prefix="tabetabi_fix_"))
atexit.register(lambda: shutil.rmtree(FIX, ignore_errors=True))
(FIX / "data").mkdir()
os.environ["NVIDIA_API_KEY"] = "dummy-key-for-import-only"
os.environ["TABELOG_DIR"] = str(FIX)
os.environ["TABELOG_DB"] = str(FIX / "app.db")

# ---- 픽스처 DB: 스펙 핵심 사실 재현 ----
#  · 表参道 = area2에 없음, stations_json엔 있음 (동네 앵커는 station 검색이 정답 — R2)
#  · 新宿 = area2에 있음 (area2 경로 분기 확인용)
#  · 저품질 저녁(コロッケ ★3.04 리뷰6) = 하한/테이크아웃 게이트 대상 (S7)
#  · 中野 = 앵커(表参道)에서 4km 초과 (이탈 라벨 확인용)
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
]
conn.executemany("INSERT INTO restaurants_agg VALUES (%s)" % ",".join("?" * 16), rows)
conn.executemany("INSERT INTO restaurant_genres VALUES (?,?)", [
    ("r1", "寿司"), ("r2", "焼肉"), ("r3", "ラーメン"), ("r4", "コロッケ"),
    ("r5", "ラーメン"), ("r6", "カフェ"), ("r6", "スイーツ"),
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

# ---- 검증 체크리스트 ----
results: list[tuple[str, str, bool, str]] = []


def check(dcode: str, crit: str, cond: bool, detail: str = "") -> None:
    results.append((dcode, crit, bool(cond), detail))


# ========== D1: stay_area · day_anchors 1급 시민화 ==========
from tabetabi.contract import LockedItem, TripContract

c1 = TripContract(pref="tokyo", areas=["表参道"], start_date="2026-08-22", end_date="2026-08-23",
                  stay_area="駒込", day_anchors={1: "表参道", 2: "駒込"},
                  locked=[LockedItem(day=1, slot="lunch", name="とんかつ ナナイド")])
da1 = c1.effective_day_anchors()
check("D1", "day_anchors가 계약에서 {1:表参道,2:駒込}로 확정", da1 == {1: "表参道", 2: "駒込"}, str(da1))
check("D1", "hotel_anchor = stay_area(駒込) (areas[0] 아님)", c1.hotel_anchor() == "駒込", c1.hotel_anchor())

# 마지막 날 = stay_area 인접 규칙 (day_anchors 미지정 시)
c2 = TripContract(pref="tokyo", areas=["表参道"], start_date="2026-08-22", end_date="2026-08-24", stay_area="駒込")
da2 = c2.effective_day_anchors()
check("D1", "day_anchors 미지정 시 마지막날=stay_area(駒込)", da2.get(3) == "駒込", str(da2))

# locked stay 슬롯 → stay_area 승격 (notes에만 남기지 않음)
c3 = TripContract.from_dict({"pref": "tokyo", "start_date": "2026-08-22", "end_date": "2026-08-23",
                             "locked": [{"day": 0, "slot": "숙소", "name": "고마고메"}]})
check("D1", "locked stay 슬롯 '고마고메' → stay_area=駒込 승격", c3.stay_area == "駒込", c3.stay_area)

sm = c1.summary_md()
check("D1", "사이드바 요약에 stay_area·day_anchors 노출", ("駒込" in sm and "Day1: 表参道" in sm), "")

# ========== D2: 앵커 해석기 · 이탈 게이트 · external 좌표 ==========
from tabetabi.anchors import anchor_latlng, deviation_km, off_anchor_label, resolve_anchor

r_omote = resolve_anchor("tokyo", "表参道")
check("D2", "表参도 → area2 아닌 station 검색키로 해석", r_omote["key_type"] == "station"
      and r_omote["search_kwargs"] == {"station": "表参道"}, json.dumps(r_omote, ensure_ascii=False))
check("D2", "해석 로그에 'station 검색' 라인", "station 검색" in r_omote["log"], r_omote["log"])
r_shin = resolve_anchor("tokyo", "新宿")
check("D2", "新宿 → area2 검색키로 해석 (분기 확인)", r_shin["key_type"] == "area2", r_shin["log"])

dev_far = deviation_km("tokyo", "表参道", "中野")
check("D2", "中野은 앵커(表参道)에서 4km 초과 → 이탈 라벨 강제",
      dev_far is not None and dev_far > 4.0 and off_anchor_label(dev_far) != "", f"{dev_far}km / '{off_anchor_label(dev_far)}'")
dev_near = deviation_km("tokyo", "表参道", "明治神宮前")
check("D2", "明治神宮前(인접)은 이탈 라벨 없음",
      dev_near is not None and off_anchor_label(dev_near) == "", f"{dev_near}km")
ll = anchor_latlng("tokyo", "表参道")
check("D2", "external 좌표 근사 = 앵커 역 좌표 확보", ll is not None, str(ll))

# ========== D3 + D4 코드 게이트: 슬롯 규칙 · 종일형 차단 · dedup ==========
from tabetabi import timemodel

check("D3", "디즈니랜드 = 종일형 POI 판정", timemodel.is_allday_poi("東京ディズニーランド"), "")
check("D3", "新宿御苑 → garden 분류", timemodel.classify("新宿御苑") == "garden", timemodel.classify("新宿御苑"))
check("D3", "evening 슬롯은 garden 금지 규칙", timemodel.slot_forbids("evening", "garden"), "")

seen: set = set()
day1_items = [
    {"title": "明治神宮", "best_time": "morning", "why": "메이지 신궁"},
    {"title": "新宿御苑", "best_time": "evening", "why": "정원"},          # evening 금지 → 이동/제외
    {"title": "六本木ヒルズ展望台", "best_time": "evening", "why": "전망대 야경"},
    {"title": "東京ディズニーランド", "why": "테마파크"},                    # allday → 슬롯 제외
]
sched1, allday1 = timemodel.schedule_day(day1_items, seen, day=1)
ev_gardens = [a for a in sched1 if a["slot"] == "evening" and a["category"] == "garden"]
check("D3", "evening 슬롯에 공원/정원 배정 0건", len(ev_gardens) == 0, f"{[ (a['slot'],a['category']) for a in sched1]}")
check("D3", "종일형 POI 슬롯 배정 0건 · allday 섹션으로 분리",
      all("ディズニー" not in a["title"] for a in sched1) and any("ディズニー" in a["title"] for a in allday1), "")
check("D3", "각 활동 카드에 tip 1줄 존재", all(a.get("tip") for a in sched1), "")
gone_garden = all(a["category"] != "garden" or a["slot"] != "evening" for a in sched1)
check("D3", "新宿御苑(정원)이 evening이 아닌 낮 슬롯으로 조정/제외", gone_garden, "")

# dedup: 다음 날 같은 title 재등장 → 제거
day2_items = [{"title": "明治神宮", "best_time": "morning"}, {"title": "駒込 六義園", "best_time": "morning", "why": "정원"}]
sched2, _ = timemodel.schedule_day(day2_items, seen, day=2)
check("D4", "활동 dedup — 明治神宮 이틀 연속 배정 금지", all(a["title"] != "明治神宮" for a in sched2),
      f"{[a['title'] for a in sched2]}")

# ========== D5: 식당 품질 하한 게이트 ==========
from tabetabi.agents import concierge
from tabetabi.tools.tabelog_server import fetch_by_ids, search_lib

rows_by_id = fetch_by_ids(["r1", "r4", "r6"])
check("D5", "고품질(리뷰180/신뢰3.72) 하한 통과", not concierge._below_floor(rows_by_id["r1"]), "")
check("D5", "저품질(★3.04·리뷰6) 하한 미달 차단", concierge._below_floor(rows_by_id["r4"]), "")
check("D5", "コロッケ 단독 = 저녁 테이크아웃 업태 배제", concierge._is_takeout_dinner(rows_by_id["r4"]), "")
check("D5", "카페 단독 장르 = 식사 슬롯 배제 대상", concierge._is_cafe_only(rows_by_id["r6"]), "")

# _sanitize_foodie: 저품질/테이크아웃 후보 실제 제거
foodie_data = {"slots": [
    {"day": 1, "slot": "dinner", "candidates": [
        {"restaurant_id": "r1", "name": "鮨 おもて"},
        {"restaurant_id": "r4", "name": "コロッケ肉店"},   # 제거되어야
    ]},
    {"day": 1, "slot": "lunch", "candidates": [
        {"restaurant_id": "r6", "name": "表参道カフェ"},    # lunch에 카페 → 제거
        {"restaurant_id": "r3", "name": "新宿ラーメン横丁"},
    ]},
]}
san = concierge._sanitize_foodie(foodie_data, log=lambda s: None)
din_ids = [c["restaurant_id"] for c in san["slots"][0]["candidates"]]
lun_ids = [c["restaurant_id"] for c in san["slots"][1]["candidates"]]
check("D5", "_sanitize_foodie: 저녁 후보에서 저품질 코로케 제거", "r4" not in din_ids and "r1" in din_ids, str(din_ids))
check("D5", "_sanitize_foodie: 점심 후보에서 카페 단독 제거", "r6" not in lun_ids and "r3" in lun_ids, str(lun_ids))

# 품질 하한 > 장르 다양성 우선순위: _backfill이 하한 통과 픽만 채우는지
backfilled = concierge._backfill([], c1, {1: r_omote, 2: resolve_anchor("tokyo", "駒込")}, log=lambda s: None)
bad = [p for p in backfilled if fetch_by_ids([p["restaurant_id"]]).get(p["restaurant_id"]) and
       concierge._below_floor(fetch_by_ids([p["restaurant_id"]])[p["restaurant_id"]]) and not p.get("relaxed")]
check("D5", "_backfill 픽은 품질 하한 통과(또는 희소 완화 라벨)", len(bad) == 0, f"미달 무라벨 {len(bad)}건")

# ---- 리포트 ----
print("\n" + "=" * 72)
print("  P0 수용 기준 검증 체크리스트 (결정론 게이트 · 픽스처 DB)")
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
sys.exit(0 if npass == len(results) else 1)
