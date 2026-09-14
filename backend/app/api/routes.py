"""Facility risk API.

* ``GET  /api/facilities``              -- list facilities (optional ``?archetype=``)
* ``GET  /api/facilities/{id}``         -- one facility
* ``POST /api/facilities/{id}/what-if`` -- recompute risk_score + both models'
  incident_likelihood under a partial override of factors/flags
* ``GET  /api/shap-summary``            -- precomputed SHAP feature importances
  (computed in the EDA notebook, not recomputed live)

All data is synthetic. See ``data/README.md``.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.risk import dataset
from app.risk.config import FACTORS, FLAGS
from app.risk.predict import score_facility
from app.risk.schemas import (
    ArchetypeKey,
    FacilityOut,
    ShapSummaryOut,
    WhatIfRequest,
    WhatIfResponse,
)

router = APIRouter(prefix="/api")

REPO_ROOT = Path(__file__).resolve().parents[3]
SHAP_SUMMARY_PATH = REPO_ROOT / "models" / "shap_summary.json"


@router.get("/facilities", response_model=list[FacilityOut])
def get_facilities(
    archetype: ArchetypeKey | None = Query(
        default=None, description="Filter to one of the 4 facility archetypes."
    ),
) -> list[dict]:
    return dataset.list_facilities(archetype=archetype.value if archetype else None)


@router.get("/facilities/{facility_id}", response_model=FacilityOut)
def get_facility(facility_id: str) -> dict:
    facility = dataset.get_facility(facility_id)
    if facility is None:
        raise HTTPException(status_code=404, detail=f"No facility with id {facility_id!r}")
    return facility


@router.post("/facilities/{facility_id}/what-if", response_model=WhatIfResponse)
def what_if(facility_id: str, body: WhatIfRequest) -> dict:
    facility = dataset.get_facility(facility_id)
    if facility is None:
        raise HTTPException(status_code=404, detail=f"No facility with id {facility_id!r}")

    original_factors = {factor: facility[factor] for factor in FACTORS}
    original_flags = {flag: facility[flag] for flag in FLAGS}

    factor_overrides = body.factors.as_overrides()
    flag_overrides = body.flags.as_overrides()

    updated_factors = {**original_factors, **factor_overrides}
    updated_flags = {**original_flags, **flag_overrides}

    before = score_facility(original_factors, original_flags)
    after = score_facility(updated_factors, updated_flags)
    delta = {key: round(after[key] - before[key], 2) for key in before}

    return {
        "facility_id": facility_id,
        "applied_overrides": {"factors": factor_overrides, "flags": flag_overrides},
        "before": before,
        "after": after,
        "delta": delta,
    }


@router.get("/shap-summary", response_model=ShapSummaryOut)
def shap_summary() -> dict:
    if not SHAP_SUMMARY_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                f"No precomputed SHAP summary at {SHAP_SUMMARY_PATH}. "
                "Run notebooks/01-eda-risk-scoring.ipynb, Section 10."
            ),
        )
    return json.loads(SHAP_SUMMARY_PATH.read_text())
