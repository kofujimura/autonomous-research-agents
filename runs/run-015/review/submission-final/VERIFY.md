# Verification procedure

**Author verification passed.** The final reduced procedure completed in 935.5 seconds (15.59 minutes), with 456 CSV comparisons and maximum absolute difference 0. All 16,477 source files kept their hashes. This is an author re-run, not independent reproduction.

The submitted source is a fixed Git commit/tag. Verify on a copy made elsewhere; leave that copy unchanged. Every command below writes only into a separate working location. Main recomputation requires no external network and no AI API. Data acquisition is not repeated.

## Environment and source preparation

The implementation was developed on macOS arm64 with Python 3.13.7. The required direct package versions are in `requirements-verify.txt`; `requirements-observed.txt` records the complete dedicated environment inventory, including packages not needed for offline verification. Other platforms are not separately validated. HiGHS results are compared numerically to tolerance 1e-7; integer/time-limited optimization is discussed separately below.

Obtain the submitted commit using a read-only archive/copy. Set the following example paths to locations outside that source copy:

```sh
SOURCE_COPY=/absolute/path/to/submitted-source-copy
VERIFY_WORK=/absolute/path/to/separate-verification-work
mkdir -p "$VERIFY_WORK"
python3 -m venv "$VERIFY_WORK/env"
PIP_CACHE_DIR="$VERIFY_WORK/pip-cache" "$VERIFY_WORK/env/bin/pip" install -r "$SOURCE_COPY/requirements-verify.txt"
```

Package installation is the only required network step if a compatible environment is not already available. It writes the environment into `VERIFY_WORK`, not the source. A pre-existing compatible environment may be used instead. The source copy must include the tracked `data/`, `results/`, `protocol/`, `scripts/`, `manuscript/` and research records. No excluded large data are needed for offline analysis. The source environment, package caches, Git object database and author verification working copies are excluded from the deliverable hash scope; the exact finalized scope is stated with `SHA256SUMS`.

## Single offline entry point

```sh
PYTHONDONTWRITEBYTECODE=1 "$VERIFY_WORK/env/bin/python" "$SOURCE_COPY/scripts/verify.py" --mode reduced --output "$VERIFY_WORK/reduced-results"
```

Use a fresh output path: the program refuses to overwrite an existing completed verification location. It rejects an output path inside the source checkout. Child processes inherit bytecode/cache settings pointing into the output working location. It does not write experiment events into the source.

The procedure:

1. Checks every retained member vector against its source index, recorded hash and complete combined array, including retained partial inputs; then runs the analytic/random bound fixtures, subset-product fixtures and in-memory HTTP-fragment fixture. The latter does not contact a server.
2. Reconstructs the city selection from the bundled public-domain archive and compares the realized design, excluding only the new creation timestamp. If the optional IFS mask is bundled, re-extracts its selected values offline. Repeats the nearest/indexed extraction comparisons on that mask and all retained full-temperature validation fixtures.
3. Re-solves **all available primary** fifty-member forecast units from selected-temperature arrays; re-solves the completed ten/twenty-five-member sensitivities and compares their saved CSV endpoints and identities.
4. Re-solves four deterministically hash-selected subset-product units. For the remaining subset units it uses their saved bound CSVs. This costly-LP part is explicitly **reduced**; all aggregate subset tables are recomputed from the full saved numerical result set.
5. Re-derives every complete city/time horizon from its four member-aligned source arrays, compares derived arrays exactly, re-solves its bounds, and recomputes all city/time summaries. A separate audit checks the paired strata's counts and mean differences directly from saved cases, recomputing land eligibility from the bundled mask table.
6. Recomputes full primary summaries, historical-rank reconstructions, date-block resampling, subset summaries, completed sensitivity summaries, identification classifications, midpoint/common-query controls, overlapping-extraction checks and coverage diagnostics. Saved integer/perturbation outputs are reused for their summaries; all 480 perturbation endpoints are additionally re-solved and compared. All exploratory controlled-precision endpoints are re-solved as well. Integer feasibility witnesses and saved continuous primal/dual multipliers are checked against raw moments.
7. Checks the saved seeds, member identities and forecast coverage for every completed repeated-member draw, recomputes every draw-level aggregate, and re-solves draw0 only. Checks all saved fixed-size precision witnesses and optimization bounds, repeats tiny exhaustive MILP fixtures, and regenerates its full summary. It does not re-solve all large time-limited MILPs. No API response is regenerated.
8. Recomputes post-review state-count bins, width/window intersections and the displayed prespecified geometry/lead/product table from saved/replayed primary outputs (`results/review-response/`, claim C20 and primary stratification). These additions introduce no new LP endpoint.
9. Regenerates the main figures and a manuscript from the recomputed numerical reports. Numerical CSVs are compared against the submitted analysis values. Timestamps, output paths, numerical-certificate residuals and solver iteration counts are not required to be byte-identical. PDF/PNG metadata are not a numerical comparison target.

`verification.json` must have `status: passed`. Its comparisons contain row counts, maximum absolute differences and exact selected columns. The expected values for each main claim appear in `claims.jsonl`; numerical main values should agree within 1e-7 and all case/availability counts should agree exactly. The report states the number of subset units actually re-solved and those supplying bundled results. This procedure is an author re-run when executed by the author, not independent reproduction.

The final revised measured run is `experiments/V016-review-response-end-to-end/`; its complete report is `review/verification-summary.json`. The copied scientific snapshot is commit `375ee1a7ea549a1aa6431ea132b5fe0f8ac49809`, described in `review/revision-source.json`, with before/after hash records in `review/revision-source-before.SHA256SUMS` and `review/revision-source-after-check.json`. The first-draft replay remains separately documented in `review/submission-1-verification-summary.json` and the immutable `review/submission-1/` guide. Final documentation, verification status and sealing records are added afterward; the sealing guard requires the scientific files to retain their verified bytes. The procedure completed within one 30-minute run. Retain any failure on another machine rather than silently dropping checks.

## Full subset LP replay in bounded chunks

Full raw-vector-to-subset-LP replay may exceed 30 minutes. The reduced replay above preserves every reported aggregate and gives a deterministic numerical spot-check of this more costly component. To re-solve all subset units, run the same entry point with `--mode subset-chunk`, using disjoint output locations and contiguous chunks of completed forecast units:

```sh
PYTHONDONTWRITEBYTECODE=1 "$VERIFY_WORK/env/bin/python" "$SOURCE_COPY/scripts/verify.py" --mode subset-chunk --start 0 --count 10 --output "$VERIFY_WORK/subset-000"
PYTHONDONTWRITEBYTECODE=1 "$VERIFY_WORK/env/bin/python" "$SOURCE_COPY/scripts/verify.py" --mode subset-chunk --start 10 --count 10 --output "$VERIFY_WORK/subset-010"
```

Continue starts20,30,... until the number of available original units in `results/primary/summary.json` is covered. The order is fixed date, then product, then lead as enumerated from `protocol/design-v1.json`, omitting incomplete original units. The final chunk may contain fewer than ten units. Each invocation compares all query endpoints in its selected units to the submitted CSV. A reviewer may run these sequentially; the author runs them under the trial's two-worker and thirty-minute limits. No continuously running scheduler is used.

## Secondary and exploratory checks

The main entry point recomputes the ten/twenty-five-member analyses, all moment-perturbation endpoints, and the **summaries** of integer outputs. Individual selected cases and hash ordering are in `results/secondary-runs/`. The constant five-second integer endpoint limit can produce different completion statuses on another machine; only an optimal re-solve can be compared as an exact optimum. Unresolved submitted solves are retained, not assigned fabricated endpoints.

For an optional new raw-vector solve of selected integer or perturbation cases, use a writable output path and the immutable submitted cases:

```sh
PYTHONDONTWRITEBYTECODE=1 "$VERIFY_WORK/env/bin/python" "$SOURCE_COPY/scripts/secondary.py" --task integer --cases "$SOURCE_COPY/results/primary/cases.csv" --start 0 --count 30 --output "$VERIFY_WORK/integer-000"
PYTHONDONTWRITEBYTECODE=1 "$VERIFY_WORK/env/bin/python" "$SOURCE_COPY/scripts/secondary.py" --task epsilon --cases "$SOURCE_COPY/results/primary/cases.csv" --start 0 --count 20 --output "$VERIFY_WORK/epsilon-000"
```

Use further disjoint chunks to cover the selected cohort. This repeats local mathematical optimization, not the OpenAI API. The saved continuous witnesses and dual multipliers in the integer cohort provide additional numerical evidence. Positive moment tolerances are sensitivity neighborhoods, not statistical confidence intervals.

`scripts/identification_diagnostics.py` and `protocol/plan-v6-identification-diagnostics.md` describe the exploratory numerical rank/row-space classifications. All completed classifications are recomputed by the main entry point. Their category counts are separate from the main interval endpoints. Rank deficiency does not prove nonuniqueness under nonnegative constraints.

The repeated-member component is reduced only in its new LP solves: every saved draw is aggregated and its selections checked, but draw0 alone is re-solved. To replay all 100 draws, use five disjoint outputs, substituting starts 0, 20, 40, 60, 80; each 20-draw block took less than two minutes in the observed environment:

```sh
PYTHONDONTWRITEBYTECODE=1 "$VERIFY_WORK/env/bin/python" "$SOURCE_COPY/scripts/repeated_members.py" --cases "$SOURCE_COPY/results/primary/cases.csv" --start 0 --count 20 --output "$VERIFY_WORK/repeated-000"
```

Compare each generated `chunk-NNN/cases.csv` against its submitted counterpart with numerical tolerance 1e-7. Conditional draw quantiles are not confidence intervals over weather. For an optional new fixed-size precision solve, use the following fresh output; allow for machine-dependent MILP completion. It attempts 120 cases with a five-second limit for each endpoint and refuses an existing output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 "$VERIFY_WORK/env/bin/python" "$SOURCE_COPY/scripts/integer_precision.py" --cases "$SOURCE_COPY/results/primary/cases.csv" --output "$VERIFY_WORK/integer-precision-new"
```

The reported all-case width bounds use saved feasible witnesses and solver bounds even where an optimum was unresolved. A different timed solve need not reproduce its completion status. These numerical bounds are distinct from statistical confidence limits.

## Evidence map and time required

- Primary widths, informative denominators, aggregate narrowing share, action certification and point reconstruction: `results/primary/`, claim records C01–C05; all primary LPs and summary calculations are covered by the reduced entry point.
- Integer, moment tolerance and member-count sensitivity: `results/sensitivity/`, original numeric outputs in `results/secondary-runs/` and `results/member-sensitivity/`; claims C06–C08. Summary recomputation is included; optional full re-solves are separate above.
- Reusable subset products and exact coherent-mask/count comparators: `results/subsets/`, claims C09–C10. All aggregate values and round trips are recomputed; the reduced procedure re-solves four units, and full LP replay uses bounded chunks.
- City/time boundary and conditional land diagnostic: `results/city-time/`, `data/cities/land-mask/`, claim C11; all complete derived horizons are covered. This overlaps original forecasts and is not independent confirmation.
- Controlled-precision results: `results/controlled-moments/`, claim C17; every endpoint is re-solved.
- Overlapping extraction coverage: `results/overlap-recovery/`, claim C15; all retained-member checks, derived arrays and auxiliary-calendar numerical tables are recomputed, while the primary exclusion remains intact.
- Numerical identification classifications and additional midpoint/common-member controls: `results/identification/`, `results/midpoints/`, `results/common-members/`; claims C13, C14 and C16. These are exploratory and included in the reduced replay.
- Missing-data envelopes and weighting/resampling sensitivity: `results/coverage/`, claim C12; recomputation uses saved primary/subset outputs and the fixed scheduled population.
- Repeated-member conditional variation: `results/repeated-members/`, claim C18; all selections and aggregates plus one newly solved draw are included. Full replay commands are above.
- Fixed-size moment precision: `results/integer-precision/`, claim C19; all saved witnesses, lattice checks, bounds and tiny exhaustive fixtures are included. Optional large-MILP replay is above.

All claim groups above use the same single entry point: run it once to check C01–C20 together. Their shared measured computational cost was 940.2 seconds in the observed environment, not an additional cost per claim. The individual files/rows and exact expected values are in claims.jsonl. The separate full subset replay covered all 115 units and 198,720 rows in 2433.6 summed worker seconds across bounded chunks. The five complete repeated-member blocks took 528.8 summed worker seconds. These are observed timings, not promises for another platform; environment setup and file inspection add time. The main reduced replay recomputes every saved aggregate, re-solves four subset units and draw0, and checks saved integer witnesses/fixtures; it does not newly solve every large time-limited MILP. Treat unexecuted stages as incomplete, not as passed.

## Inputs and optional network operations

The primary raw analysis inputs are the selected site temperatures bundled as lossless NPZ vectors. Per-member metadata retain the exact public index, GRIB field hashes, byte ranges, date/step/member checks and selected coordinates. Apart from the explicitly indexed offline decoder-validation fixtures in `data/extraction-validation/`, global temperature GRIB transport fields outside selected sites were not retained; outside-site values are not analyzed. A reviewer can recompute the paper without those global fields. The optional land-mask field is bundled in full; the city archive and fixed candidate/selected tables are bundled.

Fresh extraction from the public operational archive is **optional and not part of offline verification**. It needs network access and a separate writable research copy. The archive can change or become unavailable, so fresh hashes need not match; preserve differences rather than overwrite the submitted inputs. The submitted original unit-invocation limits and exhausted failures must not be reset in the source copy. Source licences/terms and retrieval dates are in `sources.jsonl` and the archived official pages.

There are **no AI API calls in verification**. Exactly one API generation was used for authorized topic-candidate critique; requests, responses, usage and cost calculations are bundled. The critique is not experimental data or peer review, and a new generation is unnecessary. Recomputing analyses from saved outputs does not require an API key. Consult the latest unique call record in `api_calls.jsonl` when tallying usage: intermediate status entries are not additional generations.

## Timeline and deviations

Topic selection was fixed in commit `16575cc53a173d9cca00b11a55b54246597f00de`; primary plan v1 was fixed in `f3e88ecc7fe6676a7dfce69662ee9829c65301db`, before main extraction. Apart from the preserved failed D002-identification-remaining record indexed in protocol/deviations.md, every experiment record identifies its plan path/commit, code commit, provided input hashes, command, start/end UTC times and exit status. Per-unit source/analysis hashes supplement those run records.

Inspect `git log`, `events.jsonl`, `protocol/` and each `experiments/*/record.json`. Technical transport revisions preserve the scientific calendar and retry caps. Subset, city/time, coverage and identification-mechanism extensions have their own prospective plans and are labelled exploratory. The initial failed gazetteer proposal, exhausted original acquisition and failed optional-mask logging run remain recorded. `protocol/deviations.md` indexes deviations and exploratory additions.

The manifest and intervention log record observed usage-limit resumptions, confirmed deadline extensions and pauses with unrecoverable final pre-stop clock readings; no estimated extensions are retained for the latter. The generated final report counts these records separately from administrative corrections. Session/model identifiers not visible to the author remain null/unknown. Git timestamps are self-reported; local history and SHA-256 lists support consistency and order inspection but do not prove absence of tampering or independence.

## Review-response additions

Plan v14 was fixed in a9fa8a471ef7a6f6ec19994511e65cff09546c59 before the new saved-data summary. Appendix L displays prespecified geometry × lead × product results; Appendix M contains post-review exploratory state-count and width/window diagnostics (C20). The single offline entry point regenerates and compares their three CSVs. First-draft copies remain in review/submission-1; REVIEW-1 is preserved literally, with pointwise decisions in review/response-1.md. The reviewer reports same-machine re-runs and a separate implementation; the author did not inspect sibling review files or call the reviewer.

The revised author replay completed at 2026-10-26T13:38:08Z in 940.2 seconds. It compared 459 CSVs with maximum absolute difference 0.0, including all three post-review CSVs. All 16,535 read-only source files retained their hashes, and the regenerated manuscript was byte-identical. This is an author re-run on the same machine, not independent reproduction.
