#!/usr/bin/env python3
"""Task P19: stream the recovered BioNeRF evals onto the second GPU box.

The remote host has a free RTX 3090 but only ~13 GB of disk, so nothing is
staged there in bulk: each scene is shipped, evaluated, harvested and deleted,
and only the metrics JSON is kept (here, not there). Peak remote footprint is
one scene per worker (~250 MB) plus the container.

Work is driven from this side so the remote never needs credentials or an
inbound route back: we already have outbound SSH to it. Scenes are claimed
atomically by creating the local result file's lock dir, so several drivers can
share one queue without coordinating.

Prep (PIL pyramid, colmap -> transforms.json) happens locally and only the
files the dataparser actually reads are shipped. The pyramid is deliberately
NOT shipped: nerfstudio resolves these scenes at downscale factor 1, so it
reads full-resolution images/ and never opens images_{2,4,8}.

Usage: rebuttal_e19_bionerf_remote_eval.py <num_workers>
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rebuttal_e19_bionerf_recover_eval import (  # noqa: E402
    CKPTS, OUT_JSON, REF_CSV, SCRATCH, find_scene, metrics_of, prep_shadow,
    run_dirs)

# set RASS_REMOTE=user@host for the second GPU box; RASS_REMOTE_SIF and
# RASS_REMOTE_ROOT override where the container and scratch live there
HOST = os.environ["RASS_REMOTE"]
RSIF = os.environ.get("RASS_REMOTE_SIF", "~/bionerf.sif")
RROOT = os.environ.get("RASS_REMOTE_ROOT", "~/rass_eval")
K6 = (pathlib.Path(__file__).resolve().parents[1]
      / "sweep_cluster_k/k_6/clustered_scenes_k6_dish_cluster_mapping.csv")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20"]
CHUNK = int(os.environ.get("RASS_EVAL_CHUNK", "0"))
_claim = threading.Lock()


def sh(*args: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(SSH + [HOST, " ".join(args)],
                          capture_output=True, text=True, timeout=timeout)


def claim(dish: str) -> bool:
    """Atomically take a scene; a lock left behind by a crash is reclaimed."""
    lock = SCRATCH / "bionerf_claims" / dish
    with _claim:
        if (OUT_JSON / f"{dish}.json").exists():
            return False
        try:
            lock.mkdir(parents=True)
            return True
        except FileExistsError:
            return False


def eval_remote(dish: str, run: pathlib.Path, wid: int) -> bool:
    src = find_scene(dish)
    if src is None:
        print(f"NO DATA {dish}", flush=True)
        return False
    # the pyramid is never read at downscale factor 1 and is not shipped,
    # so building it would burn local CPU for nothing
    sh_dir = prep_shadow(dish, src, pyramid=False)
    rdir = f"{RROOT}/w{wid}/{dish}"
    # rsync 3.1.3 on the remote has no --mkpath, so every destination
    # directory has to exist before the transfer starts
    # nerfstudio rebuilds the checkpoint path from the config as
    # output_dir/experiment_name/method_name/timestamp, so the run dir must
    # keep its ORIGINAL timestamp name rather than a placeholder
    ts = run.name
    sh("mkdir", "-p", f"{rdir}/scene/images", f"{rdir}/run/{dish}/bionerf/{ts}")

    # ship only what the dataparser and the checkpoint loader read
    # trailing slash on the source: without it rsync copies the directory
    # itself into the destination and the images land in scene/images/images
    images = str((sh_dir / "images").resolve()) + "/"
    for src_path, dst in ((images, f"{rdir}/scene/images/"),
                          (str(sh_dir / "transforms.json"), f"{rdir}/scene/")):
        r = subprocess.run(
            ["rsync", "-a", "--copy-links", src_path, f"{HOST}:{dst}"],
            capture_output=True, text=True, timeout=1800)
        if r.returncode != 0:
            print(f"SHIP FAIL {dish}: {r.stderr[-200:]}", flush=True)
            return False
    r = subprocess.run(["rsync", "-a", f"{run}/", f"{HOST}:{rdir}/run/{dish}/bionerf/{ts}/"],
                       capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        print(f"SHIP FAIL {dish} (ckpt): {r.stderr[-200:]}", flush=True)
        return False

    # repath the config on the remote: data -> shipped scene, output_dir -> run root
    remote_fix = (
        f"python3 - <<'EOF'\n"
        f"import re,pathlib\n"
        f"p=pathlib.Path('{rdir}/run/{dish}/bionerf/{ts}/config.yml')\n"
        f"lines=p.read_text().split('\\n');out=[];i=0\n"
        f"while i<len(lines):\n"
        f"    ln=lines[i]\n"
        f"    m=re.match(r'^(\\s*)(data|output_dir): (&id\\d+ )?"
        f"!!python/object/apply:pathlib\\.PosixPath\\s*$',ln)\n"
        f"    if m:\n"
        f"        ind,key,anc=m.group(1),m.group(2),m.group(3) or ''\n"
        f"        j=i+1;ii=None\n"
        f"        while j<len(lines) and lines[j].strip().startswith('-'):\n"
        f"            ii = ii if ii is not None else lines[j][:len(lines[j])-len(lines[j].lstrip())]\n"
        f"            j+=1\n"
        f"        tgt='{rdir}/scene' if key=='data' else '{rdir}/run'\n"
        f"        out.append(ind+key+': '+anc+'!!python/object/apply:pathlib.PosixPath')\n"
        f"        out.append(ii+'- /')\n"
        f"        out += [ii+'- '+x for x in tgt.strip('/').split('/')]\n"
        f"        i=j;continue\n"
        f"    out.append(ln);i+=1\n"
        f"t='\\n'.join(out)\n"
        + (f"t=re.sub(r'^(\\s*)num_rays_per_chunk: \\d+$', r'\\g<1>num_rays_per_chunk: {CHUNK}', t, flags=re.M)\n"
           if CHUNK else "")
        + f"p.write_text(t)\n"
        f"EOF")
    r = sh(remote_fix)
    if r.returncode != 0:
        print(f"CONFIG FAIL {dish}: {r.stderr[-200:]}", flush=True)
        return False

    cfg = f"{rdir}/run/{dish}/bionerf/{ts}/config.yml"
    r = sh("singularity", "exec", "--nv", "--bind", f"{RROOT}:{RROOT}", RSIF,
           "ns-eval", "--load-config", cfg, "--output-path", f"{rdir}/out.json",
           timeout=5400)
    ok = r.returncode == 0
    if ok:
        got = subprocess.run(
            ["rsync", "-a", f"{HOST}:{rdir}/out.json", str(OUT_JSON / f"{dish}.json")],
            capture_output=True, text=True, timeout=300)
        ok = got.returncode == 0 and (OUT_JSON / f"{dish}.json").exists()
    if not ok:
        print(f"EVAL FAIL {dish}: {(r.stderr or r.stdout)[-300:]}", flush=True)
    else:
        d = json.load(open(OUT_JSON / f"{dish}.json"))
        d["provenance"] = (
            "BioNeRF checkpoint trained on the cluster (step-000025999), "
            "evaluated in the original bionerf.sif container on a second local "
            "GPU after the cluster's eval sweep was cut short by the Slurm wall "
            "clock; 2026-07 (P19)")
        json.dump(d, open(OUT_JSON / f"{dish}.json", "w"), indent=2)
        print(f"DONE {dish} {metrics_of(d)}", flush=True)
    sh("rm", "-rf", rdir)                       # nothing accumulates remotely
    shutil.rmtree(SCRATCH / "bionerf_shadow" / dish, ignore_errors=True)
    return ok


def worker(wid: int, todo: list[str], runs: dict[str, pathlib.Path]) -> None:
    for dish in todo:
        if not claim(dish):
            continue
        ok = False
        try:
            ok = eval_remote(dish, runs[dish], wid)
        except Exception as exc:
            print(f"ERROR {dish}: {str(exc)[:200]}", flush=True)
        if not ok:
            # release the claim so a later pass retries it; a transient OOM or
            # dropped connection must not silently retire a scene
            shutil.rmtree(SCRATCH / "bionerf_claims" / dish, ignore_errors=True)


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    OUT_JSON.mkdir(parents=True, exist_ok=True)
    (SCRATCH / "bionerf_claims").mkdir(parents=True, exist_ok=True)
    ref = set(pd.read_csv(REF_CSV)["dish_id"].astype(str))
    # Restrict to the k=6 audit population. The cluster also holds checkpoints
    # for scenes outside the 3,522 (they have ~8 images, so train_split_fraction
    # 0.9 leaves zero eval views and ns-eval cannot run). Evaluating them would
    # fail forever and they are of no use to the audit.
    pop = set(pd.read_csv(K6)["dish_id"].astype(str))
    t0 = time.time()
    # Re-scan between passes: the checkpoint tree grows while this runs, and a
    # single snapshot would retire the queue early (as it did on the first run,
    # stopping at 287 of 997).
    while True:
        runs = run_dirs()
        todo = sorted(d for d in runs
                      if d in pop and d not in ref
                      and not (OUT_JSON / f"{d}.json").exists())
        if not todo:
            break
        print(f"pass over {len(todo)} scenes; {n} remote workers", flush=True)
        with ThreadPoolExecutor(n) as ex:
            list(ex.map(lambda w: worker(w, todo, runs), range(n)))
        remaining = [d for d in todo if not (OUT_JSON / f"{d}.json").exists()]
        if len(remaining) == len(todo):
            print(f"no progress on {len(remaining)} scenes; stopping", flush=True)
            break
    done = len({p.stem for p in OUT_JSON.glob("*.json")} & pop)
    print(f"{done}/{len(pop - ref)} in-population scenes recovered "
          f"after {(time.time()-t0)/3600:.2f} h", flush=True)


if __name__ == "__main__":
    main()
