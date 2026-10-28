# Offline verification

Run on a copy of the submitted commit, with a fresh output directory outside the copy. The numerical procedure writes no source-file contents, makes no network request and calls no AI API. The final pre-submission full rerun passed: 88 main and 93 supplemental CSV files; 1530 main and 3291 supplemental raw-array files; exact paper/claim matches, in 775.332 seconds. Its unchanged original result is in review/verification-submission-1.json; source snapshot 384a16a633ccf793da1423266852b47151eab24b is identified in review/snapshot-submission-1.json. Later submission changes are documentation/receipts, with scientific files checked unchanged. The earlier preliminary check remains separately identified and is not substituted for this final check.

## Environment and data

Use Python 3.13 and requirements-verify.txt: NumPy, SciPy, pandas, scikit-learn and Matplotlib. The full acquisition environment has a separate package lock. For example, prepare a separate source copy and environment:

```sh
git clone --no-hardlinks /path/to/submitted/repository /scratch/crop-check-source
git -C /scratch/crop-check-source checkout submission-1
python3 -m venv /scratch/crop-check-env
/scratch/crop-check-env/bin/python -m pip install --cache-dir /scratch/crop-check-cache -r /scratch/crop-check-source/requirements-verify.txt
```

Use tag `final` for the reviewed version. Installation needs a package index; numerical verification is offline. No API key is needed.

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
5. Repeats completed supplements: reference frames, stable arable support, sparse transitions/envelopes, jackknife variants, stratification, bounded weights, gradient floors, coherent panels, native-grid comparison, offsets, hypothetical reference errors, additional geography, higher-replication arable checks, projection derivatives and cohort context. NPZ array schemas/values and regenerated supplemental draws are compared, not just pooled averages.
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

The self-rerun uses the original dedicated full environment with the listed scientific-package versions. A fresh minimal package installation was not separately tested. Inspection of the verification import paths found no acquisition/geospatial/model-download dependency in the offline numerical procedure.


## Claim checks and observed contributing computation times

Open each claim's listed evidence file and compare the fields in its `expected` object, then run the single entry point. The following are observed contributing-phase times in the final full rerun, not estimates for another computer. Shared phases appear under multiple claims; their times are not additive across rows. Model acquisition/refitting is outside these times.

| Claim | Check | Contributing computation seconds |
| --- | --- | --- |
| C01 | Revisiting lowers direct broad-group change MSE relative to independent annual samples across the five prespecified budgets. See claims.jsonl for exact expected values and file paths. | 66.774 |
| C02 | At n=128 the direct revisited intervals have lower aggregate coverage than independent-sample intervals on the main agricultural cohort. See claims.jsonl for exact expected values and file paths. | 66.774 |
| C03 | The no-change point baseline beats n=128 direct and frozen-model-assisted broad estimates in squared error on this cohort. See claims.jsonl for exact expected values and file paths. | 129.851 |
| C04 | Original soft-logistic assisted intervals are conservative in aggregate and rarely report directions, with very frequent simplex projection. See claims.jsonl for exact expected values and file paths. | 66.774 |
| C05 | The aggregate coverage gap is much smaller on the exploratory complete stable-arable reference frame. See claims.jsonl for exact expected values and file paths. | 17.472 |
| C06 | Revisited draws with no changed labels account for a substantial portion of direct interval misses; the exploratory conservative interval union does not restore nominal coverage. See claims.jsonl for exact expected values and file paths. | 2.371 |
| C07 | Changing only the numerical entropy-gradient floor changes soft-assisted interval coverage and reporting while preserving point estimates exactly. See claims.jsonl for exact expected values and file paths. | 63.596 |
| C08 | A coherent half-retained panel has intermediate direct precision and higher simultaneous coverage than the full-revisit panel in this benchmark, without reaching nominal95% joint coverage. See claims.jsonl for exact expected values and file paths. | 12.856 |
| C09 | The prospective native-grid case check exposes differences between sampled-point and whole-population reference changes. See claims.jsonl for exact expected values and file paths. | 14.348 |
| C10 | The additional stable-arable broad-group subset has observed revisited MSE above independent MSE, while its finer hierarchy retains a modest gain. See claims.jsonl for exact expected values and file paths. | 25.095 |
| C11 | Applying the local projection derivative changes soft-assisted interval coverage and reporting while preserving all point estimates. See claims.jsonl for exact expected values and file paths. | 56.593 |

The additional arable precision check keeps all estimates/SE/directions and regenerates its index arrays from documented NumPy seeds, shapes, dtypes and array-byte hashes. The original smaller-run index arrays remain bundled. Both simulations are on the same fixed references.
