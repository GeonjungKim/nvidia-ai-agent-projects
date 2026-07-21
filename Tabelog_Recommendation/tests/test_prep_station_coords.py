import json

import pytest

from scripts.prep_station_coords import (
    GEO_DIR,
    REVIEWERS_DIR,
    _centroid,
    _dominant_pref,
    _load_all_records,
    _station_to_prefs,
    compute_group_coordinates,
    resolve_station_coords,
)


def test_centroid_averages_linestring_points():
    lat, lng = _centroid([[139.70, 35.68], [139.72, 35.70]])
    assert lat == pytest.approx(35.69)
    assert lng == pytest.approx(139.71)


def test_dominant_pref_picks_highest_count_then_alphabetical_tiebreak():
    assert _dominant_pref({"tokyo": 5, "osaka": 5}) == "osaka"
    assert _dominant_pref({"tokyo": 10, "osaka": 3}) == "tokyo"


def test_compute_group_coordinates_averages_multi_platform_group():
    features = [
        {
            "properties": {"N02_005": "テスト駅", "N02_005g": "G1"},
            "geometry": {"coordinates": [[139.0, 35.0], [139.0, 35.0]]},
        },
        {
            "properties": {"N02_005": "テスト駅", "N02_005g": "G1"},
            "geometry": {"coordinates": [[139.2, 35.2], [139.2, 35.2]]},
        },
    ]

    result = compute_group_coordinates(features)

    name, lat, lng = result["G1"]
    assert name == "テスト駅"
    assert lat == pytest.approx(35.1)
    assert lng == pytest.approx(139.1)


def test_resolve_station_coords_exact_match_for_nationally_unique_name():
    group_coords = {"G1": ("A駅", 35.0, 139.0)}

    result = resolve_station_coords(
        station_pref_counts={"A駅": {"tokyo": 1}},
        group_coords=group_coords,
    )

    assert result["A駅"] == {"lat": 35.0, "lng": 139.0, "matched": "exact"}


def test_resolve_station_coords_disambiguates_by_nearest_to_pref_centroid():
    group_coords = {
        "G_unique_tokyo": ("확정역", 35.0, 139.0),
        "G_amb_near": ("모호역", 35.01, 139.01),  # close to tokyo's confirmed centroid
        "G_amb_far": ("모호역", 40.0, 141.0),  # far away
    }

    result = resolve_station_coords(
        station_pref_counts={"확정역": {"tokyo": 1}, "모호역": {"tokyo": 1}},
        group_coords=group_coords,
    )

    assert result["모호역"]["matched"] == "disambiguated"
    assert result["모호역"]["lat"] == pytest.approx(35.01)
    assert result["모호역"]["lng"] == pytest.approx(139.01)


def test_resolve_station_coords_ties_broken_by_coordinate_sort_order():
    group_coords = {
        "G_unique_tokyo": ("확정역", 35.0, 139.0),
        "G_amb_a": ("모호역", 34.0, 138.0),  # both equidistant from (35,139)
        "G_amb_b": ("모호역", 36.0, 140.0),
    }

    result = resolve_station_coords(
        station_pref_counts={"확정역": {"tokyo": 1}, "모호역": {"tokyo": 1}},
        group_coords=group_coords,
    )

    # equidistant -> smaller (lat, lng) tuple wins
    assert result["모호역"]["lat"] == pytest.approx(34.0)
    assert result["모호역"]["lng"] == pytest.approx(138.0)


def test_resolve_station_coords_unmatched_name_is_absent_from_result():
    result = resolve_station_coords(
        station_pref_counts={"없는역": {"tokyo": 1}},
        group_coords={},
    )

    assert "없는역" not in result


def test_resolve_station_coords_is_deterministic_across_two_runs():
    group_coords = {
        "G1": ("역A", 35.0, 139.0),
        "G2": ("역B", 34.0, 138.0),
        "G3": ("역B", 36.0, 140.0),
    }
    prefs = {"역A": {"tokyo": 1}, "역B": {"tokyo": 1}}

    first = resolve_station_coords(prefs, group_coords)
    second = resolve_station_coords(prefs, group_coords)

    assert first == second


def test_real_geo_file_present_for_prep_script():
    assert GEO_DIR.exists()
    assert list(GEO_DIR.glob("N02-*_Station.geojson")), (
        "N02 station geojson missing in data/geo/"
    )


def test_shinjuku_coordinate_within_tokyo_bounding_box():
    geo_path = sorted(GEO_DIR.glob("N02-*_Station.geojson"))[-1]
    with open(geo_path, encoding="utf-8") as f:
        features = json.load(f)["features"]
    group_coords = compute_group_coordinates(features)

    records = _load_all_records(REVIEWERS_DIR)
    station_pref_counts = _station_to_prefs(records)

    result = resolve_station_coords(station_pref_counts, group_coords)

    shinjuku = result["新宿"]
    assert 35.6 <= shinjuku["lat"] <= 35.8
    assert 139.6 <= shinjuku["lng"] <= 139.8
