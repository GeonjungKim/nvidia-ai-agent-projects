"""표시 언어 다국어화 (ko/ja/en) — 이전 프로젝트의 검증된 라벨 사전을 재사용한다.

전략(자원 최적): 구조화 메타데이터(장르·역·지역·정기휴무)만 정적 사전으로 번역한다.
- 이 필드들은 모든 카드에 반복 등장하고 개수가 유한하다 → 사전 조회가 정확·즉시·무비용(LLM 0회).
- 식당 '이름'은 고유명사라 번역하지 않는다 — 지도/타베로그/예약에 원문이 필요하고, 번역해도
  검색성이 오르지 않는다 (구글맵·현지 앱도 현지명을 그대로 보여준다). 장기 스크랩으로 계속
  늘어나는 이름을 LLM으로 번역하는 것이 바로 피해야 할 자원 낭비다.
- LLM 자유서술(추천 이유·활동 설명)은 별도 번역 에이전트 대신 '생성 단계에서 해당 언어로 바로
  출력'하게 한다(같은 호출·같은 비용). 이 부분은 Phase 2에서 각 에이전트 프롬프트에 언어를 주입.
"""
from __future__ import annotations

# 표시 언어 (라벨=UI 표기, 값=코드)
LANGS: dict[str, str] = {"한국어": "ko", "日本語": "ja", "English": "en"}
LANG_CODES = ("ko", "ja", "en")
DEFAULT_LANG = "ko"

# 검증된 라벨 사전·헬퍼를 이전 프로젝트에서 그대로 import (Tabelog_Recommendation).
# config를 먼저 import해 sys.path에 데이터 폴더가 들어가도록 보장한다 (import 순서 무관하게).
# 배포/누락 시에도 죽지 않게 항등 함수로 폴백한다 (fail-soft — 최악의 경우 원문 일본어 표시).
import tabetabi.config  # noqa: F401  (부작용: sys.path에 Tabelog_Recommendation 추가)

try:
    from app.labels import genre_label as _genre_label
    from app.labels import pref_label as _pref_label
    from app.labels import station_label as _station_label
    I18N_READY = True
except Exception:      # pragma: no cover - 데이터 폴더 부재 등
    I18N_READY = False

    def _genre_label(genre: str, lang: str = "ko") -> str:
        return genre

    def _pref_label(slug: str, lang: str = "ko") -> str:
        return slug

    def _station_label(name: str, lang: str = "ko") -> str:
        return name


# 역 접미사 (station_label은 역명만 주므로 접미사는 언어별로 붙인다)
_STATION_SUFFIX = {"ko": "역", "ja": "駅", "en": " Sta."}

# 정기휴무 어휘 — DB 실측(상위 토큰) 기반 유한 집합. 원자 토큰 단위로 번역한다.
_CLOSED_TOKENS = {
    "日曜日": {"ko": "일요일", "en": "Sun"}, "月曜日": {"ko": "월요일", "en": "Mon"},
    "火曜日": {"ko": "화요일", "en": "Tue"}, "水曜日": {"ko": "수요일", "en": "Wed"},
    "木曜日": {"ko": "목요일", "en": "Thu"}, "金曜日": {"ko": "금요일", "en": "Fri"},
    "土曜日": {"ko": "토요일", "en": "Sat"},
    "日曜": {"ko": "일요일", "en": "Sun"}, "月曜": {"ko": "월요일", "en": "Mon"},
    "火曜": {"ko": "화요일", "en": "Tue"}, "水曜": {"ko": "수요일", "en": "Wed"},
    "木曜": {"ko": "목요일", "en": "Thu"}, "金曜": {"ko": "금요일", "en": "Fri"},
    "土曜": {"ko": "토요일", "en": "Sat"},
    "祝日": {"ko": "공휴일", "en": "Holidays"}, "祝後日": {"ko": "공휴일 다음날", "en": "Day after holiday"},
    "祝前日": {"ko": "공휴일 전날", "en": "Day before holiday"},
    "無休": {"ko": "연중무휴", "en": "Open daily"}, "不定休": {"ko": "부정기 휴무", "en": "Irregular"},
}


def norm_lang(lang: str | None) -> str:
    return lang if lang in LANG_CODES else DEFAULT_LANG


def t_genre(genre: str, lang: str = "ko") -> str:
    return _genre_label(genre, norm_lang(lang))


def t_genres(csv: str, lang: str = "ko") -> str:
    """콤마로 이어진 장르 문자열을 통째로 번역한다 (예: 'ラーメン, 寿司')."""
    lang = norm_lang(lang)
    if lang == "ja" or not csv:
        return csv or ""
    parts = [t_genre(g.strip(), lang) for g in str(csv).split(",") if g.strip()]
    return ", ".join(parts)


def t_pref(slug: str, lang: str = "ko") -> str:
    return _pref_label(slug, norm_lang(lang))


def t_station(name: str, lang: str = "ko", suffix: bool = True) -> str:
    """역/지역명 번역 (+ 언어별 접미사). 사전에 없으면 원문 유지."""
    lang = norm_lang(lang)
    if not name:
        return ""
    label = _station_label(name, lang)
    return label + _STATION_SUFFIX[lang] if suffix else label


def t_area(name: str, lang: str = "ko") -> str:
    """앵커/세부지역 표기 — 대개 역명과 같은 어휘라 station 사전을 재사용 (접미사 없음)."""
    return t_station(name, lang, suffix=False)


def t_closed(csv: str, lang: str = "ko") -> str:
    """정기휴무 문자열 번역 (예: '土曜日、日曜日、祝日'). 구분자(、·,)는 유지."""
    lang = norm_lang(lang)
    if lang == "ja" or not csv:
        return csv or ""
    import re
    return re.sub(r"[^、・,\s]+",
                  lambda m: _CLOSED_TOKENS.get(m.group(0), {}).get(lang, m.group(0)),
                  str(csv))
