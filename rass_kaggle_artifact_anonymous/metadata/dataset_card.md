# Dataset Card: RASS / NeRF Benchmark Artifact

## Summary

This artifact accompanies the NeurIPS 2026 paper "RASS: Risk-Audited Budget Selection for Compact NeRF Benchmark Subsets" and packages compact scene lists, descriptors, regime labels, audit settings, copied diagnostic results, and minimal reproduction scripts for RASS-style scene-subset auditing in a NeRF benchmark paper.

This package keeps copied-file provenance and placeholder status in `metadata/artifact_manifest.json`.

## Intended Use

- Rapid screening with RASS-48.
- Compact reporting with RASS-96, the recommended reporting subset.
- Structural validation and audit-script scaffolding on Kaggle.
- Reproduction of copied audit tables when the required external metric tables and regenerated NeRF outputs are available.

## Not Intended For

RASS does not certify arbitrary same-size subsets, regime-level fidelity, cross-method ranking preservation, or nutrition/clinical conclusions. The compact lists are not a substitute for full-population leaderboard evaluation.

## Data Composition

- Scene ID lists for compact and full audit populations.
- Normalized scene descriptors copied from the k=6 descriptor table.
- k=6 regime labels copied from the source repository.
- Existing audit frontier and cross-method diagnostic CSVs.
- Metadata, configs, validation code, Wilson LCB code, and reproduction stubs.
- Version 1.1.0: completed nerfacto/BioNeRF logs, DL3DV per-scene metrics for four methods, event configurations, FL-36', and review-period results (see README.md).

## External Data

Raw Nutrition5k-derived assets and full NeRF outputs are not redistributed here unless permitted. Users must obtain or regenerate those inputs separately. See `external_data/README_how_to_obtain_or_regenerate_inputs.md`.

## License

GPL-3.0, except DL3DV-derived files, which are CC BY-NC 4.0 (see rebuttal/method_logs/README.md). Upstream raw-data and external model-output licensing may impose separate requirements.
