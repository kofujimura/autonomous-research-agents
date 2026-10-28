# Offline verification

The tested source commits, observed runtimes and outcomes are recorded in
`analysis/verification-status.json` and its linked reports. Each is an author
re-run, not independent reproduction. A later final source check supplements
the earlier complete primary and polygon-condition-C refits; inspect each
report's scope and commit rather than treating them as one identical run.

## Prepare an immutable source copy

Verify a copy of the submitted Git tag (`submission-1`, later `final`), not the
mutable working directory. All commands below read that copy and write to a
different directory. Do not put the environment, cache or results inside the
source copy. Git timestamps and SHA-256 hashes are consistency records, not
proof of independent provenance or tamper-proofness.

The original environment was macOS ARM, Python3.13.7. Exact Python packages are
listed in `requirements-lock.txt`; native GDAL/PROJ/GEOS versions are in
`manifest.json`. A compatible Linux environment may work, but it has not been
verified unless explicitly recorded in the verification status.

```sh
RESEARCH_SOURCE=/absolute/path/to/submitted-copy
VERIFY_WORK=/absolute/path/to/a/different/new-work-directory
python3.13 -m venv "$VERIFY_WORK/venv"
"$VERIFY_WORK/venv/bin/python" -m pip install --cache-dir "$VERIFY_WORK/cache" -r "$RESEARCH_SOURCE/requirements-lock.txt"
"$VERIFY_WORK/venv/bin/python" -B "$RESEARCH_SOURCE/code/reproduce.py" --source "$RESEARCH_SOURCE" --out "$VERIFY_WORK/results" --refit primary
```

Package installation needs an external network. The reproduction entry point
uses **no network and no AI API**, and must be run from the supplied source
copy's code. It refuses to write inside that copy and checks its file list and
contents before/after execution. Source bytecode caches are disabled. Allow
approximately20–30minutes for all four primary refits on the recorded machine;
the recorded self-run supplies the observed time. Use a process timeout of
1800seconds and at most two simultaneous experiment groups.

For a reduced verification, replace `--refit primary` with `--refit none`.
This regenerates the raw-derived features, polygon pixel selection/features,
all available saved-decision summaries, tables, figures and manuscript fields,
without fitting models. It verifies claims conditional on archived model
predictions. It does not verify that supplementary predictions are obtainable
by refitting. The full primary option additionally refits all18 primary methods
and compares predictions, roles and pairs at all four rotations.

Run the same entry point separately with `--refit polygonC` and a different new
output directory to refit the dispersed-embedding/averaged-physical condition.
It regenerates the feature arrays from raw data and refits all18 methods in
that condition. Each selected refit run is bounded separately. Comprehensively
refitting every supplementary condition takes more than30minutes; the reduced
mode checks their tables from archived predictions, and the optional per-condition
commands below allow additional model refits.

## Data and expected checks

Selected raw embedding patches, scales/masks, polygon samples, numerical
physical raster windows, NWI responses and fitted predictions are bundled in
Git. No redownload is needed. Canonical corrected inputs and output paths are
explicit in `manifest.json:analysis_paths`; original extraction outputs remain
archived. The source-tile correction is in `data/corrections/` and its equality
checks are in `analysis/tile-edge-audit/feature-correction-check.json`.

The large public AlphaEarth tile-locator CSV is excluded from Git for size.
It is needed only for reacquisition, not for offline analysis or deterministic
polygon point regeneration. Its local hash and source are included in the
output inventory. Do not substitute newly downloaded annual products for the
archived patches when checking numerical reproducibility.

The single entry point must finish with `passed:true` in
`results/verification-report.json`. Its assertions check:

1. Corrected primary and recent feature arrays exactly equal the raw-derived
   arrays, with identical primary row metadata. Terrain/surface-water/HAND
   derivation uses the bundled grids, not external services.
   The reported changed-row sets are also checked directly against the
   preserved initial and corrected feature arrays. Repair counts in the paper
   are generated from the correction provenance records.
2. Deterministic dispersed polygon point arrays and each completed polygon
   feature condition agree exactly. The original cohort is3667wetlands;
   the fixed common polygon cohort is3624, with43exclusions.
3. Every saved-decision summary has identical dimensions/labels and numeric
   values within absolute tolerance1e-12. Main outputs are
   `results/analysis/report-data/metrics-all.csv`, `contrasts-all.csv`,
   `pools-all.csv`, `table-primary.md`, `regime-coverage.csv`,
   `screen-decomposition.csv` and `decoder-information.csv`.
4. All main tables and figures are regenerated together in
   `results/analysis/report-data/` and `results/figures/`. The manuscript
   numeric fields are regenerated from those data, rounding only for display.
   The entire regenerated manuscript must equal the source manuscript text.
   Summary input paths are normalized to the output workspace before locating
   copied training-count records.
5. With `--refit primary`, all four corrected primary prediction files agree
   with saved decisions (categorical/integer values exactly; floats at1e-12),
   and training/query/reference/pair assignments agree exactly.
6. The submitted source copy has not changed.

When alternate-year acquisition is complete, the same entry point also
regenerates the fixed common cohort and its2024/2023/2021 feature arrays,
including identical physical arrays and ordered IDs. When the whitening audit
is present, it repeats all32 transformed-vector checks using a separate SVD
calculation by the author (vector tolerance1e-10; means/floors1e-12). These are
computational consistency checks, without independent field validation.

The canonical pool/window diagnostic is given by
`manifest.json:analysis_paths.pool_influence`. The entry point recomputes its
shared nontrivial-query screens and every recorded single-window omission.
It compares conditional counts, contributing-window counts, paired risks and
omission results at1e-12, and regenerates the expected values in `claims.jsonl`.
It also recomputes exact saved-score reference ties, constant-score pools and
half-budget cutoff ties for every completed condition, retaining zero-query
windows and explicit unavailable-field flags. Definitions were fixed before
aggregating the counts in `protocol/report-score-tie-specification.md`.
No diagnostic removes a window from the primary analysis or selects replacement
queries. The additional plan and its post-primary timing are preserved in
`protocol/plan-v18-pool-and-window-sensitivity.md`.

Each main claim in `claims.jsonl` identifies its evidence, expected numeric
value, and the relevant output from these checks. Full-precision values are
authoritative; the paper displays percentages rounded to two decimals.
Supplementary controls are paired with their stated same-input baseline.
The constant-column audit checks zero added values, zero forest splits on that
column, changed reference choices/confidences and screened-query overlap.
The corrected-path constant replays are checked against the original constant
outputs, with exact reference/mismatch comparison and confidence tolerance1e-12.
Their physical inputs are unchanged, so these are expected author replay
checks and do not supply independent observations.

The same entry point regenerates both alternative budget policies from saved
reference decisions and compares accepted IDs, vegetation coverage, risks and
paired contrasts. It repeats the point-to-polygon input-change distributions
and the stronger-transfer invariants: shared candidate pools, identical
physical boosted-tree decisions, copied original augmented-forest decisions,
and whitened-vector maximum-score equivalence. These audits do not refit the
supplementary learners. Their plan timing, evidence files and expected values
are recorded in the corresponding protocol and claim records.

## Optional supplementary model refits

The reduced entry point does not refit every exploratory model. Individual
refits can be run outside the source copy with the exact commands/parameters
in the corresponding `experiments/*/record.json` and task records, replacing
only executable/input/output locations. Examples of entry points are
`analyse_controls.py` (seed, permutation, scalar, constant, boosted-tree),
`analyse_matching.py` (boundary and polygon conditions), and
`analyse_transfer.py` (leave-one-window-out). Supply explicit `--inputs`,
`--primary` where required, `--rotation`/`--region`, and `--output` outside the
source copy; do not execute acquisition scripts for this check. Use the plan
and code commits recorded at execution to investigate differences from later
code. Supplementary repetitions are not independent experiments on new sites.

## Timeline, deviations and failures

Read `events.jsonl`, `research_log.md`, `protocol/deviations.jsonl` and every
retained plan version. Key ordering checks are topic selection commit
`2e25610adfdfe5fb6f271288c2e80d0e75b55729`, initial plan commit
`1a0e1198dfd20d779e707297fd9603b58f32a115`, and pre-fit plansv2/v3/v5.
The first author inspection of matching-loss results is recorded at
2026-10-27T17:16:36Z. Later amendments explicitly distinguish exploratory
choices and the measured tile-edge correction. Per-experiment records link
the plan commit, code commit, input hashes, UTC times, command, timeout,
stdout/stderr and exit code. Git history is never rewritten.

Inspect failures as well as completed outputs, including the original polygon
shared-pixel assertion failure and the relative-path retry failure. The first
corrected-feature launcher accepted `--out` as an argparse abbreviation;
a later log correction identifies an erroneous description of that successful
run. The duplicate run and the correction remain visible.

The candidate-3 author procedure exposed a reporting-path defect: absolute
paths in regenerated summaries made the rebuilt boundary table display
unavailable training counts. The numerical/model checks did not detect that
text-field omission. Its outputs remain preserved. The corrected procedure
normalizes those paths and compares the complete manuscript text; consult the
verification status for which source commits were checked with that guard.

`manifest.json` and `interventions.jsonl` record human-confirmed usage-limit
stops and tool-computed deadline extensions. The record does not infer the
runtime's exact interruption time. Experiments still running in a stop are
listed explicitly.

## External network and AI calls

Network acquisition is optional and separate from verification; URLs, terms,
retrieval times and raw inputs are archived. Public services and frozen model
stores may change. The sole AI generation was the authorized topic-candidate
critique, not experimental measurement or paper review. Its raw request and
response, usage and price sources are saved under `experiments/topic-critique/`
and `api_calls.jsonl`. No API key or API call is needed to inspect or recompute
these records. Do not call the critique API to verify the empirical paper.

The output hash inventory includes raw verification-workspace files, even
though those duplicate workspaces and the locator index are excluded from Git.
For a complete hash check, copy those optional paths from the local submission
directory. On a Git-only copy, use `code/check_inventory.py --root SOURCE
--allow-unbundled`; it skips only the explicitly declared unbundled paths,
while all canonical scientific inputs remain required. Caches, environments
and Git internals are outside the inventory scope. Verify against the submitted
commit. A post-commit receipt may be appended to working `events.jsonl` before
the submission announcement to record the commit ID; it is outside that
commit's hash snapshot and does not change its submitted content.

## Recorded final author runs

The complete corrected primary procedure passed 101 checks in 1180.219477 seconds on source `d3926e3337cca22e6668d038c8fc1bb08e27a8db`, including exact manuscript text and four model rotations. The critical polygon model refit passed all 8 refit checks on source `39c740729d9b7aa8ae33333594b87ea131d5cad0`; its old manuscript-path omission is covered by the corrected procedure. The model/input SHA-256 equivalence and differing run scopes are explicit in `analysis/verification-status.json` and `analysis/verification-candidate3-postcheck.json`. No independent reproduction is claimed.

Snapshot manifests created before a confirmed usage-limit pause retain their then-current deadline. The root manifest and intervention records carry the subsequent human-confirmed extension; numerical calculations do not depend on the deadline field.
