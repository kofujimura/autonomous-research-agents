# Exploratory amendment v13: endpoint composition and reference-score diagnostics

Fixed 2026-10-25T13:30:58Z, after the paired primary result was inspected at13:27:20UTC and before these new calculations. Original primary estimates and every included case remain unchanged. These additions are exploratory and test an alternative explanation rather than a new research question. No new data or AI calls. Expected computation under5minutes, existing1800second timeout and2-job guard.

## Question

Both products' cosine-change magnitude scores flagged zero of the24 known tree gains at the original operating point. Their negative class includes transitions between Grass/forb/herb and Shrubs, which are real cover changes but are negative for the specific Trees-gain endpoint. Does that endpoint composition explain the observed floor? Also, how do before/after reference similarities and the already-prespecified patch support relate to the weak gain-change score? Do not interpret either diagnostic as identifying a physical cause, encoder drift or ecological restoration performance.

## Fixed tests

1. Counterfactual gain-negative definition: retain all original known tree-gain positives; restrict both earlier negative calibration cases and later negative test cases to unchanged Grass or unchanged Shrubs. Keep the original earlier fitting set and fitted algorithms intact, including its changed non-tree negative examples. Only calibration-negative and test-negative definitions change. Recompute higher-interpolated90th-percentile thresholds, strict flags and the same12 readouts, primary reference allocation/global references, centre and patch support, both products. Loss estimates are retained only as an unchanged check. Require the original minimum10 negative calibration cases; unavailable folds remain unavailable. Save exact excluded pairs and their class/year counts. Do not select the new condition as the main result.

2. Verify score invariance: on every common point/method/support/fold, scores must match saved paired main predictions to absolute tolerance1e-12; case/training differences must not silently change the fitted readouts. Compare metrics, gain positive/negative denominators, thresholds, true/false flags and paired J contrasts. Use the original spatial bootstrap for descriptive intervals.

3. Reference-similarity diagnostic from saved primary scores: for each centre-pixel pair reconstruct a·r_a and b·r_a from the saved start-fixed, concurrent and subsequent-reference scores, respecting loss-score direction. Verify reconstructed values against directly decoded raw vectors and the original fold/year centroid (all selected pairs, tolerance1e-12). Plot before versus after similarity by product/task and truth; distinguish unchanged non-tree negatives from Grass↔Shrub negatives. Report medians/quantiles by original class route and counts. This is descriptive and does not test a new ecological mechanism.

4. Report the existing preplanned centre/patch operating points alongside these diagnostics. A small patch-support difference cannot establish exact30m footprint agreement. No new support, geolocation correction, label exclusion or causal attribution is introduced.

## Records and reporting

Save predictions, thresholds, fitting-invariance check, metrics, class-route counts, excluded-case list and scalar reconstruction diagnostics under analysis/endpoint-v13. Keep all original outputs. Record this exploratory negative-class restriction in deviations; reproduction regenerates it offline and compares saved values. If the diagnostic changes interpretation of the headline floor, state that in the abstract; otherwise include its full evidence in the appendix. Never claim zero population gain sensitivity from an observed zero count or a degenerate bootstrap interval.
