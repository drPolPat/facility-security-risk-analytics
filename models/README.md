# Models

Trained model artefacts. Committed (small, fully synthetic) so deployment
doesn't depend on re-running the notebook; everything else this notebook
might produce here stays gitignored (see `.gitignore` — only the two files
below and this README are tracked).

- `incident_likelihood_model.joblib` — produced by
  `notebooks/01-eda-risk-scoring.ipynb`, Section 11. A dict with keys `gbm`
  (shallow `GradientBoostingRegressor`), `ridge` (`Ridge`, fit on
  standardized features), `scaler` (`StandardScaler` fit on the training
  split), and `feature_cols` / `flag_cols` / `factor_cols` (column order,
  required to build a feature vector consistently). Loaded by
  `app/risk/predict.py`.
- `shap_summary.json` — produced alongside it, Section 11. `{"model",
  "n_samples", "features": [{"feature", "mean_abs_shap"}, ...]}`, sorted
  descending. Served as-is by `GET /api/shap-summary` rather than
  recomputing SHAP live.

Regenerate by re-running the notebook, then commit the updated files. Both
are loaded by the FastAPI app (`app/risk/predict.py` and `app/api/routes.py`)
rather than being recomputed per-request.
