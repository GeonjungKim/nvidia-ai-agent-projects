import sqlite3
from pathlib import Path

import pytest

from app import load

DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "reviewers"
    / "tabelog_maro_merged_20260706.json"
)


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("m1") / "app.db"
    load.load(DATA_PATH, path)
    return path


@pytest.fixture()
def conn(db_path):
    connection = sqlite3.connect(db_path)
    try:
        yield connection
    finally:
        connection.close()


def test_restaurant_row_count(conn):
    (count,) = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()
    assert count == 14281


def test_distinct_pref_count(conn):
    (count,) = conn.execute("SELECT COUNT(DISTINCT pref) FROM restaurants").fetchone()
    assert count == 48


def test_null_rating_count_and_bayes_null(conn):
    (null_rating_count,) = conn.execute(
        "SELECT COUNT(*) FROM restaurants WHERE tabelog_rating IS NULL"
    ).fetchone()
    assert null_rating_count == 94

    (mismatched,) = conn.execute(
        "SELECT COUNT(*) FROM restaurants "
        "WHERE tabelog_rating IS NULL AND bayes_score IS NOT NULL"
    ).fetchone()
    assert mismatched == 0


def test_distinct_genre_count(conn):
    (count,) = conn.execute(
        "SELECT COUNT(DISTINCT genre) FROM restaurant_genres"
    ).fetchone()
    assert count == 203


def test_award_count(conn):
    (count,) = conn.execute(
        "SELECT COUNT(*) FROM restaurants WHERE award_count > 0"
    ).fetchone()
    assert count == 3879


def test_meta_global_mean_c_and_prior_m(conn):
    rows = dict(conn.execute("SELECT key, value FROM meta").fetchall())
    global_mean_c = float(rows["global_mean_C"])
    assert 3.48 <= global_mean_c <= 3.50
    assert int(rows["prior_m"]) == 243


def test_distinct_budget_dinner_count(conn):
    (count,) = conn.execute(
        "SELECT COUNT(DISTINCT budget_dinner) FROM restaurants"
    ).fetchone()
    assert count == 17


def test_budget_dinner_floor_spot_check(conn):
    row = conn.execute(
        "SELECT DISTINCT budget_dinner_floor FROM restaurants WHERE budget_dinner = ?",
        ("￥3,000～￥3,999",),
    ).fetchone()
    assert row == (3000,)

    row = conn.execute(
        "SELECT DISTINCT budget_dinner_floor FROM restaurants WHERE budget_dinner = ?",
        ("～￥999",),
    ).fetchone()
    assert row == (0,)

    (null_mismatch,) = conn.execute(
        "SELECT COUNT(*) FROM restaurants "
        "WHERE budget_dinner IS NULL AND budget_dinner_floor IS NOT NULL"
    ).fetchone()
    assert null_mismatch == 0


def test_distinct_budget_lunch_count(conn):
    (count,) = conn.execute(
        "SELECT COUNT(DISTINCT budget_lunch) FROM restaurants"
    ).fetchone()
    assert count == 16


def test_budget_lunch_floor_spot_check(conn):
    row = conn.execute(
        "SELECT DISTINCT budget_lunch_floor FROM restaurants WHERE budget_lunch = ?",
        ("￥3,000～￥3,999",),
    ).fetchone()
    assert row == (3000,)

    row = conn.execute(
        "SELECT DISTINCT budget_lunch_floor FROM restaurants WHERE budget_lunch = ?",
        ("～￥999",),
    ).fetchone()
    assert row == (0,)

    (null_mismatch,) = conn.execute(
        "SELECT COUNT(*) FROM restaurants "
        "WHERE budget_lunch IS NULL AND budget_lunch_floor IS NOT NULL"
    ).fetchone()
    assert null_mismatch == 0


def test_idempotent_reload(db_path):
    load.load(DATA_PATH, db_path)
    connection = sqlite3.connect(db_path)
    try:
        (count,) = connection.execute("SELECT COUNT(*) FROM restaurants").fetchone()
    finally:
        connection.close()
    assert count == 14281
