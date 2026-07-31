# Additional per-scene method logs

- `nutrition5k_nerfacto_metrics.csv`, `nutrition5k_bionerf_metrics.csv`:
  per-scene method logs for the Nutrition5k-derived scenes (PSNR/SSIM/LPIPS;
  bionerf uses the fine-network metrics). **Coverage is complete as of
  2026-07-30: 3,521 of 3,522 scenes for both methods** (E19 recovery).

  The `note` column records provenance:
  - `recovered-P19` (385 nerfacto, 997 bionerf) — scenes whose training had
    finished but whose evaluation was cut short when the compute jobs hit
    their wall-clock limit. The original checkpoints were re-evaluated, so
    these rows come from the same training runs as the rest of the table.
    Verified against 10 scenes that already had reference values: PSNR and
    SSIM reproduce exactly, LPIPS to <= 1.6e-4.
  - `retrained-P19` (173 nerfacto, 3 bionerf) — no checkpoint survived, so
    these were retrained under the same configuration and seed. Different
    weights from the original runs; kept distinguishable for that reason.
  - one nerfacto scene evaluated from a 93%-trained checkpoint is also
    flagged here.

  `dish_1563900172` is absent from both files and cannot be produced: its
  source image `images/0006.png` is a truncated PNG, which aborts camera-pose
  generation and therefore any training or evaluation run.
- `dl3dv_nerfacto/`: 140 per-scene DL3DV-Benchmark metric JSONs generated
  by us (see provenance field in each file); `dl3dv_nerfacto_metrics.csv`
  is the consolidated table. Only our derived metrics are redistributed -
  no DL3DV images or inputs (per the DL3DV-10K license, CC BY-NC 4.0 +
  terms of use; metrics released for non-commercial research with
  attribution to DL3DV).

Source paths have been rewritten for anonymity; provenance beyond
"additional per-scene method logs" (machines, accounts) is intentionally
omitted.
