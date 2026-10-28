# Exploratory magnitude of the changed measurements

Fixed after polygon matching outcomes and the factor-isolation audit, before
computing these input-change summaries. This addresses the self-check question
of whether compared conditions are effectively identical. It does not select
new cohorts, refit predictors or change any primary metric.

On the fixed common polygon cohort, compare point physical covariates in B
with the same feature maps averaged at dispersed positions in C. For every
feature and wetland, record finite-value changes and missingness changes.
For each of the four archived B-forest training transforms, divide differences
at jointly finite entries by the recorded physical scale (training IQR, with
the original unit-scale fallback for zero IQR). Report each wetland's maximum
absolute scaled difference, counts at<=0.01,<=0.1 and>1 scale units, and
missingness-change counts. Report all four rotations separately; they are not
independent samples. These thresholds describe numerical exposure, without
an ecological equivalence interpretation. Save feature-level median/95th
percentile scaled changes and all wetland-level values.

For each product, compare normalized mean embedding vectors A versus B and A
versus D. Save every within-wetland cosine distance and report its median,
95th percentile and counts at<=1e-12,<=1e-4 and<=1e-3. Clip numerical cosine
distances to[0,2]; no matching scores or selected references are altered.
All thresholds are fixed before inspecting these input-change distributions.

Assert identical ordered IDs and physical feature names. Save input hashes.
Run in a free bounded local slot, without network or AI calls, and add to
offline verification. This exploratory exposure check supplements the exact
factor-isolation checks; it does not validate field hydrology or identify a
unique cause of changes in fitted tree predictions.

Pre-execution numeric clarification 2026-10-28T02:53:33.537423+00:00: re-normalize saved directions in float64 for this input-only cosine calculation, so floating storage norms do not masquerade as directional changes at the1e-12 bin. Matching scores and vectors are unchanged.
