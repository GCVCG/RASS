# Rebuttal results index (NeurIPS 2026 submission 675)

Machine-readable results: `rebuttal/rebuttal_results.json` (one key per
task, all seeds recorded). Each summary below is self-contained.

| Task | Key | Summary | Status | One-line result |
|---|---|---|---|---|
| P0 validation | `P0` | P0.md | COMPLETE, 20/20 checks | Pipeline reproduces every paper number exactly; INGP PSNR column convention documented |
| P1 joint event | `E1` | E1.md | COMPLETE | RASS-96 passes all 16 constraints; RASS-48 passes 14/16 (only FS-LPIPS, already disclosed in paper); joint LCB target unreached ≤120sc |
| P2 ranking | `E2` | E2.md | COMPLETE | Ordering preservation is FREE (variant A ≡ E1 at every budget; 100% conditional) |
| P3 sensitivity | `E3` | E3.md | COMPLETE | Tolerances 4.5–8% of std, below every method gap; budget stable 36–48 near defaults; subset non-unique (Jaccard 0.005) |
| P4 regime fidelity | `E4` | E4.md | COMPLETE (negative) | Per-regime means uncertifiable ≤360sc (0/400 at c=1) — statistical inevitability, keep guarantees global |
| P5 FL-36 | `E5` | E5.md | RESOLVED via labeled reimplementation | Original FL artifacts unrecoverable (search documented); FL-36′ certified+packaged; FL unstable (overlap 0.038), breaks PSNR ordering |
| P6 descriptors | `E6` | E6.md | COMPLETE | DINOv2 gives the SAME 36-scene budget; full 57-D beats every group ablation |
| P7 DL3DV transfer | `E7` | E7.md | GATE FAILED → superseded by E13 | Per-scene DL3DV-140 logs not published (benchmark-meta.csv = labels only); logs since generated locally, see E13 |
| — extended audit | `E8` | E8.md | STRESS TEST ONLY | 0/400 under equal allocation on skewed coverage = audit correctly detects population shift; fair rerun pending full training |
| — multi-method | `E9` | E9.md | COMPLETE (updated after E19) | On the full 3,473-scene intersection, proportional allocation: 4-method event certifies at 96sc (LCB .1116), 5-method at 120sc (LCB .1027); RASS-96 passes the 4-method event, fails 2 BioNeRF constraints of the 5-method event |
| P10 proportional E1 | `E10` | E10.md | COMPLETE | Proportional allocation reaches the 0.08 LCB target at 72sc under default tolerances (equal never does ≤120sc); E1 frontier reproduced as baseline |
| P11 dispersion-matched | `E11` | E11.md | COMPLETE (post-hoc label mandatory) | Dispersion-matched taus: 0.08 at 60sc equal / 48sc proportional; RASS-96 passes all 16; RASS-48 still fails only FS-LPIPS |
| P12 why-48 | `E12` | E12.md | COMPLETE, verdict (a) | Selection-time sweep evaluated 36 and it failed its recorded rule (LCB 0.041<0.08); 48 smallest passing; paper frontier starts at 48 by design |
| P13 DL3DV logs+audit | `E13` | E13.md | COMPLETE (in window) | 140/140 nerfacto logs generated locally; audit transfers: proportional certifies 32sc at p_min=0.08 (LCB .123), equal-allocation bias replicated on second dataset |
| P14 single-method prop. | `E14` | E14.md | COMPLETE | Paper's Zip-NeRF frontier under proportional: 0.08 budget unchanged (36sc), comparable at 48 (LCB .168 vs .182), dominates beyond (0.20: 60 vs 96sc); RASS-48/96 unaffected |
| P15 contract evidence | `E15` | E15.md | COMPLETE, verdict (a) | "Declared before results" holds for the core contract (timestamped trail packaged); proportional/uniform companions + budget grid labeled post hoc; 9 event configs exported |
| P16 repo sync | `E16` | E16.md | COMPLETE, commit d50bf31 | 223 files pushed to anonymous repo; 33/33 release claims resolve to live paths; DL3DV license gate PROCEED (metrics only); anonymity grep 0 hits |
| P17 DL3DV multi-method | `E17` | E17.md | COMPLETE (camera-ready) | nerfacto, splatfacto, TensoRF, Instant-NGP (16k steps) on all 140 scenes; proportional certifies 32/40/64/64 scenes for 1-4 methods; equal allocation never reaches 0.08 |
| — coverage bias | `E18` | (in JSON) | RESOLVED by E19 | Missing nerfacto/BioNeRF logs were not missing at random (-3.72 dB / -2.18 dB); motivated E19 |
| P19 log completion | `E9.p19_recovery_effect` | E19.md | COMPLETE | nerfacto and BioNeRF cover 3,521/3,522 scenes; 1,382 recovered from checkpoints, 176 retrained; rows tagged recovered-P19 / retrained-P19 |
