#!/usr/bin/env python3
"""Check one scene list (e.g. RASS-48) against the joint fidelity event.

Prints full-population and subset means, mean gaps, KS distances, and the
pass/fail of each constraint, i.e. the export audit reported in the paper.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from compute_audit import METRICS, fidelity_event, load_population, load_settings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/audit_settings.yaml"))
    parser.add_argument("--candidate-scenes", type=Path, default=Path("scene_lists/rass48_scene_ids.txt"),
                        help="Text file with one dish_id per line.")
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    args = parser.parse_args()

    settings = load_settings(args.config)
    df = load_population(settings)
    ids = [line.strip() for line in args.candidate_scenes.read_text().splitlines() if line.strip()]
    ev = fidelity_event(df, ids, settings["thresholds"])
    if args.json:
        print(json.dumps(ev, indent=2))
        return 0
    sub = df[df["dish_id"].isin(set(ids))]
    th = settings["thresholds"]
    print(f"{args.candidate_scenes}: {len(ids)} scenes, {ev['evaluated_scenes']} in the audit population")
    for m in METRICS:
        print(f"{m:5s} full {df[m].mean():.4f} subset {sub[m].mean():.4f} gap {ev[f'{m}_gap']:+.4f} "
              f"(tol {th[f'{m}_tol']}) KS {ev[f'ks_{m}']:.4f} (tol {th['ks_tol']})")
    print("JOINT PASS" if ev["joint_pass"] else "JOINT FAIL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
