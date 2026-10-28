# Research report

Observed at 2026-10-27T03:56:35.779988Z. Final revised submission; see review/response-1.md or the recorded no-review decision.

## Study and attained scope

Title: Revisiting reference locations for changes in Swiss declared crop-group diversity: a resampling benchmark.

Question: At a fixed annual reference-label budget, how reliably do estimates using frozen annual-embedding classifiers identify changes in declared crop-group diversity, and does revisiting improve inference relative to independent samples?

The original cohort contains 20 training, 10 calibration and 30 test landscapes; three target-year transitions and 500 Monte Carlo trials per condition. Main results concern 17 published agricultural groups; 54 groups are a prespecified check. Methods, source input sizes and label burden are in paper.md and its generated tables. Labels measure declared intent rather than independently observed harvest.

Prespecified finer taxonomy, forest, secondary years, native-grid and reference-error checks are complete. Refreshed-head comparison complete: True. Added geographical reference-only comparison complete: True. Exploratory strata, weighting, jackknife, entropy envelopes, gradient floors and coherent panels retain all original results.

## Confirmed numerical results

- C01: Revisiting lowers direct broad-group change MSE relative to independent annual samples across the five prespecified budgets. Expected values: `{"minimum_ratio": 0.26672848977312164, "maximum_ratio": 0.2779824094721747}`. Scope and reproduction: claims.jsonl.

- C02: At n=128 the direct revisited intervals have lower aggregate coverage than independent-sample intervals on the main agricultural cohort. Expected values: `{"paired_coverage": 0.8342444444444445, "independent_coverage": 0.9309333333333333, "tiny_changes": 35, "zero_changes": 4, "entropy_floor_cases": 0}`. Scope and reproduction: claims.jsonl.

- C03: The no-change point baseline beats n=128 direct and frozen-model-assisted broad estimates in squared error on this cohort. Expected values: `{"no_change_rmse": 0.026049685443117764, "direct_revisited_rmse": 0.055890465394763354}`. Scope and reproduction: claims.jsonl.

- C04: The original soft-logistic assisted interval rule, which omitted the projection derivative, gives overly conservative aggregate coverage and rarely reports directions. Expected values: `{"coverage_range": [0.9879777777777777, 0.9913555555555555], "report_range": [0.011444444444444445, 0.014444444444444444], "projection_range": [0.9876, 0.9912222222222222]}`. Scope and reproduction: claims.jsonl.

- C05: The aggregate coverage gap is much smaller on the exploratory complete stable-arable reference frame. Expected values: `{"landscapes": 25, "primary_transitions": 75, "paired_coverage": 0.9306666666666666, "independent_coverage": 0.9308266666666667}`. Scope and reproduction: claims.jsonl.

- C06: Revisited draws with no changed labels account for a substantial portion of direct interval misses; the exploratory conservative interval union does not restore nominal coverage. Expected values: `{"zero_observed_change_fraction": 0.1292, "miss_fraction_with_zero_changes": 0.5480627429950397, "units_with_exact_ceiling_below_0_95": 12, "guarded_coverage": 0.9250888888888888}`. Scope and reproduction: claims.jsonl.

- C07: Changing only the numerical entropy-gradient floor changes soft-assisted interval coverage and reporting while preserving point estimates exactly. Expected values: `{"broad_tessera_revisited_floor_0_01_coverage": 0.9366666666666666, "floor_1e_minus10_coverage": 0.9951555555555556, "report_rate_floor_0_01": 0.08344444444444445, "report_rate_floor_1e_minus10": 0.005755555555555555, "rmse_identical": 0.060533015178934016}`. Scope and reproduction: claims.jsonl.

- C08: A coherent half-retained panel has intermediate direct precision and higher simultaneous coverage than the full-revisit panel in this benchmark, without reaching nominal95% joint coverage. Expected values: `{"full_revisit_joint_coverage_bonferroni": 0.7780666666666667, "half_retained_joint_coverage_bonferroni": 0.9239333333333334, "half_retained_rmse": 0.08636076727658054, "full_revisit_rmse": 0.05624504742405229}`. Scope and reproduction: claims.jsonl.

- C09: The prospective native-grid case check exposes differences between sampled-point and whole-population reference changes. Expected values: `{"cases": 3, "transitions": 9, "sign_disagreements": 2, "change_discrepancy_rmse": 0.008518667804907641}`. Scope and reproduction: claims.jsonl.

- C10: The additional stable-arable cohort has an observed broad MSE ratio above 1 and fine ratio below 1; both landscape-resampling ranges include 1. Expected values: `{"landscapes": 6, "contrasts": 18, "broad_mse_ratio_n128": 1.0740138695445287, "broad_ratio_mcse": 0.021117453404207294, "fine_mse_ratio_n128": 0.940626318246262, "negative_broad_influence_covariance_units": 12, "linearized_variance_ratio": 1.0770164477007351, "high_replication_broad_ratio": 1.0659482514047205, "high_replication_broad_mcse": 0.006409961427491315, "high_replication_fine_ratio": 0.9130515288696791, "broad_landscape_resampling_range": [0.964833858974568, 1.19691222314428], "fine_landscape_resampling_range": [0.7945440723948336, 1.0296162333942251]}`. Scope and reproduction: claims.jsonl.

- C11: Applying the local projection derivative changes soft-assisted interval coverage and reporting while preserving all point estimates. Expected values: `{"paired_coverage_range": [0.9358222222222222, 0.9372], "paired_reporting_range": [0.08013333333333333, 0.08202222222222222], "point_estimates_identical": true}`. Scope and reproduction: claims.jsonl.

- C12: Synthetic independent annual label error reduces the revisited interval coverage deficit while worsening its point accuracy. Expected values: `{"error_0_01_paired_coverage": 0.9168222222222222, "error_0_01_mse_ratio": 0.3096617791958573, "error_0_05_paired_coverage": 0.9250444444444444, "error_0_05_mse_ratio": 0.42910459184753397}`. Scope and reproduction: claims.jsonl.

- C13: Landscape composition sensitivity is wider than Monte Carlo precision of the original fixed-cohort MSE ratio. Expected values: `{"n128_ratio": 0.27514443301948255, "within_cohort_95_percentile_range": [0.20745669002487588, 0.3568010833035102]}`. Scope and reproduction: claims.jsonl.

Magnitude coverage and wrong-direction reporting are different outcomes. In the original n128 direct comparison, revisiting gives more reports and fewer wrong directions in aggregate despite lower magnitude-interval coverage. A no-change point baseline is not evidence that an individual landscape did not change.

## Limits, failures and unfinished work

No representative national estimate, field-visit cost, user outcome, policy effect, ecological effect or independent harvest validation was measured. Source training/calibration and five-year eligibility information are outside audit-label counts. Reference frames, model releases, taxonomy, numerical gradient, conditional fitted maps and the selected period bound every claim.

Initial source fits reaching their iteration limit: 3/4; all revised source heads were fixed before target outcomes. Failed bounded run count: 2. Label-attempt statuses: `{"failed": 3, "accepted": 60, "ineligible": 25}`. Feature-attempt statuses: `{"completed": 520}`. Per-case and pilot failure records remain in their ledgers/directories; batch exit0 is not universal candidate success.

One recorded short unwrapped diagnostic briefly exceeded the two-experiment limit and lacked a configured runner timeout; it exited normally and its record is retained. One paper-formatting run recorded a stale code commit because the commit was still finishing; the correction identifies its actual later code snapshot and a committed-code rerun. The runner now checks committed scripts/plans and stores script hashes.

Automatic Git packing occurred between checkpoints. Temporary peak unknown; possible transient ceiling breach cannot be ruled out. Current counts do not establish continuous compliance. See review/git-packing-storage-observation.json. Subsequent study commits disable automatic maintenance with per-command options, without global configuration changes or history rewriting.

The refreshed diagnostic is complete; its extra training labels are explicitly not budget-matched to small audits.

Additional-geography results are retained separately and exploratory.

## Verification

- review/verification-final.json: passed; 795.986s; CSV checks 88+102; raw-array files 1530+3382; valid as final submission check: True.

- review/verification-preliminary-1.json: passed; 606.798s; CSV checks 72+51; raw-array files 1230+2337; valid as final submission check: False.

- review/verification-review-initial.json: passed; 803.254s; CSV checks 88+102; raw-array files 1530+3382; valid as final submission check: True.

- review/verification-submission-1.json: passed; 775.332s; CSV checks 88+93; raw-array files 1530+3291; valid as final submission check: True.

These are reruns by this same session. Immutable input sharing and post-comparison exact-array sharing preserve all scientific arrays while reducing duplicate storage; neither constitutes independent reproduction. VERIFY.md is the single procedure. A full final check must reject still-running experiments.

## Interventions and observable usage

Human intervention records by type: `{"runtime_resume": 3, "peer_review": 1}`. No unplanned human research advice is inferred. Planned AI-agent review received: True.

- I0001: runtime_resume, observed 2026-10-26T21:12:10Z; decision `resume; exclude confirmed usage-limit interval under initial instructions`; effect `Research deadline extended by tool-computed1372seconds; no other conditions changed`. Message identifiers/approver details are not invented when unobservable.

- I-runtime-resume-2: runtime_resume, observed 2026-10-26T23:36:53Z; decision `Confirmed usage-limit pause excluded from elapsed research time`; effect `Deadline extended; no experiments running during this interval.`. Message identifiers/approver details are not invented when unobservable.

- I-runtime-resume-3: runtime_resume, observed 2026-10-27T02:13:33Z; decision `Exclude confirmed usage-limit pause under original trial rule`; effect `Deadline extended; E55 completed successfully during the pause. No review received.`. Message identifiers/approver details are not invented when unobservable.

- I-review-016-1: peer_review, observed 2026-10-27T02:50:07Z; decision `Evaluate each of nine points; no automatic acceptance of interpretation`; effect `Begin review response with deadline 2026-10-27T04:50:07Z`. Message identifiers/approver details are not invented when unobservable.

Unique AI API generations: 1. Tariff-derived actual cost: USD 1.943910 of the USD 20 total budget. Status retrievals and ledger corrections are not additional generations. Outside the mandatory candidate critique and human-supplied AI-agent review, this session called no other AI. Reviewer-only analyses were not taken as this study’s experimental data. No numerical verification step calls an API.

| Model returned | Purpose | Input tokens | Cached read | Cache write | Output incl. reasoning | Reasoning subset | Web calls | Actual USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-6-astra | Required candidate critique, skill step 6 | 116436 | 0 | 6420 | 12670 | 7760 | 13 | 1.943910 |

Prices and check dates are in api_calls.jsonl, sources/openai-pricing.md and the prompt-caching documentation. The actual tally includes the cache-write premium and web searches; the original estimate/correction is retained. Reasoning tokens are a subset of billed output. Provider invoices and this session model's own token usage/billing are not exposed. No figures are guessed for them.

Confirmed usage-limit exclusion: 7007.086862 seconds. The second exclusion has a documented endpoint uncertainty; see manifest.json. Research elapsed time as of this report: 35375.121 seconds; the pre-review waiting interval is excluded once submission/receipt events exist. Current deadline: 2026-10-27T04:31:56.086862Z. Session identifier: None; continuation IDs: `[]`.

Storage at tally time: 10401610674 unique-inode payload bytes; 29479079833 logical path bytes including hardlink aliases. All unique payload is inside the research directory; dependencies/caches/Git are included. This is a point observation, not a measured high-water mark.

## Outputs and ending state

Main files: paper.md, claims.jsonl, VERIFY.md, README.md, DATA_LICENSES.md, manifest.json, protocol/, experiments/, results/, sources.jsonl, review/self-check.md, review/ verification records and the submission SHA-256 manifest. Initial instructions/skill copies are unchanged. Each completed stage and failed attempt remains referable; missing future-stage files are not marked complete.

Final revised submission; see review/response-1.md or the recorded no-review decision. The submitted commit/tag and terminal submission time are recorded in events.jsonl and reported to the conversation. No external publication or contact was made. Tallies are as of the report timestamp; subsequent terminal commit receipts are append-only bookkeeping.

## Review response

```json
{
  "observed_at_utc": "2026-10-27T03:56:35.704364Z",
  "review_id": "review-016-1",
  "points": 9,
  "decisions": {
    "R1-1": "adopted",
    "R1-2": "adopted",
    "R1-3": "adopted",
    "R1-4": "partly adopted",
    "R1-5": "partly adopted",
    "R1-6": "partly adopted",
    "R1-7": "partly adopted",
    "R1-8": "adopted",
    "R1-9": "adopted"
  },
  "decision_counts": {
    "adopted": 5,
    "partly adopted": 4
  },
  "claims_changed": [
    "C01",
    "C02",
    "C04",
    "C06",
    "C10"
  ],
  "claim_status_changes": [],
  "claims_withdrawn": [],
  "claims_added": [
    "C12",
    "C13"
  ],
  "analyses_added": [
    "E56-review-label-error",
    "E57-review-summaries"
  ],
  "new_statistical_analyses": 2,
  "revision_code_commit": "fd7bed21eb31d92677fae1e55fd174e4900ca819",
  "review_directly_observed": false,
  "review_observability": "Human supplied AI-agent review; reviewer model/runtime and reviewer calculations are not directly observed by this research session.",
  "verification_status": "passed",
  "verified_source_commit": "fd7bed21eb31d92677fae1e55fd174e4900ca819",
  "verification_elapsed_seconds": 795.9858575840481
}
```

One review by an AI agent was supplied by the human. The review reports a clean fresh-environment rerun; this is recorded as the reviewer’s report, not a verification directly observed by this session. Additional exploratory label-error and within-cohort resampling analyses used no other AI and no new API calls. Review-response start and deadline: 2026-10-27T02:50:07Z; 2026-10-27T04:50:07Z.

The intermediate post-review full check in review/verification-review-initial.json applies to its earlier aa05 snapshot and is not used to seal the final wording. The final full check is review/verification-final.json, source fd7bed21eb31d92677fae1e55fd174e4900ca819. Both originals are retained.

Review-response elapsed time at 2026-10-27T03:57:47.994580Z: 4060.995seconds; confirmed review-period usage-limit exclusions:0. New statistical analyses: 2; additional runner records (including rendering and verification): 7 (E56-review-label-error, E57-review-summaries, E58-review-render, E59-review-render-final, E60-reviewed-final-full-verification, E61-review-readable-render, E62-reviewed-final-verification-v2). Claims qualified: 5; status changes: 0; withdrawn: 0; added exploratory claims: 2.

Reason for ending: the planned study and single review response are complete, with all review points disposed and the final offline self-rerun passed. Real field/interpretation error rates, audit costs, realised harvest validity and population-wide external validity remain unmeasured limitations. No study experiment process remains active. No external publication or contact occurred.
