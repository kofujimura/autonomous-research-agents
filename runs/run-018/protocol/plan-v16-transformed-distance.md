# Exploratory stronger-distance comparison

Written after inspection of the original and polygon outcomes. The planned
whitened TESSERA nearest-reference diagnostic was favourable in the original
panel. Raw cosine augmentation therefore cannot by itself justify a statement
about every embedding-distance method. This amendment tests the already fixed
whitening operator as an augmented pair feature, without changing its ridge
floor or tuning against outcomes. The original study and all negative controls
remain preserved. This is exploratory, not a new confirmatory primary test.

## Fixed measurements and comparisons

Use two existing input conditions: corrected original interior-patch features,
and the common polygon condition with dispersed embeddings and physical-map
values averaged at those same sample locations. No site, label, role, pair,
buffer, exclusion, screening budget, loss, uncertainty estimator or sample size
changes. All four spatial rotations are required.

For each representation and rotation, use `centred_whitened` from the original
implementation: training-only mean, covariance eigenvalues floored at1% of
the largest (minimum1e-12), symmetric inverse-square-root transform, then
unit normalization. Append its cosine distance to the existing physical pair
features. The transform is fitted only to retained training wetlands. Save
transformed vectors/IDs, training IDs and transformation metadata so distances
are recomputable. Original full-vector decoder inputs are not transformed by
this pair-feature experiment.

Check the transformed distances against the already archived whitened-cosine
nearest-reference diagnostic before interpreting new losses: compare maximum
cosine scores to absolute tolerance1e-12, count identical selected references,
and require any differing reference to be within1e-12 of the maximum. This
tolerance is an implementation audit only; the new method still chooses its
exact maximum with identifier tie breaking, without tolerance-based selection.

For each input condition, fit the two single-distance pair models using:

1. The fixed histogram gradient-boosting learner and its already archived
   same-condition physical pair/category baselines.
2. The fixed random forest with all features considered per split, seed
   offset0, and its same-condition all-feature physical pair/category baselines.

The original condition's all-feature baseline is being completed under planv15.
For the polygon condition, first fit the same four core all-feature models
(physical pair/category and both raw single-distance pairs); retain those raw
comparisons too. No additional seed is selected after transformed-distance
outcomes. Forest variability is already a limitation and three raw all-feature
seeds are fixed separately in planv15. Existing initial-extraction null controls
remain internally paired; do not silently mix inputs or baseline parameters.

## Analysis and stopping

Use the unchanged20/50/80/100% coverage summaries, both physical comparators,
window bootstrap, pool bounds, fixed-query screens and decision-overlap counts.
Report all products, input conditions and learners regardless of direction.
No p-values, search over whitening floors, or selection of a best result for
an unqualified main conclusion. No field hydroperiod or user-benefit claim.

Implementation must preserve files that active fit batches will load. Add the
new mode/arguments only after the active all-feature batch finishes; defaults
must retain the prior raw-distance behavior. Commit implementation before any
new fit and retain parameter/input/plan linkage. Each bounded execution is at
most1800seconds, no more than two experiment groups concurrently; all original
storage, deadline and final-hour rules apply.
