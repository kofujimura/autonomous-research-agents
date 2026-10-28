# Alternate-year common-cohort implementation

This clarification precedes alternate-year data retrieval and all alternate-year
matching outcomes. Years2023/2021 were already specified in the original plan.
The revised implementation isolates the embedding year from any completeness-
driven change in wetlands, training pairs, candidate pools or physical inputs.
It is a secondary clarification after primary outcomes, and is recorded as
exploratory rather than retroactively part of the initial primary test.

Collect both frozen products for all originally selected polygons, subject to
the existing bounded retries, terms, storage and deadline rules. Use the repaired
AlphaEarth adjacent-tile assembly and audit missing tile-edge pixels. Require
alternate-year TESSERA zone metadata to equal the archived primary product's
metadata. Preserve failed/missing inputs; never replace windows or polygons.

Before matching, derive each year from its saved raw patches with the same
decoding/inside-mask/at-least-five-valid-vector rules and unchanged2024 physical
grids. Fix the common set as the intersection with finite means for both
representations and essential elevation at2024,2023,2021, preserving original
ID order, labels, geometry/folds and minimum15m margin. Save all exclusions by
year and input hashes. Do not choose completeness thresholds from matching loss.

On that set, fit all18original methods at each year with the original forest
parameters/seeds, spatial rotations/buffers and20/50/80/100% evaluations. The
2024 input uses corrected patches. If the intersection equals the entire original
cohort, reuse the archived corrected2024 fits; otherwise fit a separate common-
cohort2024 reference and retain the full original primary results unchanged.
Assert identical physical arrays and ordered IDs across years, then check that
physical-only predictions agree across years to absolute tolerance1e-12.

If a year/product cannot be retrieved completely within the predefined attempts
or remaining resources, report the incomplete comparison. Do not silently
substitute another product/year or broaden the cohort. These experiments test
inventory-label agreement under different embedding years with fixed2024
physical covariates. They do not validate annual hydroperiod, identify temporal
water change or establish forecasting performance.

No new paid APIs, human data or external AI calls. Each group≤1800seconds,
at most two concurrent experiment groups, all storage/deadline limits retained.
