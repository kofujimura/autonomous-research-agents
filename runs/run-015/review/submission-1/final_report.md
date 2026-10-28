# Research report — free-research-015

Generated 2026-10-26T11:51:35Z. Stage: **first-draft**. Ending reason: Main study and prespecified checks completed with retained failures and unresolved endpoints. Clock-based closure left four exploratory city dates unattempted. Final self-check and offline author replay passed; prepare a locally frozen first draft for the planned review by an AI agent.

## Topic and measured scope

The study audits partial identification of spatial temperature-exceedance count-tail probabilities from individual, aggregate-second-moment and pairwise releases of operational ensemble data. The target is the retained empirical forecast law. Observed weather skill, public-health benefit, real service demand, human usability, adoption, actual traffic and realized economic value were not measured. No novelty of the probability LP, dependence loss, count sufficiency or exact mask is asserted.

This document is based on data and products of the European Centre for Medium-Range Weather Forecasts (ECMWF). © 2026 ECMWF. Data are used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and the recorded general terms. Location extraction, thresholding and analysis are modifications by this study; ECMWF has not endorsed them.

Primary coverage: 115 complete units of 116 scheduled, 28 fully matched dates, status `adequate_predeclared_date_count`.

| Stratum | Queries | q=0 | q=1 | ≤2 uncertain | Marginal width | Aggregate width | Pair width | Pair identified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 12096 | 3941 | 3469 | 5064 | 0.1407 | 0.0885 | 0.0142 | 9895 |
| informative | 2871 | 0 | 0 | 0 | 0.5139 | 0.3146 | 0.0547 | 1068 |

The exploratory city/time schedule contains 12 dates and 48 product/horizon combinations. It has 8 fully matched dates, 32 complete combinations and 128 complete raw fields; status `adequate_predeclared_date_count`. An adequate-date status does not mean every scheduled acquisition finished. Remaining combinations are listed in results/city-time/availability.json; all partial data and bounded failures are retained.

Primary results, prespecified sensitivities and exploratory subset/city/coverage/identification comparisons retain separate labels. Additional midpoint, common-query member and controlled-precision comparisons are exploratory. The English manuscript is generated from analysis outputs; `claims.jsonl` maps statements to evidence and expected checks. Consult their stated denominators and scope rather than treating every query as independent.

## Failures, incomplete matters and limitations

The original AIFS20260709/84h unit exhausted the fixed two-invocation cap, retaining 41 complete member vectors and remaining incomplete. Later overlapping coordinate extraction does not restore it to the primary sample. Technical transfer failures and all recoveries remain in per-unit logs. G002 optional IFS mask extraction failed on a relative-path log error after one HTTP request; its response outcome was lost, recorded as unknown and counted as a used attempt. G003 recovered without resetting the cap. The initially proposed city source was not downloaded after robots disallowed retrieval; Natural Earth was substituted and fixed before city data/weather extraction.

The selected question had two relevant closest full texts checked; a second full-text check for one unselected topic candidate remained inaccessible. This is an incomplete topic-selection check, not evidence that the missing literature does not exist. Selection took less than the skill’s 60-minute guide, with the reason recorded at selection. Public author/affiliation/contact metadata occur incidentally in archived scholarly sources and are not individual-level analytical variables or contact targets.

D002 completed a prefix of identification-diagnostic units before a numerical SVD failure. Its run command also named a nonexistent abbreviated plan path; an append-only correction identifies the actual previously committed v6 plan. D003 refused an attempted overwrite from a stale resume index. D004 resumed at the checked incomplete prefix with a documented gesvd fallback and unchanged scientific tolerances; all completed outputs and failures remain.

A later manual audit found that the exploratory paired all-land city rows reused the broader common-informative mask. The old table, summary and source are preserved in review/corrections/city-paired-land-before. The named conditional mask was repaired under protocol/analysis-correction-v1.md, and a separate audit now checks counts and mean differences directly from saved cases and the bundled land table. Main LP endpoints and the ordinary paired comparison were unaffected. Earlier code-consistency replays did not establish correctness of that filter.

The sampled calendar, locations, thresholds and exact finite ensembles limit generalization. LP extremal laws impose the released binary information, not an atmospheric dynamical model. Exact zero cells can strongly constrain compatibility. Resampling intervals describe a convenience calendar; sensitivity neighborhoods are not statistical confidence sets. City points are coarse snapped cartographic samples; the four-time maximum is not a continuous daily maximum or simultaneous peak load. No product/region ranking of observed forecast quality is established.

- `results/sensitivity/`: completed report; inspect denominators.
- `results/subsets/`: completed report; inspect denominators.
- `results/city-time/`: adequate_predeclared_date_count.
- `results/coverage/`: completed report; inspect denominators.
- `results/identification/`: completed report; inspect denominators.
- `results/midpoints/`: completed report; inspect denominators.
- `results/common-members/`: completed report; inspect denominators.
- `results/controlled-moments/`: completed report; inspect denominators.
- `results/overlap-recovery/`: checks_passed.
- `results/repeated-members/`: complete.
- `results/integer-precision/`: complete.

The exploratory known-size precision check recorded 120 queries: 94 with both endpoints optimal and 26 unresolved. At radius 0.005 all 120 retain exactly the original integer moment counts. At radius 0.02 the mean width over all cases is bounded by [0.3025, 0.3621]. These optimization bounds are not confidence limits or a measured rounding process.

The repeated-member check completed 100 of 100 fixed draws, status `complete`. It conditions on the same retained fifty-member forecasts and frozen sensitivity queries; draws do not add independent weather cases.


## Verification and records

The author ran `reduced` verification with status `passed` in a fresh copy in 935.5 seconds. It is an author re-run, not independent reproduction. The report and VERIFY.md distinguish all recomputed aggregates from the reduced subset and repeated-member LP re-solves; submitted integer witnesses, solver bounds and tiny exact fixtures are checked without claiming every large MILP was solved anew.

An earlier integrated replay (V012) failed on absolute source-path strings after its numerical solve phases. A root-relative report-reference repair was planned and recorded; the old source/output and failure remain. V013 passed an intermediate replay after the repair, and a separate final-state replay is required for submission. Source-file hashes are checked before and after each completed replay.

Plans, commit links, input hashes, raw selected vectors, stdout/stderr, failed/partial runs, source passages, deviations and the original API response are retained. Git times are self-reported; hashes support consistency rather than tamper-proofness or independence. SHA256SUMS and hash-scope.json state the finalized exclusions; the auxiliary review/verification-work-SHA256SUMS covers retained verification copies and raw replay outputs. Package environments/caches and author verification working copies count toward the storage limit even when excluded from Git.

## Interventions and observed usage

| Intervention type | Count |
| --- | --- |
| record_correction | 1 |
| runtime_resume | 7 |

Total intervention records (including author record corrections): 8. Permission requests/decisions: 0/0; unplanned scientific feedback: 0; peer review received: 0. There are 7 human resume confirmations; record corrections are administrative entries, not additional human messages. Exact human messages and observability limits are in interventions.jsonl. Confirmed excluded stop time totals 10265 seconds; 3 confirmed stops lack an exact prior tool clock reading and received no estimated extension. Current research deadline: 2026-10-26T12:24:40Z.

| Returned model | Purpose | Generations | Input | Cache-write input | Output | Reasoning within output | Web searches | Actual usage cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-6-astra | research-question skill step 6 candidate critique | 1 | 116195 | 6424 | 14327 | 9849 | 13 | 2.0244 |

Usage-computed actual API cost: **$2.02436**, remaining combined-period budget **$17.97564**. Cache-write tokens are part of input, reasoning tokens part of output; do not add them twice. Costs use the archived official price and caching pages, checked 25 October 2026 UTC, including web-search charges. No provider invoice was visible. Status checks of one response are not new generations. The copied skill explicitly exempts its one critique call from the pre-call maximum-cost check/output cap; actual cost is included. No other AI API generation or sub-agent was used for research work.

Recorded experiment runs: 141; statuses `{'completed': 120, 'failed': 21}`. Sum of recorded worker elapsed times is 53007.5 seconds, not CPU time or wall-clock research duration. The main experiment runner enforces at most two workers and 1800 seconds per run. Directory allocated size at the tool check: 6930740KiB; limit 10 GiB. Source and extension raw-unit counts: `{'weather': {'complete_forecast_units': 115, 'incomplete_attempted_units': 1, 'acquisition_invocations': 122}, 'weather-v4': {'complete_forecast_units': 128, 'incomplete_attempted_units': 0, 'acquisition_invocations': 134}}`. No new paid service/cloud route was added.

Session-model token usage/cost, exact runtime model/provider identifier, runtime build and marginal prices of existing session tools were not observable. The presented session model is GPT-6/Codex with provider OpenAI; the critic response identifier is separately confirmed from API output. Persistent-memory/profile existence is unknown and none was sought or used for topic selection. No private user files outside the authorized scope were investigated.

## Review response and end state

No planned review has yet been received. The first draft must be frozen after its submission until the human supplies REVIEW-1; this report is not a substitute review.

Main files: paper.md, claims.jsonl, VERIFY.md, README.md, final_report.md, protocol/, results/, review/, manifest.json, events.jsonl, interventions.jsonl, sources.jsonl, api_calls.jsonl, checkpoint.md, SHA256SUMS. Files absent at this stage remain incomplete. No external publication/contact has occurred.

Conversation session ID: None; continuation IDs: []. These are unknown/empty when not exposed; process/PTY session IDs are not substituted for conversation IDs. Preserve this conversation and the submitted Git tag/commit.

## Intervention record index

This table is generated from interventions.jsonl. Administrative corrections are not additional human messages.

| ID | Type | Observed UTC | Decision |
| --- | --- | --- | --- |
| I0001 | runtime_resume | 2026-10-25T22:13:57Z | Extend research deadline by 1359 seconds under original conditions |
| I0002 | runtime_resume | 2026-10-25T22:43:58Z | Confirmed usage-limit stop excluded from research period |
| I0003 | runtime_resume | 2026-10-26T01:20:09Z | Resume with existing deadline; unquantified stop not excluded |
| I0004 | runtime_resume | 2026-10-26T03:14:42Z | Exclude confirmed5180second usage-limit stop from research period |
| I0005 | runtime_resume | 2026-10-26T05:38:01Z | Confirmed usage-limit stop; extend first-draft deadline by 221 seconds. (superseded by I0006) |
| I0006 | record_correction | 2026-10-26T06:20:10Z | Supersede I0005 claimed221second extension; keep human confirmation of usage stop, take0extension. |
| I0007 | runtime_resume | 2026-10-26T08:35:47Z | Resume same study; conservatively retain existing deadline. |
| I0008 | runtime_resume | 2026-10-26T11:10:35Z | Exclude confirmed 3513-second usage-limit pause; resume same study. |
