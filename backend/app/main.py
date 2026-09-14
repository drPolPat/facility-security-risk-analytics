"""FastAPI entrypoint. Health check plus the facility risk API (``/api/*``)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=f"{settings.app_name} API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/debug/cors")
def debug_cors() -> dict[str, str | None]:
    # TEMPORARY: diagnosing a CORS mismatch against a Railway env var whose
    # value looks correct when pasted but doesn't match at runtime. Remove
    # once resolved.
    return {
        "cors_origins_repr": repr(settings.cors_origins),
        "cors_origin_regex_repr": repr(settings.cors_origin_regex),
    }
