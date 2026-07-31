#!/usr/bin/env python3
"""Task P19: recover BioNeRF per-scene metrics from the checkpoints that survived
on the retired cluster.

997 of the 1,001 Nutrition5k scenes missing from nutrition5k_bionerf_metrics.csv
were trained to completion (step-000025999, uniform across all 1,444 surviving
checkpoints) but never evaluated: the April/May eval sweep was killed by the
Slurm 5 h wall clock (66 CANCELLED / 63 DUE TO TIME LIMIT in evals4/*.err), so
ns-eval never reached the tail of each node's chunk. Recovering them therefore
needs eval only, and -- because we reuse the ORIGINAL checkpoints inside the
ORIGINAL container (bionerf.sif, pulled off the cluster before shutdown) -- the
recovered rows come from the same training run as the existing 2,521.

Scene prep replicates the cluster recipe exactly (script_helpers/resize.py +
steps_create_transforms_json.sh), because both steps feed the eval images:
  - PIL LANCZOS downscales at (w // f, h // f) into images_{2,4,8}/images/.
    nerfstudio's own downscaler uses ffmpeg, which resamples differently and
    would shift PSNR, so the pre-generated pyramid must be reproduced bit for
    bit rather than left to the dataparser.
  - colmap model_converter -> sparse/0_txt, then colmap2nerf.py with
    --keep_colmap_coords, giving the same camera poses used at training.
The scene is shadowed in scratch (images symlinked) so the read-only source
tree is never modified.

VALIDATION GATE: --validate re-evaluates scenes that already have a reference
row and refuses to proceed unless the recovered metrics reproduce them. Nothing
is merged into the metrics CSV until that gate passes.

Usage:
  rebuttal_e19_bionerf_recover_eval.py --validate [N]     # gate, no writes
  rebuttal_e19_bionerf_recover_eval.py <worker_id> <num_workers>
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pandas as pd

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRATCH = pathlib.Path(os.environ.get("RASS_SCRATCH", "/tmp/rass_scratch"))
RECOVERY = pathlib.Path(os.environ.get(
    "RASS_RECOVERY", "/tmp/rass_bsc_recovery"))
SIF = RECOVERY / "sif/bionerf.sif"
CKPTS = RECOVERY / "bionerf_ckpts"
SHADOWS = SCRATCH / "bionerf_shadow"
OUT_JSON = SCRATCH / "bionerf_recovered/json"
REF_CSV = REPO / "rebuttal/method_logs/nutrition5k_bionerf_metrics.csv"
COLMAP2NERF = SCRATCH / "cluster_code/src/colmap2nerf.py"
SCENE_ROOTS = [REPO / "n5k360p/n5k360l" / d for d in ("360_4", "360_3", "360_2")]
FINAL_CKPT = "step-000025999.ckpt"
# the cluster's own tolerance for "same metrics": these are reproductions of a
# fixed checkpoint, so agreement should be far tighter than the audit tolerances
# (0.5 dB / 0.01). Anything looser means the prep is not faithful.
TOL = {"psnr": 1e-2, "ssim": 1e-3, "lpips": 1e-3}
# 0 keeps the cluster's 32768. Set lower when the GPU is shared with training
# runs, which otherwise leaves too little VRAM for full-resolution rendering.
CHUNK = int(os.environ.get("RASS_EVAL_CHUNK", "0"))


def find_scene(dish: str) -> pathlib.Path | None:
    for r in SCENE_ROOTS:
        if (r / dish).is_dir():
            return r / dish
    return None


def run_dirs() -> dict[str, pathlib.Path]:
    """dish_id -> run directory holding the final checkpoint."""
    out: dict[str, pathlib.Path] = {}
    for ck in CKPTS.rglob(FINAL_CKPT):
        m = re.search(r"dish_\d+", str(ck))
        if m:
            out.setdefault(m.group(0), ck.parent.parent)
    return out


def prep_shadow(dish: str, src: pathlib.Path,
                pyramid: bool = True) -> pathlib.Path:
    """Replicate the cluster scene prep in a scratch shadow of the source.

    pyramid=False skips the images_{2,4,8} generation. These scenes resolve at
    downscale factor 1, so the dataparser reads full-resolution images/ and
    never opens the pyramid -- building it costs CPU and disk for nothing. Kept
    switchable because that is an empirical property of this dataset, not a
    guarantee, and the validation gate is what confirms it.
    """
    sh = SHADOWS / dish
    sh.mkdir(parents=True, exist_ok=True)
    if not (sh / "images").exists():
        (sh / "images").symlink_to(src / "images")
    if not (sh / "sparse/0").exists():
        (sh / "sparse").mkdir(parents=True, exist_ok=True)
        (sh / "sparse/0").symlink_to(src / "sparse/0")

    # 1. PIL LANCZOS pyramid, byte-identical to script_helpers/resize.py
    if pyramid and not (sh / "images_8/images").exists():
        from PIL import Image
        names = sorted(n for n in os.listdir(src / "images")
                       if n.lower().endswith(".png"))
        for factor in (2, 4, 8):
            (sh / f"images_{factor}/images").mkdir(parents=True, exist_ok=True)
        for n in names:
            img = Image.open(src / "images" / n)
            w, h = img.size
            for factor in (2, 4, 8):
                img.resize((w // factor, h // factor), Image.LANCZOS).save(
                    sh / f"images_{factor}/images" / n)

    # 2. sparse/0 -> sparse/0_txt (colmap model_converter equivalent)
    txt = sh / "sparse/0_txt"
    if not (txt / "images.txt").exists():
        txt.mkdir(parents=True, exist_ok=True)
        import pycolmap
        pycolmap.Reconstruction(str(src / "sparse/0")).write_text(str(txt))

    # 3. transforms.json with the training-time camera convention
    tj = sh / "transforms.json"
    if not tj.exists():
        subprocess.run(
            [sys.executable, str(COLMAP2NERF), "--colmap_camera_model",
             "SIMPLE_RADIAL", "--images", str(sh), "--text", str(txt),
             "--out", str(tj), "--keep_colmap_coords"],
            check=True, capture_output=True, text=True, cwd=str(sh),
        )
    return sh


def eval_scene(dish: str, run: pathlib.Path) -> dict | None:
    """Evaluate one recovered checkpoint.

    The config is repathed as text rather than loaded: it pickles bionerf.*
    classes that only exist inside the container.
    """
    src = find_scene(dish)
    if src is None:
        print(f"NO DATA {dish}", flush=True)
        return None
    sh = prep_shadow(dish, src)
    # nerfstudio derives the checkpoint dir from
    # output_dir/experiment_name/method_name/timestamp, so the copy has to
    # mirror those levels or ns-eval looks for nerfstudio_models in the wrong
    # place. run is <...>/<dish>/bionerf/<timestamp>.
    dst_run = SCRATCH / "bionerf_runs" / dish / run.parent.name / run.name
    if (SCRATCH / "bionerf_runs" / dish).exists():
        shutil.rmtree(SCRATCH / "bionerf_runs" / dish)
    dst_run.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(run, dst_run, symlinks=True)
    out = OUT_JSON / f"{dish}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    # rewrite the pickled PosixPath component lists for data/output_dir
    cfg = dst_run / "config.yml"
    lines = cfg.read_text().split("\n")
    fixed, i = [], 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^(\s*)(data|output_dir): (&id\d+ )?!!python/object/apply:pathlib\.PosixPath\s*$", ln)
        if m:
            indent, key, anchor = m.group(1), m.group(2), m.group(3) or ""
            j = i + 1
            item_indent = None
            while j < len(lines) and (lines[j].strip().startswith("- ") or lines[j].strip() == "-"):
                if item_indent is None:
                    item_indent = lines[j][: len(lines[j]) - len(lines[j].lstrip())]
                j += 1
            target = sh if key == "data" else (SCRATCH / "bionerf_runs")
            fixed.append(f"{indent}{key}: {anchor}!!python/object/apply:pathlib.PosixPath")
            fixed.append(f"{item_indent}- /")
            for part in str(target).strip("/").split("/"):
                fixed.append(f"{item_indent}- {part}")
            i = j
            continue
        fixed.append(ln)
        i += 1
    text = "\n".join(fixed)
    # Rendering is tiled in chunks of num_rays_per_chunk and concatenated, so
    # shrinking it changes peak VRAM but not the output. That invariance is not
    # assumed: the validation gate reproduces reference rows produced at the
    # cluster's 32768 while running at CHUNK here, which tests it directly.
    if CHUNK:
        text = re.sub(r"^(\s*)num_rays_per_chunk: \d+$",
                      rf"\g<1>num_rays_per_chunk: {CHUNK}", text, flags=re.M)
    cfg.write_text(text)

    r = subprocess.run(
        ["singularity", "exec", "--nv",
         "--bind", f"{SCRATCH}:{SCRATCH}", "--bind", f"{REPO}:{REPO}",
         "--bind", f"{RECOVERY}:{RECOVERY}",
         # the scene images are symlinks onto the media disks; without these
         # the shadow's images/ resolves to a path that does not exist in the
         # container and the dataparser dies on the first frame
         "--bind", "/media:/media",
         str(SIF), "ns-eval", "--load-config", str(cfg),
         "--output-path", str(out)],
        capture_output=True, text=True, timeout=3600,
    )
    if r.returncode != 0 or not out.exists():
        print(f"EVAL FAIL {dish}: {r.stderr[-400:]}", flush=True)
        return None
    return json.load(open(out))


def metrics_of(d: dict) -> dict[str, float]:
    """BioNeRF reports coarse and fine networks; the CSV uses the fine one."""
    res = d.get("results", d)
    out = {}
    for k in ("psnr", "ssim", "lpips"):
        for cand in (f"fine_{k}", k):
            if cand in res:
                out[k] = float(res[cand])
                break
    return out


def validate(n: int) -> int:
    ref = pd.read_csv(REF_CSV).set_index("dish_id")
    runs = run_dirs()
    cands = [d for d in runs if d in ref.index and find_scene(d)]
    cands.sort()
    cands = cands[:n]
    print(f"validating {len(cands)} scenes against reference rows\n", flush=True)
    rows, bad = [], 0
    for d in cands:
        got = eval_scene(d, runs[d])
        if not got:
            bad += 1
            continue
        m = metrics_of(got)
        r = ref.loc[d]
        deltas = {k: m[k] - float(r[k]) for k in m}
        ok = all(abs(v) <= TOL[k] for k, v in deltas.items())
        bad += (not ok)
        rows.append((d, m, dict(psnr=r.psnr, ssim=r.ssim, lpips=r.lpips), deltas, ok))
        print(f"{'PASS' if ok else 'FAIL'} {d}  "
              f"PSNR {m.get('psnr', float('nan')):8.4f} vs {r.psnr:8.4f} "
              f"(d={deltas.get('psnr', float('nan')):+.4f})  "
              f"SSIM d={deltas.get('ssim', float('nan')):+.5f}  "
              f"LPIPS d={deltas.get('lpips', float('nan')):+.5f}", flush=True)
    json.dump([{"dish": d, "recovered": m, "reference": r, "delta": dl, "pass": ok}
               for d, m, r, dl, ok in rows],
              open(SCRATCH / "bionerf_validation.json", "w"), indent=1)
    print(f"\n{len(rows) - bad}/{len(rows)} reproduced within "
          f"{TOL['psnr']} dB / {TOL['ssim']} SSIM / {TOL['lpips']} LPIPS")
    return 1 if bad else 0


def main() -> None:
    OUT_JSON.mkdir(parents=True, exist_ok=True)
    if sys.argv[1:2] == ["--validate"]:
        sys.exit(validate(int(sys.argv[2]) if len(sys.argv) > 2 else 3))
    worker = int(sys.argv[1])
    nworkers = int(sys.argv[2])
    ref = set(pd.read_csv(REF_CSV)["dish_id"].astype(str))
    pop = set(pd.read_csv(
        REPO / "sweep_cluster_k/k_6/clustered_scenes_k6_dish_cluster_mapping.csv"
    )["dish_id"].astype(str))
    runs = run_dirs()
    todo = sorted(d for d in runs
                  if d in pop and d not in ref
                  and not (OUT_JSON / f"{d}.json").exists())
    todo = [d for i, d in enumerate(todo) if i % nworkers == worker]
    print(f"[w{worker}] {len(todo)} scenes to recover", flush=True)
    for d in todo:
        # Same claim directory as the remote driver: both consume one queue in
        # sorted order, so without this they would race on the same scenes.
        claims = SCRATCH / "bionerf_claims"
        try:
            (claims / d).mkdir(parents=True)
        except FileExistsError:
            continue
        try:
            got = eval_scene(d, runs[d])
            if got:
                got["provenance"] = (
                    "BioNeRF checkpoint trained on the cluster (step-000025999), "
                    "evaluated locally in the original bionerf.sif container "
                    "after the cluster's eval sweep was cut short by the Slurm "
                    "wall clock; 2026-07 (P19)")
                json.dump(got, open(OUT_JSON / f"{d}.json", "w"), indent=2)
                print(f"DONE {d} {metrics_of(got)}", flush=True)
        except Exception as exc:
            print(f"ERROR {d}: {str(exc)[:200]}", flush=True)
        finally:
            shutil.rmtree(SCRATCH / "bionerf_runs" / d, ignore_errors=True)
            shutil.rmtree(SHADOWS / d, ignore_errors=True)
            if not (OUT_JSON / f"{d}.json").exists():
                shutil.rmtree(claims / d, ignore_errors=True)


if __name__ == "__main__":
    main()
