# Exploratory amendment v17: initial-vector baselines and held-out Forest check

Fixed 2026-10-25T14:29:10Z, after LCMAP primary/v12–v14 outcomes and before any initial-vector diagnostic or NLCD score analysis. This extends the same study: strong subsequent-state readouts can coexist with weak reference changes, and the supplied initial class makes persistent information a possible alternative explanation. No original endpoint, fitting/calibration partition, reference choice or primary claim is replaced. All additions are exploratory. No AI/API/human experiment or new download is needed. Use the existing2-job/1800second limits; expected numerical runs under5minutes each.

## Questions

Does useful retrospective discrimination in this conditional benchmark require the after-year **target vector values**? Do the three v12 exploratory readouts and these diagnostic baselines behave similarly in the separate, not-yet-analysed NLCD Forest sample? Initial-vector success does not establish forecasting, leakage, static-context causation, encoder error or ecological change. The encoders/labels were produced later, training/calibration uses earlier labelled pairs, and the comparable complete-case mask still uses availability of both target vectors.

## Added fixed scores and comparisons

Use centre support, global references, primary allocation/seed14014, nominal10percent negative calibration with the original higher quantile/strict flag/minimum10 negatives. Keep both products and every existing readout.

1. Initial-reference similarity a·r_a, directed positive for gain and negative for loss. A matched subsequent-state comparator b·r_a uses exactly the same start-year reference. Require8 valid start-year R vectors outside the held-out region; no control vector is used in these two scores. The supplied target initial class remains part of task definition.
2. Initial-vector probability from the original state random forest, with identical earlier fitting labels, weights, parameters and model. Obtain P(Trees|a) as P(Trees|b) minus the already-computed probability difference, or evaluate a directly; verify algebra against saved test outputs. Sign for loss is negative. Compare to the original subsequent-state forest, not just to the reference-change baseline.
3. Initial-vector probabilities from the v12 baseline-cohort random forest and logistic classifier, with their original2017/2018 cohort fitting only. Replace the target input b by a; preserve all earlier negative calibration cases and model parameters. Compare to each corresponding subsequent-state cohort readout. Both variants still use earlier target negative labels for calibration, so no claim of zero transition-label use or equal annotation cost is allowed.

The original raw vectors, target masks and fitting sets do not change. All before/after variants get their own earlier-negative threshold. Report sensitivity/FPR/J, AUROC, counts and flags. Compare initial minus subsequent J using common rows and2,000 paired5-degree-block resamples, seed14014, as descriptive conditional intervals. Do not claim equivalence without a justified margin, select a winner or interpret a point-estimate similarity as proof of the information's origin.

## Software/input-dependence check

On LCMAP only, perform one deterministic permutation (seed14014) of finite later after-year target vectors within before-year, using the same point permutation for both products. Earlier fitting/calibration targets and all R/C vectors stay untouched. Because each LCMAP plot supplies one pair, changed after keys are disjoint from initial and cohort fitting keys; assert this. Recompute the new initial-vector scores/thresholds and require equality within1e-12 and identical flags/cases. This is a software/input-dependence check, not an independent scientific replication. Do not globally permute NLCD raw keys because its plot-years repeat across pairs.

## Separate NLCD boundary test, fixed before its scores

Apply all three v12 readouts (baseline-cohort forest/logistic after-state and embedding-matched controls), all five scores above, and the original v4/v6/v7/v2 comparisons to the existing fixed NLCD sample. Generalize feature lookups using feature_point_id and years through2023 without altering LCMAP outputs. Use original earlier LCMAP fitting/calibration only; assert equality of every newly added method's earlier thresholds to its LCMAP counterpart to1e-12, with identical calibration counts. Do not fit or select methods on NLCD outcomes.

Report Forest gains/losses separately for overlapping2019/2020 and beyond2021/2022 before-years, and primary/alternate-agreeing label subsets as v4. Never pool the distinct dominant-Trees and Forest endpoints, or attribute differences solely to time. Preserve repeated plot-years and bootstrap whole spatial cells. No new sample or exclusion rule. If retrieval is incomplete at17:00UTC, report it with availability; do not prioritize classes or replace points.

## Records and stopping

Save predictions, thresholds, fitting counts, metrics, initial-minus-subsequent paired contrasts, source hashes and the permutation check under analysis/initial-vector-v17 and analysis/nlcd-initial-v17, with run/plan/code commits and actual times. Reproduction regenerates both offline. Include an exploratory result in the abstract only if it changes interpretation of the main results; retain all other additions in the appendix. Revisit close prior work on single-date/context baselines in change detection during self-check. No claim of novelty from failure to find prior work.
