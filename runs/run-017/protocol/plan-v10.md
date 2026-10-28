# Exploratory deterministic reference-alignment stress test

Fixed after original performance, before computing this stress test. This does not change the original reference, fits or primary metric. It tests a remaining alternative explanation: fine-grid spatial alignment may determine an apparent small-patch interaction even when nominal source years agree. It does not estimate the distribution or size of actual inventory error.

## Synthetic reference transformations

Use only the saved original main four arms (AEF/optical × area/object,2,000positions,RF,five original seeds) and their sixteen original test cores. Translate the reference label raster, reference valid-domain raster and reference-patch center masks by exactly one10m cell north, south, east or west; include the unchanged reference as a fifth condition. Fill outside translated domains as invalid, never wrap cells. Predictor scores and model fits remain unchanged. For each translated condition score only the intersection of the original finite-score domain and the translated reference domain. The original model excludes other inventory aquatic systems from scoring, so the domain intersection is an explicit limitation.

Use a common patch cohort across all five conditions and all arms. A complete originally eligible small patch is retained only if translation crops none of its original common-valid center pixels and at least90% of those pixels remain in the condition's common scoring domain for every direction. Decide this cohort from reference geometry/masks alone before inspecting transformed-condition scores. Record all exclusions and counts by region; do not call an identical cohort independent evidence. Keep original vector size classes and translate existing valid center masks, rather than claiming to redelineate ecological wetlands.

## Evaluation

Within each direction, recompute the pooled test-reference-upland higher95th-percentile threshold and strict> predictions, then compute the unchanged50%-coverage recovery on the shared cohort. Report achieved FPR, per-core confusion counts, per-patch counts/coverage, thresholds, regional and macro recovery. Use the same2,000 paired core/seed bootstrap with fixed directional thresholds, report all five interactions, and compare the unchanged common-cohort result with the original unfiltered result. These are exploratory deterministic perturbations, not an empirical error model or proof of reference correctness.

## Records and resources

Source provenance is the fixed dataset manifest and each saved fit's prediction/reference hashes; synthetic data are generated solely by the integer translations described above. No additional fitting, external retrieval, AI call or agent. Save translations, cohort, raw counts and summary. At most two workers, each<=1,800seconds; preserve all outcomes and stop at the original resource/deadline rules.
