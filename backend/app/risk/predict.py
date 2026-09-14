"""Prediction service: loads the trained models and scores a facility.

Both models trained in the EDA notebook are exposed deliberately, not
collapsed into one "winner" — Ridge has the better raw fit (R^2=0.56 on
n=300) but structurally cannot represent the threat_exposure x
existing_countermeasures interaction; the shallow GBM has a worse raw fit
(R^2=0.46) but is the one that recovers that interaction (confirmed via
SHAP in the notebook). The accuracy-vs-interaction-capture gap between them
is meant to be a visible talking point in the dashboard, not something this
service resolves on the caller's behalf.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from .config import FLAGS
from .scoring import compute_risk_score

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = REPO_ROOT / "models" / "incident_likelihood_model.joblib"


class ModelNotTrainedError(RuntimeError):
    """Raised when the trained model artifact hasn't been produced yet."""


@lru_cache(maxsize=1)
def _load_bundle() -> dict:
    if not MODEL_PATH.exists():
        raise ModelNotTrainedError(
            f"No trained model at {MODEL_PATH}. Run "
            "notebooks/01-eda-risk-scoring.ipynb (Section 11) to train and save it."
        )
    return joblib.load(MODEL_PATH)


def reload_model() -> None:
    """Clear the cached model bundle. Call after MODEL_PATH changes (e.g. in tests)."""
    _load_bundle.cache_clear()


def _clip_0_100(value: float) -> float:
    return max(0.0, min(100.0, value))


def predict_incident_likelihood(
    factors: dict[str, float], flags: dict[str, bool]
) -> dict[str, float]:
    """Both models' predicted incident_likelihood for one facility, clipped to [0, 100]."""
    bundle = _load_bundle()
    feature_cols: list[str] = bundle["feature_cols"]
    factor_cols: list[str] = bundle["factor_cols"]
    flag_cols: list[str] = bundle["flag_cols"]

    row = {
        **{f: factors[f] for f in factor_cols},
        **{f: float(flags[f]) for f in flag_cols},
    }
    features = pd.DataFrame([row], columns=feature_cols)
    features_scaled = pd.DataFrame(
        bundle["scaler"].transform(features), columns=feature_cols
    )

    ridge_pred = float(bundle["ridge"].predict(features_scaled)[0])
    gbm_pred = float(bundle["gbm"].predict(features)[0])

    return {
        "ridge": round(_clip_0_100(ridge_pred), 2),
        "gbm": round(_clip_0_100(gbm_pred), 2),
    }


def score_facility(factors: dict[str, float], flags: dict[str, bool]) -> dict[str, float]:
    """The deterministic risk_score plus both models' predicted incident_likelihood."""
    predictions = predict_incident_likelihood(factors, flags)
    return {
        "risk_score": round(compute_risk_score(factors), 2),
        "ridge_incident_likelihood": predictions["ridge"],
        "gbm_incident_likelihood": predictions["gbm"],
    }


__all__ = [
    "FLAGS",
    "ModelNotTrainedError",
    "predict_incident_likelihood",
    "reload_model",
    "score_facility",
]
