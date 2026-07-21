import urllib.parse

from app.maplinks import apple_url, build_route_url, google_search_url


def test_google_search_url_format():
    url = google_search_url("らぁ麺や 嶋", "新宿")
    assert url.startswith("https://www.google.com/maps/search/?api=1&query=")
    assert urllib.parse.quote("らぁ麺や 嶋 新宿駅") in url


def test_apple_url_format():
    url = apple_url("らぁ麺や 嶋", "新宿")
    assert url.startswith("https://maps.apple.com/?q=")
    assert urllib.parse.quote("らぁ麺や 嶋 新宿駅") in url


def test_build_route_url_basic_n5():
    records = [{"name": f"식당{i}", "stations": [f"역{i}"]} for i in range(5)]

    url = build_route_url(records, n=5)

    assert "api=1" in url
    assert "%7C" in url
    assert len(url) <= 2048


def test_build_route_url_uses_walking_travelmode_by_default():
    records = [{"name": f"식당{i}", "stations": [f"역{i}"]} for i in range(3)]

    url = build_route_url(records, n=3)

    assert "travelmode=walking" in url


def test_build_route_url_destination_is_last_and_waypoints_are_rest():
    records = [{"name": f"식당{i}", "stations": [f"역{i}"]} for i in range(3)]

    url = build_route_url(records, n=3)

    assert urllib.parse.quote("식당2 역2駅") in url  # last -> destination
    assert "waypoints=" in url


def test_build_route_url_reduces_n_when_over_length_limit():
    long_records = [
        {"name": f"LongPlaceName{i}_" + "X" * 500, "stations": [f"Sta{i}"]}
        for i in range(5)
    ]

    url = build_route_url(long_records, n=5)

    assert len(url) <= 2048
    included_markers = sum(1 for i in range(5) if f"LongPlaceName{i}_" in url)
    assert included_markers < 5
