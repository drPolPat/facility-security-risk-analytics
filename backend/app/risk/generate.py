"""Synthetic facility dataset generator.

Every number here is fabricated for portfolio-demonstration purposes — see
``data/README.md``. Archetype-level score distributions live in
``config.ARCHETYPES``; this module only handles sampling, countermeasure-flag
correlation, and the synthetic ``incident_likelihood`` outcome variable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ARCHETYPES, COUNTERMEASURE_FLAGS, SCORE_MAX, SCORE_MIN
from .scoring import compute_risk_score


def _truncated_normal(rng: np.random.Generator, mean: float, std: float) -> float:
    return float(np.clip(rng.normal(mean, std), SCORE_MIN, SCORE_MAX))


def _simulate_incident_likelihood(
    rng: np.random.Generator, factors: dict[str, float], risk_score: float
) -> float:
    """Synthetic ground-truth outcome — NOT real incident data.

    Modeled as the weighted risk_score plus a deliberate
    threat-exposure x weak-countermeasures interaction term (something the
    linear weighted formula can't express, so a nonlinear model has
    something real to recover) plus Gaussian noise standing in for the many
    real-world drivers a 7-factor model can't capture. Clipped to [0, 100].
    """
    threat = (factors["threat_exposure"] - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)
    countermeasure_strength = (factors["existing_countermeasures"] - SCORE_MIN) / (
        SCORE_MAX - SCORE_MIN
    )
    # high iff threat is high AND countermeasures are weak
    interaction = threat * (1 - countermeasure_strength)

    noise = rng.normal(0, 6.0)
    raw = 0.72 * risk_score + 28.0 * interaction - 8.0 + noise
    return float(np.clip(raw, 0.0, 100.0))


def generate_dataset(n_per_archetype: int = 75, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    facility_counter = 1

    for archetype in ARCHETYPES.values():
        for _ in range(n_per_archetype):
            factors = {
                factor: round(_truncated_normal(rng, mean, std), 2)
                for factor, (mean, std) in archetype.factor_params.items()
            }
            risk_score = compute_risk_score(factors)

            countermeasures_raw = factors["existing_countermeasures"]
            flags = {
                flag_name: bool(
                    rng.random()
                    < np.clip(
                        params["base_prob"] + params["slope"] * (countermeasures_raw - 3),
                        0.03,
                        0.97,
                    )
                )
                for flag_name, params in COUNTERMEASURE_FLAGS.items()
            }

            incident_likelihood = _simulate_incident_likelihood(rng, factors, risk_score)

            rows.append(
                {
                    "facility_id": f"F{facility_counter:03d}",
                    "archetype": archetype.key,
                    "archetype_label": archetype.label,
                    **factors,
                    "risk_score": round(risk_score, 2),
                    **flags,
                    "incident_likelihood": round(incident_likelihood, 2),
                }
            )
            facility_counter += 1

    return pd.DataFrame(rows)
