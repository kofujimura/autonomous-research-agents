# Value to readers (review-017-1)

This file was written after reading the paper and records and after my read-only recomputations from the submitted analysis files, but while the full offline re-run (verify.py) was still running; its outcome is appended at the end with a time stamp. This is my self-report as a reviewer, not a measurement of any change in readers' behaviour.

## Comparison with my prior expectation (prior_expectation.md, saved 2026-10-27T12:06:32Z)

| Prior expectation | Result in the study | As expected? |
| --- | --- | --- |
| Patch-first allocation gives a small positive gain in small-patch recovery (few pp) | Within-project gains are positive for embeddings in all four fixed splits (12.8, 9.1, 1.8, 7.9 pp) and for optical in the pooled splits (+3.9 pp); pooled embeddings +8.4 pp | Direction as expected; magnitude for embeddings larger than I expected |
| Interaction with predictor type small/unclear | Original split 11.6 pp (larger than I expected); but the three new splits give 4.7, −0.4, 1.2 pp, pooled 4.5 [0.3, 8.3]; whole-region transfer ~0.9 pp; other planned operating points/definitions 3.5–7.0 pp (one larger, 15.5 at ≥75% coverage) | Overall evidence is close to my expectation (small, split-dependent); the headline differs from it |
| Image-derived allocation recovers little of the oracle gain | Optical-teacher proposals: none (−0.2 pp); embedding-guided uncertainty: +5.4 pp (exploratory) | Partly as expected; the embedding-uncertainty partial recovery is better than I expected |
| Large geographic heterogeneity | Vermont 14.9% vs Prairie Pothole 71.8% embedding recovery; threshold transfer between projects gives achieved FPR 0.1–15% | As expected |
| (not anticipated) | At any-overlap coverage optical predictors detect more small patches than embeddings at the same FPR (pooled splits 71.5–76.1% vs 62.4–71.4%), while embeddings cover detected patches more fully (≥50% coverage) — reviewer-computed from saved scores, not reported in the paper | Not expected; potentially informative |

Why the differences: the original split appears to be a favourable draw for the embedding-specific interaction (optical gain only +1.2 pp there, versus +2.2 to +6.7 pp in the other splits). The paper discloses the rotations but leads with the original split.

## Which understanding or judgment could change, supporting claims, and trust

1. "Pooled pixel accuracy/IoU can stay flat while small-patch recovery changes by >10 pp" (C10, descriptive; Table 2 text). Readers who compare training designs or representations using only pixel/area metrics could change their evaluation practice. Trust: high for the observed means (recomputed from saved scores; verification outcome below); it is descriptive, for these projects.
2. "Within an inventory project, sampling training positives polygon-first rather than pixel-uniformly can raise small-patch recovery at a fixed FPR" (C01, C06, C09). Trust: moderate for the within-project direction for embeddings (all four splits positive) and for both predictors pooled; low for the size of the embedding-specific advantage (split-dependent). Not established for new regions (C04).
3. "Thresholds chosen on validation cores do not hold their FPR on test cores, and transfer between projects is poor" (C03, Appendix D). Readers planning to apply a fitted map to new areas should validate thresholds locally. Trust: high as a descriptive observation for these data.
4. "An image-derived proposal rule with an optical teacher did not reproduce the oracle gain; embedding-guided uncertainty sampling recovered part of it" (C02, C08). Trust: moderate for the specific rules; exploratory for C08.
5. "Embeddings are better than seasonal optical predictors for small wetlands" — the paper does not claim this in general, and the any-overlap result (not reported) suggests the answer depends on the recovery definition. Readers should not change their judgment on this point from this paper as written.

## Is the abstract accurate?

The individual statements in the abstract are accurate for the conditions they name (the numbers match the saved outputs). The abstract over-weights the original split: it presents the optical gain as 36.4→37.6% without saying that optical predictors gained in every other split, and it states that transfer interactions were "small and uncertain" whereas under the pre-specified other-region thresholds the embedding oracle gain was negative (−3.6 pp [−7.0, −0.6]) with large FPR deviations. It does not over-generalise geographically (it names four US inventory projects and inventory agreement), but it is too dense for the intended readers and mixes in many exploratory results.

## If nothing changes

For readers already familiar with sampling-design effects, the qualitative direction (patch-first sampling helps small-patch recall) is as expected; the useful new information is the quantification for annual embeddings vs optical predictors, the flat pixel metrics, and the poor threshold transport.

## Limitation

This assessment is my judgement as one reviewer and does not measure readers' actual changes in understanding or behaviour.

## Addition after the full re-run (appended 2026-10-27T12:34:09Z)

The full offline re-run (verify.py, not reduced) finished with status PASS (0 failures, 1,284.5 s); all ten claims' expected values match the regenerated outputs at 1e-12, and the regenerated scores/regional/bootstrap-block CSVs are byte-identical to the submitted ones. My reviewer-computed values above therefore hold for the regenerated data as well. Using the research side's own bootstrap function, the interaction under the pre-registered validation-threshold replay is 4.5 pp [−2.4, 12.0] (embedding oracle gain 6.7 [2.4, 10.7]); at 1% and 10% pooled FPR it is 7.0 [2.1, 12.2] and 5.9 [0.5, 13.0]. This strengthens the reading that the within-project embedding gain is robust while the embedding-specific excess is condition-dependent.
