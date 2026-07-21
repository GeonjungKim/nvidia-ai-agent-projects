import json

from app.mapview import build_map_points, compute_default_view, load_station_coords, render_map

STATION_COORDS = {
    "銀座": {"lat": 35.6717, "lng": 139.7650, "matched": "exact"},
    "新橋": {"lat": 35.6664, "lng": 139.7580, "matched": "exact"},
}


def _rec(restaurant_id, name, stations, rating=4.0):
    return {
        "restaurant_id": restaurant_id,
        "name": name,
        "url": f"https://tabelog.com/tokyo/A1301/A130101/{restaurant_id}/",
        "stations": stations,
        "tabelog_rating": rating,
    }


def test_build_map_points_excludes_records_without_coords():
    records = [
        _rec("1", "A", ["銀座"]),
        _rec("2", "B", ["없는역"], rating=3.5),
        _rec("3", "C", [], rating=None),
    ]

    points, excluded = build_map_points(records, STATION_COORDS, n=10)

    assert len(points) == 1
    assert points[0]["name"] == "A"
    assert points[0]["restaurant_id"] == "1"
    assert points[0]["url"].endswith("/1/")
    assert excluded == 2


def test_build_map_points_enforces_n_cap_on_input_slice():
    records = [_rec(str(i), f"R{i}", ["銀座"]) for i in range(10)]

    points, excluded = build_map_points(records, STATION_COORDS, n=3)

    assert len(points) == 3
    assert excluded == 0
    assert [p["name"] for p in points] == ["R0", "R1", "R2"]


def test_build_map_points_jitters_duplicate_station_coordinates():
    records = [_rec("1", "A", ["銀座"]), _rec("2", "B", ["銀座"])]

    points, _ = build_map_points(records, STATION_COORDS, n=10)

    assert (points[0]["lat"], points[0]["lng"]) != (points[1]["lat"], points[1]["lng"])


def test_build_map_points_is_deterministic():
    records = [_rec("1", "A", ["銀座"]), _rec("2", "B", ["銀座"], rating=4.2)]

    first, _ = build_map_points(records, STATION_COORDS, n=10)
    second, _ = build_map_points(records, STATION_COORDS, n=10)

    assert first == second


def test_load_station_coords_returns_none_when_file_missing(tmp_path):
    missing_path = tmp_path / "does_not_exist.json"

    assert load_station_coords(missing_path) is None


def test_load_station_coords_reads_file_when_present(tmp_path):
    path = tmp_path / "station_coords.json"
    path.write_text(json.dumps(STATION_COORDS, ensure_ascii=False), encoding="utf-8")

    assert load_station_coords(path) == STATION_COORDS


# --- M10 (§15.2): map interaction ---


def test_compute_default_view_fits_points():
    points = [
        {"lat": 35.68, "lng": 139.70},
        {"lat": 35.70, "lng": 139.75},
        {"lat": 35.66, "lng": 139.65},
    ]

    view = compute_default_view(points)

    assert 35.66 <= view.latitude <= 35.70
    assert 139.65 <= view.longitude <= 139.75
    assert view.zoom > 0


def test_render_map_returns_none_for_empty_points():
    # No Streamlit runtime is active in tests — this must short-circuit
    # before touching st.pydeck_chart at all. Full render/selection behavior
    # is manual-only (§13.4 precedent), consistent with "no network in tests".
    assert render_map([], view_state=None) is None
