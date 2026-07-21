import json
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REVIEWERS_DIR = ROOT / "data" / "reviewers"
GEO_DIR = ROOT / "data" / "geo"
OUTPUT_PATH = ROOT / "data" / "station_coords.json"

N02_ATTRIBUTION = "「国土数値情報（鉄道データ）」（国土交通省）を加工して作成"


def _load_all_records(reviewers_dir: Path) -> list[dict[str, Any]]:
    # §14's multiple reviewer files, unioned — station coverage must reflect
    # every reviewer, not just the original single-reviewer file.
    records: list[dict[str, Any]] = []
    for path in sorted(reviewers_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            records.extend(json.load(f)["records"])
    return records


def _centroid(coords: list[list[float]]) -> tuple[float, float]:
    # GeoJSON coordinates are [lng, lat]; we return (lat, lng).
    lngs = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return mean(lats), mean(lngs)


def _dominant_pref(pref_counts: dict[str, int]) -> str:
    # Deterministic: highest reference count wins; ties broken alphabetically.
    return sorted(pref_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def _station_to_prefs(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for r in records:
        for station in r["stations"]:
            pref_counts = counts.setdefault(station, {})
            pref_counts[r["pref"]] = pref_counts.get(r["pref"], 0) + 1
    return counts


def compute_group_coordinates(
    features: list[dict[str, Any]],
) -> dict[str, tuple[str, float, float]]:
    """{N02_005g group code: (station name, avg lat, avg lng)} — one point per
    group, merging multi-platform features that share the same group code."""
    points: dict[str, list[tuple[float, float]]] = {}
    names: dict[str, str] = {}
    for feature in features:
        props = feature["properties"]
        group = props["N02_005g"]
        names[group] = props["N02_005"]
        points.setdefault(group, []).append(_centroid(feature["geometry"]["coordinates"]))

    return {
        group: (names[group], mean(p[0] for p in pts), mean(p[1] for p in pts))
        for group, pts in points.items()
    }


def resolve_station_coords(
    station_pref_counts: dict[str, dict[str, int]],
    group_coords: dict[str, tuple[str, float, float]],
) -> dict[str, dict[str, Any]]:
    """Pure function implementing §13.2's 3-tier matching, deterministically."""
    name_to_groups: dict[str, list[str]] = {}
    for group, (name, _lat, _lng) in group_coords.items():
        name_to_groups.setdefault(name, []).append(group)

    result: dict[str, dict[str, Any]] = {}
    pref_confirmed_points: dict[str, list[tuple[float, float]]] = {}
    ambiguous_names = []

    # Pass 1: nationally-unique names are confirmed immediately.
    for name in station_pref_counts:
        groups = name_to_groups.get(name)
        if not groups:
            continue  # unmatched (§13.2 ③) — simply absent from the result
        if len(groups) == 1:
            _, lat, lng = group_coords[groups[0]]
            result[name] = {"lat": lat, "lng": lng, "matched": "exact"}
            pref = _dominant_pref(station_pref_counts[name])
            pref_confirmed_points.setdefault(pref, []).append((lat, lng))
        else:
            ambiguous_names.append(name)

    # Pass 2: same-name multiple candidates -> nearest to that pref's
    # pass-1-confirmed centroid; ties broken by coordinate sort order.
    for name in sorted(ambiguous_names):
        pref = _dominant_pref(station_pref_counts[name])
        candidates = [group_coords[g] for g in name_to_groups[name]]
        reference_points = pref_confirmed_points.get(pref)

        if reference_points:
            center_lat = mean(p[0] for p in reference_points)
            center_lng = mean(p[1] for p in reference_points)

            def sort_key(candidate: tuple[str, float, float]) -> tuple[float, float, float]:
                _, lat, lng = candidate
                return ((lat - center_lat) ** 2 + (lng - center_lng) ** 2, lat, lng)
        else:
            # No confirmed reference for this pref yet — fall back to the
            # same deterministic coordinate-sort tiebreak used above.
            def sort_key(candidate: tuple[str, float, float]) -> tuple[float, float, float]:
                _, lat, lng = candidate
                return (0.0, lat, lng)

        _, lat, lng = sorted(candidates, key=sort_key)[0]
        result[name] = {"lat": lat, "lng": lng, "matched": "disambiguated"}

    return result


def main() -> None:
    geo_files = sorted(GEO_DIR.glob("N02-*_Station.geojson"))
    if not geo_files:
        raise SystemExit(
            f"N02 역(철도) geojson을 찾을 수 없습니다: {GEO_DIR}/N02-*_Station.geojson\n"
            "국토교통성 국토수치정보 다운로드 서비스에서 최신 N02(철도) 데이터를 받아 "
            f"{GEO_DIR}에 배치한 뒤 다시 실행하세요."
        )
    geo_path = geo_files[-1]

    with open(geo_path, encoding="utf-8") as f:
        features = json.load(f)["features"]

    records = _load_all_records(REVIEWERS_DIR)

    station_pref_counts = _station_to_prefs(records)
    group_coords = compute_group_coordinates(features)
    result = resolve_station_coords(station_pref_counts, group_coords)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)

    total = len(station_pref_counts)
    exact = sum(1 for v in result.values() if v["matched"] == "exact")
    disambiguated = sum(1 for v in result.values() if v["matched"] == "disambiguated")
    unmatched = total - len(result)

    print(f"입력 geojson: {geo_path.name}")
    print(f"전체 역명: {total}")
    print(f"전국 유일 매칭(exact): {exact}")
    print(f"동명 해소(disambiguated): {disambiguated}")
    print(f"미매칭(핀 생략): {unmatched}")
    print(f"매칭률: {(exact + disambiguated) / total:.1%}")
    print(f"출처: {N02_ATTRIBUTION}")
    print(f"출력: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
