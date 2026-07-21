import json
import sqlite3
from pathlib import Path

from app.labels_i18n import GENRE_LABELS
from app.stations_i18n import STATION_LABELS

PREF_LABELS: dict[str, dict[str, str]] = {
    "hokkaido": {"ko": "홋카이도", "ja": "北海道", "en": "Hokkaido"},
    "aomori": {"ko": "아오모리현", "ja": "青森県", "en": "Aomori"},
    "iwate": {"ko": "이와테현", "ja": "岩手県", "en": "Iwate"},
    "miyagi": {"ko": "미야기현", "ja": "宮城県", "en": "Miyagi"},
    "akita": {"ko": "아키타현", "ja": "秋田県", "en": "Akita"},
    "yamagata": {"ko": "야마가타현", "ja": "山形県", "en": "Yamagata"},
    "fukushima": {"ko": "후쿠시마현", "ja": "福島県", "en": "Fukushima"},
    "ibaraki": {"ko": "이바라키현", "ja": "茨城県", "en": "Ibaraki"},
    "tochigi": {"ko": "도치기현", "ja": "栃木県", "en": "Tochigi"},
    "gunma": {"ko": "군마현", "ja": "群馬県", "en": "Gunma"},
    "saitama": {"ko": "사이타마현", "ja": "埼玉県", "en": "Saitama"},
    "chiba": {"ko": "지바현", "ja": "千葉県", "en": "Chiba"},
    "tokyo": {"ko": "도쿄도", "ja": "東京都", "en": "Tokyo"},
    "kanagawa": {"ko": "가나가와현", "ja": "神奈川県", "en": "Kanagawa"},
    "niigata": {"ko": "니가타현", "ja": "新潟県", "en": "Niigata"},
    "toyama": {"ko": "도야마현", "ja": "富山県", "en": "Toyama"},
    "ishikawa": {"ko": "이시카와현", "ja": "石川県", "en": "Ishikawa"},
    "fukui": {"ko": "후쿠이현", "ja": "福井県", "en": "Fukui"},
    "yamanashi": {"ko": "야마나시현", "ja": "山梨県", "en": "Yamanashi"},
    "nagano": {"ko": "나가노현", "ja": "長野県", "en": "Nagano"},
    "gifu": {"ko": "기후현", "ja": "岐阜県", "en": "Gifu"},
    "shizuoka": {"ko": "시즈오카현", "ja": "静岡県", "en": "Shizuoka"},
    "aichi": {"ko": "아이치현", "ja": "愛知県", "en": "Aichi"},
    "mie": {"ko": "미에현", "ja": "三重県", "en": "Mie"},
    "shiga": {"ko": "시가현", "ja": "滋賀県", "en": "Shiga"},
    "kyoto": {"ko": "교토부", "ja": "京都府", "en": "Kyoto"},
    "osaka": {"ko": "오사카부", "ja": "大阪府", "en": "Osaka"},
    "hyogo": {"ko": "효고현", "ja": "兵庫県", "en": "Hyogo"},
    "nara": {"ko": "나라현", "ja": "奈良県", "en": "Nara"},
    "wakayama": {"ko": "와카야마현", "ja": "和歌山県", "en": "Wakayama"},
    "tottori": {"ko": "돗토리현", "ja": "鳥取県", "en": "Tottori"},
    "shimane": {"ko": "시마네현", "ja": "島根県", "en": "Shimane"},
    "okayama": {"ko": "오카야마현", "ja": "岡山県", "en": "Okayama"},
    "hiroshima": {"ko": "히로시마현", "ja": "広島県", "en": "Hiroshima"},
    "yamaguchi": {"ko": "야마구치현", "ja": "山口県", "en": "Yamaguchi"},
    "tokushima": {"ko": "도쿠시마현", "ja": "徳島県", "en": "Tokushima"},
    "kagawa": {"ko": "가가와현", "ja": "香川県", "en": "Kagawa"},
    "ehime": {"ko": "에히메현", "ja": "愛媛県", "en": "Ehime"},
    "kochi": {"ko": "고치현", "ja": "高知県", "en": "Kochi"},
    "fukuoka": {"ko": "후쿠오카현", "ja": "福岡県", "en": "Fukuoka"},
    "saga": {"ko": "사가현", "ja": "佐賀県", "en": "Saga"},
    "nagasaki": {"ko": "나가사키현", "ja": "長崎県", "en": "Nagasaki"},
    "kumamoto": {"ko": "구마모토현", "ja": "熊本県", "en": "Kumamoto"},
    "oita": {"ko": "오이타현", "ja": "大分県", "en": "Oita"},
    "miyazaki": {"ko": "미야자키현", "ja": "宮崎県", "en": "Miyazaki"},
    "kagoshima": {"ko": "가고시마현", "ja": "鹿児島県", "en": "Kagoshima"},
    "okinawa": {"ko": "오키나와현", "ja": "沖縄県", "en": "Okinawa"},
    "taiwan": {"ko": "타이완(해외)", "ja": "台湾(海外)", "en": "Taiwan (overseas)"},
    # §14 (v2.0): additional reviewers brought 9 overseas countries beyond the
    # original 47-prefectures-+-Taiwan set (measured on data/reviewers/).
    "singapore": {"ko": "싱가포르(해외)", "ja": "シンガポール(海外)", "en": "Singapore (overseas)"},
    "hawaii": {"ko": "하와이(해외)", "ja": "ハワイ(海外)", "en": "Hawaii (overseas)"},
    "indonesia": {"ko": "인도네시아(해외)", "ja": "インドネシア(海外)", "en": "Indonesia (overseas)"},
    "southkorea": {"ko": "대한민국(해외)", "ja": "韓国(海外)", "en": "South Korea (overseas)"},
    "unitedkingdom": {"ko": "영국(해외)", "ja": "イギリス(海外)", "en": "United Kingdom (overseas)"},
    "luxembourg": {"ko": "룩셈부르크(해외)", "ja": "ルクセンブルク(海外)", "en": "Luxembourg (overseas)"},
    "belgium": {"ko": "벨기에(해외)", "ja": "ベルギー(海外)", "en": "Belgium (overseas)"},
    "italy": {"ko": "이탈리아(해외)", "ja": "イタリア(海外)", "en": "Italy (overseas)"},
    "france": {"ko": "프랑스(해외)", "ja": "フランス(海外)", "en": "France (overseas)"},
}

_AREA_SUFFIX = {"ko": "일대", "ja": "周辺", "en": "area"}
_AREA_UNKNOWN = {"ko": "정보 없음", "ja": "情報なし", "en": "Unknown"}


def genre_label(genre: str, lang: str = "ko") -> str:
    if lang == "ja":
        return genre
    return GENRE_LABELS.get(genre, {}).get(lang, genre)


def pref_label(slug: str, lang: str = "ko") -> str:
    return PREF_LABELS.get(slug, {}).get(lang, slug)


def station_label(name: str, lang: str = "ko") -> str:
    if lang == "ja":
        return name
    return STATION_LABELS.get(name, {}).get(lang, name)


def area_label(db: str | Path, pref: str, code: str, lang: str = "ko") -> str:
    conn = sqlite3.connect(db)
    try:
        # restaurants_agg (§14.2): one row per restaurant, so a restaurant
        # reviewed by multiple reviewers doesn't skew station frequency.
        rows = conn.execute(
            "SELECT stations_json FROM restaurants_agg "
            "WHERE pref = ? AND (area2 = ? OR area3 = ?)",
            (pref, code, code),
        ).fetchall()
    finally:
        conn.close()

    counts: dict[str, int] = {}
    for (stations_json,) in rows:
        for station in json.loads(stations_json):
            counts[station] = counts.get(station, 0) + 1

    # Deterministic per §11.3: frequency descending, ties broken by station
    # name ascending — always on the original name, so the ranking (and thus
    # which 2 stations win) never changes across languages.
    top_stations = sorted(counts, key=lambda s: (-counts[s], s))[:2]
    if not top_stations:
        # The area code itself is an internal value only (§12.1) — never
        # surface it in a display string, even in this no-data fallback.
        return _AREA_UNKNOWN.get(lang, _AREA_UNKNOWN["ko"])

    suffix = _AREA_SUFFIX.get(lang, _AREA_SUFFIX["ko"])
    labels = [station_label(s, lang) for s in top_stations]
    return f"{'·'.join(labels)} {suffix}"
