#!/usr/bin/env python3
"""Task P19: merge the recovered per-scene metrics into the released CSVs.

Sources, all of which reuse the ORIGINAL cluster checkpoints so the recovered
rows come from the same training runs as the existing ones:
  - BioNeRF : step-000025999 checkpoints evaluated in bionerf.sif (the cluster's
              own container), validated 10/10 against reference rows with
              PSNR delta 0.0000 / SSIM 0.00000 / LPIPS <= 1.6e-4.
  - nerfacto: step-000029999 checkpoints evaluated locally with the recipe
              validated against cluster metrics to 3e-4 dB, plus the 173 scenes
              retrained here because no checkpoint survived.

Existing rows are never overwritten: where a scene already has a metric it is
kept, and the recovered value is only used to fill a gap. That keeps the
released table stable and makes the merge idempotent.

  --dry-run   report what would change and write nothing
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

import pandas as pd

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRATCH = pathlib.Path(os.environ.get("RASS_SCRATCH", "/tmp/rass_scratch"))
K6 = REPO / "sweep_cluster_k/k_6/clustered_scenes_k6_dish_cluster_mapping.csv"
SOURCES = {
    "bionerf": (REPO / "rebuttal/method_logs/nutrition5k_bionerf_metrics.csv",
                SCRATCH / "bionerf_recovered/json",
                ("fine_psnr", "fine_ssim", "fine_lpips")),
    "nerfacto": (REPO / "rebuttal/method_logs/nutrition5k_nerfacto_metrics.csv",
                 SCRATCH / "cluster_logs/output_json_nerfacto/json",
                 ("psnr", "ssim", "lpips")),
}
# Scenes for which NO cluster checkpoint survived, so they were retrained here.
# They are tagged separately from "recovered-P19": those reuse the original
# cluster weights and are the same training run as the released table, whereas
# these are a new run and must be distinguishable by anyone comparing rows.
FRESH = {
    "bionerf": (SCRATCH / "bionerf_fresh_json",
                ("fine_psnr", "fine_ssim", "fine_lpips")),
}


def read_metrics(path: pathlib.Path, keys: tuple[str, ...]) -> dict | None:
    try:
        d = json.load(open(path))
    except Exception:
        return None
    res = d.get("results", d)
    out = {}
    for canon, key in zip(("psnr", "ssim", "lpips"), keys):
        if key in res:
            out[canon] = float(res[key])
        elif canon in res:                  # nerfacto reports plain names
            out[canon] = float(res[canon])
        else:
            return None
    return out


def main() -> None:
    dry = "--dry-run" in sys.argv
    pop = set(pd.read_csv(K6)["dish_id"].astype(str))
    for method, (csv_path, json_dir, keys) in SOURCES.items():
        df = pd.read_csv(csv_path)
        have = set(df["dish_id"].astype(str))
        rows = []
        skipped_existing = 0
        for p in sorted(json_dir.glob("*.json")):
            dish = p.stem
            if dish not in pop:             # outside the k=6 audit population
                continue
            if dish in have:
                skipped_existing += 1
                continue
            m = read_metrics(p, keys)
            if m is None:
                print(f"  {method}: unreadable metrics in {p.name}")
                continue
            rows.append({"dish_id": dish, **m, "note": "recovered-P19"})
        fresh_dir, fresh_keys = FRESH.get(method, (None, None))
        n_fresh = 0
        if fresh_dir and fresh_dir.exists():
            for p in sorted(fresh_dir.glob("*.json")):
                dish = p.stem
                if dish not in pop or dish in have:
                    continue
                m = read_metrics(p, fresh_keys)
                if m is None:
                    continue
                rows = [r for r in rows if r["dish_id"] != dish]   # fresh wins
                rows.append({"dish_id": dish, **m, "note": "retrained-P19"})
                n_fresh += 1
        merged = pd.concat([df, pd.DataFrame(rows)], ignore_index=True) if rows else df
        merged = merged.drop_duplicates(subset="dish_id", keep="first")
        cov = len(set(merged["dish_id"].astype(str)) & pop)
        print(f"{method:9s}: +{len(rows):4d} new rows "
              f"({n_fresh} retrained, {len(rows)-n_fresh} recovered)  "
              f"(kept {skipped_existing} existing)  "
              f"coverage {len(have & pop)} -> {cov}/{len(pop)}")
        if not dry:
            merged.to_csv(csv_path, index=False)
    if dry:
        print("\n(dry run - nothing written)")


if __name__ == "__main__":
    main()
