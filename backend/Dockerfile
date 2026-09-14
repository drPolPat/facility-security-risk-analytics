# Backend image for Railway (or any container host).
# BUILD CONTEXT MUST BE THE REPO ROOT -- the image needs backend/ plus the
# committed synthetic dataset and trained models. On Railway: leave "Root
# Directory" blank and set the Dockerfile path to `backend/Dockerfile` (the
# repo-root railway.json does this).
#
#   docker build -f backend/Dockerfile -t fsra-backend .

FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

WORKDIR /srv/backend

# 1. Dependencies (runtime only) -- cached until the lockfile changes.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2. Application code + the committed synthetic dataset and trained models.
#    Paths mirror the repo layout (backend/app/risk resolves the repo root as
#    three parents up), so no path env vars are needed at runtime.
COPY backend/ ./
COPY data/processed/facilities.csv /srv/data/processed/facilities.csv
COPY models/incident_likelihood_model.joblib models/shap_summary.json /srv/models/
RUN uv sync --frozen --no-dev

EXPOSE 8000
CMD ["sh", "-c", "uv run python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
