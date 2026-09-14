"""Pydantic request/response models for the risk API."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from .config import ARCHETYPES, SCORE_MAX, SCORE_MIN

# Dynamic enum so the query-param validator (and OpenAPI docs) stay in sync
# with config.ARCHETYPES automatically -- adding an archetype there doesn't
# require touching this file.
ArchetypeKey = Enum("ArchetypeKey", {key: key for key in ARCHETYPES})


class FacilityOut(BaseModel):
    facility_id: str
    archetype: str
    archetype_label: str
    asset_criticality: float
    public_accessibility: float
    perimeter_vulnerability: float
    threat_exposure: float
    existing_countermeasures: float
    site_complexity: float
    response_readiness: float
    risk_score: float
    cameras: bool
    access_control: bool
    guards: bool
    lighting: bool
    fencing: bool
    incident_likelihood: float


class FactorOverride(BaseModel):
    """Partial override of the 7 raw factor scores. Omitted fields keep the
    facility's stored value; provided fields must be in [1, 5]."""

    asset_criticality: float | None = Field(default=None, ge=SCORE_MIN, le=SCORE_MAX)
    public_accessibility: float | None = Field(default=None, ge=SCORE_MIN, le=SCORE_MAX)
    perimeter_vulnerability: float | None = Field(default=None, ge=SCORE_MIN, le=SCORE_MAX)
    threat_exposure: float | None = Field(default=None, ge=SCORE_MIN, le=SCORE_MAX)
    existing_countermeasures: float | None = Field(default=None, ge=SCORE_MIN, le=SCORE_MAX)
    site_complexity: float | None = Field(default=None, ge=SCORE_MIN, le=SCORE_MAX)
    response_readiness: float | None = Field(default=None, ge=SCORE_MIN, le=SCORE_MAX)

    def as_overrides(self) -> dict[str, float]:
        return {k: v for k, v in self.model_dump().items() if v is not None}


class FlagOverride(BaseModel):
    """Partial override of the 5 countermeasure flags. Omitted fields keep
    the facility's stored value."""

    cameras: bool | None = None
    access_control: bool | None = None
    guards: bool | None = None
    lighting: bool | None = None
    fencing: bool | None = None

    def as_overrides(self) -> dict[str, bool]:
        return {k: v for k, v in self.model_dump().items() if v is not None}


class WhatIfRequest(BaseModel):
    factors: FactorOverride = Field(default_factory=FactorOverride)
    flags: FlagOverride = Field(default_factory=FlagOverride)


class ScoreBundle(BaseModel):
    risk_score: float
    ridge_incident_likelihood: float
    gbm_incident_likelihood: float


class AppliedOverrides(BaseModel):
    factors: dict[str, float]
    flags: dict[str, bool]


class WhatIfResponse(BaseModel):
    facility_id: str
    applied_overrides: AppliedOverrides
    before: ScoreBundle
    after: ScoreBundle
    delta: ScoreBundle


class ShapFeatureImportance(BaseModel):
    feature: str
    mean_abs_shap: float


class ShapSummaryOut(BaseModel):
    model: str
    n_samples: int
    features: list[ShapFeatureImportance]
