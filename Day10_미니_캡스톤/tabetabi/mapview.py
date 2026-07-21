"""클릭 가능한 지도 — folium 마커 팝업에 식당 링크(타베로그·구글지도)를 넣는다.

st.map의 단순 점 대신, 핀을 누르면 그 식당의 타베로그·구글지도로 바로 이동할 수 있게 한다.
folium 미설치 시 호출부가 st.map으로 폴백한다 (build_map이 None을 반환).
"""
from __future__ import annotations

from tabetabi.i18n import t_genres, t_station

_SLOT_KO = {"lunch": "점심", "cafe": "카페", "dinner": "저녁"}
_SLOT_COLOR = {"lunch": "orange", "cafe": "green", "dinner": "red"}


def build_map(points: list[dict], lang: str = "ko"):
    """포인트 목록 → folium.Map (클릭 팝업에 링크 포함). folium 없거나 좌표 없으면 None."""
    pts = [p for p in (points or []) if p.get("lat") and p.get("lon")]
    if not pts:
        return None
    try:
        import folium
    except Exception:
        return None

    lat = sum(p["lat"] for p in pts) / len(pts)
    lon = sum(p["lon"] for p in pts) / len(pts)
    fmap = folium.Map(location=[lat, lon], zoom_start=12, tiles="cartodbpositron")

    for i, p in enumerate(pts, 1):
        slot_ko = _SLOT_KO.get(p.get("slot"), "")
        day = f"Day{p['day']} " if p.get("day") else ""
        star = f" ★{p['rating']}" if p.get("rating") else ""
        station = t_station(p["station"], lang) if p.get("station") else ""
        genres = t_genres(p.get("genres", ""), lang)
        links = []
        if p.get("tabelog_url"):
            links.append(f'<a href="{p["tabelog_url"]}" target="_blank">🍜 타베로그</a>')
        if p.get("gmap"):
            links.append(f'<a href="{p["gmap"]}" target="_blank">📍 구글지도</a>')
        popup_html = (
            f'<div style="min-width:180px">'
            f'<b>{p["name"]}</b>{star}<br>'
            f'<span style="color:#666">{day}{slot_ko} · {genres}</span><br>'
            f'<span style="color:#888">{station}</span><br>'
            f'<div style="margin-top:6px">{" · ".join(links)}</div></div>'
        )
        folium.Marker(
            [p["lat"], p["lon"]],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{i}. {p['name']}",
            icon=folium.Icon(color=_SLOT_COLOR.get(p.get("slot"), "blue"), icon="cutlery", prefix="fa"),
        ).add_to(fmap)
    return fmap
