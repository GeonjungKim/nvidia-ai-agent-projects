import urllib.parse
from typing import Any

MAX_URL_LENGTH = 2048


def _place_query(name: str, station: str) -> str:
    return f"{name} {station}駅"


def google_search_url(name: str, station: str) -> str:
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(
        _place_query(name, station)
    )


def apple_url(name: str, station: str) -> str:
    return "https://maps.apple.com/?q=" + urllib.parse.quote(
        _place_query(name, station)
    )


def _route_url(places: list[str], travelmode: str) -> str:
    destination = places[-1]
    waypoints = places[:-1]
    parts = [
        "api=1",
        f"destination={urllib.parse.quote(destination)}",
    ]
    if waypoints:
        parts.append(f"waypoints={urllib.parse.quote('|'.join(waypoints))}")
    parts.append(f"travelmode={travelmode}")
    return "https://www.google.com/maps/dir/?" + "&".join(parts)


def build_route_url(
    records: list[dict[str, Any]], n: int = 5, travelmode: str = "walking"
) -> str:
    candidates = [r for r in records if r.get("stations")]
    if not candidates:
        return ""

    url = ""
    for count in range(min(n, len(candidates)), 0, -1):
        places = [
            _place_query(r["name"], r["stations"][0]) for r in candidates[:count]
        ]
        url = _route_url(places, travelmode)
        if len(url) <= MAX_URL_LENGTH:
            return url
    # Even a single destination exceeded the limit (pathological input) —
    # return the smallest attempt rather than raising.
    return url
