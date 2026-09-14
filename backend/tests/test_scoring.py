from app.risk.config import WEIGHTS
from app.risk.generate import generate_dataset
from app.risk.scoring import compute_risk_score, factor_contributions

ALL_FIVES = {factor: 5.0 for factor in WEIGHTS}
ALL_ONES = {factor: 1.0 for factor in WEIGHTS}


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_all_fives_is_not_max_risk_because_countermeasures_is_inverse():
    # existing_countermeasures=5 means *strong* countermeasures, so it should
    # pull the score down relative to a facility with weak countermeasures.
    weak_countermeasures = {**ALL_FIVES, "existing_countermeasures": 1.0}
    assert compute_risk_score(ALL_FIVES) < compute_risk_score(weak_countermeasures)


def test_score_range_is_0_to_100():
    # Minimum risk: every direct factor at 1, countermeasures at 5 (strong,
    # so it inverts to a contribution of 1 too).
    best_case = {**ALL_ONES, "existing_countermeasures": 5.0}
    assert compute_risk_score(best_case) == 0.0
    # Maximum risk: every direct factor at 5, countermeasures at 1 (weak,
    # inverts to a contribution of 5).
    worst_case = {**ALL_FIVES, "existing_countermeasures": 1.0}
    assert compute_risk_score(worst_case) == 100.0


def test_factor_contributions_sum_to_weighted_average():
    contributions = factor_contributions(ALL_FIVES)
    weighted_average = sum(contributions.values())
    # risk_score is that weighted average rescaled from [1, 5] to [0, 100]
    assert abs((weighted_average - 1.0) / 4.0 * 100 - compute_risk_score(ALL_FIVES)) < 1e-9


def test_generate_dataset_shape_and_ranges():
    df = generate_dataset(n_per_archetype=5, seed=1)
    assert len(df) == 20
    assert df["archetype"].nunique() == 4
    assert df["risk_score"].between(0, 100).all()
    assert df["incident_likelihood"].between(0, 100).all()
    for factor in WEIGHTS:
        assert df[factor].between(1, 5).all()


def test_generate_dataset_is_reproducible_with_same_seed():
    a = generate_dataset(n_per_archetype=5, seed=7)
    b = generate_dataset(n_per_archetype=5, seed=7)
    assert a.equals(b)
