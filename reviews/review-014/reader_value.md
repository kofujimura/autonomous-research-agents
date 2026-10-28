# Value to readers (review-014-1)

This is a self-report by the reviewer (an AI agent), written after reading and verifying the submission. It is not a measurement of any change in the understanding or behaviour of actual readers.

Caveat on the comparison: prior_expectation.md was written after I had already seen the abstract and Sections 1–3.5 of paper.md (disclosed in that file). The "as expected" judgments below are therefore biased toward agreement.

## 1. Comparison with the prior expectation

As expected:
- Concurrent (year-matched) references and tree-control subtraction gave no consistent improvement over the start-year reference (paper Table 2; C001). The 8 primary J contrasts range from -0.037 to +0.011, and the partition check (C018) shows all 8 contrasts change sign across fitting/calibration splits. My own check on the saved predictions shows why little could change: on the test rows, the corrected scores have Spearman rank correlations of 0.947–0.996 with the start-fixed score, and the control adjustment is an exact constant within each held-out region and year pair (maximum within-group SD of the difference about 6e-18). The null result for the corrections is largely predictable from the design (adjacent-year pairs, a slowly moving reference centroid, a constant shift that a re-used threshold mostly absorbs).
- Supervised readouts that use the supplied initial class beat the reference-similarity scores (C002). This is a standard expectation in land-cover change mapping.
- Loss (Trees to Grass/Shrubs) is much easier to detect than gain in both products.
- Transferred thresholds did not keep the nominal 10% false-positive rate: test FPRs range from 0.035 to 0.329 across the primary-condition readouts (0.329 = 28/85 for AlphaEarth standardized-concurrent gain; my recomputation, verification/independent/main_operating_points.csv).

Different from expectation, or stronger than expected:
- The unsigned cosine change magnitude (1 − a·b, the quantity behind common "embedding change" maps) flags 0/24 gains in both products. Its AUROC for gains is 0.287 (AlphaEarth) and 0.318 (TESSERA), clearly *below* 0.5. In my recomputation, the median magnitude of gain plots is lower than that of non-tree negatives in both test year pairs and both products (e.g., AlphaEarth 2019–2020: 0.033 vs 0.044; TESSERA: 0.090 vs 0.130). So the labelled tree gains are *more* stable in embedding space than plots that stay grass/shrub. I expected a weak signal, not an inverted ranking. The paper reports the AUROC only in a table and does not discuss the inversion.
- The start-year reference score itself is close to chance for AlphaEarth gains (3/24 detected at FPR 0.106, J = 0.019, AUROC 0.556 in my recomputation). For the separate NLCD Forest endpoint, the start-fixed J is negative in 3 of the 4 gain conditions. The abstract reports only differences between corrections, not this floor.
- Initial-vector-only learners detect gains about as well as both-date learners (LCMAP direct learner J 0.436 vs 0.429 for AlphaEarth; C017). I did not expect this. Possible contributors the paper does not mention: AlphaEarth was trained with the NLCD 2019 land-cover map as a reconstruction target for every year except 2021 (Brown et al., 2025, Supplement S1.9), and 21 of the 24 LCMAP gain positives fall in a single year pair (2019→2020).

## 2. Which understanding or judgment could change, and how far the claims can be trusted

1. Practitioners who use year-over-year embedding change (for example the Google Earth "Detect change" tool built on AlphaEarth embeddings, or cosine-dissimilarity thresholds such as τ = 0.15 in Yao et al., CaGIS 2026) to look for tree-cover *gain* or regrowth: this study gives concrete evidence that, on these labelled US plots, such magnitude scores did not flag gains and ranked gains below unchanged non-tree plots (C003, C005). Trust: high for the observed counts (re-computed exactly; raw-array recomputation of magnitudes matched to about 1e-16). Moderate for generality: there are 24 gain positives in 13 five-degree cells, 21 of them in one year pair, and the endpoint is LCMAP dominant cover in CONUS. This is probably the most decision-relevant result for practitioners, but the paper does not state it in their terms.
2. Restoration researchers who compute cosine similarity to reference-forest embeddings (Heiman, 2026): the result that a year-matched reference or a control subtraction changes few decisions (3–19 changed flags per condition) and gives no consistent benefit at adjacent-year intervals (C001, C014, C018) tells them that such corrections are not a substitute for validation against the endpoint. Trust: high for what was measured. It is limited to one-year intervals, so it does not settle the multi-year trajectory use (restoration start to +3 years or more) that motivates the question.
3. Remote-sensing researchers evaluating embeddings: performance on a subsequent-state label does not isolate change information, because before-only inputs retain gain discrimination (C009, C017). Trust: moderate. The results are exploratory, fixed after both endpoints had been seen, and the mechanism is unresolved.
4. Few readers would change their view on supervised versus unsupervised readouts (C002). This is expected and was carried out with unequal label resources.

## 3. Accuracy of the abstract

- Every number in the abstract that I compared matched the saved outputs, and all claims.jsonl expected values matched both the submitted and the regenerated outputs (verification/).
- The abstract does not overgeneralize in wording: it hedges heavily and labels exploratory results. Its problem is the opposite. It is overloaded with paired counts ("3/9 of 109 gain cases, 19/6 of 337 loss cases ...") and internal labels ("start-fixed", "readouts"). A reader cannot tell which result is the main message. The most decision-relevant facts (the near-chance reference score for AlphaEarth gains, magnitude AUROC < 0.5 for gains, corrections changing few alerts) are absent or hard to recover.
- The abstract includes at least four groups of exploratory results (matched direct inputs, partition perturbations, single-date native input, Forest initial/later counts). Research Instructions §8 allow only exploratory results that change the interpretation of the main results. The partition result does qualify. The native single-date check and the full Forest changed-flag listing do not need to be in the abstract.
- Scope limits that matter for interpretation are missing from the abstract: one-year intervals only, CONUS only, and 21/24 gains from one year pair.

## 4. Limitation of this self-report

This is the reviewer's judgment of likely changes in understanding. It is not measured and is biased by the non-blind prior expectation.
