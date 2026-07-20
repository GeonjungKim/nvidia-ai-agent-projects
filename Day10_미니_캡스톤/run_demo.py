"""CLI 데모 — UI 없이 전체 파이프라인을 검증한다 (발표 리허설/테스트용).

실행: python run_demo.py
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")   # Windows cp949 콘솔에서 일본어 깨짐 방지
sys.stderr.reconfigure(encoding="utf-8")

from tabetabi.agents.concierge import run_pipeline
from tabetabi.contract import LockedItem, TripContract
from tabetabi.render import itinerary_md, map_points


def main() -> None:
    contract = TripContract(
        pref="tokyo",
        areas=["新宿", "銀座"],
        start_date="2026-08-22",
        end_date="2026-08-23",
        origin="서울",
        party=2,
        max_dinner_budget=8000,
        genres_pref=["ラーメン", "寿司"],
        locked=[LockedItem(day=1, slot="lunch", name="らぁ麺や 嶋", note="사용자 고정")],
        notes="첫 일본 여행, 걷는 것 선호",
    )
    print("=== SHARED CONTRACT ===")
    print(contract.to_json())
    print("\n=== PIPELINE ===")
    t0 = time.time()
    itinerary = asyncio.run(run_pipeline(contract, log=print))
    print(f"\n(소요 {time.time() - t0:.1f}s)")
    print("\n=== ITINERARY (markdown) ===\n")
    print(itinerary_md(itinerary))
    print("\n=== MAP POINTS ===")
    for p in map_points(itinerary):
        print("  ", p)


if __name__ == "__main__":
    main()
