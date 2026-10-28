# Response to review-014-1

The original review is preserved verbatim in review/review-1.md. It is a review by an AI agent, arranged and reported by the human; the reviewer model/settings and its same-machine rerun are not directly observable by the author. The reported check is not described as independent reproduction. Author-side additions use only saved public data and are explicitly exploratory after review. No other AI was called for the response.

Review-response period began 2026-10-25T19:51:35Z; deadline 2026-10-25T21:51:35Z. The revised title is **Screening one-year tree-cover transitions in CONUS with annual satellite embeddings**. The abstract now has 246 whitespace-separated words, with 0 occurrences of readout terminology in the paper. Primary per-comparison changed-case counts are retained to satisfy the original trial instruction, using a compact defined order rather than the earlier horizon lists.

All 8 points have a decision: {"adopted": 5, "partly adopted": 3}. Main claim entries modified: C001, C002, C003, C005, C009, C012, C014, C017, C018. New entries: C019, C020. Claim status changes: 0; withdrawn: 0. Modified scopes preserve supported observed counts while narrowing interpretation; they are not silently recast as new primary hypotheses.

## R1-1 — adopted

Reason: Exact-fold diagnostics quantify the limited variation and near-identity of the compared scores. Their transferred J signs are not algebraically guaranteed, but the null is a weak test of correcting substantial harmful drift.

Use original region-excluded, separately-valid annual means, with same-membership comparison and every valid count. Include reference-only 2017–2023 spans. Main pooled changed-decision share is 1.5–9.2%, not a strict upper bound 9%; year-specific conditions can be larger. Physical change and representation drift are not separated.

Changes:

- paper.md Abstract and sections 3.5/4.2/4.3/6; Appendix E
- Table 1 AUROC; Table 2 correlations and changed decisions
- C001,C014,C018 scoped; newC019

Writing changes: 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6; saved-data analysis/code: 40fdcf0d9ce3b467abee309def61fd494869d263.

Experiments added: review-diagnostics-r1.

## R1-2 — partly adopted

Reason: The year concentration and sparse regional negatives must constrain interpretation. Two test pairs were actually evaluated; three positives in the second do not mean it was untested, but do not establish broad gain transfer.

State21of24gains in 2019–2020 and3in 2020–2021; conclusions chiefly describe the former. Anonymous region indices retain every small denominator rather than implying uniform geographic support.

Changes:

- paper.md title, Abstract, research question, sections 4.1/6
- All year/region denominators table
- ScopesC001–C003,C009,C017; newC020

Writing changes: 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6; saved-data analysis/code: 40fdcf0d9ce3b467abee309def61fd494869d263.

Experiments added: review-diagnostics-r1.

## R1-3 — partly adopted

Reason: The NLCD target detail is verified and added. Its weight0.5 describes the evaluated AEF v2.0 model; the same saved paper S8.3 and current official catalogue document production v2.1 adding CDL and reducing NLCD/CDL weights 0.25. The unofficial V1-labelled mosaic does not verify its exact encoder lineage. Also, release year is not mapped year: the official 2019_REL collection contains multiple epochs and Brown specifies nearest mapped-year assignment. A single static2019map for every2017–2020training sample is not established.

Do not assign v2.0 training settings or causal smoothing to the measured mosaic as established facts. NLCD annotations differ from map targets, but independence from training-target information is not established. Similar TESSERA patterns show the AEF-specific target is not necessary, without constituting a matched encoder ablation. This qualifies the reviewer’s static-map inference rather than asserting its mechanism. See sources/nlcd-release-year-clarification.json and the full official catalogue description/example; only scholarly metadata was consulted, with no new raster acquisition.

Changes:

- paper.md sections 3.2/5/6
- Scope qualifiersC003,C005,C009,C012,C017
- sources.jsonlS002extended-range/S038; sources/review-1-literature-checks.json
- sources.jsonlS002correction and S044; sources/nlcd-release-year-clarification.json

Writing changes: 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6.

Experiments added: none; documentation/presentation change.

## R1-4 — adopted

Reason: Absolute scores and the ranking inversion are more decision-relevant than correction differences alone; their scope must remain observational.

Original all-negative gain AUROC 0.287/0.318 differs from unchanged-only 0.339/0.352; report both definitions, not interchange them. Include weak AlphaEarth reference gains, stronger loss magnitude and negative Forest gainJ. No measured growth-rate/timing mechanism is claimed.

Changes:

- paper.md Abstract, sections 4.2/4.4/4.5/5
- Table 1 AUROC; per-year magnitude medians/AUROC versus unchanged negatives
- C003adds planned AUROC; C005/C012 scopes; newC020

Writing changes: 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6; saved-data analysis/code: 40fdcf0d9ce3b467abee309def61fd494869d263.

Experiments added: review-diagnostics-r1.

## R1-5 — partly adopted

Reason: Add every identified work with actual access range and established algorithm names. Full methods/results could not be verified for Manikandan, Yao or Stehman through the ordinary routes checked.

MDPI returned 429; Yao title/authors confirmed inCaGIS programme but extended abstract unavailable after exact-title/author/domain searches, so tau 0.15 and 15-site claims are not adopted as verified. Stehman official abstract is explicitly labelled abstract-only and is not proof of our timing mechanism. Malila classic repository abstract was checked; original empirical results were not adopted. Full LandTrendr/CCDC documentation was checked; neither algorithm was run.

Changes:

- paper.md section 2 and context discussion
- references.json and sources.jsonlS026/S039–S042
- sources/review-1-literature-checks.json

Writing changes: 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6.

Experiments added: none; documentation/presentation change.

## R1-6 — adopted

Reason: Reorganize the main text around sample support, absolute screening and the limited correction test, keeping every earlier result in files/appendices.

Remove native single-date and per-horizon Forest flag listings from abstract. Retain compact counts for each primary correction comparison because the original trial requires counts when conditions are near-identical. Eliminate readout terminology from rendered text; do not conflate FPR with commission error.

Changes:

- paper.md Abstract and sections 3.5/4; AppendicesD–F
- scripts/write_revision.py
- Main terminology: change score, classifier, alert threshold, sensitivity/producer accuracy andFPR

Writing changes: 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6.

Experiments added: none; documentation/presentation change.

## R1-7 — adopted

Reason: Tie importance to verifiable current embedding-change and restoration-trajectory workflows without claiming user effects or benchmarking an untested interface.

Official GoogleEarth docs describe annual 10m change layers and imagery verification; EarthEngine describes dot-product comparison. State intended selection for detailed assessment, with no measured human benefit. Our mosaic-derived scores are not the exact GoogleEarth product pipeline.

Changes:

- paper.md Introduction
- references.jsonS037/S038; sources/review-1-literature-checks.json

Writing changes: 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6.

Experiments added: none; documentation/presentation change.

## R1-8 — adopted

Reason: The small continental pool and annual valid counts are part of the tested construction and must delimit restoration-reference conclusions.

Report 116baseline plots, 58assigned to references / 58controls before region exclusions, and every fold/year valid count. No later stability filter or verified local ecological matching is implied.

Changes:

- paper.md sections 3.1/4.3/6 and Appendix E
- C001,C014 scopes; C019 expected valid counts

Writing changes: 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6; saved-data analysis/code: 40fdcf0d9ce3b467abee309def61fd494869d263.

Experiments added: review-diagnostics-r1.

## Verification and preserved records

The final numerical procedure adds review-diagnostics-r1 to the complete existing entry point; every original metric and all new CSV columns are compared. See review/self-rerun-4.json for the actual candidate, timing, source-integrity result and numerical-module coverage. The first-draft tag/submission snapshot and earlier self-reruns remain unchanged. VERIFY.md explains how to verify the revised and original versions. The response decisions are in review/response-points.json, and tool-counted tallies in review/review-response-summary.json.
