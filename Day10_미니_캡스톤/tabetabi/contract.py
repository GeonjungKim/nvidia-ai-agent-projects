"""SHARED CONTRACT — 모든 에이전트가 공유하는 여행 계약.

Day9 원칙: 병렬로 흩어지기 전에 계약을 먼저 고정한다.
사용자가 잠근(locked) 항목은 어떤 에이전트도 변경할 수 없다.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta


# 흔한 장르 표기 → 타베로그 DB 표기(일본어) 정규화. 미등록 표기는 그대로 통과.
_GENRE_ALIASES = {
    "라멘": "ラーメン", "라면": "ラーメン", "らーめん": "ラーメン", "ramen": "ラーメン",
    "스시": "寿司", "초밥": "寿司", "すし": "寿司", "sushi": "寿司", "鮨": "寿司",
    "츠케멘": "つけ麺", "쓰케멘": "つけ麺",
    "야키니쿠": "焼肉", "yakiniku": "焼肉", "야키토리": "焼鳥",
    "이자카야": "居酒屋", "izakaya": "居酒屋",
    "카페": "カフェ", "cafe": "カフェ",
    "우동": "うどん", "udon": "うどん", "소바": "そば", "soba": "そば",
    "이탈리안": "イタリアン", "프렌치": "フレンチ", "중식": "中華料理", "중화요리": "中華料理",
    "텐푸라": "天ぷら", "튀김": "天ぷら", "돈카츠": "とんかつ", "돈가스": "とんかつ",
    "카레": "カレー", "빵": "パン", "베이커리": "パン", "디저트": "スイーツ", "스위츠": "スイーツ",
}


def normalize_genre(g) -> str:
    s = str(g).strip()
    return _GENRE_ALIASES.get(s.lower(), _GENRE_ALIASES.get(s, s))


# 흔한 세부지역 한국어 표기 → 타베로그 DB 표기(일본어)
_AREA_ALIASES = {
    "신주쿠": "新宿", "시부야": "渋谷", "긴자": "銀座", "아사쿠사": "浅草", "우에노": "上野",
    "이케부쿠로": "池袋", "롯폰기": "六本木", "아키하바라": "秋葉原", "에비스": "恵比寿",
    "나카메구로": "中目黒", "키치조지": "吉祥寺", "요코하마": "横浜",
    "오모테산도": "表参道", "표참도": "表参道", "하라주쿠": "原宿", "아오야마": "青山",
    "고마고메": "駒込", "코마고메": "駒込", "스가모": "巣鴨", "타바타": "田端",
    "메이지진구마에": "明治神宮前", "시나가와": "品川", "도쿄": "東京",
    "도톤보리": "道頓堀", "난바": "難波", "우메다": "梅田", "신사이바시": "心斎橋", "텐노지": "天王寺",
    "기온": "祇園", "가와라마치": "河原町", "하카타": "博多", "텐진": "天神", "스스키노": "すすきの",
}


def normalize_area(a) -> str:
    """세부지역/역 표기 정규화. 뒤의 '역'·'駅'은 떼고, 한국어 통용 표기는 일본어로 매핑."""
    s = str(a).strip()
    for suffix in ("역", "駅"):
        if s.endswith(suffix) and len(s) > len(suffix):
            s = s[: -len(suffix)]
    return _AREA_ALIASES.get(s, s)


_SLOT_ALIASES = {"점심": "lunch", "런치": "lunch", "브런치": "lunch", "저녁": "dinner", "디너": "dinner",
                 "카페": "cafe", "디저트": "cafe", "숙소": "stay", "활동": "activity", "관광": "activity"}


@dataclass
class LockedItem:
    day: int = 0            # 1-based, 0 = 미지정(콘시어지가 배치)
    slot: str = ""          # lunch | dinner | activity | stay
    name: str = ""
    note: str = ""


@dataclass
class TripContract:
    pref: str = ""                      # Tabelog 지역 코드 (예: tokyo, osaka)
    areas: list[str] = field(default_factory=list)   # 세부지역/역 힌트 (예: 新宿, 銀座)
    start_date: str = ""                # YYYY-MM-DD
    end_date: str = ""
    origin: str = "서울"                 # 출발 도시 (항공 링크용)
    party: int = 2
    max_dinner_budget: int | None = None   # 저녁 1인 예산 상한 (엔)
    genres_pref: list[str] = field(default_factory=list)
    locked: list[LockedItem] = field(default_factory=list)
    stay_area: str = ""                 # 숙소 앵커 (일본어 역/지명, 예: 駒込) — 1급 시민 (D1)
    day_anchors: dict[int, str] = field(default_factory=dict)   # 일자별 앵커 (사용자 수정 가능, D1)
    theme_park: bool = False            # 테마파크 종일 일정 의향 (D3)
    notes: str = ""

    @property
    def num_days(self) -> int:
        try:
            d0 = date.fromisoformat(self.start_date)
            d1 = date.fromisoformat(self.end_date)
        except (ValueError, TypeError):
            return 0
        n = (d1 - d0).days + 1
        return n if 1 <= n <= 14 else 0

    def date_of(self, day: int) -> str:
        try:
            return (date.fromisoformat(self.start_date) + timedelta(days=day - 1)).isoformat()
        except (ValueError, TypeError):
            return ""

    def is_ready(self) -> bool:
        return bool(self.pref and self.num_days > 0)

    def hotel_anchor(self) -> str:
        """호텔 검색·추천 앵커 = 숙소역(stay_area). 없으면 areas[0] 폴백 (D1)."""
        return self.stay_area or (self.areas[0] if self.areas else "")

    def effective_day_anchors(self) -> dict[int, str]:
        """일자별 앵커를 결정론으로 확정한다 (D1).

        규칙: 사용자가 day_anchors에 지정한 날은 그대로 → 마지막 날은 stay_area 인접 →
        나머지는 areas 순환 (areas가 없으면 stay_area로 채운다).
        """
        n = self.num_days
        if n <= 0:
            return {}
        pool = list(self.areas) or ([self.stay_area] if self.stay_area else [])
        out: dict[int, str] = {}
        for d in range(1, n + 1):
            fixed = self.day_anchors.get(d) or self.day_anchors.get(str(d))
            if fixed:
                out[d] = normalize_area(fixed)
            elif d == n and self.stay_area:
                out[d] = self.stay_area
            elif pool:
                out[d] = pool[(d - 1) % len(pool)]
            elif self.stay_area:
                out[d] = self.stay_area
        return out

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "TripContract":
        locked = []
        for it in d.get("locked") or []:
            if isinstance(it, dict) and it.get("name"):
                slot_raw = str(it.get("slot") or "").strip().lower()
                try:
                    day = int(it.get("day") or 0)
                except (ValueError, TypeError):
                    day = 0
                locked.append(LockedItem(
                    day=day,
                    slot=_SLOT_ALIASES.get(slot_raw, slot_raw),
                    name=str(it["name"]),
                    note=str(it.get("note") or ""),
                ))
        budget = d.get("max_dinner_budget")
        try:
            budget = int(budget) if budget not in (None, "", 0) else None
        except (ValueError, TypeError):
            budget = None
        areas_raw = d.get("areas") or []
        if isinstance(areas_raw, str):          # LLM이 배열 대신 문자열을 주는 경우 방어
            areas_raw = [areas_raw]

        # 숙소 앵커: stay_area 필드 우선, 없으면 locked의 stay 슬롯을 승격 (notes에만 남기는 것 금지, D1)
        stay_area = normalize_area(d.get("stay_area") or "")
        if not stay_area:
            stay = next((lk for lk in locked if lk.slot == "stay" and lk.name), None)
            if stay:
                stay_area = normalize_area(stay.name)

        day_anchors_raw = d.get("day_anchors") or {}
        day_anchors: dict[int, str] = {}
        if isinstance(day_anchors_raw, dict):
            for k, v in day_anchors_raw.items():
                try:
                    day_anchors[int(k)] = normalize_area(v)
                except (ValueError, TypeError):
                    continue

        return cls(
            pref=str(d.get("pref") or "").strip().lower(),
            areas=[normalize_area(a) for a in areas_raw if a],
            start_date=str(d.get("start_date") or ""),
            end_date=str(d.get("end_date") or ""),
            origin=str(d.get("origin") or "서울"),
            party=int(d.get("party") or 2),
            max_dinner_budget=budget,
            genres_pref=[normalize_genre(g) for g in (d.get("genres_pref") or []) if g],
            locked=locked,
            stay_area=stay_area,
            day_anchors=day_anchors,
            theme_park=bool(d.get("theme_park")),
            notes=str(d.get("notes") or ""),
        )

    def summary_md(self) -> str:
        lines = [f"**지역** `{self.pref or '?'}`  ·  **기간** {self.start_date or '?'} ~ {self.end_date or '?'} ({self.num_days or '?'}일)  ·  **인원** {self.party}명"]
        if self.areas:
            lines.append(f"**세부지역 힌트** {', '.join(self.areas)}")
        if self.stay_area:
            lines.append(f"🏨 **숙소 앵커** {self.stay_area} — 호텔은 이 역 기준으로 추천")
        anchors = self.effective_day_anchors()
        if anchors:
            lines.append("🧭 **일자별 앵커** " + " / ".join(f"Day{d}: {a}" for d, a in sorted(anchors.items())))
        if self.theme_park:
            lines.append("🎢 **테마파크** 하루 통째 일정 편성 의향 있음")
        if self.max_dinner_budget:
            lines.append(f"**저녁 예산** 1인 ~¥{self.max_dinner_budget:,}")
        if self.genres_pref:
            lines.append(f"**선호 장르** {', '.join(self.genres_pref)}")
        for lk in self.locked:
            day = f"{lk.day}일차 " if lk.day else ""
            slot = f"{lk.slot} " if lk.slot else ""
            lines.append(f"🔒 **고정** {day}{slot}— {lk.name}" + (f" ({lk.note})" if lk.note else ""))
        if self.origin:
            lines.append(f"**출발지** {self.origin}")
        if self.notes:
            lines.append(f"메모: {self.notes}")
        return "\n\n".join(lines)


def extract_json(text: str) -> dict | None:
    """LLM 출력에서 JSON 오브젝트를 관대하게 추출 (```펜스·앞뒤 잡담 허용)."""
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    raw = m.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 흔한 오류 보정: 후행 콤마 제거 후 1회 재시도
        try:
            return json.loads(re.sub(r",\s*([}\]])", r"\1", raw))
        except json.JSONDecodeError:
            return None
