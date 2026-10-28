# Offline verification

Run on a copy of the submitted commit, with a fresh output directory outside the copy. Numerical verification writes no source files, uses no network and calls no AI API. The reviewed-final full self-rerun passed in 795.986s: 88 main and 102 supplemental CSV files, 1530 main and 3382 supplemental raw-array files, and exact paper.md/claims.jsonl matches. Source commit fd7bed21eb31d92677fae1e55fd174e4900ca819; original result review/verification-final.json; snapshot review/snapshot-final.json. This is a rerun by this session, not independent reproduction. The first-draft verification remains unchanged in review/verification-submission-1.json.

## Environment and data

Use Python 3.13 and requirements-verify.txt: NumPy, SciPy, pandas, scikit-learn and Matplotlib. The full acquisition environment has a separate package lock. For example, prepare a separate source copy and environment:

```sh
git clone --no-hardlinks /path/to/submitted/repository /scratch/crop-check-source
git -C /scratch/crop-check-source checkout submission-1
python3 -m venv /scratch/crop-check-env
/scratch/crop-check-env/bin/python -m pip install --cache-dir /scratch/crop-check-cache -r /scratch/crop-check-source/requirements-verify.txt
```

For the original first draft, use `git checkout submission-1`. For this reviewed final version, replace that checkout command with `git checkout final`. The tags identify different preserved submissions. Installation needs a package index; numerical verification is offline. No API key is needed.

Git includes reference rasters, sampled labels, numerical embeddings, logistic coefficients/scalers, calibration matrices, predictions and audit draws. Large catalogue indexes and original compressed-label byte-range caches are excluded from Git. They remain in original data/catalogues/ and data/labels-chunks/ with URLs/hashes, and are optional for the numerical check. Raw-label decoding requires copying those folders into a separate mutable reproduction workspace or retrieving the recorded public objects/ranges. Upstream objects can change; bundled numerical extracts define this benchmark.

## Single entry point

```sh
OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4 NUMEXPR_MAX_THREADS=4 /scratch/crop-check-env/bin/python -B /scratch/crop-check-source/scripts/verify.py --all --output /scratch/crop-check-output
```

The output must not already exist. verification-config.json indexes completed analyses. The script:

1. Checks event schemas and plan hashes against referenced Git commits; confirms code commits exist. A final check rejects snapshots with experiments still marked running.
2. Checks manifests, reference/feature/prediction hashes and label alignment. Frozen and annually refreshed logistic conditions, including native-grid cases, reconstruct probabilities from features/coefficients/scalers, tolerance 2×10^-6.
3. Repeats the saved 500 Monte Carlo draws per condition/budget using archived fitted predictions. No new models or data are requested.
4. Regenerates CSV tables and standalone SVG/PNG figures; compares CSV schema, missingness, strings and numbers at absolute tolerance 10^-10 and relative tolerance 10^-9.
5. Repeats completed supplements: reference frames, stable arable support, sparse transitions/envelopes, jackknife variants, stratification, bounded weights, gradient floors, coherent panels, native-grid comparison, offsets, hypothetical reference errors, additional geography, higher-replication arable checks, projection derivatives, synthetic annual label-error scenarios, whole-landscape resampling, decision summaries and cohort context. NPZ array schemas/values and regenerated supplemental draws are compared, not just pooled averages.
6. Regenerates paper.md and claims.jsonl and checks exact document matches.

verification-result.json contains elapsed time, per-file differences, input and document checks. Inspect it rather than treating an exit code alone as evidence. The preliminary full run took about ten minutes in the recorded environment, below the 30-minute process limit. A slower environment can use the reduced option or separate bounded groups, disclosing the reduction.

`--quick` checks tables from saved complete Monte Carlo outputs and inexpensive context summaries; it does not rerun all estimators. `--skip-feature-reconstruction` retains stored-input/hash/label checks but skips coefficient reconstruction. The default without `--all` checks only primary broad logistic conditions. The full submission procedure uses `--all`.

`--allow-running` is for preliminary debugging only. Its report has valid_as_final_submission_check=false and cannot satisfy the final pre-submission check.

## Self-rerun location and storage

This session uses a new location inside verification-work/. scripts/make_snapshot.py shares committed Git objects, copies text from commit blobs, and hardlinks immutable NPZ/NPY/PDF inputs plus frozen versioned data/scientific-result manifests, tables and raw-output metadata only after matching their committed blob hashes. Mutable ledgers, code, documents, figures and bookkeeping tallies are copied. Revisions must use new scientific destinations. Verification outputs use another fresh path. This is a new working location with shared immutable inputs, not independent reproduction.

The self-rerun may use `--share-identical-arrays` on the same filesystem. Computation and comparison happen first; exact array bytes must then match before identical recomputed containers share storage with canonical checked inputs. Every array remains at its output path; differing files are retained. For reference-frame runs it checks each freshly written array before sharing, records its pre-sharing comparison, and checks the complete file layout. This bounds temporary storage. This does not reduce trials, comparisons or numerical computation. Ordinary reviewer verification does not need this option. review/deduplication-preliminary-1.json records the preliminary post-check sharing. Unique payload remains inside the research directory and is counted toward its limit.

## Claims and chronology

claims.jsonl maps principal statements to evidence, exact expected values, scope and exploratory status. The entry point checks the evidence and regenerates the claim document. Inspect per-unit distributions too. Wrong-direction frequency can reflect abstention; magnitude coverage and direction reporting are distinct outcomes.

Chronology anchors: topic selection 51640d9; main plan 419a86a; source-mask revision d225d51; prospective native-grid plan e627841; registration plan 086dcc9; numerical source-fit revision c605092; frozen revised heads c8539e5. Two target diagnostic units preceded exploratory v6–v8; complete broad outcomes preceded v9–v12. Experiment records give times, inputs, plan/code references, commands and exit status. New runs require committed script/plan preflight and record script SHA-256 values.

protocol/deviations.md retains changes and corrections: duplicated event E0103/correction E0104; the short concurrency-limit deviation; cache-write cost correction; a CSV readout mistake with unchanged numbers; and the formatting-code provenance correction followed by a committed-code rerun. Git and timestamps are self-reported chronology, not proof against tampering. Batch exit0 does not imply every candidate succeeded: inspect per-case ledgers. Failed attempts remain under experiments/ and protocol/.

## Optional operations and API records

Refitting/acquisition are separate from the read-only entry point. Use another mutable copy, fresh result destinations and the exact recorded settings, source manifests and package versions. Numerical libraries can produce slightly different fitted coefficients; the main sampling results condition on archived maps. Raw acquisition requires network access, recorded public terms and bounded requests; never overwrite the submitted copy.

No AI API call is required. The sole topic critique is archived in experiments/topic-critic/. Its model/date, request/response, usage and tariff-based cost can be checked in api_calls.jsonl and official saved price documentation. scripts/study_tallies.py recomputes costs offline. A new critic response is not a reproduction criterion.

The final SHA-256 manifest specifies exclusions and append-only terminal commit receipts. It covers scientific raw inputs/outputs, including source ranges and the duplicate self-rerun trees excluded from Git. Dependency environments/caches, Git internals and the current inventory itself are excluded. On the original full archive run `python -B scripts/verify_hashes.py`. On a Git-only copy use `--allow-missing-optional`: it explicitly lists absent original ranges/catalogues/self-rerun trees and does not claim a complete-archive hash check. Numerical verification does not need these optional folders. Hashes do not establish independence or tamper-proofness.

The self-rerun uses the original dedicated full environment with the listed scientific-package versions. This session did not separately test a fresh minimal installation. The supplied AI-agent review reports that a fresh requirements-verify.txt environment passed the complete first-draft check; that is the reviewer’s report, not an action directly observed by this session. Inspection of the verification import paths found no acquisition/geospatial/model-download dependency in the offline numerical procedure.


## Claim checks and chronology after review

For each claim, inspect the listed evidence paths and exact expected values in claims.jsonl; the entry point recomputes all numerical sources and regenerates the entire claim document. C01–C11 retain the original analyses; C01,C02,C06 explicitly condition on perfectly repeatable labels, C04 diagnoses the original interval rule, and C10 reports unresolved composition variation. C12 adds label-error sensitivity and C13 adds within-cohort resampling. The new error sensitivity originally took17.723seconds and the summary analysis4.228seconds (observed run records, not time guarantees). Together with the full rerun, verification stays under the trial’s30-minute per-process limit in the observed environment; slower machines can use the clearly reduced --quick mode.

The pre-review anchors remain above. Planv15 was fixed after receipt of REVIEW-1 and before E56/E57; inspect their plan_commit_id, code_commit_id, input hashes, start/end times and the response letter. All added analyses are exploratory. protocol/deviations.md lists the review additions and preserves earlier changes. No reviewer-only script/output was used as this study’s experimental evidence.
## Claim checks and chronology after review

For each claim, inspect the listed evidence paths and exact expected values in claims.jsonl; the entry point recomputes all numerical sources and regenerates the entire claim document. C01–C11 retain the original analyses; C01,C02,C06 explicitly condition on perfectly repeatable labels, C04 diagnoses the original interval rule, and C10 reports unresolved composition variation. C12 adds label-error sensitivity and C13 adds within-cohort resampling. The new error sensitivity originally took17.723seconds and the summary analysis4.228seconds (observed run records, not time guarantees). Together with the full rerun, verification stays under the trial’s30-minute per-process limit in the observed environment; slower machines can use the clearly reduced --quick mode.

The pre-review anchors remain above. Planv15 was fixed after receipt of REVIEW-1 and before E56/E57; inspect their plan_commit_id, code_commit_id, input hashes, start/end times and the response letter. All added analyses are exploratory. protocol/deviations.md lists the review additions and preserves earlier changes. No reviewer-only script/output was used as this study’s experimental evidence.
