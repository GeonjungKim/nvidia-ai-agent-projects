import json
from pathlib import Path
from typing import Any

N02_ATTRIBUTION = "「国土数値情報（鉄道データ）」（国土交通省）を加工して作成"

LAYER_ID = "restaurant-pins"

_PIN_COLOR = [220, 30, 30, 180]
_HIGHLIGHT_COLOR = [255, 190, 0, 230]

# Small deterministic offsets (~20-30m) so restaurants sharing the same
# nearest-station coordinate don't render as a single overlapping pin.
_JITTER_OFFSETS = [
    (0.0, 0.0),
    (0.0003, 0.0),
    (-0.0003, 0.0),
    (0.0, 0.0003),
    (0.0, -0.0003),
    (0.0002, 0.0002),
    (-0.0002, -0.0002),
    (0.0002, -0.0002),
    (-0.0002, 0.0002),
]


def load_station_coords(path: str | Path) -> dict[str, dict[str, Any]] | None:
    path = Path(path)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_map_points(
    records: list[dict[str, Any]],
    station_coords: dict[str, dict[str, Any]],
    n: int,
) -> tuple[list[dict[str, Any]], int]:
    """Pure function (§13.4): pins for the top-n records whose first station
    resolves to a coordinate. Returns (points, excluded_count) where
    excluded_count is how many of those n records had no resolvable coordinate."""
    subset = records[:n]
    points: list[dict[str, Any]] = []
    excluded = 0
    station_seen: dict[str, int] = {}

    for r in subset:
        stations = r.get("stations") or []
        coord = station_coords.get(stations[0]) if stations else None
        if coord is None:
            excluded += 1
            continue

        station = stations[0]
        occurrence = station_seen.get(station, 0)
        station_seen[station] = occurrence + 1
        d_lat, d_lng = _JITTER_OFFSETS[occurrence % len(_JITTER_OFFSETS)]

        points.append(
            {
                "restaurant_id": r["restaurant_id"],
                "name": r["name"],
                "url": r["url"],
                "station": station,
                "rating": r.get("tabelog_rating"),
                "lat": coord["lat"] + d_lat,
                "lng": coord["lng"] + d_lng,
            }
        )

    return points, excluded


def compute_default_view(points: list[dict[str, Any]]) -> Any:
    """§15.2 dynamic viewport: officially-supported pydeck helper that fits
    a ViewState (position + zoom) to the current result pins."""
    import pydeck as pdk

    coords = [[p["lng"], p["lat"]] for p in points]
    return pdk.data_utils.compute_view(coords)


def focused_view(lat: float, lng: float, zoom: float = 15) -> Any:
    """§15.2 card -> map focus: a ViewState centered on one restaurant.
    (Programmatically setting the *selection* itself isn't supported by
    st.pydeck_chart — only the viewport and the pin's own color can react.)"""
    import pydeck as pdk

    return pdk.ViewState(latitude=lat, longitude=lng, zoom=zoom)


def render_map(
    points: list[dict[str, Any]],
    view_state: Any,
    highlight_restaurant_id: str | None = None,
) -> Any:
    """Renders the pin map and returns st.pydeck_chart's selection event
    (None if pydeck couldn't be used, or there was nothing to show)."""
    import streamlit as st

    if not points:
        return None

    try:
        import pydeck as pdk

        data = [
            {
                **p,
                "color": _HIGHLIGHT_COLOR
                if p["restaurant_id"] == highlight_restaurant_id
                else _PIN_COLOR,
            }
            for p in points
        ]
        layer = pdk.Layer(
            "ScatterplotLayer",
            id=LAYER_ID,  # required by st.pydeck_chart's on_select="rerun"
            data=data,
            get_position=["lng", "lat"],
            get_radius=60,
            get_fill_color="color",
            pickable=True,
        )
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_provider="carto",
            map_style="light",
            tooltip={"text": "{name}\n★{rating}\n{station}"},
        )
        return st.pydeck_chart(
            deck,
            on_select="rerun",
            selection_mode="single-object",
            key="restaurant_map",
        )
    except Exception:
        # §13.3: pydeck issues fall back to the simpler built-in map, never a
        # crash — but st.map has no click-selection, so the bottom panel
        # feature (§15.2) is naturally unavailable in this fallback.
        st.map([{"lat": p["lat"], "lon": p["lng"]} for p in points])
        return None
