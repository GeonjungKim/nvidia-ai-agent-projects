"""시간 모델 — 슬롯 규칙표·종일형 POI 차단·활동 스케줄링 (D3, 원인 R3).

증상: 디즈니랜드를 반나절 슬롯에 배정(S3), 신주쿠 교엔을 20:30에 배정(S4).
근본 원인: 체류/이동시간·영업시간·시간대 적합성 모델 부재.

이 모듈은 전부 결정론 코드 상수/함수다 (LLM 무관). @scout이 무엇을 가져오든
슬롯 규칙에 맞게 코드가 재배치하고, 규칙 위반·종일형은 걸러낸다.
"""
from __future__ import annotations

import re

# 활동 슬롯 타입 (시각은 렌더 기준값)
ACT_SLOTS = ("morning", "late_afternoon", "evening")
ACT_SLOT_TIME = {"morning": "10:00", "late_afternoon": "16:30", "evening": "20:00"}
ACT_SLOT_KO = {"morning": "오전", "late_afternoon": "늦은 오후", "evening": "저녁"}

# ---------- Day Window — 항공 시간을 반영한 하루 가용 시간창 (전부 결정론) ----------
# 원칙: 스마트 디폴트 + 가정의 가시화 + 한마디 수정. 항공 시간이 없어도 즉시 생성하되
# 현실적인 기본 가정(첫날 낮 시작·마지막날 오후 종료)을 깔고, 배너로 가정을 명시한다.
ARRIVAL_OVERHEAD_MIN = 150      # 입국심사·수하물 ~60분 + 공항→도심 이동 ~90분
DEPART_OVERHEAD_MIN = 210       # 도심→공항 ~90분 + 국제선 2시간 전 공항 도착
DEFAULT_FIRST_DAY_START = 12 * 60 + 30   # 항공 미정: 오전 항공편(ICN 07~09시 발) 도착 가정
DEFAULT_LAST_DAY_END = 15 * 60           # 항공 미정: 15:00 공항 출발 가정
DAY_START, DAY_END = 9 * 60, 22 * 60     # 평일반 하루 활동 범위

MEAL_NOMINAL = {"lunch": 12 * 60, "cafe": 15 * 60, "dinner": 18 * 60 + 30}
LUNCH_LATEST = 14 * 60 + 30              # 이보다 늦으면 점심 슬롯 무의미


def hhmm_to_min(s) -> int | None:
    m = re.match(r"^(\d{1,2}):(\d{2})$", str(s or "").strip())
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    return h * 60 + mi if 0 <= h <= 23 and 0 <= mi <= 59 else None


def min_to_hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def day_window(day: int, num_days: int, arrival_time: str = "", departure_time: str = "") -> dict:
    """그날의 (시작, 종료) 가용 시간창과 사용자에게 보여줄 가정 배너를 계산한다.

    첫날은 도착편, 마지막날은 귀국편이 창을 좁힌다. 시간 미정이면 기본 가정을 쓰되
    assumed_* 플래그와 배너로 '가정임'을 숨기지 않는다 (조용한 가정 금지).
    """
    start, end = DAY_START, DAY_END
    assumed_start = assumed_end = False
    notes: list[str] = []
    if day == 1:
        a = hhmm_to_min(arrival_time)
        if a is not None:
            start = max(start, a + ARRIVAL_OVERHEAD_MIN)
            notes.append(f"✈️ {arrival_time} 도착 기준 — 입국·이동 포함 {min_to_hhmm(start)}부터 일정 시작")
        else:
            start, assumed_start = DEFAULT_FIRST_DAY_START, True
            notes.append(f"✈️ 첫날은 오전 항공편 도착 가정으로 {min_to_hhmm(start)}부터 시작해요 — "
                         "도착 시간을 알려주시면 맞춰 드려요")
    if day == num_days:
        d = hhmm_to_min(departure_time)
        if d is not None:
            end = min(end, max(d - DEPART_OVERHEAD_MIN, start))
            notes.append(f"🛫 귀국편 {departure_time} 출발 — {min_to_hhmm(end)}에는 공항으로 이동을 시작하세요")
        else:
            end, assumed_end = DEFAULT_LAST_DAY_END, True
            notes.append(f"🛫 귀국편 미정 — {min_to_hhmm(end)} 공항 출발 가정으로 저녁 전에 마무리했어요. "
                         "출발 시간을 알려주시면 조정해 드려요")
    if end <= start:
        notes.append("⚠️ 항공 시간을 반영하면 이 날은 자유 시간이 거의 없어요")
    return {"start": start, "end": end, "assumed_start": assumed_start, "assumed_end": assumed_end,
            "banner": " · ".join(notes)}


def plan_meal_slots(start: int, end: int) -> dict[str, int]:
    """시간창 안에 들어가는 식사 슬롯과 시각(분)을 결정한다 — 창 밖 슬롯은 아예 뺀다.

    규칙: 점심은 14:30 이후면 무의미 → 제외. 저녁은 종료 60분 전까지 시작 가능해야 함.
    카페는 점심+90분 이후, 저녁 60분 전까지. 고정(locked) 슬롯은 이 계획과 무관하게 계약이 이긴다.
    """
    times: dict[str, int] = {}
    lunch = max(MEAL_NOMINAL["lunch"], start + 15)
    if lunch <= LUNCH_LATEST and lunch + 60 <= end:
        times["lunch"] = lunch
    dinner = max(MEAL_NOMINAL["dinner"], start + 15)
    if dinner + 60 <= end:
        times["dinner"] = dinner
    cafe = max(MEAL_NOMINAL["cafe"], times.get("lunch", start) + 90)
    cafe_cap = min(end, times.get("dinner", end) - 60)
    if cafe + 45 <= cafe_cap:
        times["cafe"] = cafe
    return times


def allowed_activity_slots(start: int, end: int) -> set[str]:
    """시간창 안에서 배치 가능한 활동 슬롯 — 창 밖(도착 전 오전, 출국일 저녁 등)은 제외."""
    allowed: set[str] = set()
    if start <= 10 * 60 and end >= 11 * 60 + 30:
        allowed.add("morning")
    if start <= 16 * 60 + 30 and end >= 17 * 60 + 30:
        allowed.add("late_afternoon")
    if start <= 20 * 60 and end >= 21 * 60:
        allowed.add("evening")
    return allowed

# 종일형 POI 차단 목록 — 슬롯 배정 금지, 하단 '하루를 통째로 쓰는 옵션'에만 노출 (S3)
ALLDAY_KEYWORDS = (
    "ディズニー", "disney", "디즈니", "ディズニーランド", "ディズニーシー", "disneysea", "disneyland",
    "usj", "ユニバーサル", "universal", "유니버설", "유니버셜",
    "富士急", "후지큐", "fuji-q", "fujiq",
    "ワーナー", "warner", "워너", "ハリー・ポッター", "harry potter", "해리포터", "스튜디오 투어",
    "サンリオピューロランド", "sanrio", "산리오", "レゴランド", "legoland", "레고랜드",
    "よみうりランド", "としまえん",
)

# 카테고리 분류용 키워드 (일본어 + 한국어 통용 표기 모두)
_CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "garden": ("庭園", "御苑", "公園", "苑", "garden", "park", "정원", "공원", "교엔", "고엔", "가든"),
    "shrine": ("神社", "神宮", "寺", "大社", "shrine", "temple", "신사", "신궁", "지구", "절", "사원", "사찰"),
    "market": ("市場", "market", "시장", "마켓"),
    "museum": ("美術館", "博物館", "記念館", "ミュージアム", "museum", "gallery", "미술관", "박물관", "뮤지엄", "갤러리"),
    "observatory": ("展望", "タワー", "スカイツリー", "tower", "observ", "skytree", "전망", "타워", "스카이트리", "스카이 트리"),
    "nightview": ("夜景", "イルミネーション", "night", "illumination", "야경", "일루미네이션"),
    "izakaya": ("横丁", "横町", "居酒屋", "ゴールデン街", "飲み屋", "yokocho", "izakaya", "요코초", "요코쵸", "이자카야", "골목", "포장마차"),
    "shopping": ("商店街", "アウトレット", "ショッピング", "モール", "通り", "銀座", "outlet", "mall", "shopping", "쇼핑", "상점가", "아울렛", "몰", "거리"),
}

# 슬롯별 금지 카테고리 (규칙표) — 조용한 위반 금지
_SLOT_FORBIDS = {
    "morning": {"observatory", "nightview"},       # 야경·전망대는 오전 비추
    "late_afternoon": set(),                          # 제약 없음
    "evening": {"garden", "shrine", "market"},      # 공원·정원·신사·시장 = 입장마감 리스크 (S4)
}

# 카테고리 → 선호 슬롯
_PREFERRED_SLOT = {
    "garden": "morning", "shrine": "morning", "market": "morning", "museum": "morning",
    "shopping": "late_afternoon",
    "observatory": "evening", "nightview": "evening", "izakaya": "evening",
    "other": "late_afternoon",
}

# 카테고리별 기본 팁 (스니펫에 tip이 없을 때의 결정론 폴백)
_CATEGORY_TIP = {
    "garden": "정원·공원은 입장마감이 이르다(대개 ~17:00) — 낮 슬롯에만.",
    "shrine": "신사·사원은 오전이 한산하고 사진이 좋다.",
    "market": "시장은 오전에 활기가 최고 — 늦으면 문 닫는 점포가 많다.",
    "museum": "미술관·박물관은 폐관 시간(대개 17:00~18:00) 확인 필요.",
    "shopping": "쇼핑거리는 늦은 오후~해질녘이 붐비고 활기차다.",
    "observatory": "전망대는 황혼~야경 시간이 베스트 — 일몰 30분 전 입장 추천.",
    "nightview": "야경 스팟은 해가 진 뒤가 제맛.",
    "izakaya": "이자카야 골목은 저녁부터 — 첫 집은 예약 없이도 대개 가능.",
    "other": "방문 전 영업시간을 한 번 확인하세요.",
}


def _norm(s) -> str:
    return str(s or "").lower()


def is_allday_poi(title: str, why: str = "") -> bool:
    """종일형 테마파크류인가 (슬롯 배정 금지 대상)."""
    text = _norm(title) + " " + _norm(why)
    return any(k.lower() in text for k in ALLDAY_KEYWORDS)


def classify(title: str, why: str = "") -> str:
    """활동을 카테고리로 분류한다 (슬롯 적합성 판정용)."""
    text = _norm(title) + " " + _norm(why)
    for cat, kws in _CATEGORY_KEYWORDS.items():
        if any(k.lower() in text for k in kws):
            return cat
    return "other"


def slot_forbids(slot: str, category: str) -> bool:
    return category in _SLOT_FORBIDS.get(slot, set())


def default_tip(category: str) -> str:
    return _CATEGORY_TIP.get(category, _CATEGORY_TIP["other"])


def _valid_best_time(bt) -> str | None:
    bt = str(bt or "").strip().lower()
    aliases = {"morning": "morning", "오전": "morning", "아침": "morning",
               "afternoon": "late_afternoon", "late_afternoon": "late_afternoon", "오후": "late_afternoon",
               "늦은오후": "late_afternoon", "저물녘": "late_afternoon",
               "evening": "evening", "night": "evening", "저녁": "evening", "밤": "evening", "야간": "evening"}
    return aliases.get(bt)


def schedule_day(items: list[dict], seen_titles: set[str], log=None, day: int = 0,
                 allowed: set[str] | None = None) -> tuple[list[dict], list[dict]]:
    """하루 활동을 슬롯 규칙에 맞게 배치한다 (D3 + D4 코드 게이트).

    - 종일형 POI는 슬롯에서 제외하고 allday 목록으로 분리한다.
    - 전 일정 중복(같은 title 2일 배정) 제거 — seen_titles로 추적.
    - 각 활동을 선호 슬롯에 배치하되, 금지 규칙 위반 슬롯은 피한다.
    - 슬롯당 1개, 하루 최대 3개(morning/late_afternoon/evening).

    반환: (scheduled_items, allday_items)
    """
    log = log or (lambda s: None)
    scheduled: dict[str, dict] = {}
    allday: list[dict] = []

    for it in items:
        if not isinstance(it, dict):
            continue
        title = str(it.get("title") or "").strip()
        if not title:
            continue
        why = str(it.get("why") or "")

        if is_allday_poi(title, why):
            allday.append(it)
            log(f"[시간] {day}일차 활동 '{title}': 종일형 POI → 슬롯 제외, 별도 섹션으로")
            continue

        key = title.lower()
        if key in seen_titles:
            log(f"[시간] {day}일차 활동 '{title}': 다른 날과 중복 → 제거 (dedup)")
            continue

        cat = classify(title, why)
        # 선호 슬롯 결정: scout의 best_time이 유효하고 규칙 위반이 아니면 존중, 아니면 카테고리 기본
        want = _valid_best_time(it.get("best_time")) or _PREFERRED_SLOT.get(cat, "late_afternoon")
        order = [want] + [s for s in ACT_SLOTS if s != want]
        placed = False
        for slot in order:
            if allowed is not None and slot not in allowed:   # 시간창 밖 슬롯 (항공 시간 반영)
                continue
            if slot in scheduled:
                continue
            if slot_forbids(slot, cat):
                continue
            note = ""
            if slot != want and _valid_best_time(it.get("best_time")) == want and slot_forbids(want, cat):
                note = f"(시간대 규칙상 {ACT_SLOT_KO[want]}→{ACT_SLOT_KO[slot]} 조정)"
                log(f"[시간] {day}일차 '{title}': {want} 배정은 규칙 위반({cat}) → {slot}로 조정")
            entry = {
                "title": title,
                "url": str(it.get("url") or ""),
                "why": why,
                "area": str(it.get("area") or ""),
                "category": cat,
                "slot": slot,
                "time": ACT_SLOT_TIME[slot],
                "dwell_min": it.get("dwell_min"),
                "open_hours": str(it.get("open_hours") or ""),
                "last_entry": str(it.get("last_entry") or ""),
                "tip": (str(it.get("tip") or "").strip() or default_tip(cat)) + (f" {note}" if note else ""),
            }
            scheduled[slot] = entry
            seen_titles.add(key)
            placed = True
            break
        if not placed:
            log(f"[시간] {day}일차 활동 '{title}': 배치 가능한 슬롯 없음 → 제외")

    ordered = [scheduled[s] for s in ACT_SLOTS if s in scheduled]
    return ordered, allday
