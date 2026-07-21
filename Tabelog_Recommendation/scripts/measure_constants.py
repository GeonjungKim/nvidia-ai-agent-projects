import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.load import load_reviewers  # noqa: E402

REVIEWERS_DIR = ROOT / "data" / "reviewers"
DB_PATH = ROOT / "app.db"


def _cell_count(conn: sqlite3.Connection, pref: str, genre: str) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM restaurants_agg r "
        "JOIN restaurant_genres g ON g.restaurant_id = r.restaurant_id "
        "WHERE r.pref = ? AND g.genre = ?",
        (pref, genre),
    ).fetchone()[0]


def _top1(conn: sqlite3.Connection, pref: str, genre: str) -> tuple[str, float] | None:
    return conn.execute(
        "SELECT r.name, r.bayes_score FROM restaurants_agg r "
        "JOIN restaurant_genres g ON g.restaurant_id = r.restaurant_id "
        "WHERE r.pref = ? AND g.genre = ? AND r.bayes_score IS NOT NULL "
        "ORDER BY r.bayes_score DESC LIMIT 1",
        (pref, genre),
    ).fetchone()


def measure(db_path: Path) -> dict:
    conn = sqlite3.connect(db_path)
    try:
        meta = dict(conn.execute("SELECT key, value FROM meta").fetchall())
        return {
            "total_records": conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0],
            "total_restaurants": conn.execute(
                "SELECT COUNT(*) FROM restaurants_agg"
            ).fetchone()[0],
            "reviewer_rows": conn.execute(
                "SELECT reviewer_id, COUNT(*) FROM restaurants "
                "GROUP BY reviewer_id ORDER BY reviewer_id"
            ).fetchall(),
            "duplicate_restaurants": conn.execute(
                "SELECT COUNT(*) FROM restaurants_agg WHERE reviewer_count > 1"
            ).fetchone()[0],
            "reviewer_count_dist": conn.execute(
                "SELECT reviewer_count, COUNT(*) FROM restaurants_agg "
                "GROUP BY reviewer_count ORDER BY reviewer_count"
            ).fetchall(),
            "pref_distinct": conn.execute(
                "SELECT COUNT(DISTINCT pref) FROM restaurants_agg"
            ).fetchone()[0],
            "genre_distinct": conn.execute(
                "SELECT COUNT(DISTINCT genre) FROM restaurant_genres"
            ).fetchone()[0],
            "budget_distinct": conn.execute(
                "SELECT COUNT(DISTINCT budget_dinner) FROM restaurants_agg"
            ).fetchone()[0],
            "records_c": meta.get("global_mean_C"),
            "records_m": meta.get("prior_m"),
            "agg_c": meta.get("agg_global_mean_C"),
            "agg_m": meta.get("agg_prior_m"),
            "tokyo_ramen_count": _cell_count(conn, "tokyo", "ラーメン"),
            "tokyo_ramen_top1": _top1(conn, "tokyo", "ラーメン"),
            "nagano_ramen_count": _cell_count(conn, "nagano", "ラーメン"),
            "okinawa_french_count": _cell_count(conn, "okinawa", "フレンチ"),
        }
    finally:
        conn.close()


def main() -> None:
    report = load_reviewers(REVIEWERS_DIR, DB_PATH)
    stats = measure(DB_PATH)

    print("=== 파일별 레코드 수 ===")
    for name, count in report["file_counts"]:
        print(f"  {name}: {count}")

    print()
    print("=== 리뷰어별 레코드 수 (restaurants 테이블) ===")
    for reviewer_id, count in stats["reviewer_rows"]:
        print(f"  {reviewer_id}: {count}")

    print()
    print("=== reviewer_count 분포 (restaurants_agg) ===")
    for count, n in stats["reviewer_count_dist"]:
        print(f"  reviewer_count={count}: {n}곳")

    print()
    print(f"총 레코드: {stats['total_records']}")
    print(f"총 식당(agg): {stats['total_restaurants']}")
    print(f"중복(다중 리뷰어) 식당 수: {stats['duplicate_restaurants']}")
    print(f"속성 상이 건수(§14.2 anomaly signal): {report['attribute_discrepancy_count']}")
    print(f"pref distinct: {stats['pref_distinct']}")
    print(f"genre distinct: {stats['genre_distinct']}")
    print(f"budget_dinner distinct: {stats['budget_distinct']} (기존 17종 유지: "
          f"{stats['budget_distinct'] == 17})")
    print(f"records 기준 C={stats['records_c']} m={stats['records_m']}")
    print(f"agg 기준     C={stats['agg_c']} m={stats['agg_m']}")
    print(f"tokyo×ラーメン 식당 수: {stats['tokyo_ramen_count']}")
    print(f"tokyo×ラーメン bayes top1: {stats['tokyo_ramen_top1']}")
    print(f"nagano×ラーメン 식당 수: {stats['nagano_ramen_count']}")
    print(f"okinawa×フレンチ 식당 수: {stats['okinawa_french_count']}")


if __name__ == "__main__":
    main()
