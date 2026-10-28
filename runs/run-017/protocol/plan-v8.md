# Exploratory split-rotation and matched transfer analysis

This amendment is fixed after primary outcomes and before any additional split fits or analysis of their outcomes. It retains all original data, results and hypotheses. Its results are exploratory. No additional external data, API or agent is used.

## Alternative explanation: a favorable original test split

The original experiment has four held-out test cores per region. Rotate through four groups of four cores per region so each existing core serves once as test and once as validation, with eight other cores supplying training. Group zero is the original test set, group one the original validation set, group two the first four sorted original training core IDs, and group three the other four. Rotation j tests group j, validates the next group cyclically, and trains the remaining eight cores. Rotation zero is exactly the original split and is not refit or changed. The complete role assignments are frozen in rotation-splits.json. Inspection before fixing this plan found no palustrine source polygon ID shared between these groups in any region.

Fit only the main four arms: area/object allocation crossed with AEF/optical predictors, primary RF, 2,000 fitting positions, the five original seeds. Three new rotations require sixty final fits. Keep the same common-valid grid, patch definitions and evaluation settings. Store scope rotation1/rotation2/rotation3 and exact split-file SHA; preserve original within models. No tuning or rotation selection.

Report each rotation separately under the same pooled-test 5% FPR and validation replay. As an additional summary, pool held-out patch/core counts across all four rotations within each region, then average the four regional fractions and five seeds. Use the same 2,000 paired region-stratified test-core and seed bootstrap on these fixed predictions. All 64 cores and all eligible mapped small patches are represented in the pooled rotation summary. Models have overlapping training sets, so this is conditional robustness to split selection, not independent replication or national generality. Test-standardized thresholds are chosen within each rotation, not pooled anew. Validation replay still freezes that rotation's validation threshold before test scoring. Undefined domains/strata stay undefined.

## Matched-cohort geographic transfer analysis

The already planned leave-one-region-out fits predict all sixteen cores in their held region. Their larger test cohort should not silently be compared as though it were the original four-core test cohort. From saved evaluation rows, restrict each geographic-transfer fit to the originally designated test cores, retain its original thresholds (standardized and out-of-region validation replay), and compare with within-region training on exactly the same 227 original small test patches. These subgroup descriptions and paired contrasts are exploratory, including the fact that the standardized transfer threshold was chosen on the wider held-region cohort. For the full held-region cohort, report all four regional results and their equal-region mean; do not silently change the operating point to the matched subgroup.

## Stopping and records

At most two experiment workers, each <=1,800 seconds; 9 GiB model-start guard; total 10 GiB limit; unchanged extended deadline. Execute the previously fixed v7 checks as well, without selecting favorable results. Save failures/omitted fits. Report split-file provenance, exact scope and exploratory status in the paper and claims.
