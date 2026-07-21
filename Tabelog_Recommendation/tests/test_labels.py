import sqlite3

from app.labels import PREF_LABELS, area_label, genre_label, station_label
from app.labels_i18n import GENRE_LABELS
from app.stations_i18n import STATION_LABELS


def test_pref_labels_keys_match_db_distinct_prefs(real_db):
    # §14 (v2.0): 9 overseas countries joined the original 48 once the two
    # new reviewer files were included — PREF_LABELS now has 57 keys.
    conn = sqlite3.connect(real_db)
    try:
        rows = conn.execute("SELECT DISTINCT pref FROM restaurants_agg").fetchall()
    finally:
        conn.close()
    db_prefs = {row[0] for row in rows}
    assert set(PREF_LABELS.keys()) == db_prefs


def test_pref_labels_taiwan_is_marked_overseas():
    # PREF_LABELS was restructured in M6 to {slug: {"ko","ja","en"}} — v1.4 §11.2.
    assert PREF_LABELS["taiwan"]["ko"] == "타이완(해외)"


def test_pref_labels_get_with_default_avoids_keyerror():
    assert PREF_LABELS.get("unknown_slug", "unknown_slug") == "unknown_slug"


# --- M6 (§11.5): multi-language labels ---


def test_genre_labels_keys_match_db_distinct_genres(real_db):
    # Independently verified replacement labels_i18n.py (2026-07-09) now
    # covers all 220 genres exactly — back to a strict equality check.
    conn = sqlite3.connect(real_db)
    try:
        rows = conn.execute("SELECT DISTINCT genre FROM restaurant_genres").fetchall()
    finally:
        conn.close()
    db_genres = {row[0] for row in rows}
    assert set(GENRE_LABELS.keys()) == db_genres


def test_genre_label_ko_and_ja_and_fallback():
    assert genre_label("ラーメン", "ko") == "라멘"
    assert genre_label("ラーメン", "ja") == "ラーメン"
    assert genre_label("존재하지 않는 장르", "ko") == "존재하지 않는 장르"


def test_pref_labels_have_all_three_languages_for_all_57_keys():
    for slug, translations in PREF_LABELS.items():
        for lang in ("ko", "ja", "en"):
            assert lang in translations, f"{slug} missing {lang}"
            assert translations[lang]


def test_area_label_tokyo_a1301_contains_most_frequent_station(real_db):
    # ja mode never translates station names (§13.1), so this checks the
    # underlying frequency computation independent of the M8 translation table.
    label = area_label(real_db, "tokyo", "A1301", "ja")
    assert "銀座" in label


# --- M7 (§12.4): area label drops the code prefix ---


def test_area_label_does_not_include_area_code(real_db):
    label = area_label(real_db, "tokyo", "A1301", "ja")
    assert "A1301" not in label
    assert "A13" not in label
    assert "銀座" in label


# --- M8 (§13.4): station name labels ---


def test_station_labels_has_1889_keys():
    # Independently verified replacement stations_i18n.py (2026-07-09)
    # expanded coverage from 1,142 to 1,889 station names.
    assert len(STATION_LABELS) == 1889


def test_station_label_ko_en_and_fallback():
    assert station_label("銀座", "ko") == "긴자"
    assert station_label("銀座", "en") == "Ginza"
    assert station_label("銀座", "ja") == "銀座"
    assert station_label("등록되지 않은 역", "ko") == "등록되지 않은 역"


def test_area_label_uses_translated_station_name_in_ko_mode(real_db):
    label = area_label(real_db, "tokyo", "A1301", "ko")
    assert "긴자" in label
    assert "銀座" not in label
