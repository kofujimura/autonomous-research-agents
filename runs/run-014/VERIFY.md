# Verification procedure

Use a copy of the submitted commit outside the supplied research directory. The numerical procedure writes only to a new output directory outside its source checkout. All selected labels, raw measurements, failed/pilot outputs and AI-response records needed for verification are bundled; no live download or AI call is required. The fixed paired-native test is unfinished: reproducing its empty common-case denominators does not validate native-grid stability.

## Set up a separate environment

Copy the repository, preserving local Git history if you will inspect the timeline, and check out tag `final`. Create a dedicated Python 3.13 environment outside the source checkout. Package installation is the only required network step; use the pinned packages in requirements-analysis.txt. The author's original environment is excluded from Git. Cross-platform numerical agreement has not been independently tested.

```
python3 -m venv /path/to/verification-venv
/path/to/verification-venv/bin/python -m pip install -r /path/to/source-copy/requirements-analysis.txt
```

## Single numerical entry point

```
/path/to/verification-venv/bin/python -B /path/to/source-copy/scripts/reproduce.py --output /path/to/new-results
```

The output must not exist and must be outside source-copy. The entry point sets thread counts, disables bytecode writes and PROJ network access, and places the Matplotlib cache in the output location. It reconstructs samples from the bundled archives/CSVs, checks every analysis's raw-input hashes, decodes vectors, re-fits the fixed learners, calibrates on earlier negative cases, and regenerates the original and exploratory tables/figures. It checks every compared CSV column (numeric rtol1e-10/atol1e-12, exact categorical values), original-to-extension threshold equality, software input-dependence checks, missingness and incomplete-test status. PDF metadata may differ; numerical tables and plotted values, rather than PDF byte identity, are compared. `verification.json` must say PASS. `progress.json` and its final `stage_timings` contain measured UTC times and elapsed seconds for every stage.

## Measured self-rerun

Latest record: review/self-rerun-4.json. Candidate 40fdcf0d9ce3b467abee309def61fd494869d263 returned PASS with 256 checks and 37 timed stages in 896.385 seconds (wrapper elapsed 898.605 seconds). Its 8916 source working files were unchanged: True. Current numerical code covered by that candidate: **True**. This is an author self-rerun, not independent reproduction. If coverage is False, later scientific additions still require an expanded run. Environment installation is not included in these durations. The author used an external 1800-second experiment timeout for this run; the direct entry point does not impose a timeout itself.

## Quick saved-evidence check

```
/path/to/verification-venv/bin/python -B /path/to/source-copy/scripts/audit_saved.py
```

This separate counter checks saved prediction/flag counts and operating points, including strict-threshold flags and native case summaries. It does not reconstruct raw vectors or fit models, and is not a substitute for the full entry point. It prints PASS or raises an error and writes no source files. The saved check in that candidate took 0.646577 seconds for 30 result sets.

## Main claims and expected checks

Exact unrounded expected values, scope and verification paths are in claims.jsonl. Regenerated folders have the same names under new-results. The observed stage durations below are measured on the author's machine **after shared prerequisites**, not independent per-claim runtimes or promises for other hardware. Rows share stages and their times must not be added. The single full run remains the complete procedure. Manual reading times were not measured.

| Claim | First evidence file | Expected result and check | Observed stage time(s) |
| --- | --- | --- | --- |
| C001 | analysis/main-v1/main-table.csv | 8 contrasts, mixed point directions; every changed-flag count and interval matches expected. | 89.572s: main_v1 |
| C002 | analysis/main-v1/main-table.csv | Higher direct J point estimates in 4/4 original conditions, unequal label resources. | 89.572s: main_v1 |
| C003 | analysis/main-v1/metrics.csv | Magnitude flags 0/24 gains in all 4 product/support rows; retain loss counts. | 89.572s: main_v1 |
| C004 | protocol/plan-v1.md | All supplied initial classes and counts match; read task definitions and official metadata; no ecological outcome measured. | 0.145s: prepare_lcmap |
| C005 | analysis/endpoint-v13/metrics.csv | Stable-negative condition: 24 gain positives/64 negatives, magnitude TP=0; raw scalar reconstruction matches. | 50.177s: endpoint_v13 |
| C006 | analysis/reference-completeness-v14/reference-membership.csv | Changed test scores=0; TESSERA gain contrast -0.011765 to +0.023529 via calibration. | 34.129s: reference_completeness_v14 |
| C007 | analysis/robustness-aef-v12/partial-label-audit.csv | 109/166 later labels, 0 known disagreements; saved-history route matches=0. | 36.180s: robustness_aef_v12, cohort_history_feasibility |
| C008 | analysis/robustness-paired-v12/metrics.csv | All 12 added-readout rows and fixed calibration conditions match; no winning rule selected. | 81.473s: secondary_v2, robustness_paired_v12 |
| C009 | analysis/initial-vector-v17/metrics.csv | Input-period rows match separately by endpoint; permutation leaves 3568 initial-only rows unchanged. | 47.868s: initial_lcmap_v17, initial_nlcd_v17 |
| C010 | analysis/geography-v18/metrics.csv | All 6 LCMAP geographic readout/task rows match; one baseline without embedding values. | 2.018s: geography_lcmap_v18 |
| C011 | analysis/initial-class-v19/metrics.csv | Class-rate gain TP=0/24, FP=0/85; initial-class strata retained; constant loss condition is predictable. | 1.754s: class_lcmap_v19 |
| C012 | analysis/nlcd-v4/metrics.csv | 620 original thresholds match; direct J higher in 7/8; later TESSERA magnitude TP=1/7. | 38.855s: nlcd_v4 |
| C013 | analysis/native-v5/comparisons.csv | Native 113/120 slots, 113 valid centres, 49 raw centre matches; all summary quantiles match. | 0.126s: native_v5 |
| C014 | analysis/reference-access-v20/paired-comparisons.csv | Eighth-reference median 1071.139 to 579.178 km; all contrasts and supervised invariance match. | 75.678s: reference_access_lcmap_v20, reference_access_nlcd_v20 |
| C015 | analysis/native-pairs-v21/checks.json | not_tested_no_complete_native_pairs: 1/32 point-years, 0/16 complete pairs. Empty counts are not stability evidence. | 15.276s: unfinished_native_pairs_v21 |
| C016 | analysis/native-single-date-v22/comparisons.csv | 20 single-date cases, 5 pairs with any flag change; all input/score identity and method-case counts match. | 15.339s: native_single_date_v22, native_identity_v22 |
| C017 | analysis/direct-inputs-v23/metrics.csv | Difference-only minus both-date point J negative in 6/6 gain and positive in 6/6 loss conditions; all inputs/intervals retained, exploratory reused data. | 23.811s: direct_inputs_lcmap_v23, direct_inputs_nlcd_v23 |
| C018 | analysis/partition-sensitivity-v24/primary-ranges.csv | All 10 fixed partition assignments, reconstruction/invariance and 12 primary range rows match; retain availability counts. | 341.092s: partition_sensitivity_v24 |
| C019 | analysis/review-diagnostics-r1/score-similarity.csv | All 8 primary score correlations and exact fold/year drift/count rows match; multi-year summaries are reference-only. | 2.339s: review_diagnostics_r1 |
| C020 | analysis/review-diagnostics-r1/sample-support.csv | All 33 support rows and 12 magnitude-ranking rows match, including unchanged-only negatives. | 2.339s: review_diagnostics_r1 |
| P001 | experiments/fetch-nlcd-aef-008-011/run.json | Peak 3 rather than permitted 2 for 21 seconds; later guard recorded. | Read-only manual log/definition inspection; time not measured |
| P002 | experiments/fetch-controls-aef/run.json | 486 recorded errors/162 task IDs; original arrays lost and repair used. | Read-only manual log/definition inspection; time not measured |

## Integrity and chronology

The compressed review/self-rerun-N-source-inventories.json.gz files contain before/after membership and SHA-256 maps for each tested candidate, excluding Git internals. Their maps should agree. The final candidate covers the current numerical-module hashes; later manuscript refinements change reporting only. Working copies are excluded, but these inspection records are bundled.

On the sealed submitted copy, check the final inventory separately:

```
/path/to/verification-venv/bin/python -B /path/to/source-copy/scripts/hash_outputs.py --check
```

This is read-only. HASH_SCOPE.md lists exclusions, including Git internals, environments, caches and the author's verification working copies. Raw selected measurements, invalid measurements, retained failed outputs and API requests/responses are included. Hashes do not prove chronology or independence.

Inspect `git log --all --oneline --decorate` and events.jsonl. Topic selection is a9a9ebdd6f241688300755187a536bb16d8ec557; original main plan is 16950d0443b1a60305016500941e1c6448a65d40; paired main results were committed 17a54b89abf377c16b503fd5f376393c60f1b73b. Every experiment run.json gives its plan/code commits, exact command, input SHA256, start/end times, timeout and exit code. Inspect the named plan at that commit with `git show COMMIT:protocol/FILE.md`; verify plan ancestry against its recorded code commit. Later amendments explicitly state which results were already seen. Consult protocol/deviations.md for all departures and post-result checks. Git times and event times are self-reported. A submission's own commit is identified by a resolvable tag; its hexadecimal ID is available from Git and the submission message.

## Network and AI calls

After environment setup, neither numerical command uses a network or AI API. Optional live re-acquisition is separate, may differ if sources change, and must not overwrite this source copy. It is not required for verification. The original retrieval plans and dataset/version/licence records describe it; the study's 17:00 acquisition cutoff has already closed.

The authoring session’s sole other-model API generation was the authorized topic-candidate critique, not a scientific instrument or paper review. The human separately supplied REVIEW-1; its reported checks do not require another API call. Original requests/responses, final model identifier, usage and polling/accounting corrections are saved under experiments/topic-critique and api_calls.jsonl. The full entry point recomputes its token/search cost from the saved response without loading an SDK or calling an API. It uses the saved official price list and documented default 30-minute cache-write accounting; legacy retention metadata lacks a lifetime token breakdown, and invoices were not observed. Do not run scripts/api_wrapper.py for verification. New model responses are not required to agree with the saved critique.

## Original first draft and revised package

Tag `submission-1` and review/submission-1/ preserve the original report. To rerun that original procedure/inventory, check out submission-1 on a separate copy; its copied hash list describes that commit, not the revised root. Tag `final` supplies the updated offline entry point and inventory, including review-diagnostics-r1. The latter is post-review exploratory and uses no new data acquisition. Numerical diagnostics do not require rerunning any AI API.
