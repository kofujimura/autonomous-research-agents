# Exploratory stronger comparators for geographic transfer

Fixed after inspecting the complete original transfer results and before these
new fits. The raw TESSERA augmentation improves the original physical-forest
point estimate, while geographic neighbours and whitened TESSERA cosine offer
strong comparisons. Probe learner/metric explanations on the same held-out
windows, without adding sites, choosing outcomes or revising primary results.

Use2024 corrected features and the archived transfer cohort, training IDs,
training pairs, four query/reference roles and candidate pools for every
target. No target-window labels enter fitting or preprocessing. Start targets
R01→R12, one bounded three-target batch at a time; other experiment capacity
continues the already planned comparisons. Preserve incomplete/failed targets.

Fit these three fixed comparison conditions:

- Stronger physical benchmark: physical pair and physical category forests
  with max_features1.0, retaining all other original transfer forest parameters
  and target-specific seeds. Compare with the archived original max_features0.7
  single-distance augmentations. This is deliberately a cross-setting
  benchmark, not a claim that the copied augmented forests use1.0.
- Boosted trees with raw cosine: same fixed HGB parameters as plan-v6
  (200iterations, learning rate0.05,31leaves,L2=1,min leaf20pair/10category,
  no early stopping), physical pair/category and both single-distance models.
- Boosted trees with whitened cosine: reuse those same physical HGB models and
  append each training-only whitened cosine distance to pair covariates. Use
  the existing1% covariance-eigenvalue floor and normalization, without tuning.

All cases use the original vegetation indicators without window indicators.
Save fitted parameters, raw decisions, physical decoder probabilities, white
vectors, transforms and source hashes. Verify training pairs/targets exactly
match the archived source. For whitened vectors, compare nearest-reference
maxima against the original transfer whitening diagnostic at1e-12; any changed
reference must have a score gap<=1e-12. This audit does not alter exact score
maxima or OID tie rules.

After all12targets, combine each condition by rotation and run the common
20/50/80/100% risk/coverage and paired-window summary. Show all three conditions
and all core methods. Verify physical decisions agree between raw/white HGB,
pool IDs/counts agree across conditions, and copied forest augmentations retain
the original half-coverage selected-query/reference decisions. If a check
fails, preserve the failure and diagnose before interpreting the new contrast.

These are post-transfer exploratory comparisons, with the existing12-window
bootstrap and its limits. No validated model-selection procedure, field
hydrology, independent replication or universal transfer claim is established.
No API/network calls. Local groups<=1800seconds, at most two groups total.

Pre-fit implementation clarification 2026-10-28T03:36:57.761322+00:00: combine new condition files with the round-trip CSV reader to avoid an extra lossy numeric parse for copied augmentation scores. The standard summary/tie policy is unchanged; exact accepted-query/reference equality with original augmentations remains required.
