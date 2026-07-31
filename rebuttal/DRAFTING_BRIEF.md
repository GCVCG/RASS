# Drafting brief — NeurIPS 2026 submission 675 rebuttal

Everything needed to write the rebuttal. Attach
`rebuttal/rebuttal_handoff_675.zip` (240 KB) alongside this file; it contains
`rebuttal_results.json` (every key, every seed), all task summaries, the nine
versioned event configs, the DL3DV audit card and contract declaration, the
selection-time artifacts, and the 140 DL3DV per-scene metric logs.

Anonymous repository reviewers can inspect: `github.com/nobody-eh/RASS`
(current head `26f95c2`). Every "released" claim below resolves to a live
path there.

---

## 1. Hard rules — violating any of these is a defect

1. **Never claim E17 results in the rebuttal.** E17 is now COMPLETE (four
   DL3DV methods, four-method audit run) but it is **camera-ready material**,
   not discussion-period evidence. The only permitted rebuttal statement is
   the existing commitment: additional DL3DV methods **in the camera-ready**.
   If E17 is used in the camera-ready, instant-ngp's 16k-step deviation must
   travel with it (see the E17 disclosure block).
2. **Never present these as pre-declared** (they are labeled post hoc in
   `dl3dv_contract_declaration.json`): the proportional and uniform
   companion frontiers in E13, and E13's concrete budget grid. The core
   DL3DV contract (k=4, dispersion-rule tolerances, size-dependent KS,
   balanced generator, M=400, seed 0) *was* declared first — verdict (a),
   evidence trail packaged.
3. **E11 requires its label on every use**: "dispersion-matched operating
   point, declared post hoc during the discussion period." Report the
   default contract's numbers first, always.
4. **Never call FL-36′ the paper's FL-36.** It is a labeled reimplementation;
   the original selection code and seeds were unrecoverable.
5. **State the population honestly**: effective Zip-NeRF audit set is
   **3,521** scenes (one descriptor scene has no log entry — documented
   off-by-one vs the stated 3,522; the paper's own exports already use
   3,521). Cross-method intersection is **3,473**.
6. **E9 coverage is now complete (E19).** nerfacto and BioNeRF each cover
   3,521 of 3,522 scenes, so **I4 = I5 = 3,473** — the full intersection.
   Never repeat the withdrawn "common-coverage subpopulation" caveat, the
   old I4 = 2,915 / I5 = 2,228 sizes, or the superseded 72-scene/LCB-0.105
   and 120-scene/LCB-0.148 figures. Recovered rows are tagged
   `recovered-P19` (original cluster weights re-evaluated) vs
   `retrained-P19` (no checkpoint survived; fresh run). One scene,
   `dish_1563900172`, is permanently excluded (corrupt source image).
7. **Re-check every "released / ships / we release / audited configuration"
   phrase you write** against E16's 33-row claims table. A claim without a
   live repository path is a STOP.
8. Do not quote the deprecated `multi_method_frontier` or
   `full_budget_sweep` multi-method numbers where they overlap E1 — they
   used a different Instant-NGP PSNR column and are superseded.

---

## 2. Reviewer → evidence mapping

| Reviewer | Concern | Answer with |
|---|---|---|
| p5AG W1/Q1 | formal multi-method guarantee | E1 (+ E10 proportional) |
| p5AG W2/Q2 | generalization beyond Nutrition5k | **E13** (DL3DV, 140 scenes) + E6 |
| p5AG W3 | regime-level fidelity | E4 (honest negative) |
| p5AG W4 | tolerance justification | E3 + E6 |
| p5AG Q3 | facility location / FL-36 | E5 (FL-36′, labeled) |
| rTZt W1 | transfer to another dataset | **E13** |
| rTZt W2 | multi-method | E1 |
| rTZt W3 | sensitivity of tolerances | E3 |
| 6aTr Q2 | more methods | **E9 on the full intersection** (+ E19) |
| 6aTr Q3 | ranking preservation | E2 |
| 6aTr W3 | FL | E5 |
| MU2f | joint event | E1 |
| (anticipated) | "why 48 and not 36?" | **E12** |
| (anticipated) | "does proportional change your headline?" | **E14** |

---

## 3. Results to use, with the honest framing

**E1 — formal three-method joint event** (3,473 scenes, default tolerances,
KS ≤ 0.14, equal allocation, M=400, seed 0). RASS-96 passes all 16
constraints. RASS-48 passes 14/16, failing only Feature-Splatting LPIPS —
already disclosed in the paper. The joint LCB target is **not** reached at
any budget ≤ 120 under equal allocation (96 scenes: 30/400, LCB 0.053).
Report that plainly; E10 is the constructive answer.

**E10 — proportional allocation fixes it.** Same event, proportional-to-
regime-size allocation with largest-remainder rounding: **0.08 target reached
at 72 scenes, 0.20 at 120**, versus "not reached up to 120" for equal
allocation. This is the paper's own diagnosis of why equal allocation is
biased on regime-skewed populations.

**E2 — ranking preservation is free.** Variant A (joint event + sign
preservation of all six pairwise method gaps) is identical to E1 at every
budget; 100% conditional preservation. Ordering costs nothing.

**E3 — tolerances are calibrated, not arbitrary.** They sit at 4.5–8% of
per-scene standard deviations and below every cross-method gap. The
recommended budget is stable across 36–48 scenes near the defaults. Subsets
are non-unique (Jaccard 0.005), which is a feature: the audit certifies a
distribution of subsets, not one magic list.

**E4 — honest negative.** Per-regime means are uncertifiable at any budget
≤ 360 scenes (0/400 at c=1). This is a statistical inevitability at these
regime sizes, and it is *why* the guarantees are scoped globally. Present it
as a scoping justification, not a failure.

**E5 — FL-36′.** Original FL artifacts unrecoverable (search documented).
The labeled reimplementation is certified and packaged. Finding: FL is
unstable (overlap 0.038 across seeds) and breaks PSNR ordering — supports
the paper's choice to export the balanced subset.

**E6 — descriptors.** DINOv2 embeddings give the **same** 36-scene budget as
the 57-D hand-crafted descriptors, and the full 57-D set beats every group
ablation. The descriptor design is not load-bearing for the result.

**E9 — multi-method on the FULL intersection. The old E18 caveat is
WITHDRAWN (see E19).** Coverage was completed in P19, so I4 = I5 = **3,473**,
the full cross-method intersection — the same population as E1, no longer a
subpopulation. Proportional allocation. Current numbers, which **supersede**
the previously circulated 72-scene/LCB-0.105 and 120-scene/LCB-0.148 figures:

| event | 72 scenes | 96 scenes | 120 scenes |
|---|---|---|---|
| 4-method (I4) | LCB 0.0700 | **LCB 0.1116** | LCB 0.2007 |
| 5-method (I5) | LCB 0.0248 | LCB 0.0636 | **LCB 0.1027** |

RASS-96 **passes** the 4-method joint event on the full I4 (94/96 in
intersection, zero violations); it fails the 5-method event
(`bionerf.ssim`, `bionerf.lpips`). RASS-48 fails both.

**Be honest that this moved against us**: the 4-method 0.08 target now needs
96 scenes rather than 72. That is *because* the easy-scene bias is gone — it
is the confirmation of E18's prediction, and the resulting claim covers the
whole benchmark rather than a convenient subpopulation. Frame it that way,
do not hide it.

**E18 — coverage bias: FOUND, then FIXED (E19).** E18 established that the
missing logs were not missing at random: nerfacto's missing scenes averaged
Zip-NeRF PSNR 15.73 vs 19.40 (-3.72 dB, KS 0.317 against the 0.14 guardrail,
regime shares shifted by up to 0.20); BioNeRF -2.18 dB, KS 0.178. **That gap
no longer exists** — both methods now cover 3,521 of 3,522 scenes, so the
statistics are undefined by construction. Cite E18 as the diagnosis that
motivated the recovery and as the quantitative explanation for E8's 0/400
stress-test result, **not** as a live limitation. The single permanent
exclusion is `dish_1563900172` (corrupt source image; see E19).

**E13 — DL3DV transfer, the strongest new result.** We generated all 140
per-scene nerfacto logs ourselves (DL3DV publishes none — verified three
times; `benchmark-meta.csv` is labels only). The protocol transferred
unmodified — descriptors, clustering, E3c tolerance calibration, KS
guardrail, audit machinery — and certifies a **32-scene subset (4.4×
reduction) at p_min = 0.08** under proportional allocation (62/400, LCB
0.123). Equal allocation never reaches 0.08 and *declines* past 48 scenes,
independently replicating the E10 bias diagnosis on a second dataset whose
largest regime holds 42% of scenes.
Mandatory caveats: single method; logs self-generated during the discussion
period; DL3DV chosen after submission; at N=140 the KS critical distances
are loose (0.19–0.49), so the binding constraints are the dispersion-matched
means; the proportional/uniform frontiers are post hoc (rule 2).

**E17 — four-method DL3DV audit (CAMERA-READY ONLY, do not quote in the
rebuttal).** All 140 DL3DV scenes trained and evaluated under one harness for
nerfacto, splatfacto, tensorf and instant-ngp (560 per-scene logs, all
committed). Headline: the audit cost **saturates** in the number of methods —
certified budget at p_min = 0.08 goes 32 -> 40 -> 64 -> **64** scenes for
1 -> 2 -> 3 -> 4 methods, so a fourth method tightens the event (pass count at
64 falls 67 -> 56) without moving the budget. Equal allocation fails at every
budget in every multi-method event; proportional is required throughout,
independently corroborating E10. Mandatory disclosure: instant-ngp was trained
to 16,000 steps versus 30,000 for the other three (35,000 in NVlabs'
reference implementation); valid for the within-method scaling curve, NOT for
ranking method quality. Note the shortened schedule did not flatter the
result — instant-ngp has the smallest sigma and hence the tightest tolerance
of the four.

**E15 — provenance.** The DL3DV contract was declared 2026-07-24 22:53 UTC,
recorded in the repo 23 minutes later with `"audit": null`, ~2 h before the
first scene log and ~36 h before the first audit statistic. Evidence is
local (session transcript, file mtimes, the placeholder) — there was no
pushed-commit timestamp at declaration time. Say so if pressed. The
validation gate rejected a mis-wired population on its first run, which
demonstrates the gate was live.

**E16 — artifacts.** 223 files on the anonymous remote; 33/33 release claims
resolve; DL3DV license gate PROCEED (CC BY-NC + ToU permit releasing our
derived metrics, not dataset inputs — and no inputs are released);
anonymity scrub returned zero hits.

---

## 4. Verbatim hold-ready replies (use as-is or tighten)

**"Why 48 scenes when the audit passes at 36?" (E12, 346 chars)**

> The rule is recorded: the selection-time sweep
> (budget_recommendation.json) evaluated {12,24,36,48}; 36 scored LCB 0.041
> (<0.08), 48 was the smallest passing (LCB 0.081). The paper frontier
> evaluates budgets from 48 upward, hence 'lowest-cost evaluated'. The
> revision adds the current audit's 36-scene row (LCB 0.114) and reconciles
> the frontier.

**"Does proportional allocation undermine RASS-48/96?" (E14, 345 chars)**

> No. RASS-48/96 are export-audited scene lists, allocation-independent;
> equal allocation is the documented generator of record. Proportional keeps
> the 0.08 budget at 36 scenes, is comparable at 48 (LCB .168 vs .182), and
> dominates beyond (0.20 target: 60 vs 96 scenes). The revision reports both
> allocations and adopts proportional going forward.

**Dispersion-matched operating point (E11, 154 chars — needs the post-hoc label)**

> under it the three-method joint event gives 27/400 at 48 scenes and
> reaches the 0.08 LCB target at 60 scenes with equal allocation (48 with
> proportional).

---

## 5. Revision commitments that are safe to make

- Report both allocations throughout and adopt proportional as the
  recommended design going forward (E10, E13, E14).
- Add the 36-scene row to the frontier and reconcile the selection-time vs
  paper-frontier grids (E12).
- State the 3,521-scene erratum (already in the README and audit cards).
- Release the versioned event configs so every audited configuration is
  reproducible (E15/E16, already live).
- Add 3DGS as a second DL3DV method in the camera-ready (E17 — commitment
  only, no numbers).

---

## 6. Before you post — run these three checks on the FINAL text

These are not optional polish; each has already caught a real defect.

1. **Claims check.** For every phrase you wrote of the form "we release /
   ships / audited configuration / available at", confirm it appears in
   `rebuttal_results.json["E16"].claims_checklist` (33 rows, each with a
   `path` and `exists: true`). A claim you introduced that is *not* in that
   list has no verified repository path behind it — either point it at a
   real path or delete the sentence. `claims_all_live` was true at commit
   time; it says nothing about sentences added afterwards.

2. **Superseded-number sweep.** Search your draft for these strings. Every
   one is wrong and was circulated before the P19 recovery:
   - `0.105` / "72 scenes" in a 4-method context → now **96 scenes,
     LCB 0.1116** (72 scenes is LCB 0.0700)
   - `0.148` in a 5-method context → now **LCB 0.1027** at 120 scenes
   - `2,915` or `2,228` → both are now **3,473**
   - "common-coverage subpopulation" → withdrawn entirely; E9 runs on the
     full intersection
   - any statement that nerfacto/BioNeRF coverage is incomplete, or that
     E18's coverage bias is a live limitation → it was fixed (E19)

3. **Rule sweep.** Re-read section 1 against what you actually wrote,
   especially rule 1 (no E17 numbers — camera-ready only), rule 2 (post-hoc
   labels), rule 3 (E11's label), and rule 6 (E9 coverage).

If a check fails, fix the text rather than the check.

---

## 7. What is deliberately absent

- **E7** is superseded by E13; the gate-failure framing ("logs not
  published") is still true and is *why* E13 exists.
- **E8** is stress-test material only, superseded by E9; its 0/400 result
  demonstrates the audit correctly detects population shift under equal
  allocation on skewed coverage. Its fair rerun is incomplete and is not
  rebuttal-critical.
- **E17** — see rule 1.
