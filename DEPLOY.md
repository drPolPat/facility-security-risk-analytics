# Deployment

Frontend → **Vercel** (static Vite build). Backend → **Railway** (Docker).
Both deploy from the `drPolPat/facility-security-risk-analytics` GitHub repo
via each platform's GitHub integration — no CLI needed.

```
 browser ──HTTPS──▶ Vercel (static SPA)
    │
    └──fetch $VITE_API_BASE_URL/api/...──▶ Railway (FastAPI: risk scoring + what-if)
```

The backend has **no secrets and makes no outbound calls**. The synthetic
dataset (`data/processed/facilities.csv`) and the trained models
(`models/incident_likelihood_model.joblib`, `models/shap_summary.json`) are
committed (small — a few hundred KB total, fully synthetic) and copied into
the image, so the build never re-runs the generator or the notebook.

---

## 1 · Backend on Railway

1. **railway.app → New Project → Deploy from GitHub repo →**
   `drPolPat/facility-security-risk-analytics`.
2. Railway reads [`railway.json`](railway.json) at the repo root and builds
   with [`backend/Dockerfile`](backend/Dockerfile). **Leave "Root Directory"
   blank** — the build context must be the repo root (the image copies
   `backend/`, the committed dataset, and the committed models).
3. **Variables** tab — add:

   | Variable | Value | Notes |
   |---|---|---|
   | `CORS_ORIGIN_REGEX` | `https://.*\.vercel\.app` | allows every Vercel preview + production URL, so there's no "update CORS after deploying the frontend" round-trip |

   No API keys are needed. **Do not set `PORT`** — Railway injects it and the
   container reads `$PORT`.

   **CORS uses two different variables — the code reads both, they are not
   interchangeable** (see `backend/app/config.py`):

   - `CORS_ORIGIN_REGEX` → a single **regex**, wired to Starlette's
     `allow_origin_regex`. Use this for the `*.vercel.app` pattern above.
     Value is a bare regex: `https://.*\.vercel\.app` — backslashes, **no
     quotes**.
   - `CORS_ORIGINS` → a **comma-separated list of exact origins**
     (`https://a.example.com,https://b.example.com`), wired to
     `allow_origins`. A regex put here is treated as one literal origin
     string and never matches. Leave it unset in production unless you add a
     fixed custom domain later.

4. **Settings → Networking → Generate Domain.** Copy the URL, e.g.
   `https://facility-security-risk-analytics-production.up.railway.app`.
5. First build is a couple of minutes (`uv sync`, no training step, no model
   download). When it's live:

   ```bash
   curl https://<your-railway-domain>/api/health
   curl https://<your-railway-domain>/api/facilities | head -c 300
   curl https://<your-railway-domain>/api/shap-summary
   ```

---

## 2 · Frontend on Vercel

1. **vercel.com → Add New → Project → Import** the same GitHub repo.
2. **Root Directory:** `frontend`. Framework preset auto-detects as **Vite**
   (build `npm run build`, output `dist`). Leave both as detected.
3. **Environment Variables** — add:

   | Variable | Value |
   |---|---|
   | `VITE_API_BASE_URL` | `https://<your-railway-domain>` (from step 1.4, **no trailing slash**) |

   `VITE_*` values are inlined at **build** time — if the backend URL changes
   later, redeploy the frontend.
4. **Deploy.** Copy the production URL, e.g.
   `https://facility-security-risk-analytics.vercel.app`.

---

## 3 · Confirm the round trip

- `CORS_ORIGIN_REGEX=https://.*\.vercel\.app` already covers the Vercel
  domain, so no extra CORS step is needed after the frontend deploys. (Add a
  custom domain later? Put its exact origin in `CORS_ORIGINS` on Railway and
  let it redeploy.)
- Open the Vercel URL. The facility list should load within a couple of
  seconds. Click into a facility, move a slider (e.g. "existing
  countermeasures"), click **Recalculate**, and confirm the headline
  risk_score and the Ridge/GBM model-comparison panel update with a
  before → after delta.
- **CORS error in the browser console** → the regex is in the wrong
  variable. It belongs in `CORS_ORIGIN_REGEX`, **not** `CORS_ORIGINS`. Fix
  the name, keep the value `https://.*\.vercel\.app` (backslashes, no
  quotes), confirm the Railway service redeployed.
- **`/api/facilities` or `/api/shap-summary` returns 503** → the committed
  `data/processed/facilities.csv` / `models/*.joblib` / `models/*.json`
  files did not make it into the image. Check they're committed
  (`git ls-files data/processed models`) and that the Docker build context
  is the repo root (Root Directory blank on Railway).

---

## Redeploys

- Push to `main` → both platforms auto-redeploy the affected service.
- Regenerated the dataset or retrained the models? Commit the updated
  `data/processed/facilities.csv` / `models/*.joblib` / `models/*.json`,
  push → Railway rebuilds with them.
- Changing `VITE_API_BASE_URL` needs a **frontend** redeploy (build-time
  inline).
