import sys
from pathlib import Path

# streamlit's bootstrap puts only the script's own directory (app/) on
# sys.path, not the project root, so `from app.*` below would otherwise
# fail with ModuleNotFoundError when launched via `streamlit run app/ui.py`.
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import sqlite3

import streamlit as st

from app.generate import generate, load_model
from app.labels import area_label, genre_label, pref_label, station_label
from app.mapview import (
    LAYER_ID,
    N02_ATTRIBUTION,
    build_map_points,
    compute_default_view,
    focused_view,
    load_station_coords,
    render_map,
)
from app.maplinks import apple_url, build_route_url, google_search_url
from app.query import count, search

DB_PATH = Path("app.db")
STATION_COORDS_PATH = Path("data/station_coords.json")
RECOMMEND_TOP_N = 5
PAGE_SIZE = 30

LANG_OPTIONS = {"ko": "한국어", "ja": "日本語", "en": "English"}

UI_TEXT: dict[str, dict[str, str]] = {
    "ko": {
        "page_title": "Tabelog 리뷰어 추천 검색",
        "filter_header": "필터",
        "region_popover": "지역 선택",
        "region_dialog_done": "확인",
        "advanced_filter": "고급 필터 (지역 세부)",
        "area2_label": "지역(시군구)",
        "area3_label": "지역(동네)",
        "genre_label": "장르",
        "station_label": "역 이름으로 찾기 (예: 銀座)",
        "station_mode_label": "역 검색 방식",
        "station_mode_exact": "정확히 일치",
        "station_mode_partial": "부분 포함",
        "station_primary_only_label": "대표역만 검색",
        "budget_label": "예산(저녁)",
        "budget_lunch_label": "예산(점심)",
        "all_option": "전체",
        "count_suffix": "{n}건",
        "budget_notice": "예산 미기재 식당은 제외됩니다",
        "budget_lunch_notice": "점심 예산 미기재 식당은 제외됩니다",
        "sort_label": "정렬",
        "sort_bayes": "추천순",
        "sort_rating": "평점순",
        "sort_reviews": "리뷰 많은 순",
        "sort_reviewer": "리뷰어 평점순",
        "no_results": "조건에 맞는 식당이 없습니다. 지역 범위를 넓히거나 장르·예산 필터를 완화해 보세요.",
        "result_count_paged": "전체 {total}곳 중 {start}–{end}",
        "prev_page": "◀ 이전",
        "next_page": "다음 ▶",
        "card_view_on_map": "지도에서 보기",
        "map_panel_tabelog_link": "Tabelog에서 보기",
        "generate_button": "추천문 생성",
        "generating": "추천문 생성 중...",
        "card_genre": "장르",
        "card_station": "역",
        "card_no_rating": "평점 없음",
        "card_review_count": "리뷰 {n}건",
        "card_budget": "예산 · 저녁 {dinner} / 점심 {lunch}",
        "card_not_listed": "미기재",
        "card_reviewer_rating": "리뷰어 평균 평점 {rating}",
        "card_visit": "리뷰어 {k}명 · 총 {n}회 방문 (최근 {month})",
        "card_maps_link_google": "Google 지도에서 검색",
        "card_maps_link_apple": "Apple 지도에서 검색",
        "db_missing": "DB 파일이 없습니다: {path}. 먼저 python -m app.load ...로 적재하세요.",
        "route_n_label": "경로에 포함할 곳 수",
        "route_button": "상위 {n}곳 경로 보기",
        "route_link_text": "Google 지도에서 경로 보기",
        "route_caption_mobile_limit": "모바일 브라우저에서는 경유지 3곳까지 표시될 수 있음",
        "route_caption_approx": "위치는 이름 검색 기반 근사",
        "map_n_label": "지도에 표시할 곳 수",
        "map_caption_approx": "핀은 최인접 역 기준 근사 위치",
        "map_caption_source": N02_ATTRIBUTION,
        "map_caption_excluded": "좌표 미확보 역의 식당 {k}곳 제외",
    },
    "ja": {
        "page_title": "Tabelog レビュアーおすすめ検索",
        "filter_header": "フィルター",
        "region_popover": "地域を選択",
        "region_dialog_done": "確定",
        "advanced_filter": "詳細フィルター(地域詳細)",
        "area2_label": "地域(市区町村)",
        "area3_label": "地域(エリア)",
        "genre_label": "ジャンル",
        "station_label": "駅名で検索 (例: 銀座)",
        "station_mode_label": "駅名検索方式",
        "station_mode_exact": "完全一致",
        "station_mode_partial": "部分一致",
        "station_primary_only_label": "代表駅のみ検索",
        "budget_label": "予算(夜)",
        "budget_lunch_label": "予算(昼)",
        "all_option": "すべて",
        "count_suffix": "{n}件",
        "budget_notice": "予算未記載の店舗は除外されます",
        "budget_lunch_notice": "昼の予算が未記載の店舗は除外されます",
        "sort_label": "並び替え",
        "sort_bayes": "おすすめ順",
        "sort_rating": "評価順",
        "sort_reviews": "レビュー数順",
        "sort_reviewer": "レビュアー評価順",
        "no_results": "条件に合う店舗がありません。地域範囲を広げるか、ジャンル・予算フィルターを緩和してください。",
        "result_count_paged": "全{total}件中 {start}–{end}",
        "prev_page": "◀ 前へ",
        "next_page": "次へ ▶",
        "card_view_on_map": "地図で見る",
        "map_panel_tabelog_link": "Tabelogで見る",
        "generate_button": "おすすめ文生成",
        "generating": "おすすめ文を生成中...",
        "card_genre": "ジャンル",
        "card_station": "駅",
        "card_no_rating": "評価なし",
        "card_review_count": "レビュー{n}件",
        "card_budget": "予算 · 夜 {dinner} / 昼 {lunch}",
        "card_not_listed": "未記載",
        "card_reviewer_rating": "レビュアー平均評価 {rating}",
        "card_visit": "レビュアー{k}名 · 合計{n}回訪問 (最近{month})",
        "card_maps_link_google": "Googleマップで検索",
        "card_maps_link_apple": "Appleマップで検索",
        "db_missing": "DBファイルがありません: {path}。先に python -m app.load ... で読み込んでください。",
        "route_n_label": "経路に含める件数",
        "route_button": "上位{n}件の経路を見る",
        "route_link_text": "Googleマップで経路を見る",
        "route_caption_mobile_limit": "モバイルブラウザでは経由地が3か所までしか表示されない場合があります",
        "route_caption_approx": "位置は名前検索に基づく近似値です",
        "map_n_label": "地図に表示する件数",
        "map_caption_approx": "ピンは最寄り駅を基準とした近似位置です",
        "map_caption_source": N02_ATTRIBUTION,
        "map_caption_excluded": "座標未取得の駅の店舗{k}件を除外",
    },
    "en": {
        "page_title": "Tabelog Reviewer Recommendations",
        "filter_header": "Filters",
        "region_popover": "Select region",
        "region_dialog_done": "Done",
        "advanced_filter": "Advanced filters (region detail)",
        "area2_label": "Region (city/ward)",
        "area3_label": "Region (neighborhood)",
        "genre_label": "Genre",
        "station_label": "Search by station name (e.g. Ginza)",
        "station_mode_label": "Station search mode",
        "station_mode_exact": "Exact match",
        "station_mode_partial": "Partial match",
        "station_primary_only_label": "Primary station only",
        "budget_label": "Budget (dinner)",
        "budget_lunch_label": "Budget (lunch)",
        "all_option": "All",
        "count_suffix": "{n}",
        "budget_notice": "Restaurants without a listed budget are excluded",
        "budget_lunch_notice": "Restaurants without a listed lunch budget are excluded",
        "sort_label": "Sort",
        "sort_bayes": "Recommended",
        "sort_rating": "Rating",
        "sort_reviews": "Most reviewed",
        "sort_reviewer": "Reviewer rating",
        "no_results": "No restaurants match these filters. Try widening the region or relaxing the genre/budget filters.",
        "result_count_paged": "{start}–{end} of {total}",
        "prev_page": "◀ Previous",
        "next_page": "Next ▶",
        "card_view_on_map": "View on map",
        "map_panel_tabelog_link": "View on Tabelog",
        "generate_button": "Generate recommendation",
        "generating": "Generating recommendation...",
        "card_genre": "Genre",
        "card_station": "Station",
        "card_no_rating": "No rating",
        "card_review_count": "{n} reviews",
        "card_budget": "Budget · Dinner {dinner} / Lunch {lunch}",
        "card_not_listed": "Not listed",
        "card_reviewer_rating": "Reviewer avg rating {rating}",
        "card_visit": "{k} reviewer(s) · {n} visits total (last: {month})",
        "card_maps_link_google": "Search on Google Maps",
        "card_maps_link_apple": "Search on Apple Maps",
        "db_missing": "DB file not found: {path}. Run python -m app.load ... first.",
        "route_n_label": "Number of stops to include",
        "route_button": "View route for top {n}",
        "route_link_text": "View route on Google Maps",
        "route_caption_mobile_limit": "Mobile browsers may only display up to 3 waypoints",
        "route_caption_approx": "Locations are approximate, based on name search",
        "map_n_label": "Number of pins to show",
        "map_caption_approx": "Pins show an approximate location based on the nearest station",
        "map_caption_source": N02_ATTRIBUTION,
        "map_caption_excluded": "{k} restaurants excluded (station coordinates unavailable)",
    },
}


def _fetch_pref_options(db_path: Path) -> list[tuple[str, int]]:
    # restaurants_agg (§14.2): one row per restaurant, so counts aren't
    # inflated by restaurants with multiple reviewers.
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(
            "SELECT pref, COUNT(*) FROM restaurants_agg GROUP BY pref ORDER BY pref"
        ).fetchall()
    finally:
        conn.close()


def _fetch_area2_options(db_path: Path, pref: str) -> list[tuple[str, int]]:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(
            "SELECT area2, COUNT(*) FROM restaurants_agg WHERE pref = ? "
            "GROUP BY area2 ORDER BY area2",
            (pref,),
        ).fetchall()
    finally:
        conn.close()


def _fetch_area3_options(db_path: Path, pref: str, area2: str) -> list[tuple[str, int]]:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(
            "SELECT area3, COUNT(*) FROM restaurants_agg WHERE pref = ? AND area2 = ? "
            "GROUP BY area3 ORDER BY area3",
            (pref, area2),
        ).fetchall()
    finally:
        conn.close()


def _fetch_genre_options(
    db_path: Path,
    prefs: list[str] | None,
    area2: str | None,
    area3: str | None,
) -> list[tuple[str, int]]:
    conditions = []
    params: list[str] = []
    if prefs:
        placeholders = ",".join("?" for _ in prefs)
        conditions.append(f"r.pref IN ({placeholders})")
        params.extend(prefs)
    for column, value in (("r.area2", area2), ("r.area3", area3)):
        if value is not None:
            conditions.append(f"{column} = ?")
            params.append(value)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(
            "SELECT g.genre, COUNT(*) FROM restaurant_genres g "
            "JOIN restaurants_agg r ON r.restaurant_id = g.restaurant_id "
            f"{where_clause} "
            "GROUP BY g.genre ORDER BY COUNT(*) DESC",
            params,
        ).fetchall()
    finally:
        conn.close()


def _fetch_budget_options(db_path: Path, meal: str) -> list[str]:
    # meal is "dinner" or "lunch" -> a fixed pair of trusted column names,
    # never user input, so this f-string can't be an injection vector.
    column = f"budget_{meal}"
    floor_column = f"budget_{meal}_floor"
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            f"SELECT DISTINCT {column}, {floor_column} FROM restaurants_agg "
            f"WHERE {column} IS NOT NULL ORDER BY {floor_column} ASC"
        ).fetchall()
    finally:
        conn.close()
    return [bucket for bucket, _floor in rows]


@st.cache_data
def _cached_area_label(db_path: str, pref: str, code: str, lang: str) -> str:
    # area_label() itself stays a plain (streamlit-free, testable) function in
    # labels.py; caching lives only here, in the UI-side wrapper (§11.3).
    return area_label(db_path, pref, code, lang)


def _pref_selected_slugs(pref_counts: dict[str, int]) -> list[str]:
    return [slug for slug in pref_counts if st.session_state.get(f"pref_cb_{slug}", False)]


def _render_pref_selector(
    pref_counts: dict[str, int], text: dict[str, str], lang: str
) -> list[str]:
    # st.popover has no way to force which direction it opens, and it was
    # flipping upward off the top of the viewport for this tall 6-column
    # grid. st.dialog renders a centered modal instead, which doesn't have
    # that failure mode. (Click-based either way — Streamlit has no
    # hover-trigger widget.) Dialogs can't render inside st.sidebar, so only
    # the trigger button lives there; the grid itself renders at page level.
    @st.dialog(text["region_popover"], width="large")
    def _dialog() -> None:
        slugs = sorted(pref_counts, key=lambda s: pref_label(s, lang))
        cols = st.columns(6)
        for i, slug in enumerate(slugs):
            label = f"{pref_label(slug, lang)} ({pref_counts[slug]})"
            with cols[i % 6]:
                st.checkbox(label, key=f"pref_cb_{slug}")
        if st.button(text["region_dialog_done"]):
            st.rerun()

    if st.sidebar.button(text["region_popover"]):
        _dialog()

    return _pref_selected_slugs(pref_counts)


def _select_area(
    label: str,
    rows: list[tuple[str, int]],
    db_path: Path,
    pref: str,
    lang: str,
    text: dict[str, str],
) -> str | None:
    # Plain st.selectbox (not st.sidebar.selectbox): this is called from
    # inside `with st.sidebar.expander(...)`, and st.sidebar.X always targets
    # the sidebar root regardless of the active `with` block, which is why
    # the advanced-filter expander used to render empty (§11.4 layout bug).
    idx = st.selectbox(
        label,
        options=range(len(rows) + 1),
        format_func=lambda i: text["all_option"]
        if i == 0
        else (
            f"{_cached_area_label(str(db_path), pref, rows[i - 1][0], lang)} "
            f"({text['count_suffix'].format(n=rows[i - 1][1])})"
        ),
    )
    return None if idx == 0 else rows[idx - 1][0]


def _render_card(
    r: dict, lang: str, text: dict[str, str], station_coords: dict | None
) -> None:
    with st.container(border=True):
        st.markdown(f"#### [{r['name']}]({r['url']})")

        genres = "、".join(genre_label(g, lang) for g in r["genres"]) if r["genres"] else "-"
        st.write(f"{text['card_genre']}: {genres}")

        stations = (
            "、".join(station_label(s, lang) for s in r["stations"])
            if r["stations"]
            else "-"
        )
        st.write(f"{text['card_station']}: {stations}")

        rating = r["tabelog_rating"]
        rating_text = f"★{rating}" if rating is not None else text["card_no_rating"]
        bayes_text = (
            f" · bayes {r['bayes_score']:.3f}" if r["bayes_score"] is not None else ""
        )
        review_count_text = text["card_review_count"].format(n=r["tabelog_review_count"])
        st.write(f"{rating_text} ({review_count_text}){bayes_text}")

        dinner = r["budget_dinner"] or text["card_not_listed"]
        lunch = r["budget_lunch"] or text["card_not_listed"]
        st.write(text["card_budget"].format(dinner=dinner, lunch=lunch))

        if r["awards"]:
            st.write(" ".join(f"🏅{a['label']}" for a in r["awards"]))

        if r["reviewer_rating_mean"] is not None:
            st.write(text["card_reviewer_rating"].format(rating=f"{r['reviewer_rating_mean']:.1f}"))

        last_visited = r["last_visited"] or text["card_not_listed"]
        st.caption(
            text["card_visit"].format(
                k=r["reviewer_count"], n=r["visit_count_total"], month=last_visited
            )
        )

        if r["stations"]:
            station = r["stations"][0]
            google_url = google_search_url(r["name"], station)
            apple_map_url = apple_url(r["name"], station)
            st.markdown(
                f"[{text['card_maps_link_google']}]({google_url}) · "
                f"[{text['card_maps_link_apple']}]({apple_map_url})"
            )

            # §15.2 card -> map focus. Selection itself can't be set
            # programmatically, so this only repositions the viewport and
            # recolors the matching pin (main() reads map_focus next rerun).
            coord = station_coords.get(station) if station_coords else None
            if coord is not None and st.button(
                text["card_view_on_map"], key=f"map_focus_btn_{r['restaurant_id']}"
            ):
                st.session_state["map_focus"] = {
                    "restaurant_id": r["restaurant_id"],
                    "lat": coord["lat"],
                    "lng": coord["lng"],
                }


@st.cache_resource
def _cached_load_model():
    return load_model()


def main() -> None:
    st.set_page_config(
        page_title="Tabelog", layout="wide", initial_sidebar_state="expanded"
    )

    lang = st.sidebar.radio(
        "🌐 언어 / 言語 / Language",
        options=list(LANG_OPTIONS),
        format_func=lambda code: LANG_OPTIONS[code],
        horizontal=True,
    )
    text = UI_TEXT[lang]

    st.title(text["page_title"])

    if not DB_PATH.exists():
        st.error(text["db_missing"].format(path=DB_PATH))
        return

    st.sidebar.header(text["filter_header"])

    pref_counts = dict(_fetch_pref_options(DB_PATH))
    selected_prefs = _render_pref_selector(pref_counts, text, lang)
    pref = selected_prefs or None

    area2 = None
    area3 = None
    if pref is not None and len(pref) == 1:
        with st.sidebar.expander(text["advanced_filter"]):
            area2 = _select_area(
                text["area2_label"],
                _fetch_area2_options(DB_PATH, pref[0]),
                DB_PATH,
                pref[0],
                lang,
                text,
            )
            if area2 is not None:
                area3 = _select_area(
                    text["area3_label"],
                    _fetch_area3_options(DB_PATH, pref[0], area2),
                    DB_PATH,
                    pref[0],
                    lang,
                    text,
                )

    genre_rows = _fetch_genre_options(DB_PATH, pref, area2, area3)
    genre_label_to_value = {
        f"{genre_label(g, lang)} ({text['count_suffix'].format(n=c)})": g
        for g, c in genre_rows
    }
    selected_genre_labels = st.sidebar.multiselect(
        text["genre_label"], options=list(genre_label_to_value)
    )
    genre = [genre_label_to_value[label] for label in selected_genre_labels] or None

    station_query = st.sidebar.text_input(text["station_label"])
    station = station_query.strip() or None

    station_modes = ["exact", "partial"]
    station_mode_labels = {
        "exact": text["station_mode_exact"],
        "partial": text["station_mode_partial"],
    }
    station_mode = st.sidebar.radio(
        text["station_mode_label"],
        options=station_modes,
        format_func=lambda m: station_mode_labels[m],
    )
    station_exact = station_mode == "exact"
    station_primary_only = st.sidebar.checkbox(text["station_primary_only_label"])

    budget_dinner_buckets = _fetch_budget_options(DB_PATH, "dinner")
    budget_dinner_idx = st.sidebar.selectbox(
        text["budget_label"],
        options=range(len(budget_dinner_buckets) + 1),
        format_func=lambda i: text["all_option"] if i == 0 else budget_dinner_buckets[i - 1],
    )
    budget_dinner = None if budget_dinner_idx == 0 else budget_dinner_buckets[budget_dinner_idx - 1]
    if budget_dinner is not None:
        st.sidebar.caption(text["budget_notice"])

    budget_lunch_buckets = _fetch_budget_options(DB_PATH, "lunch")
    budget_lunch_idx = st.sidebar.selectbox(
        text["budget_lunch_label"],
        options=range(len(budget_lunch_buckets) + 1),
        format_func=lambda i: text["all_option"] if i == 0 else budget_lunch_buckets[i - 1],
    )
    budget_lunch = None if budget_lunch_idx == 0 else budget_lunch_buckets[budget_lunch_idx - 1]
    if budget_lunch is not None:
        st.sidebar.caption(text["budget_lunch_notice"])

    sort_keys = ["bayes", "rating", "reviews", "reviewer"]
    sort_key_to_label = {
        "bayes": text["sort_bayes"],
        "rating": text["sort_rating"],
        "reviews": text["sort_reviews"],
        "reviewer": text["sort_reviewer"],
    }
    sort = st.sidebar.radio(
        text["sort_label"],
        options=sort_keys,
        format_func=lambda s: sort_key_to_label[s],
    )

    filter_kwargs = dict(
        pref=pref,
        area2=area2,
        area3=area3,
        genre=genre,
        station=station,
        station_exact=station_exact,
        station_primary_only=station_primary_only,
        budget_dinner=budget_dinner,
        budget_lunch=budget_lunch,
    )
    total_count = count(DB_PATH, **filter_kwargs)

    if total_count == 0:
        st.warning(text["no_results"])
        return

    # §15.1 pagination: Prev/Next adjust session_state["page"] before results
    # are fetched below, so the count/caption/results all reflect the same page.
    max_page = (total_count - 1) // PAGE_SIZE
    current_page = min(st.session_state.get("page", 0), max_page)

    col_prev, col_next = st.columns(2)
    with col_prev:
        prev_clicked = st.button(
            text["prev_page"], disabled=current_page == 0, width="stretch"
        )
    with col_next:
        next_clicked = st.button(
            text["next_page"], disabled=current_page >= max_page, width="stretch"
        )
    if prev_clicked:
        current_page -= 1
    elif next_clicked:
        current_page += 1
    current_page = max(0, min(current_page, max_page))
    st.session_state["page"] = current_page

    results = search(
        DB_PATH,
        **filter_kwargs,
        sort=sort,
        limit=PAGE_SIZE,
        offset=current_page * PAGE_SIZE,
    )

    start = current_page * PAGE_SIZE + 1
    end = start + len(results) - 1
    st.caption(text["result_count_paged"].format(total=total_count, start=start, end=end))

    route_n = st.slider(text["route_n_label"], min_value=2, max_value=10, value=5)
    if st.button(text["route_button"].format(n=route_n)):
        route_url = build_route_url(results, n=route_n)
        if route_url:
            st.markdown(f"[{text['route_link_text']}]({route_url})")
            st.caption(text["route_caption_mobile_limit"])
            st.caption(text["route_caption_approx"])

    # station_coords.json is a manually-prepared, optional artifact (§13.2) —
    # its absence must not break the page, so the whole map section is
    # skipped rather than erroring (existing map/route links stay unaffected).
    station_coords = load_station_coords(STATION_COORDS_PATH)
    if station_coords is not None:
        map_n = st.slider(text["map_n_label"], min_value=5, max_value=30, value=10)
        points, excluded = build_map_points(results, station_coords, n=map_n)
        if points:
            map_focus = st.session_state.get("map_focus")
            highlight_id = None
            if map_focus and any(
                p["restaurant_id"] == map_focus["restaurant_id"] for p in points
            ):
                view_state = focused_view(map_focus["lat"], map_focus["lng"])
                highlight_id = map_focus["restaurant_id"]
            else:
                view_state = compute_default_view(points)

            event = render_map(points, view_state, highlight_restaurant_id=highlight_id)
            st.caption(text["map_caption_approx"])
            st.caption(text["map_caption_source"])
            if excluded:
                st.caption(text["map_caption_excluded"].format(k=excluded))

            # §15.2: clicked-pin panel — tooltips can't hold clickable links,
            # so the selected object's facts + links render below the map instead.
            selected_objects = (
                event["selection"]["objects"].get(LAYER_ID, []) if event else []
            )
            if selected_objects:
                selected = selected_objects[0]
                with st.container(border=True):
                    st.markdown(f"**{selected['name']}**")
                    if selected.get("rating") is not None:
                        st.write(f"★{selected['rating']}")
                    g_url = google_search_url(selected["name"], selected["station"])
                    a_url = apple_url(selected["name"], selected["station"])
                    st.markdown(
                        f"[{text['map_panel_tabelog_link']}]({selected['url']}) · "
                        f"[{text['card_maps_link_google']}]({g_url}) · "
                        f"[{text['card_maps_link_apple']}]({a_url})"
                    )

    for r in results:
        _render_card(r, lang, text, station_coords)

    st.divider()
    if st.button(text["generate_button"]):
        model, tokenizer, warning = _cached_load_model()
        if warning:
            st.warning(warning)
        with st.spinner(text["generating"]):
            generated_text = generate(
                results[:RECOMMEND_TOP_N], model=model, tokenizer=tokenizer
            )
        st.markdown(generated_text)


if __name__ == "__main__":
    main()
