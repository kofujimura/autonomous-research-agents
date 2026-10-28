# Verification of the wetland allocation study

Use a copy of the submitted Git tag (`submission-1` for the first draft, later `final` if present). The numerical procedure reads that copy and writes to a separate, newly created output directory. It does not fit models, use the network, call an AI API, or change its input copy. The complete measured self-rerun status and duration are recorded in `review/self-check.md`; an unfinished status there is not a successful verification claim.

## Environment and input preparation

Development used Python 3.13.7 on macOS arm64. The minimal offline numerical dependencies are pinned in `requirements-verify.txt`; the fuller retrieval/refitting environment is in `requirements.lock.txt`. Install packages in a dedicated environment outside the immutable input copy, with package caches in that working area. Package installation needs the network unless the packages are already available. It is separate from numerical verification. For example:

```sh
python3.13 -m venv /path/to/verification-work/env
/path/to/verification-work/env/bin/python -m pip install --cache-dir /path/to/verification-work/package-cache -r /path/to/input-copy/requirements-verify.txt
```

Copy the tagged tree using ordinary local Git. Most source data and records are committed. New large probability NPZ files are bundled in the research directory but excluded from Git to avoid duplicating gigabytes in its object store. Each completed fit records the exact path and SHA-256 of its probability file. Supplement the tagged copy before verification:

```sh
/path/to/verification-work/env/bin/python /path/to/input-copy/code/copy_large_inputs.py --bundle /path/to/research-bundle --copy /path/to/input-copy
```

This copies exactly the probability files referenced by that commit, verifies each before and after copying, and stops rather than overwriting a differing file. No external download is necessary. Previously tracked probability files remain in Git. All raw probability files are included in the output hash list regardless of Git tracking.

For a smaller *file copy* of the same statistical experiment, `code/prepare_verification.py` can prepare the committed code, reference arrays and metadata, all fit metadata, all required sampled-position/weight arrays and expected results from a Git revision. It omits raw predictor clips, literature and other files unused by offline numerical verification; it includes every final fitted model and all reported comparisons. Run it from the research bundle, which must have its local Git history:

```sh
/path/to/verification-work/env/bin/python /path/to/research-bundle/code/prepare_verification.py --revision submission-1 --destination /path/to/new-input-copy
```

The author session's storage-bounded self-check instead adds `--reuse-read-only`. That creates probability-file links to the original bundle, which the procedure uses only for reading. It shares the input bytes; it is not an independent data copy, independent environment, or independent reproduction. The copied committed files are checked before and after verification, and each probability/reference file is hash-checked when read. Input links are a storage measure, not an operating-system guarantee that the source cannot be changed by other processes.

## Single offline entry point

Choose an output path that does not exist and lies outside the input copy:

```sh
PYTHONDONTWRITEBYTECODE=1 /path/to/verification-work/env/bin/python /path/to/input-copy/code/verify.py --out /path/to/new-verification-output
```

The procedure has an internal 1,700-second limit; experiment wrappers impose a maximum of 1,800 seconds. It regenerates thresholds, per-core confusion counts, patch coverage, regional/macro metrics, paired bootstrap intervals, allocation/weight/quota checks, inventory counts, split-rotation and cohort-matched transfer summaries, deterministic reference shifts, manuscript tables and figures. The threshold-reselection bootstrap is recomputed from the saved scores. Each step writes stdout/stderr in the new output directory. The final `verification.json` reports numerical agreement and input-copy integrity. All expected numerical values are compared with absolute tolerance `1e-12`; generated Markdown tables must match their expected SHA-256. Figure rendering can differ across platforms, so figure byte identity is not required.

Frozen values are in `analysis/expected-results.json` and `analysis/expected-artifacts.json`. Main claim records in `claims.jsonl` identify their specific fields and expected values. The original primary interaction is the four-arm contrast under `primary_contrasts/H1_interaction`; the component gains, proposal contrasts and regional sensitivity are adjacent fields. `scores.csv` and `regional-scores.csv` contain the arm-level estimates. The exact threshold-reselection results are in the regenerated `threshold-bootstrap/summary.json`. Split rotations and transfer cohorts are in `analysis/robustness/`; alignment stress results and their restricted cohort are in `alignment-stress/`.

This entry point recomputes the reported statistics from saved model outputs. It is different from rerunning stochastic model fitting. The paper does not require a future API response to match the one saved candidate critique.

## Optional source and model checks

These steps are separate and require a writable working copy; never run them in the reviewer's immutable input copy.

- Raw NWI query responses, AEF clips, Sentinel-2 clips and STAC metadata are bundled under `data/main/cores/`. Their provenance, licences, acquisition times and hashes are recorded in `sources.jsonl`, per-core completion records and the fixed dataset manifest. Public inputs can change; the retained clips define this study.
- Feature matrices are regenerable NPZ caches excluded from Git. `code/features.py --out /path/to/new-derived/features` can rebuild them and reference arrays into a fresh output area from retained clips. Compare their feature/reference hashes with the fixed manifest before fitting. Preserve the original metadata: regenerated metadata contains a new processing time and is not the original provenance record. Full dependencies are needed for raster/vector rebuilding.
- Original fitting commands are recorded in each `experiments/*/run.json`; `protocol/execution-priorities.json`, the versioned plans and `protocol/rotation-splits.json` define seeds and conditions. Refit into a separate result directory, preserving saved probabilities. Hardware/library differences can affect a refit's exact floating-point output; the offline saved-score recomputation remains the specified check of the published numerical results.
- New retrieval needs the network and must follow the original ordinary-public-access, terms, storage and billing restrictions. No network step is needed for the bundled-data check.
- No AI API is needed. The one candidate-critique request, original response and cost accounting are saved under `api/` and `api_calls.jsonl`. The key is never part of the bundle. Recalling the critic would be a new expenditure and is not a reproduction requirement.

## Timeline, deviations and output hashes

Inspect the local Git log together with `events.jsonl`, `protocol/deviations.jsonl`, `protocol/implementation-clarifications.md`, and the per-experiment `run.json` records. The main milestones are initialization; topic selection; protocol v1; pre-performance v2–v6; frozen 64-core dataset; the first real performance observation; post-result v7–v10; completed batches; and submission tags. Commit messages name event IDs. Each experiment records plan/code commits, commands, timestamps, exit status and input hashes. The original E03 code-provenance mistake is retained with `experiments/E03/provenance-correction.json`; E62 has a failed-launch correction/addendum, and E64 has a lazy presentation-helper import addendum. Later snapshots are not retroactively described as pre-run commits. E65/E66/E67 separately verify the final numerical and manuscript outputs.

The plans precede their dependent results in the recorded history. Later additions remain exploratory and earlier failures remain available. Git timestamps are self-reported; these records do not prove absence of tampering. A final commit receipt necessarily can be appended to the working event log only after that commit exists; the tagged tree contains the preceding receipts. Hash verification should use the tagged snapshot plus its bundled large files, rather than assuming a later append-only receipt is part of the earlier snapshot.

The output SHA-256 list documents its exact scope and exclusions. It includes raw measurements, saved AI requests/responses and probability arrays outside Git. It excludes Git internals, environments/caches, the self-rerun work area, regenerable feature-matrix caches and the hash lists themselves. Hashes establish byte agreement with the listed snapshot, not truth, independence, completeness or tamper-proofness.

## Observed self-check and claim lookup

The full offline numerical entry point passed in **1,471.200 seconds** on the recorded development environment. The wrapped preparation-plus-verification job took **1,482.477 seconds**. It used revision `5d222f64614fa2de18d68f54492d676a16e11c8b`, shared probability input bytes, and confirmed 879 copied committed files unchanged. This is a self-rerun. All claims share this one computation; individual claim execution times were not measured separately and should not be added as if separate runs were needed. Its observed runtime is below 30 minutes, so no statistically reduced verification is required.

| Claims | Confirmation after the joint run | Exact expectations |
| --- | --- | --- |
| C01–C02 | Original four-arm interaction and proposal contrasts in regenerated `analysis/summary.json` | `claims.jsonl`, `analysis/expected-results.json` |
| C03 | Original validation-replay rows of regenerated `analysis/scores.csv`; average the five seeds within representation/allocation | `claims.jsonl`, threshold-replay table |
| C04 | Per-held-region contrasts and cohort-specific FPRs | Summary secondary conditions and `analysis/robustness/` |
| C05 | Regenerated alignment summary and shared cohort | `alignment-stress/summary.json`, claim C05 |
| C06 | Pooled rotated cohort plus individual split intervals | `analysis/robustness/summary.json`, claim C06 |
| C07 | No-bootstrap weighted contrasts and exact saved-position/weight audit | Summary secondary conditions, weight records and claim C07 |
| C08–C09 | Stronger proposal/query and geographical-quota contrasts | Primary-contrast dictionary, generated control tables and claims |
| C10 | Pooled original pixel metrics and small-patch means from regenerated scores | Claim C10; these are descriptive means, not equivalence tests |

After the frozen numerical run, the final manuscript and all ten claims were re-rendered from its fresh numerical outputs using `code/check_manuscript.py`. The complete manuscript bytes and all twenty numeric tables matched; claim values matched within `1e-12`. See `review/manuscript-check/comparison.json`. This checks later prose/formatting changes without describing them as new model experiments or independent reproduction.
