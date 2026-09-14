"""Loads the synthetic facilities dataset once and serves it to the API.

All data here is synthetic — see ``data/README.md``. This module owns the
CSV -> Python-native-types conversion (pandas/numpy scalar types don't
always validate cleanly against Pydantic response models) so the API layer
just deals in plain dicts.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from .config import FACTORS, FLAGS

REPO_ROOT = Path(__file__).resolve().parents[3]
FACILITIES_CSV_PATH = REPO_ROOT / "data" / "processed" / "facilities.csv"


class DatasetNotFoundError(RuntimeError):
    """Raised when the synthetic dataset hasn't been generated yet."""


@lru_cache(maxsize=1)
def _load() -> pd.DataFrame:
    if not FACILITIES_CSV_PATH.exists():
        raise DatasetNotFoundError(
            f"No dataset at {FACILITIES_CSV_PATH}. Run: "
            "cd backend && uv run python -m app.risk"
        )
    return pd.read_csv(FACILITIES_CSV_PATH)


def reload_dataset() -> None:
    """Clear the cached dataframe. Call after FACILITIES_CSV_PATH changes (e.g. in tests)."""
    _load.cache_clear()


def _row_to_dict(row: pd.Series) -> dict:
    record = row.to_dict()
    record["facility_id"] = str(record["facility_id"])
    record["archetype"] = str(record["archetype"])
    record["archetype_label"] = str(record["archetype_label"])
    for factor in FACTORS:
        record[factor] = float(record[factor])
    record["risk_score"] = float(record["risk_score"])
    record["incident_likelihood"] = float(record["incident_likelihood"])
    for flag in FLAGS:
        record[flag] = bool(record[flag])
    return record


def list_facilities(archetype: str | None = None) -> list[dict]:
    df = _load()
    if archetype is not None:
        df = df[df["archetype"] == archetype]
    return [_row_to_dict(row) for _, row in df.iterrows()]


def get_facility(facility_id: str) -> dict | None:
    df = _load()
    matches = df[df["facility_id"] == facility_id]
    if matches.empty:
        return None
    return _row_to_dict(matches.iloc[0])


__all__ = [
    "DatasetNotFoundError",
    "get_facility",
    "list_facilities",
    "reload_dataset",
]
