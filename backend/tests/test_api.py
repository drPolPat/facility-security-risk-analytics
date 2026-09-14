"""Stage 3: the facility risk API.

Uses a small self-contained fixture (its own synthetic dataset + trained
models in a temp dir) rather than the repo's checked-in `data/`/`models/`
artifacts, since both are gitignored build outputs a fresh clone won't have
until the notebook is run.
"""

from __future__ import annotations

import json

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from app.api import routes
from app.risk import dataset, predict
from app.risk.config import FACTORS, FLAGS
from app.risk.generate import generate_dataset

FEATURE_COLS = list(FACTORS) + list(FLAGS)


@pytest.fixture
def client(tmp_path, monkeypatch):
    df = generate_dataset(n_per_archetype=30, seed=1)

    csv_path = tmp_path / "facilities.csv"
    df.to_csv(csv_path, index=False)

    X = df[FEATURE_COLS].copy()
    X[list(FLAGS)] = X[list(FLAGS)].astype(float)
    y = df["incident_likelihood"]

    scaler = StandardScaler().fit(X)
    X_scaled = pd.DataFrame(scaler.transform(X), columns=FEATURE_COLS)
    ridge = Ridge(alpha=1.0, random_state=42).fit(X_scaled, y)
    gbm = GradientBoostingRegressor(n_estimators=50, max_depth=2, random_state=42).fit(X, y)

    model_path = tmp_path / "incident_likelihood_model.joblib"
    joblib.dump(
        {
            "gbm": gbm,
            "ridge": ridge,
            "scaler": scaler,
            "feature_cols": FEATURE_COLS,
            "flag_cols": list(FLAGS),
            "factor_cols": list(FACTORS),
        },
        model_path,
    )

    shap_path = tmp_path / "shap_summary.json"
    shap_path.write_text(
        json.dumps(
            {
                "model": "gbm",
                "n_samples": len(df),
                "features": [{"feature": f, "mean_abs_shap": 1.0} for f in FEATURE_COLS],
            }
        )
    )

    monkeypatch.setattr(dataset, "FACILITIES_CSV_PATH", csv_path)
    dataset.reload_dataset()
    monkeypatch.setattr(predict, "MODEL_PATH", model_path)
    predict.reload_model()
    monkeypatch.setattr(routes, "SHAP_SUMMARY_PATH", shap_path)

    from app.main import app

    return TestClient(app), df


def test_list_facilities(client):
    api, df = client
    resp = api.get("/api/facilities")
    assert resp.status_code == 200
    assert len(resp.json()) == len(df)


def test_list_facilities_filters_by_archetype(client):
    api, df = client
    key = df.iloc[0]["archetype"]
    resp = api.get("/api/facilities", params={"archetype": key})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == (df["archetype"] == key).sum()
    assert all(f["archetype"] == key for f in body)


def test_list_facilities_rejects_unknown_archetype(client):
    api, _ = client
    resp = api.get("/api/facilities", params={"archetype": "not_a_real_archetype"})
    assert resp.status_code == 422


def test_get_facility_by_id(client):
    api, df = client
    facility_id = df.iloc[0]["facility_id"]
    resp = api.get(f"/api/facilities/{facility_id}")
    assert resp.status_code == 200
    assert resp.json()["facility_id"] == facility_id


def test_get_facility_404_for_unknown_id(client):
    api, _ = client
    resp = api.get("/api/facilities/does-not-exist")
    assert resp.status_code == 404


def test_what_if_strengthening_countermeasures_reduces_risk(client):
    api, df = client
    # Facility with the weakest countermeasures, so raising it to the max (5)
    # is guaranteed to be a real, large change rather than a no-op.
    facility_id = df.loc[df["existing_countermeasures"].idxmin(), "facility_id"]

    resp = api.post(
        f"/api/facilities/{facility_id}/what-if",
        json={"factors": {"existing_countermeasures": 5.0}},
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["delta"]["risk_score"] < 0
    assert body["delta"]["ridge_incident_likelihood"] < 0
    assert body["delta"]["gbm_incident_likelihood"] < 0
    assert body["after"]["risk_score"] == pytest.approx(
        body["before"]["risk_score"] + body["delta"]["risk_score"]
    )


def test_what_if_rejects_out_of_range_factor_score(client):
    api, df = client
    facility_id = df.iloc[0]["facility_id"]

    resp = api.post(
        f"/api/facilities/{facility_id}/what-if",
        json={"factors": {"threat_exposure": 6.0}},
    )
    assert resp.status_code == 422


def test_what_if_404_for_unknown_facility(client):
    api, _ = client
    resp = api.post(
        "/api/facilities/does-not-exist/what-if",
        json={"factors": {"threat_exposure": 3.0}},
    )
    assert resp.status_code == 404


def test_shap_summary(client):
    api, _ = client
    resp = api.get("/api/shap-summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["model"] == "gbm"
    assert {f["feature"] for f in body["features"]} == set(FEATURE_COLS)
