# Exploratory amendment v22: saved single-date native target inputs

Fixed 2026-10-25T17:19:18Z, after v5point agreement and v21lack of complete paired native inputs were inspected, before any single-date substitution readout. The failed/incomplete v21test remains unchanged and referable:0/16completepairs,1/32nativepoint-years, acquisition never launched. Searching all saved original target pairs also found0complete native pairs. No new retrieval occurs after the fixed17:00cutoff.

## Alternative using saved data

Select **all** original later LCMAP target pairs (before_year>=2019) with at least one native point-year already saved under the fixedv5sample. Save the selected target list and the available native point-year task list before computing scores. Selection depends on prior fixed acquisition/file availability, not readout scores; it is a post-primary, availability-selected case series, not a representative test sample. Do not replace or add cases. Report the task/label composition and whether the replaced date is before, after or both.

Substitute each available native date's AlphaEarth centre and3x3vector using the original decode/normalization. Keep the other date in its original geographic-mosaic representation when no native input exists. This intentionally tests single-date reading sensitivity, not a physically matched full native pair. Earlier target fitting/calibration and all R/Cvectors remain mosaics. TESSERA values stay unchanged for the common target mask. Assert replacement keys do not overlap earlier target or R/Ckeys. Native invalids are unavailable without nearby-valid fallback.

Rerun original AlphaEarth seed14014/global readouts, centre and patch separately; require all earlier thresholds to match to1e-12 and all unselected test scores/flags unchanged. Report each selected case's original/substituted score and flag, common availability, changed flags and maximum absolute score change by readout/task/support. Also show original/substituted TP/FPcounts on common cases with explicit denominators, without claiming population performance, significance, equivalence or which footprint is correct. No thresholds, models or metrics are tuned. Multiple methods on one pair are not independent observations.

Save data/native-available and analysis/native-single-date-v22; retain data/native-pairs and analysis/native-pairs-v21 with their unfinished status. Add the new deterministic sampling and numerical comparison to offline verification. Expected under1minute, hard1800seconds and max2experiment processes, no network/API/participant. A change demonstrates sensitivity to input reading under this mixed-footprint substitution, not the effect of a full native refit or the true physical land-cover change. Zero changes would only concern the selected available cases and fixed rule.

## Reporting clarification for v21

The original empty v21count table is preserved in Git and experiment stdout. Add explicit complete-pair/evaluated-pair/status fields to its checks.json using saved availability; zero raw counts with common_cases=0are empty counts, not observed zero sensitivity or stability. This is a reporting correction, not an added successful experiment or new inferential result. Record old and new checks and verify scientific CSVs are unchanged.
