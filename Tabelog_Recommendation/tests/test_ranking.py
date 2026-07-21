from app.ranking import bayes, get_prior


def test_bayes_high_volume_close_to_raw_rating():
    score = bayes(2106, 4.07, 243, 3.489346)
    assert abs(score - 4.010) < 0.005


def test_bayes_low_volume_pulled_toward_prior():
    score = bayes(1, 5.0, 243, 3.489346)
    assert score < 3.51


def test_get_prior_reads_meta_table(real_db):
    # §14.2 (v2.0): get_prior() now reads the agg_* prior (restaurants_agg,
    # deduplicated across all reviewer files) — re-measured via
    # scripts/measure_constants.py, not the pre-M9 single-reviewer 243/3.489.
    m, c = get_prior(real_db)
    assert m == 55
    assert 3.25 <= c <= 3.27
