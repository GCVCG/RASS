#!/usr/bin/env python3
"""Recompute the RASS budget frontier from the released per-scene logs.

Ports the audit used in the paper: balanced per-regime sampling on the k=6
regimes, the joint PSNR/SSIM/LPIPS mean + KS fidelity event against the full
Zip-NeRF audit population, M candidates per budget with generator seed
seed + b, and the 95% Wilson lower confidence bound. The other scripts in this
folder import the functions defined here.

With the default settings it reproduces the paper's frontier, including the
reference points 88/400 at 48 scenes (LCB 0.1822) and 113/400 at 96 scenes.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd
import yaml
from scipy.stats import ks_2samp

METRICS = ("psnr", "ssim", "lpips")
REFERENCE = {48: 88, 96: 113}  # paper frontier, default thresholds


def load_settings(config: Path) -> dict:
    root = config.resolve().parent.parent
    settings = yaml.safe_load(config.read_text())
    thresholds = yaml.safe_load((root / "configs/thresholds.yaml").read_text())
    settings["thresholds"] = thresholds["threshold_sets"][thresholds["selected_threshold_set"]]
    settings["root"] = root
    return settings


def load_population(settings: dict) -> pd.DataFrame:
    """Zip-NeRF metrics joined with the k=6 regime labels (3,521 scenes)."""
    root = settings["root"]
    labels = pd.read_csv(root / settings["descriptors"]["regime_labels"])
    labels = labels.drop_duplicates("dish_id")[["dish_id", "cluster"]]
    zip_df = pd.read_csv(root / settings["metric_tables"]["zipnerf"])
    zip_df = zip_df.dropna(subset=["dish_id", "psnr", "ssim"])
    zip_df = zip_df.groupby("dish_id", as_index=False)[list(METRICS)].mean(numeric_only=True)
    df = labels.merge(zip_df, on="dish_id", how="inner").dropna(subset=list(METRICS))
    return df.sort_values("dish_id", kind="mergesort").reset_index(drop=True)


def fidelity_event(df: pd.DataFrame, subset_ids, thresholds: dict) -> dict:
    """Mean gaps, KS distances, and pass flags of one subset against the full population."""
    sub = df[df["dish_id"].isin(set(subset_ids))]
    out = {"evaluated_scenes": int(sub["dish_id"].nunique())}
    for m in METRICS:
        out[f"{m}_gap"] = float(sub[m].mean() - df[m].mean())
        out[f"ks_{m}"] = float(ks_2samp(df[m].to_numpy(), sub[m].to_numpy()).statistic)
    out["max_ks"] = max(out[f"ks_{m}"] for m in METRICS)
    out["mean_pass"] = all(abs(out[f"{m}_gap"]) <= thresholds[f"{m}_tol"] for m in METRICS)
    out["ks_pass"] = out["max_ks"] <= thresholds["ks_tol"]
    out["joint_pass"] = out["mean_pass"] and out["ks_pass"]
    mean_obj = max(abs(out[f"{m}_gap"]) / thresholds[f"{m}_tol"] for m in METRICS)
    out["joint_objective"] = max(mean_obj, out["max_ks"] / thresholds["ks_tol"])
    return out


def candidates(df: pd.DataFrame, b: int, trials: int, seed: int):
    """Yield balanced candidates: b scenes drawn without replacement from each regime."""
    rng = np.random.default_rng(seed + b)
    groups = {c: df.index[df["cluster"] == c].to_numpy() for c in sorted(df["cluster"].unique())}
    ids = df["dish_id"].to_numpy()
    for _ in range(trials):
        idx = np.sort(np.concatenate([rng.choice(groups[c], size=b, replace=False) for c in sorted(groups)]))
        yield ids[idx].tolist()


def export_subset(df: pd.DataFrame, size: int, settings: dict) -> list[str]:
    """Export rule: the passing candidate with the smallest joint_objective, ties broken by draw order."""
    best = None
    for t, ids in enumerate(candidates(df, size // df["cluster"].nunique(), settings["num_trials"], settings["seed"])):
        ev = fidelity_event(df, ids, settings["thresholds"])
        if ev["joint_pass"] and (best is None or (ev["joint_objective"], t) < best[0]):
            best = ((ev["joint_objective"], t), ids)
    return best[1] if best else []


def wilson_lcb(successes: int, trials: int, confidence: float = 0.95) -> float:
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    p = successes / trials
    denom = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denom
    margin = z * np.sqrt((p * (1.0 - p) + z * z / (4.0 * trials)) / trials) / denom
    return float(max(0.0, center - margin))


def frontier(df: pd.DataFrame, budgets, settings: dict) -> list[dict]:
    k = df["cluster"].nunique()
    rows = []
    for size in budgets:
        b = size // k
        events = [fidelity_event(df, s, settings["thresholds"]) for s in candidates(df, b, settings["num_trials"], settings["seed"])]
        n_pass = sum(e["joint_pass"] for e in events)
        rows.append({"budget_scenes": k * b, "b": b, "n_trials": len(events), "n_pass": n_pass,
                     "empirical_pass_rate": n_pass / len(events),
                     "wilson_lcb": wilson_lcb(n_pass, len(events), settings["confidence_level"])})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=Path("configs/audit_settings.yaml"))
    parser.add_argument("--budgets", type=int, nargs="+", default=[48, 60, 72, 96, 120], help="Subset sizes (multiples of k).")
    parser.add_argument("--output", type=Path, help="Optional CSV for the recomputed frontier.")
    args = parser.parse_args()

    settings = load_settings(args.config)
    df = load_population(settings)
    print(f"audit population: {len(df)} scenes, {df['cluster'].nunique()} regimes, thresholds {settings['thresholds']}")
    rows = frontier(df, args.budgets, settings)
    target = settings["p_min"]
    for r in rows:
        flag = "  <= meets p_min" if r["wilson_lcb"] >= target else ""
        print(f"{r['budget_scenes']:4d} scenes: {r['n_pass']:3d}/{r['n_trials']} pass, LCB {r['wilson_lcb']:.4f}{flag}")
    if args.output:
        with args.output.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    is_default = settings["thresholds"] == {"psnr_tol": 0.5, "ssim_tol": 0.01, "lpips_tol": 0.01, "ks_tol": 0.14}
    if is_default and settings["num_trials"] == 400 and settings["seed"] == 0:
        got = {r["budget_scenes"]: r["n_pass"] for r in rows}
        bad = {s: (got[s], n) for s, n in REFERENCE.items() if s in got and got[s] != n}
        if bad:
            print(f"MISMATCH with the paper frontier (got, expected): {bad}")
            return 1
        checked = sorted(set(got) & set(REFERENCE))
        if checked:
            print(f"matches the paper frontier at {checked} scenes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
