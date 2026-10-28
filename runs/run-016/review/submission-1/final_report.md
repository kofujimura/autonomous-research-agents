# Research report

Observed at 2026-10-27T02:14:58.841111Z. First-draft snapshot prepared for the planned review by an AI agent; no review result has been received.

## Study and attained scope

Title: Repeated reference locations for estimating changes in crop diversity from annual satellite embeddings.

Question: At a fixed annual reference-label budget, how reliably do estimates using frozen annual-embedding classifiers identify changes in declared crop-group diversity, and does revisiting improve inference relative to independent samples?

The original cohort contains 20 training, 10 calibration and 30 test landscapes; three target-year transitions and 500 Monte Carlo trials per condition. Main results concern 17 published agricultural groups; 54 groups are a prespecified check. Methods, source input sizes and label burden are in paper.md and its generated tables. Labels measure declared intent rather than independently observed harvest.

Prespecified finer taxonomy, forest, secondary years, native-grid and reference-error checks are complete. Refreshed-head comparison complete: True. Added geographical reference-only comparison complete: True. Exploratory strata, weighting, jackknife, entropy envelopes, gradient floors and coherent panels retain all original results.

## Confirmed numerical results

- C01: Revisiting lowers direct broad-group change MSE relative to independent annual samples across the five prespecified budgets. Expected values: `{"minimum_ratio": 0.26672848977312164, "maximum_ratio": 0.2779824094721747}`. Scope and reproduction: claims.jsonl.

- C02: At n=128 the direct revisited intervals have lower aggregate coverage than independent-sample intervals on the main agricultural cohort. Expected values: `{"paired_coverage": 0.8342444444444445, "independent_coverage": 0.9309333333333333, "tiny_changes": 35, "zero_changes": 4, "entropy_floor_cases": 0}`. Scope and reproduction: claims.jsonl.

- C03: The no-change point baseline beats n=128 direct and frozen-model-assisted broad estimates in squared error on this cohort. Expected values: `{"no_change_rmse": 0.026049685443117764, "direct_revisited_rmse": 0.055890465394763354}`. Scope and reproduction: claims.jsonl.

- C04: Original soft-logistic assisted intervals are conservative in aggregate and rarely report directions, with very frequent simplex projection. Expected values: `{"coverage_range": [0.9879777777777777, 0.9913555555555555], "report_range": [0.011444444444444445, 0.014444444444444444], "projection_range": [0.9876, 0.9912222222222222]}`. Scope and reproduction: claims.jsonl.

- C05: The aggregate coverage gap is much smaller on the exploratory complete stable-arable reference frame. Expected values: `{"landscapes": 25, "primary_transitions": 75, "paired_coverage": 0.9306666666666666, "independent_coverage": 0.9308266666666667}`. Scope and reproduction: claims.jsonl.

- C06: Revisited draws with no changed labels account for a substantial portion of direct interval misses; the exploratory conservative interval union does not restore nominal coverage. Expected values: `{"zero_observed_change_fraction": 0.1292, "miss_fraction_with_zero_changes": 0.5480627429950397, "units_with_exact_ceiling_below_0_95": 12, "guarded_coverage": 0.9250888888888888}`. Scope and reproduction: claims.jsonl.

- C07: Changing only the numerical entropy-gradient floor changes soft-assisted interval coverage and reporting while preserving point estimates exactly. Expected values: `{"broad_tessera_revisited_floor_0_01_coverage": 0.9366666666666666, "floor_1e_minus10_coverage": 0.9951555555555556, "report_rate_floor_0_01": 0.08344444444444445, "report_rate_floor_1e_minus10": 0.005755555555555555, "rmse_identical": 0.060533015178934016}`. Scope and reproduction: claims.jsonl.

- C08: A coherent half-retained panel has intermediate direct precision and higher simultaneous coverage than the full-revisit panel in this benchmark, without reaching nominal95% joint coverage. Expected values: `{"full_revisit_joint_coverage_bonferroni": 0.7780666666666667, "half_retained_joint_coverage_bonferroni": 0.9239333333333334, "half_retained_rmse": 0.08636076727658054, "full_revisit_rmse": 0.05624504742405229}`. Scope and reproduction: claims.jsonl.

- C09: The prospective native-grid case check exposes differences between sampled-point and whole-population reference changes. Expected values: `{"cases": 3, "transitions": 9, "sign_disagreements": 2, "change_discrepancy_rmse": 0.008518667804907641}`. Scope and reproduction: claims.jsonl.

- C10: The additional stable-arable broad-group subset has observed revisited MSE above independent MSE, while its finer hierarchy retains a modest gain. Expected values: `{"landscapes": 6, "contrasts": 18, "broad_mse_ratio_n128": 1.0740138695445287, "broad_ratio_mcse": 0.021117453404207294, "fine_mse_ratio_n128": 0.940626318246262, "negative_broad_influence_covariance_units": 12, "linearized_variance_ratio": 1.0770164477007351, "high_replication_broad_ratio": 1.0659482514047205, "high_replication_broad_mcse": 0.006409961427491315, "high_replication_fine_ratio": 0.9130515288696791}`. Scope and reproduction: claims.jsonl.

- C11: Applying the local projection derivative changes soft-assisted interval coverage and reporting while preserving all point estimates. Expected values: `{"paired_coverage_range": [0.9358222222222222, 0.9372], "paired_reporting_range": [0.08013333333333333, 0.08202222222222222], "point_estimates_identical": true}`. Scope and reproduction: claims.jsonl.

Magnitude coverage and wrong-direction reporting are different outcomes. In the original n128 direct comparison, revisiting gives more reports and fewer wrong directions in aggregate despite lower magnitude-interval coverage. A no-change point baseline is not evidence that an individual landscape did not change.

## Limits, failures and unfinished work

No representative national estimate, field-visit cost, user outcome, policy effect, ecological effect or independent harvest validation was measured. Source training/calibration and five-year eligibility information are outside audit-label counts. Reference frames, model releases, taxonomy, numerical gradient, conditional fitted maps and the selected period bound every claim.

Initial source fits reaching their iteration limit: 3/4; all revised source heads were fixed before target outcomes. Failed bounded run count: 2. Label-attempt statuses: `{"failed": 3, "accepted": 60, "ineligible": 25}`. Feature-attempt statuses: `{"completed": 520}`. Per-case and pilot failure records remain in their ledgers/directories; batch exit0 is not universal candidate success.

One recorded short unwrapped diagnostic briefly exceeded the two-experiment limit and lacked a configured runner timeout; it exited normally and its record is retained. One paper-formatting run recorded a stale code commit because the commit was still finishing; the correction identifies its actual later code snapshot and a committed-code rerun. The runner now checks committed scripts/plans and stores script hashes.

Automatic Git packing occurred between checkpoints. Temporary peak unknown; possible transient ceiling breach cannot be ruled out. Current counts do not establish continuous compliance. See review/git-packing-storage-observation.json. Subsequent study commits disable automatic maintenance with per-command options, without global configuration changes or history rewriting.

The refreshed diagnostic is complete; its extra training labels are explicitly not budget-matched to small audits.

Additional-geography results are retained separately and exploratory.

## Verification

- review/verification-preliminary-1.json: passed; 606.798s; CSV checks 72+51; raw-array files 1230+2337; valid as final submission check: False.

- review/verification-submission-1.json: passed; 775.332s; CSV checks 88+93; raw-array files 1530+3291; valid as final submission check: True.

These are reruns by this same session. Immutable input sharing and post-comparison exact-array sharing preserve all scientific arrays while reducing duplicate storage; neither constitutes independent reproduction. VERIFY.md is the single procedure. A full final check must reject still-running experiments.

## Interventions and observable usage

Human intervention records by type: `{"runtime_resume": 3}`. No unplanned human research advice is inferred. Planned AI-agent review received: False.

- I0001: runtime_resume, observed 2026-10-26T21:12:10Z; decision `resume; exclude confirmed usage-limit interval under initial instructions`; effect `Research deadline extended by tool-computed1372seconds; no other conditions changed`. Message identifiers/approver details are not invented when unobservable.

- I-runtime-resume-2: runtime_resume, observed 2026-10-26T23:36:53Z; decision `Confirmed usage-limit pause excluded from elapsed research time`; effect `Deadline extended; no experiments running during this interval.`. Message identifiers/approver details are not invented when unobservable.

- I-runtime-resume-3: runtime_resume, observed 2026-10-27T02:13:33Z; decision `Exclude confirmed usage-limit pause under original trial rule`; effect `Deadline extended; E55 completed successfully during the pause. No review received.`. Message identifiers/approver details are not invented when unobservable.

Unique AI API generations: 1. Tariff-derived actual cost: USD 1.943910 of the USD 20 total budget. Status retrievals and ledger corrections are not additional generations. No other AI performed research work. No numerical verification step calls an API.

| Model returned | Purpose | Input tokens | Cached read | Cache write | Output incl. reasoning | Reasoning subset | Web calls | Actual USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-6-astra | Required candidate critique, skill step 6 | 116436 | 0 | 6420 | 12670 | 7760 | 13 | 1.943910 |

Prices and check dates are in api_calls.jsonl, sources/openai-pricing.md and the prompt-caching documentation. The actual tally includes the cache-write premium and web searches; the original estimate/correction is retained. Reasoning tokens are a subset of billed output. Provider invoices and this session model's own token usage/billing are not exposed. No figures are guessed for them.

Confirmed usage-limit exclusion: 7007.086862 seconds. The second exclusion has a documented endpoint uncertainty; see manifest.json. Research elapsed time as of this report: 34982.754 seconds; the pre-review waiting interval is excluded once submission/receipt events exist. Current deadline: 2026-10-27T04:31:56.086862Z. Session identifier: None; continuation IDs: `[]`.

Storage at tally time: 10284108826 unique-inode payload bytes; 19321097269 logical path bytes including hardlink aliases. All unique payload is inside the research directory; dependencies/caches/Git are included. This is a point observation, not a measured high-water mark.

## Outputs and ending state

Main files: paper.md, claims.jsonl, VERIFY.md, README.md, DATA_LICENSES.md, manifest.json, protocol/, experiments/, results/, sources.jsonl, review/self-check.md, review/ verification records and the submission SHA-256 manifest. Initial instructions/skill copies are unchanged. Each completed stage and failed attempt remains referable; missing future-stage files are not marked complete.

First-draft snapshot prepared for the planned review by an AI agent; no review result has been received. The submitted commit/tag and terminal submission time are recorded in events.jsonl and reported to the conversation. No external publication or contact was made. Tallies are as of the report timestamp; subsequent terminal commit receipts are append-only bookkeeping.


## Final scope and ending note

The original label-attempt tally above covers data/selection-results.jsonl. The separate additional ledger data/validation-selection-results.jsonl contains 18 attempt records: `{"accepted": 8, "ineligible": 9, "failed": 1}`; latest distinct-candidate statuses: `{"accepted": 8, "ineligible": 9, "failed": 1}`. These counts are also appended to results/study-tallies.json and do not change scientific results.

Reason for ending this research phase: the planned study and related geographic, mechanism, classifier-control and Monte Carlo-precision checks are complete, the final full offline self-rerun passed, and the first draft is ready for the required review by an AI agent. The study was deepened after the original planned experiments finished with more than two hours remaining. No new scientific experiment is needed for this submission; external-validity and nonregular-inference limitations remain explicit. Ending is not attributed to exhausting the deadline.

The final full verification completed during the third human-confirmed usage-limit pause. Both endpoints of that pause are directly visible; manifest.json records the adjusted deadline and the experiment that continued. The earlier second-pause endpoint uncertainty remains disclosed. Submission copies, inventory checks and terminal Git receipts follow this report; tallies are as of their stated times.
