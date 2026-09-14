# backend

FastAPI service for the facility security risk model, uv-managed.

- `app/risk/` — risk-scoring logic, synthetic dataset generator, and the
  prediction service (loads the trained models, answers what-if queries).
  Shared by the EDA notebook and the API.
- `app/api/` — the FastAPI routes (`/api/facilities`, `/api/facilities/{id}`,
  `/api/facilities/{id}/what-if`, `/api/shap-summary`).
- `app/main.py` — the FastAPI app + CORS.

```bash
uv sync                              # install deps
uv run python -m app.risk            # regenerate data/processed/facilities.csv
uv run jupyter lab                    # run the EDA notebook (trains + saves the models)
uv run uvicorn app.main:app --reload  # serve the API at http://localhost:8000
uv run pytest                         # run tests (self-contained, no dependency on generated data/models)
```

`data/processed/facilities.csv` and `models/*.joblib` / `models/*.json` are
committed (small, fully synthetic), so a fresh clone can run the API
immediately without regenerating anything. If you change the generator or
retrain the models, re-run the two commands above and commit the results.
Tests don't depend on either: each test builds its own tiny dataset + models
in a temp directory.

See the repo root [README](../README.md) for the overall project layout,
the API reference, and the staging plan.
