# Response to review-016-1

Prepared from the human-supplied REVIEW-1, observed 2026-10-27T03:56:35.704364Z. This was a review by an AI agent, not human peer review or independent reproduction. The original review is unchanged in review/review-1.md; the first draft is tag submission-1 (faf7dce40c1a27313b4ae7fb51554fa5d061393b).

Revision code/document anchor commit: fd7bed21eb31d92677fae1e55fd174e4900ca819. Added-analysis plan/code commits and execution times are in experiments/E56-review-label-error/run.json and experiments/E57-review-summaries/run.json; their completed results were preserved in0f1fb39c263ef2915254cc9ebcb707d1be047d98. Planv15 was committed before either analysis. Final verification state: passed.

## R1-1: adopted

Point: “Add a sensitivity analysis of independent (and ... partly correlated) annual labelling error.”

Decision and reason: Added all planned error probabilities and three annual coupling settings using saved draws. Zero-error estimates, standard errors and directions match the originals bitwise. Independent errors largely remove the aggregate coverage deficit while increasing absolute point error; shared errors can preserve it. These are synthetic scenarios, not measured field rates, and retaining the original FPC is explicitly not a newly justified measurement-error interval.

Changes: paper.md Abstract, §3.4, §4.8 Table8, §5–6; claims C01,C02,C06,C12; scripts/review_label_error.py; results/review-label-error/. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: E56-review-label-error.

## R1-2: adopted

Point: “Revise the title ... Put the model-assisted point-accuracy result in the abstract.”

Decision and reason: Revised the title to Swiss declared crop groups and a resampling benchmark. The abstract and §4.2 state that the direct gain uses no satellite input, frozen logistic assistance gives no revisited point-accuracy gain at128, and forests improve it modestly. Standard post-stratification is identified as an untested comparator. The reviewer’s post-stratified computations are not presented as this study’s experiments.

Changes: paper.md title, Abstract, §4.2, §5; scripts/review_revision.py; original frozen logistic/forest tables. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: No additional fitting or estimator experiment.

## R1-3: adopted

Point: “Report the prespecified grassland/arable ratios ... Add a landscape-level resampling interval.”

Decision and reason: Table2 now includes all budgets for the preplanned grassland/arable subsets. Added whole-landscape resampling of the original cohort and the higher-replication additional arable cohort. §4.8 reports ratio and coverage ranges, explicitly as within-cohort composition sensitivity, not national uncertainty. Both broad and fine additional-arable ratio ranges include1; C10 is now an observed ratio with unresolved landscape variation.

Changes: paper.md Abstract, §4.2 Table2, §4.8; claims C10,C13; results/review-summaries/landscape-resampling.csv; scripts/review_summaries.py. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: E57-review-summaries.

## R1-4: partly adopted

Point: “Add the conditional wrong-direction share ... state that no tested budget ... reached the no-change RMSE.”

Decision and reason: Added actual wrong/report counts, tiny/non-tiny strata, coverage minimum/percentiles/countbelow90%, and per-unit baseline comparisons early in §4.1. Added the longer2022→2025 direct contrast against its own no-change baseline. The no-change statement is restricted to direct sampling: the reviewer’s broader wording would be false because both revisited frozen forests beat no change at512labels/year. The exceptions are explicitly reported from the original outputs; no original numeric claim was contradicted.

Changes: paper.md Abstract, §4.1, AppendixE TableE1; results/review-summaries/decision-context.csv, all-budget-point-baselines.csv, long-contrast.csv. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: E57-review-summaries.

## R1-5: partly adopted

Point: “The preplanned interval rule ... omitted the derivative ... with the derivative ... behave like the direct ones.”

Decision and reason: Adopted the omitted-derivative diagnosis and plainly qualified C04 as a property of the original interval calculation. The original preplanned result and corrected exploratory calculation remain. Did not equate the corrected intervals with revisited direct coverage: corrected assisted coverage is close to independent direct coverage, whereas revisited direct coverage is substantially lower. Approximate local derivatives still do not prove coverage at changing support.

Changes: paper.md Abstract, §3.3, §4.6, §5; claims C04,C11; original projection-derivative outputs. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: No new experiment; interpretation of retained original/exploratory outputs.

## R1-6: partly adopted

Point: “Add these works ... classic successive-occasion theory ... current practice.”

Decision and reason: Added checked full-passage context for Jessen, Brown–Cai–DasGupta’s author preprint, operational LUCAS/NASS/ALL-EMA, Lu et al.version7 and van der Velde et al. The latter’s relevant full article sections were available in the indexed publisher body; direct DOI access was blocked and was not bypassed. The expected direction is explicitly attributed to classic sampling. Patterson, Basharin, Hutcheson and Cochran are retained as bibliographic leads only because relevant full text was not obtained; original instruction§8 prohibits using such leads as supporting evidence. Publisher/metadata searches and access limitations are saved, rather than implying those works were read.

Changes: paper.md §1–2 and References; sources.jsonl; sources/review-prior-access-*.json and checked PDFs. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: Literature check only; no scientific experiment.

## R1-7: partly adopted

Point: “Restructure the abstract ... move the case counts ... give ... percentage change in effective number.”

Decision and reason: Reworked the abstract around the preplanned design, accuracy and reporting outcomes with subsequent exploratory qualifications. Added actual RMS percentage error of the estimated effective-number ratio from every saved trial, rather than exponentiating entropy RMSE and calling it percentage RMSE. This new descriptive transformation is explicitly exploratory. Kept a compact tiny/zero/unchanged case count in the abstract because the original trial instruction§10 requires trivial-case counts there; other case details remain in results. Readers’ monitoring decision is stated near the beginning.

Changes: paper.md Abstract, §1, §3.4, §4.1; results/review-summaries/effective-group-errors.csv; scripts/review_revision.py. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: E57-review-summaries.

## R1-8: adopted

Point: “Add one paragraph naming the intended operational settings ... corresponding unit of a reference label.”

Decision and reason: Added map-based monitoring without complete declarations and independent photo/field checks as possible applications. Defined a label as one point-year classification in that setting, and distinguished the actual10m database reading and supplied finite frame from parcels, visits, clustering, real interpretation errors and frame/travel costs. Complete trustworthy declarations need no sample to calculate this target.

Changes: paper.md §1, §3.1, §5–6; manuscript/template.md. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: No new experiment.

## R1-9: adopted

Point: “Correct the tag name in VERIFY.md.”

Decision and reason: VERIFY.md now gives explicit submission-1 and final checkout instructions. Original first-draft hash/event receipts remain preserved; the reviewed-final inventory is regenerated separately. Terminal commit/submission events use the documented prefix rule, not an implied self-referential whole-file hash.

Changes: VERIFY.md; README.md; SHA256SUMS.json; final tag and terminal receipt in events.jsonl. Revision anchor: fd7bed21eb31d92677fae1e55fd174e4900ca819.

Added experiments: Final full offline self-rerun.

## Tally

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
