import sqlite3
from pathlib import Path


def bayes(v: int, R: float, m: int, C: float) -> float:
    return (v * R + m * C) / (v + m)


def get_prior(db: str | Path) -> tuple[int, float]:
    # §14.2: restaurants_agg.bayes_score is computed from the agg_* prior
    # (deduplicated restaurant set), not the record-level global_mean_C/prior_m.
    conn = sqlite3.connect(db)
    try:
        rows = dict(conn.execute("SELECT key, value FROM meta").fetchall())
    finally:
        conn.close()
    return int(rows["agg_prior_m"]), float(rows["agg_global_mean_C"])
