# Value to readers (review-015-1)

This is the reviewer's self-report after reading and re-running parts of the study. It is not a measurement of any change in readers' behaviour.

## Compared with the prior expectation (prior_expectation.md, saved 2026-10-26T12:10:56Z)

As expected:
- The ordering marginal > aggregate > pair in width holds (it is implied by nesting, as the paper itself says).
- A large share of all queries is trivial: 3,941 q=0, 3,469 q=1, 5,064 with at most two uncertain sites out of 12,096 (re-computed from raw arrays by the reviewer, 0 mismatches).
- Certification on the full query set is already high from per-location probabilities: in decision-summary.csv, marginal-only release certifies 85.9% / 87.5% / 87.8% of all 12,096 queries at c = 0.1 / 0.25 / 0.5. This matches my prior guess (70–90%). The paper's main text does not show these all-query figures.
- In the hard (informative, near-threshold) cases, marginals almost never certify (0.2–2.3%). Given mean marginal widths of about 0.51 and a ±0.1 selection window, this is close to what follows from the widths alone.
- A finite 50-member ensemble with exact zero cells makes pairs "nearly identify" many tails, and the identification disappears under any continuous tolerance. I expected this.

Different from expectation:
- Pair widths in the informative stratum were smaller than I expected (mean 0.0547, 1,068/2,871 numerically identified). Pair certification near the threshold was higher than I expected (75–91%).
- The aggregate second binomial moment captured 43.4% of the marginal-to-pair narrowing. I expected "a large share for k near the mean"; the measured share is moderate, and it differs strongly by geometry (compact 0.53, dispersed 0.30; from width-summary.csv, not reported in paper.md).
- The marginal-interval midpoint had a small mean absolute error (0.0437 against the empirical q) despite widths of about 0.51. Independence was much worse (0.141). I did not anticipate how small the midpoint error would be. This is an exploratory result.

## Which understanding or judgment could change, and how far I trust it

1. Ensemble-product designers and multivariate post-processing researchers. For 12-site regional portfolios at M = 50, the pairwise co-exceedance table leaves only small ambiguity about "at least k of n" tails when moments are exact (C01, C02). One aggregate scalar recovers somewhat less than half of that narrowing (C03).
   - Trust in the numbers: high. A re-run by another agent on the same machine reproduced them: an independent LP implementation by the reviewer matches all 2,871 informative endpoints, and the author replay was re-run (see review-1.md §4).
   - Trust in the interpretation as a property of forecast spatial dependence: limited. Pair width rises with ensemble size: 0.0023 (M=10), 0.0219 (M=25), 0.0547 (M=50), C08 and Appendix H/J. Identification depends strongly on how few binary states survive zero-cell pruning (reviewer analysis of cases.csv). It vanishes under any tolerance (C07). So the reader should take away "exact pair tables of a 50-member ensemble nearly pin down the count tail". They should not take away "pairwise dependence information is nearly sufficient for spatial count events". The abstract does not make this distinction clear enough.
2. Practitioners holding only per-location probability maps. For about 1 in 8 queries in this design, the map alone cannot settle a cost–loss action at c = 0.1–0.5. For queries with several uncertain sites and an intermediate joint probability, the compatible range averages about 0.51. Practitioners also learn that assuming independence gives large errors (MAE 0.141) (C04, C05, Appendix E).
   - Trust: high for the sampled design (numbers re-computed). Generality is limited: 6 regions, a June–September 2026 season, a 12 UTC snapshot, fixed 25/30/35 °C dry-bulb thresholds, and two spatial geometries whose results differ by a factor of 2–3.
3. Product designers choosing a delivery format. In §4.4 the paper notes that a 50 × 12 coherent binary mask (600 bits) is only about 28% larger than margins plus pairs (468 bits) and answers every fixed-threshold query exactly. In my view this is one of the most practically useful facts in the paper. It is understated: it appears only in §4.4.

## Accuracy of the abstract

- The numbers in the abstract match the outputs (all re-computed or re-run; see review-1.md §4).
- The abstract does not answer the second half of its own research question (how often the bounds certify an action). It gives neither all-query nor near-threshold certification rates.
- It does not state the ensemble-size dependence of pair identification, so it invites over-generalisation of "pairs numerically identified 1,068 tails".
- It is overloaded with exploratory details: subset counts, fixed-size 0.005/0.02 envelopes, a self-check note. The prespecified geometry/lead heterogeneity is missing.
- It is not inaccurate. It is over-dense and under-qualified on the most important interpretive point.

## Limitation of this self-report

This is the reviewer's judgment of what the intended readers would learn. No reader was observed, so it does not measure any actual change in understanding or behaviour.
