# Exploratory polygon sampling and physical-footprint check

Fixed after primary, HGB, recent-panel and first additional forest-seed results were inspected. This is an **exploratory robustness extension within the same research question**, with all original outcomes preserved. The immediate concern is that a small interior patch can be an unstable measurement of a heterogeneous wetland, especially with radar-derived representation inputs. A newly found wetland-classification thesis mentions aggregation sensitivity in its abstract; its full text is inaccessible, so it is a feasibility pointer, not supporting evidence for a claim here. No external AI is consulted.

This alternative explanation has priority over obtaining wetland data for the already fixed random geographic panel. Preserve those48centres and their selection history; attempt that panel if sufficient resources remain after these checks, original boundaries and transfer tests. Unexecuted work must be labelled unexecuted, not omitted from records.

## Fixed sample and conditions

Use the original12windows and exactly the originally selected polygons. Enumerate10m grid pixel centres inside each complete polygon geometry, on the common native grid already validated for both2024products. Save total eligible pixel counts and all selected coordinates. Within each polygon rank pixel centres by SHA-256 of `free-research-018|polygon-pixel|OBJECTID|integer_x|integer_y` (ties by x,y); retain the first min(256,total) pixels. This is a deterministic uniform-priority spatial sample, not an exact whole-polygon mean for polygons with>256pixels. Do not choose pixels using regime, water values, embedding values or outcomes. Use the same coordinates for both products. For huge bounding rectangles enumerate bounded strips rather than allocate an unbounded grid; any resource failure is retained, not a region replacement.

Conditions:

A. Original contiguous3x3 interior embedding mean and original30physical covariates.
B. Mean decoded embedding over up to256dispersed interior pixels, with original30physical covariates.
C. Same dispersed embedding mean asB, with the same30physical-feature definitions spatially averaged at those same sampled coordinates using the archived30m raster grids. Compute local terrain/water/HAND feature maps exactly as in the original pipeline; average each map's sampled finite values. Log area stays the same polygon attribute. No extra feature dimensions are introduced. This is a physical-footprint control, not a field hydrological assessment.
D. A dispersed sample with the **same number of geometrically inside pixels as the original3x3patch** (5–9, separately recorded), using the prefix ofB's priority list, with original30physical covariates. This separates spatial dispersion from simply increasing the nominal sample count, subject to missing-pixel differences.

Retain decoded mean magnitude for full-vector decoders; unit-normalize directions for cosine methods. ForB require>=5valid vectors and at least80% of sampled pixels valid in each representation. ForD require>=5valid vectors. ForC also require>=80% finite samples for elevation_mean90,occurrence_mean90 and recurrence_mean90; other missing covariates retain training-only imputation. Preserve per-feature/sample validity counts. These criteria are fixed before acquisition. Use the **intersection of eligibleA/B/C/D** for every comparison, including its query/reference/training pools. If this intersection equals the original cohort, A can reuse the original outputs; otherwise refitA under exactly the original algorithm and keep the original result separately. No label balancing, region replacement or result-based exclusion.

## Acquisition, checks and analysis

Use the same archived product versions/year2024, quantization and public sources/terms as the primary. Save raw sampled vectors, scales, coordinates, polygon offsets/objectIDs, source metadata, timestamps and hashes under data/polygon/. Stream in bounded chunks. No training of remote models or AI calls. Confirm source-grid alignment from coordinates; audit sampled centres inside original polygons; count any pixel reused by different polygons/roles. Spatial separation remains based on the original representative points and is not a guarantee that wider footprints are independent.

Refactor of physical-feature sampling must reproduce every archived primary physical value exactly (including missingness) before adoption. The new default behaviour must remain identical. Recompute all source-derived inputs from saved files during verification.

ForB/C/D (andA if needed), run the original18methods and fixed4rotations, seeds, pair sampling,1km point buffers,30physical features,50% primary coverage and20/80/100% secondary coverage. Repeat with the same pre-specified HGB learner to check learner dependence. Report all conditions, denominators, fixed-screen/reference-choice diagnostics and both macro/pooled risks. Comparisons concern changes to measurement footprints under the specified pipeline, not causal effects on wetland ecology. No new thresholds or hyperparameter search after observing these results. Original seed/control results remain separate; this exploratory follow-up cannot convert them into a confirmed general gain.

## Resource stops

At most2logical experiment processes, each<=1800s. Use one or a few regions per bounded collection batch, retaining partial results on timeout. Warn8GiB/stop downloads9GiB/absolute10GiB. Public data retrieval stays ordinary bounded file/range access. No long new experiment in the final research hour before2026-10-28T02:37:02Z. Remaining alternate-year/geographic checks can be submitted incomplete if this more direct alternative explanation uses the available time; state actual completion and reasons. No extension of the trial deadline or resource limits.
