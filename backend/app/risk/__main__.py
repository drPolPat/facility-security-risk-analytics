"""CLI: regenerate the synthetic facility dataset.

    uv run python -m app.risk [--n-per-archetype 75] [--seed 42] [--out PATH]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .generate import generate_dataset

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = REPO_ROOT / "data" / "processed" / "facilities.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-per-archetype", type=int, default=75)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    df = generate_dataset(n_per_archetype=args.n_per_archetype, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} facilities ({df['archetype'].nunique()} archetypes) to {args.out}")


if __name__ == "__main__":
    main()
