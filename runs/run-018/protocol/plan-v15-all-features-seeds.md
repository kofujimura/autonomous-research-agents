# Exploratory seed check with every feature considered

This amendment is written after reading the original forest, boosted-tree,
permutation, independent-scalar and constant-column outcomes. It does not
replace the primary hypothesis or reclassify exploratory results as planned.
The observed all-feature comparison currently uses one seed. We will check
whether its small single-distance increments persist across the other two
already specified forest seeds, rather than interpret one seed as a general
property of the estimator.

Use the corrected original-panel inputs and archived corrected roles/pairs.
Run the same hydrological pair, hydrological category, AlphaEarth-distance
pair and TESSERA-distance pair models at max_features=1.0, seed offsets
0,1000,2000, four rotations each. Offset0 corrects the AlphaEarth measurement
in the existing initial-extraction comparison. No other parameter, training
sample, candidate pool, metric or descriptive two-point benchmark changes.
Report all three seed-specific comparisons; do not select the most favourable
seed or interpret three seeds as a population estimate of model randomness.
No additional noise or constant fits are required: their physical-only inputs
and roles are unchanged by the AlphaEarth correction; verify this from saved
arrays before any reuse. Existing constant and scalar controls remain tied
to their original same-seed baselines and input snapshots.

Supplement the plan-v13 constant audit by reporting direct augmented-minus-
constant differences in window-mean mismatch at the fixed 50% budget, for
the initial-extraction same-seed conditions already fitted. This contrast was
chosen after those outcomes were seen, is exploratory and gets no confirmatory
test or p-value. Save the constituent window risks and the algebraic difference
so readers can verify it. The plan-v13 reference/confidence/screen counts are
implemented without changing its tolerance or definitions.

Each execution is bounded by1800seconds and the original concurrency/storage/
deadline limits. Stop at the resource limit and report incomplete conditions.
