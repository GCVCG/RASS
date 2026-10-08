#!/usr/bin/env python3
"""Write the balanced candidate subsets the audit draws at one budget.

Output: CSV with one row per (trial, dish_id). The draws are identical to those
scored by compute_audit.py for the same budget, trial count, and seed.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from compute_audit import candidates, load_population, load_settings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/audit_settings.yaml"))
    parser.add_argument("--subset-size", type=int, default=48, help="Total scenes (multiple of k).")
    parser.add_argument("--output", type=Path, default=Path("candidates_48.csv"))
    args = parser.parse_args()

    settings = load_settings(args.config)
    df = load_population(settings)
    b = args.subset_size // df["cluster"].nunique()
    with args.output.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["trial", "dish_id"])
        for t, ids in enumerate(candidates(df, b, settings["num_trials"], settings["seed"])):
            w.writerows([t, i] for i in ids)
    print(f"wrote {settings['num_trials']} candidates of {b * df['cluster'].nunique()} scenes to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
