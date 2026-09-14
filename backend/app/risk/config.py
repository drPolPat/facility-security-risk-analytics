"""Risk-model definitions: factors, weights, and per-archetype score distributions.

All facility data in this project is synthetic (see ``data/README.md``). This
module is the single source of truth for the weighted risk formula and the
generative assumptions behind the synthetic dataset — everything downstream
(the EDA notebook, the FastAPI "what-if" endpoint, the trained ML model)
reads these constants rather than re-deriving them.

Scoring convention
-------------------
Every factor is scored 1-5. For six of the seven factors, higher = more
risk. ``existing_countermeasures`` is the one exception called out in the
project brief ("inversely reduces risk"): it is scored so that a higher
value means *stronger* countermeasures, and is inverted (``6 - score``)
before being weighted, so that its contribution stays in the same
risk-increasing polarity as every other factor.

``response_readiness`` is scored directly in risk polarity (5 = slow /
under-prepared response = high risk) for consistency with the other five
non-inverted factors — the brief did not call it out as inverse, so it is
treated the same as asset_criticality, public_accessibility, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field

FACTORS: tuple[str, ...] = (
    "asset_criticality",
    "public_accessibility",
    "perimeter_vulnerability",
    "threat_exposure",
    "existing_countermeasures",
    "site_complexity",
    "response_readiness",
)

WEIGHTS: dict[str, float] = {
    "asset_criticality": 0.20,
    "public_accessibility": 0.15,
    "perimeter_vulnerability": 0.15,
    "threat_exposure": 0.15,
    "existing_countermeasures": 0.20,
    "site_complexity": 0.10,
    "response_readiness": 0.05,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

# Factors scored so that a *higher* raw value means *lower* risk, and must be
# inverted (6 - raw_score) before weighting.
INVERSE_FACTORS: frozenset[str] = frozenset({"existing_countermeasures"})

SCORE_MIN, SCORE_MAX = 1.0, 5.0


@dataclass(frozen=True)
class ArchetypeSpec:
    key: str
    label: str
    description: str
    # factor -> (mean, std) of a normal distribution, truncated to [1, 5]
    factor_params: dict[str, tuple[float, float]] = field(default_factory=dict)


ARCHETYPES: dict[str, ArchetypeSpec] = {
    "cultural_heritage_site": ArchetypeSpec(
        key="cultural_heritage_site",
        label="Cultural / Heritage Site",
        description=(
            "High public access, high asset value, restricted modification options "
            "(preservation constraints limit how much can be physically hardened)."
        ),
        factor_params={
            "asset_criticality": (4.2, 0.5),
            "public_accessibility": (4.5, 0.4),
            "perimeter_vulnerability": (3.8, 0.6),
            "threat_exposure": (3.0, 0.7),
            "existing_countermeasures": (2.6, 0.7),
            "site_complexity": (3.5, 0.6),
            "response_readiness": (2.8, 0.6),
        },
    ),
    "commercial_retail_complex": ArchetypeSpec(
        key="commercial_retail_complex",
        label="Commercial Retail Complex",
        description="Very high public access, moderate asset value, large open perimeter.",
        factor_params={
            "asset_criticality": (2.8, 0.6),
            "public_accessibility": (4.8, 0.3),
            "perimeter_vulnerability": (4.0, 0.5),
            "threat_exposure": (3.2, 0.6),
            "existing_countermeasures": (3.4, 0.6),
            "site_complexity": (3.0, 0.6),
            "response_readiness": (2.3, 0.6),
        },
    ),
    "mixed_use_tower": ArchetypeSpec(
        key="mixed_use_tower",
        label="Mixed-Use Tower",
        description=(
            "Moderate public access, vertical security challenges, high asset density "
            "across stacked tenants."
        ),
        factor_params={
            "asset_criticality": (3.6, 0.6),
            "public_accessibility": (3.0, 0.6),
            "perimeter_vulnerability": (2.6, 0.6),
            "threat_exposure": (3.0, 0.6),
            "existing_countermeasures": (3.6, 0.6),
            "site_complexity": (4.2, 0.5),
            "response_readiness": (3.2, 0.6),
        },
    ),
    "critical_infrastructure": ArchetypeSpec(
        key="critical_infrastructure",
        label="Critical Infrastructure (Substation / Warehouse)",
        description=(
            "Low public access, very high asset criticality, remote/unstaffed sites "
            "with slower response."
        ),
        factor_params={
            "asset_criticality": (4.6, 0.4),
            "public_accessibility": (1.4, 0.4),
            "perimeter_vulnerability": (3.4, 0.7),
            "threat_exposure": (3.6, 0.7),
            "existing_countermeasures": (3.0, 0.8),
            "site_complexity": (2.2, 0.6),
            "response_readiness": (4.2, 0.5),
        },
    ),
}

# Boolean countermeasure flags. Each flag's probability rises with the
# facility's existing_countermeasures score (raw, 1-5, higher = stronger):
#   p = clip(base_prob + slope * (score - 3), 0.03, 0.97)
COUNTERMEASURE_FLAGS: dict[str, dict[str, float]] = {
    "cameras": {"base_prob": 0.50, "slope": 0.16},
    "access_control": {"base_prob": 0.40, "slope": 0.18},
    "guards": {"base_prob": 0.30, "slope": 0.15},
    "lighting": {"base_prob": 0.55, "slope": 0.12},
    "fencing": {"base_prob": 0.45, "slope": 0.14},
}

FLAGS: tuple[str, ...] = tuple(COUNTERMEASURE_FLAGS.keys())
