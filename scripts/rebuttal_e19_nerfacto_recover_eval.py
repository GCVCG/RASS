#!/usr/bin/env python3
"""Task P19: recover nerfacto per-scene metrics from cluster checkpoints.

385 of the 559 Nutrition5k scenes missing from nutrition5k_nerfacto_metrics.csv
already have a final 30k checkpoint on the retired cluster: as with BioNeRF, the
eval sweep was killed by the Slurm wall clock, so training finished but ns-eval
never ran. Evaluating them costs minutes per scene instead of the ~30 min a
retrain would take, and keeps the rows in the same training run as the rest of
the table.

Only step-000029999.ckpt is used. The recovered tree also holds intermediate
checkpoints (2k, 4k, 14k, 22k...) from runs that were interrupted, and those
would not be comparable with the 30k reference.

Scene prep and the config repath reuse rebuttal_local_nerfacto_eval, whose
recipe was validated against cluster metrics to 3e-4 dB PSNR.

  --validate [N]  re-evaluate scenes that already have a reference row and
                  report deltas; writes nothing to the metrics CSV.
  <worker> <n>    recover the missing scenes.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import time

import pandas as pd
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rebuttal_local_nerfacto_eval import (  # noqa: E402
    OUT_JSON, SCRATCH, find_scene, prep_shadow)

REPO = pathlib.Path(__file__).resolve().parents[1]
RECOVERY = pathlib.Path(os.environ.get(
    "RASS_RECOVERY", "/tmp/rass_bsc_recovery"))
CKPTS = RECOVERY / "nerfacto_ckpts_bsc"
REF_CSV = REPO / "rebuttal/method_logs/nutrition5k_nerfacto_metrics.csv"
K6 = REPO / "sweep_cluster_k/k_6/clustered_scenes_k6_dish_cluster_mapping.csv"
FINAL_CKPT = "step-000029999.ckpt"
RUNS = SCRATCH / "nerfacto_recover_runs"
# reproductions of a fixed checkpoint should agree far tighter than the audit
# tolerances (0.5 dB / 0.01); the validated local recipe reaches 3e-4 dB
TOL = {"psnr": 1e-2, "ssim": 1e-3, "lpips": 1e-3}


def run_dirs() -> dict[str, pathlib.Path]:
    out: dict[str, pathlib.Path] = {}
    for ck in CKPTS.rglob(FINAL_CKPT):
        m = re.search(r"dish_\d+", str(ck))
        if m:
            out.setdefault(m.group(0), ck.parent.parent)
    return out


def eval_scene(dish: str, run: pathlib.Path, out: pathlib.Path) -> bool:
    src = find_scene(dish)
    if src is None or not (run / "config.yml").exists():
        print(f"MISSING inputs {dish}", flush=True)
        return False
    sh = prep_shadow(dish, src)
    cfg = yaml.load(open(run / "config.yml"), Loader=yaml.Loader)
    cfg.data = sh
    cfg.pipeline.datamanager.data = sh
    cfg.pipeline.datamanager.dataparser.data = sh
    # output_dir must be set so get_checkpoint_dir() resolves back to this run
    cfg.output_dir = run.parent.parent.parent
    cfg.load_dir = None
    local_cfg = run / "config_local.yml"
    with open(local_cfg, "w") as f:
        yaml.dump(cfg, f)
    env = dict(os.environ, TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD="1")
    r = subprocess.run(
        ["ns-eval", "--load-config", str(local_cfg), "--output-path", str(out)],
        env=env, capture_output=True, text=True, timeout=3600)
    if r.returncode != 0 or not out.exists():
        print(f"EVAL FAIL {dish}: {r.stderr[-300:]}", flush=True)
        return False
    return True


def validate(n: int) -> int:
    ref = pd.read_csv(REF_CSV).set_index("dish_id")
    runs = run_dirs()
    cands = sorted(d for d in runs if d in ref.index and find_scene(d))[:n]
    print(f"validating {len(cands)} nerfacto scenes against reference rows\n",
          flush=True)
    bad = 0
    tmp = SCRATCH / "nerfacto_validate"
    tmp.mkdir(parents=True, exist_ok=True)
    for d in cands:
        out = tmp / f"{d}.json"
        out.unlink(missing_ok=True)
        if not eval_scene(d, runs[d], out):
            bad += 1
            continue
        res = json.load(open(out)).get("results", {})
        r = ref.loc[d]
        dl = {k: float(res[k]) - float(r[k]) for k in ("psnr", "ssim", "lpips")
              if k in res}
        ok = all(abs(v) <= TOL[k] for k, v in dl.items())
        bad += (not ok)
        print(f"{'PASS' if ok else 'FAIL'} {d}  "
              f"PSNR {res.get('psnr', float('nan')):8.4f} vs {r.psnr:8.4f} "
              f"(d={dl.get('psnr', float('nan')):+.5f})  "
              f"SSIM d={dl.get('ssim', float('nan')):+.6f}  "
              f"LPIPS d={dl.get('lpips', float('nan')):+.6f}", flush=True)
    print(f"\n{len(cands) - bad}/{len(cands)} reproduced within "
          f"{TOL['psnr']} dB / {TOL['ssim']} SSIM / {TOL['lpips']} LPIPS")
    return 1 if bad else 0


def main() -> None:
    OUT_JSON.mkdir(parents=True, exist_ok=True)
    if sys.argv[1:2] == ["--validate"]:
        sys.exit(validate(int(sys.argv[2]) if len(sys.argv) > 2 else 5))
    worker = int(sys.argv[1])
    nworkers = int(sys.argv[2])
    ref = set(pd.read_csv(REF_CSV)["dish_id"].astype(str))
    pop = set(pd.read_csv(K6)["dish_id"].astype(str))
    runs = run_dirs()
    todo = sorted(d for d in runs if d in pop and d not in ref
                  and not (OUT_JSON / f"{d}.json").exists())
    todo = [d for i, d in enumerate(todo) if i % nworkers == worker]
    print(f"[w{worker}] {len(todo)} nerfacto scenes to recover", flush=True)
    t0, done = time.time(), 0
    for d in todo:
        out = OUT_JSON / f"{d}.json"
        if out.exists():
            continue
        try:
            if eval_scene(d, runs[d], out):
                rec = json.load(open(out))
                rec["provenance"] = (
                    "nerfacto checkpoint trained on the cluster "
                    "(step-000029999), evaluated locally after the cluster's "
                    "eval sweep was cut short by the Slurm wall clock; "
                    "2026-07 (P19)")
                json.dump(rec, open(out, "w"), indent=2)
                done += 1
                res = rec.get("results", {})
                print(f"DONE {d} psnr={res.get('psnr'):.4f} "
                      f"({done}, {(time.time()-t0)/done/60:.2f} min/scene)",
                      flush=True)
        except Exception as exc:
            print(f"ERROR {d}: {str(exc)[:200]}", flush=True)
    print(f"[w{worker}] finished: {done} evaluated "
          f"({(time.time()-t0)/3600:.2f} h)", flush=True)


if __name__ == "__main__":
    main()
