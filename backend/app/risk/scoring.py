"""The weighted risk-score formula. Shared by the dataset generator, the EDA
notebook, and (once built) the FastAPI what-if endpoint, so scoring logic
lives in exactly one place.
"""

from __future__ import annotations

from .config import INVERSE_FACTORS, SCORE_MAX, SCORE_MIN, WEIGHTS


def factor_contributions(factors: dict[str, float]) -> dict[str, float]:
    """Per-factor weighted contribution, in weighted-1-5-average units.

    Inverse factors (currently just ``existing_countermeasures``) are
    flipped via ``(SCORE_MAX + SCORE_MIN - raw)`` before weighting, so every
    value returned here is already in risk-increasing polarity and the
    dict's values sum to the overall weighted average risk score (1-5).
    """
    contributions: dict[str, float] = {}
    for factor, weight in WEIGHTS.items():
        raw = factors[factor]
        risk_polarity = (SCORE_MAX + SCORE_MIN - raw) if factor in INVERSE_FACTORS else raw
        contributions[factor] = weight * risk_polarity
    return contributions


def compute_risk_score(factors: dict[str, float]) -> float:
    """Weighted risk score rescaled from the natural [1, 5] average to [0, 100]."""
    weighted_average = sum(factor_contributions(factors).values())
    return (weighted_average - SCORE_MIN) / (SCORE_MAX - SCORE_MIN) * 100
