# RASS / NeRF Benchmark Artifact

This package is a Kaggle-ready artifact for the RASS scene-subset audit used in the NeRF benchmark paper. The manifest records the exact source path or placeholder status for each copied or generated file.

## What This Artifact Contains

- `scene_lists/rass48_scene_ids.txt`: 48 scenes for rapid screening and smoke-test style comparisons.
- `scene_lists/rass96_scene_ids.txt`: 96 scenes for the stronger compact reporting option.
- `scene_lists/full_zipnerf_audit_ids.txt`: the full ZipNeRF audit population available in the repository. Leaderboard-quality claims should be checked against the full audit population, not only a compact list.
- `scene_lists/cross_method_common_ids.txt`: scenes shared by the available cross-method tables.
- `descriptors/`: normalized scene descriptors and k=6 regime labels copied from the source repository.
- `results/`: saved audit frontier and cross-method diagnostic CSVs copied from existing outputs.
- `logs/`: per-scene Zip-NeRF, Feature-Splatting, and Instant-NGP (full-image and object-centric) metrics on the
  Nutrition5k-derived scenes; see `logs/README.md`.

## Scope And Limits

RASS-48 is intended for rapid screening. RASS-96 is the recommended compact reporting subset; it also passes the three- and four-method joint fidelity audits. The full audit population is still needed for leaderboard-quality claims.

RASS does not certify arbitrary same-size subsets. It also does not certify regime-level fidelity, cross-method ranking preservation, or nutrition/clinical conclusions. The compact lists are benchmark engineering aids, not a replacement for full-population evaluation or domain-specific validation.

Raw Nutrition5k-derived assets and complete NeRF outputs are not redistributed here unless permission is confirmed. See `external_data/README_how_to_obtain_or_regenerate_inputs.md`.

## Validate

From the repository root:

```bash
python rass_kaggle_artifact_anonymous/scripts/validate_artifact.py --root rass_kaggle_artifact_anonymous
```

From inside this folder:

```bash
python scripts/validate_artifact.py --root .
```

Validation checks required files, parses CSV/YAML/JSON files, verifies scene-list counts for the compact lists, and reports required placeholder markers.

## Reproduce The Audit

The per-scene logs in `logs/` are the inputs of every Nutrition5k audit in the paper. The audit runs on a CPU in seconds:

```bash
python scripts/compute_audit.py                      # frontier; checks 88/400 at 48 and 113/400 at 96 scenes
python scripts/compute_fidelity_event.py             # export audit of RASS-48 (paper Table 5)
python scripts/reproduce_tables.py                   # full frontier, RASS-48/96 audits, regenerates RASS-96
python scripts/generate_candidates.py --subset-size 48 --output candidates_48.csv
python scripts/compute_wilson_lcb.py --successes 113 --trials 400
```

RASS-96 is the export-rule output of the audit (smallest joint objective among passing candidates at 96 scenes).
RASS-48 is the recommended subset of the recorded selection-time sweep (`extended/selection_artifacts/`), whose event
also included cross-method gap terms; it is released as a fixed list and passes the audit above.

## Extended Audits (v1.1.0)

These files support the multi-method, sensitivity, and transfer audits of the paper (Sec. 5.5 and the appendix).

- `extended/event_configs/`: versioned audit-event configurations (multi-method, ranking, dispersion-matched,
  regime-constrained). The `_v2` four- and five-method configs use the full 3,473-scene intersection and supersede `_v1`.
- `extended/method_logs/`: completed nerfacto and BioNeRF logs on Nutrition5k and DL3DV per-scene metrics for four
  methods; provenance and licensing are in `extended/method_logs/README.md`.
- `extended/dl3dv_contract_declaration.json`, `extended/dl3dv_audit_card.json`: DL3DV audit contract and disclosures.
- `extended/selection_artifacts/`: the recorded selection-time rule that fixed RASS-48.
- `subsets/fl36/`: FL-36', a provenance-labeled reimplementation of the facility-location baseline.
- `extended/extended_results.json`: machine-readable results, contracts, and seeds.

One of the 3,522 validated scenes has no Zip-NeRF metric entry, so the audit population is 3,521.

## License

GPL-3.0 (`LICENSE`), except the DL3DV-derived files listed in `extended/method_logs/README.md`, which are released under
CC BY-NC 4.0 with attribution to DL3DV-10K.

## Citation

```bibtex
@inproceedings{almughrabi2026rass, title={{RASS}: Risk-Audited Budget Selection for Compact {NeRF} Benchmark Subsets}, author={AlMughrabi, Ahmad and Serret, Flavi{\`a} and Marques, Ricardo and Radeva, Petia}, booktitle={Advances in Neural Information Processing Systems (NeurIPS), Evaluations and Datasets Track}, year={2026}}
```
