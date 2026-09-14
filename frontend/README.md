# Frontend

React + Vite + Tailwind dashboard for the facility risk API: a facility list,
an interactive what-if detail view, and an archetype comparison.

```bash
npm install
npm run dev       # dev server on :5173, proxies /api to the backend on :8000
npm run lint
npm test
npm run build
```

The backend must be running with a generated dataset and trained models (see
`../backend/README.md`):

```bash
cd ../backend
uv run python -m app.risk            # once, if data/processed/facilities.csv doesn't exist
uv run jupyter nbconvert --to notebook --execute --inplace ../notebooks/01-eda-risk-scoring.ipynb
uv run uvicorn app.main:app --port 8000
```

## Layout

- `api.js` — fetch wrapper for `/api/facilities`, `/api/facilities/{id}`,
  the what-if POST, and `/api/shap-summary`.
- `theme.js` — shared palette, archetype colors, factor/flag labels.
- `App.jsx` — top-level view switching (Facilities / Archetypes) via plain
  React state, no router. Facilities are fetched once, unfiltered; both the
  list view and the archetype comparison filter/aggregate that same list
  client-side rather than round-tripping per filter change (the dataset is
  small — 300 rows).
- `components/FacilityList.jsx` — sortable table, client-side archetype
  filter, click-through to detail.
- `components/FacilityDetail.jsx` — the what-if view: fetches one facility,
  seeds the model-comparison panel with an empty-override what-if call (so
  it shows real numbers before any edit), and diffs edited sliders/toggles
  against the stored values before sending an override to `/what-if`.
- `components/RiskRadarChart.jsx` — radar of the 7 raw factor scores,
  original vs. live-edited, same convention as the EDA notebook.
- `components/WhatIfControls.jsx` — the 7 sliders + 5 toggles + Recalculate/Reset.
- `components/ModelComparisonPanel.jsx` — Ridge vs. GBM before/after/delta,
  deliberately smaller than the headline risk_score, plus a static
  (non-computed) caption on the accuracy-vs-interaction-capture tradeoff.
- `components/FeatureImportancePanel.jsx` — bar chart of `/api/shap-summary`.
- `components/ArchetypeComparison.jsx` — mean risk_score per archetype.

## A Recharts gotcha worth knowing about

`ArchetypeComparison`'s chart mounts synchronously on a tab click (no async
data fetch gating it, unlike the detail view's charts). Recharts'
`ResponsiveContainer` measures its container via `ResizeObserver` on mount,
and that first measurement can land before layout has actually settled,
leaving the chart stuck at a stale/zero size — nothing re-triggers
`ResizeObserver` afterwards since the container's size never subsequently
changes on its own. A synthetic `window` `resize` event does **not** fix
this (`ResizeObserver` only reacts to the observed element's box actually
changing). The fix in that component forces one genuine layout change
(toggling the container's width by a fraction of a percent, then back) a
tick after mount, which reliably re-fires `ResizeObserver` with a correct
measurement. If you add another chart that can mount synchronously (e.g.
behind a tab or an `if` with no `await` before it), it likely needs the same
treatment.
