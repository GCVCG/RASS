# RASS: Risk-Audited Budget Selection for Compact NeRF Benchmark Subsets

This repository contains the artifact package for the NeurIPS 2026 Evaluations and
Datasets Track paper "RASS: Risk-Audited Budget Selection for Compact NeRF Benchmark
Subsets" (Ahmad AlMughrabi, Flavià Serret, Ricardo Marques, Petia Radeva): compact,
risk-audited NeRF benchmark scene lists and reproduction metadata.

Canonical repository location:

```text
https://github.com/nobody-eh/RASS
```

Kaggle artifact (version 1.1.0, Croissant metadata in `croissant.json`):

```text
https://www.kaggle.com/datasets/nobodyeh/rass-nerf-benchmark-artifact
```

The Kaggle account slug `nobodyeh` and the GitHub slug `nobody-eh` are the
accounts used during double-blind review.

## What To Use

- `rass_kaggle_artifact_anonymous/`: Kaggle-ready anonymous artifact package.
- `rass_kaggle_artifact_anonymous/scene_lists/rass48_scene_ids.txt`: RASS-48,
  intended for rapid screening and smoke-test style comparisons.
- `rass_kaggle_artifact_anonymous/scene_lists/rass96_scene_ids.txt`: RASS-96,
  the stronger compact reporting option when a full run is too expensive.
- `rass_kaggle_artifact_anonymous/scene_lists/full_zipnerf_audit_ids.txt`: the
  full ZipNeRF audit population; use this for leaderboard-quality claims.
- `rass_kaggle_artifact_anonymous/metadata/artifact_manifest.json`: exact file
  inventory, source or placeholder status, required flags, and checksums.
- `REPRODUCIBILITY.md`: command checklist for validating and rebuilding the
  packaged artifact.

Raw Nutrition5k-derived assets and complete NeRF outputs are not redistributed
here unless permitted by their upstream terms. See
`rass_kaggle_artifact_anonymous/external_data/README_how_to_obtain_or_regenerate_inputs.md`.

## Scope

RASS-48 is for rapid screening. RASS-96 is the stronger compact reporting
option. The full audit population is still needed for leaderboard-quality
claims.

RASS does not certify arbitrary same-size subsets, regime-level fidelity,
cross-method ranking preservation, or nutrition/clinical conclusions. The
compact lists are benchmark engineering aids, not replacements for full
population evaluation or domain-specific validation.

## Quick Validation

From the repository root:

```bash
python -m pip install pyyaml
python rass_kaggle_artifact_anonymous/scripts/validate_artifact.py --root rass_kaggle_artifact_anonymous
```

Expected high-level checks:

- The artifact structure is complete
- JSON, CSV, and YAML files parse
- RASS-48 has 48 nonempty scene IDs
- RASS-96 has 96 nonempty scene IDs
- required `TODO_REQUIRED` placeholders are reported explicitly

## Packaged Reproduction

These commands use only the files distributed in the artifact package:

```bash
python rass_kaggle_artifact_anonymous/scripts/compute_wilson_lcb.py \
  --successes 113 \
  --trials 400 \
  --confidence 0.95

python rass_kaggle_artifact_anonymous/scripts/reproduce_tables.py \
  --root rass_kaggle_artifact_anonymous
```

To rebuild the local upload archive:

```bash
rm -f rass_kaggle_artifact_anonymous_v1.zip
zip -r rass_kaggle_artifact_anonymous_v1.zip rass_kaggle_artifact_anonymous
unzip -t rass_kaggle_artifact_anonymous_v1.zip
```

## Full Audit Reproduction

Full audit recomputation requires external inputs that are intentionally not
bundled into this repository:

- the permitted Nutrition5k-derived scene assets
- per-scene ZipNeRF full-image metrics for the full audit population
- cross-method NeRF result tables for matched-method diagnostics
- regenerated candidate manifests if auditing a new operating point

The package scripts are conservative: implemented utilities run directly, while
scripts that require unavailable external inputs state the required files rather
than inventing metrics, scene IDs, or scientific results.

## Repository Layout

- `rass_kaggle_artifact_anonymous/`: anonymous Kaggle package and validation
  scripts.
- `scripts/`: research and analysis utilities used by the broader local study.
- `src/`: feature extraction, normalization, clustering, and geometry helpers.
- `latex/`: manuscript source, if included in this checkout.
- `tests/`: regression and unit tests for source pipelines, if included in this
  checkout.

The artifact package is the review-safe entry point. Historical source scripts
may preserve older internal names or assumptions from earlier experiments.

## Review-Period Artifacts (Camera-Ready Additions)

The `rebuttal/` directory holds the NeurIPS 2026 discussion-period audit
artifacts: `rebuttal_results.json` (one key per task, all seeds recorded),
per-task summaries in `rebuttal/summaries/`, versioned event configurations in
`rebuttal/event_configs/` (schema `rass-event-config/1.0`), the DL3DV audit
card and contract-declaration package, and the FL-36′ reimplementation
artifacts in `subsets/fl36/`. The `_v2` four- and five-method event configs use
the full 3,473-scene cross-method intersection and supersede `_v1`. The same
files ship in Kaggle artifact version 1.1.0 under the same paths.

**Completed nerfacto and BioNeRF logs.** Both methods now cover 3,521 of the
3,522 scenes (`rebuttal/method_logs/`); provenance tags and their current
limitation are documented in `rebuttal/method_logs/README.md`.

**Erratum (audit population).** The effective Zip-NeRF audit population is
3,521 scenes, not the stated 3,522: one descriptor scene has no entry in the
Zip-NeRF log. The paper's own exports already use the 3,521-scene population;
audit cards record this.

**DL3DV transfer disclosures.** The DL3DV-140 audits (keys `E13`, `E17`) use
per-scene logs we generated ourselves for nerfacto, splatfacto, TensoRF, and
Instant-NGP (DL3DV publishes none); Instant-NGP was trained for 16k rather than
30k steps, so its scores must not be used to rank methods; only our derived
metrics are redistributed here, never DL3DV images or inputs. At N = 140 the
two-sample KS critical distances are loose (0.19–0.49 across the swept subset
sizes), so the binding constraints in that audit are the dispersion-matched
mean tolerances — the KS guardrail constrains little at this population size.
Further caveats (self-generated logs; dataset choice postdating submission;
post-hoc proportional and uniform frontiers) are listed in
`rebuttal/dl3dv_audit_card.json`. DL3DV-derived files are released under
CC BY-NC 4.0 with attribution to DL3DV-10K.

## License and Citation

GPL-3.0 (`LICENSE`), except DL3DV-derived files, which are CC BY-NC 4.0 (see
`rebuttal/method_logs/README.md`).

```bibtex
@inproceedings{almughrabi2026rass,
  title     = {{RASS}: Risk-Audited Budget Selection for Compact {NeRF} Benchmark Subsets},
  author    = {AlMughrabi, Ahmad and Serret, Flavi{\`a} and Marques, Ricardo and Radeva, Petia},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS), Evaluations and Datasets Track},
  year      = {2026}
}
```
