from pathlib import Path

import pytest

from app import load

REVIEWERS_DIR = Path(__file__).resolve().parent.parent / "data" / "reviewers"


@pytest.fixture(scope="session")
def real_db(tmp_path_factory):
    # Production loading path (§14): all reviewer files unioned + restaurants_agg.
    path = tmp_path_factory.mktemp("shared") / "app.db"
    load.load_reviewers(REVIEWERS_DIR, path)
    return path
