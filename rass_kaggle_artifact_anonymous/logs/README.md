# Per-scene method logs (Nutrition5k-derived scenes)

These are the per-scene metrics from which every Nutrition5k audit in the paper is computed. One row per scene.

| File | Scenes | Columns |
|---|---|---|
| `nutrition5k_zipnerf_metrics.csv` | 3,625 | `psnr`, `ssim`, `lpips` (mean over test views) and their per-view `_std`; render speed |
| `nutrition5k_feature_splatting_metrics.csv` | 3,617 | same layout as Zip-NeRF, plus `method_name` |
| `nutrition5k_instant_ngp_full_image_metrics.csv` | 3,521 | `psnr_frame_mean` (the PSNR used in the paper), per-frame min/max, `ssim` and its min/max, `psnr_from_avg_mse` |
| `nutrition5k_instant_ngp_object_centric_metrics.csv` | 3,479 | same layout, computed on the object region |

The formal audit population is the 3,521 scenes that have both a Zip-NeRF entry and a k=6 regime label
(`descriptors/regime_labels.csv`). Instant-NGP reports no LPIPS. An earlier 3-decimal export of the Instant-NGP
full-image table had 3,525 rows (4 scenes outside the audit population); on shared scenes it equals this table up to
rounding. nerfacto and BioNeRF logs are in `extended/method_logs/`.

Only metrics are released; no images, renderings, or checkpoints. License: GPL-3.0 (see `LICENSE`).
