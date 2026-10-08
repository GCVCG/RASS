# Review-period per-scene method logs (artifact v1.1.0)

- `nutrition5k_nerfacto_metrics.csv`, `nutrition5k_bionerf_metrics.csv`: per-scene PSNR/SSIM/LPIPS on the
  Nutrition5k-derived scenes (BioNeRF: fine-network metrics). Both cover 3,521 of the 3,522 validated scenes;
  `dish_1563900172` is permanently excluded because a truncated source image prevents pose generation.
  The `note` column records provenance of rows added in the 2026 review period:
  - BioNeRF: `recovered-P19` (997 rows; original checkpoints re-evaluated in the original container) and
    `retrained-P19` (3 rows; no checkpoint survived, retrained with the same configuration and seed).
  - nerfacto: 558 rows are tagged `recovered-P19`. Of these, 385 re-evaluate original checkpoints and 173 were
    retrained with the same configuration and seed; this version does not yet separate the two groups.
  - One nerfacto scene was evaluated from its step-28000 checkpoint (noted in its row).
- `dl3dv_metrics.csv`: per-scene metrics for nerfacto, splatfacto (3DGS), TensoRF, and Instant-NGP on all 140
  DL3DV-Benchmark scenes, trained and evaluated by us with nerfstudio (seed 0, downscale 4 / 960P, `ns-eval`).
  nerfacto, splatfacto, and TensoRF use 30k steps; Instant-NGP uses 16k steps (`checkpoint` column), so its
  scores are not comparable across methods. `dl3dv_descriptors.csv`: per-scene descriptors for the same scenes.

## License of the DL3DV-derived files

`dl3dv_metrics.csv`, `dl3dv_descriptors.csv`, `../dl3dv_contract_declaration.json`, and `../dl3dv_audit_card.json`
are derived from DL3DV-10K and are released under CC BY-NC 4.0 for non-commercial research, with attribution to
DL3DV-10K (https://github.com/DL3DV-10K/Dataset). No DL3DV images or other dataset inputs are redistributed.
