# Plan v4: exploratory city-location and time-aggregation boundary

This extends the same summary-information question to more realistic locations and a longer hazard-assessment window. It is exploratory and fixed before its inputs are acquired or analyzed. Original v1 results remain primary, and exploratory v3 subset-product results retain their own label. Do not replace or erase earlier weak results. The motivation is the original self-check's artificial-grid/synoptic-snapshot limitation, not a favorable effect estimate.

## Question and tests

Do the observed marginal/aggregate-moment/pairwise identification intervals remain similar when locations are anchored to public city coordinates, and when the hazard is defined by the maximum across four six-hourly forecast valid times rather than the 12 UTC snapshot?

The latter is a **maximum over four sampled times**, not a model's continuous daily maximum or an observed daily maximum. It describes spatial extent of a temperature threshold being crossed within a common UTC planning day. Exceedances need not occur at the same hour, so this is not a measurement of peak simultaneous service demand. No health trigger, population exposure, hospital load, real resource network or social effect is validated.

Primary exploratory endpoints: n=12 compatible-tail interval widths for the same marginal, marginal-plus-aggregate-second-moment and full within-universe pair conditions; fixed capacity fractions, thresholds and illustrative cost ratios from v1. Exact original count probabilities and coherent binary masks remain reference information. Compare all cases, informative cases (>=4 uncertain sites and0.1<=q<=0.9), and matched snapshot/maximum cases informative under BOTH definitions. Report floors/ceilings, <=2 uncertain sites, exact identification to tolerance, and composition changes. Neither increased exceedance probabilities nor maximum>=snapshot is a discovery; these are definition-driven code checks. Interval-width changes are empirical. Do not infer a causal effect of city placement or a forecast-system performance ranking.

## Sample fixed before acquisition

Select twelve initialization dates spread over the original fixed v1 calendar: indices round(linspace(0,D-1,12)), with NumPy round-to-even and D the number of v1 dates. Save the exact resulting dates in `city-time-parameters-v4.json` before downloading the gazetteer. They are not selected for unusual weather or the main effect sign.

Use the same AIFS ENS and IFS open products and perturbed members1–50. For each date/model, acquire2m temperature at leads72,78,84,90 and168,174,180,186 hours. The first four represent valid times00,06,12,18UTC on day3; the second four on day7. Derive the maximum MEMBER BY MEMBER before computing exceedance indicators or any summaries. The 84/180h snapshots match v1. Use published member identifiers to align times, and assert dates, steps, units and grid coordinates agree. Do not combine independently sorted members across times.

Include all original regular-grid portfolios AND twelve-site city-located portfolios selected below. Re-extracting original points provides a paired extraction check at84/180h, not an independent reproduction or a new forecast sample. Save hashes of every source field; compare these and the original-site snapshot values with retained v1 data wherever available. Preserve any archive change or mismatch without overwriting v1. Do not use this new acquisition to fill a v1 exclusion silently.

## Gazetteer, licensing and city selection (stage1)

Use the single public GeoNames `cities15000.zip` dump, its readme and terms. Official readme checked before fixation: CC BY4.0, attribution to GeoNames, data “as is”; public download is free. Do not use a web-service account, premium route or API. Check download-server robots and record result; no bypass. Keep the source archive, retrieval time, license and SHA-256 so later changes to the daily dump do not affect offline reproduction.

The unit is a public populated place, not a person, household or business. Use population>=100000 only as an eligibility filter, not as a weight, burden estimate or ranking. Population definitions/dates vary across contributors and are not harmonized. Retain fields needed for provenance, place identity, country, coordinates, feature code, population eligibility and modification date; no individual data or linkage.

Eligible features: classP, codes PPL/PPLC/PPLA/PPLA2/PPLA3/PPLA4, finite WGS84 coordinates and the population cutoff. Groups and centers:

- Iberia: ES,PT; center40,-4.
- France: FR; center47,2.
- central Europe: DE,AT,CZ; center50,14.
- Balkans: RO,BG,RS; center44,22.
- northern India: IN within latitude[22,32],longitude[70,88]; center27,75.
- Sahel: BF,ML,NE; center14,2.

Snap coordinates to the nearest0.25degree grid point using floor(4*x+0.5)/4, with longitude represented consistently. Save city and snapped coordinates separately. Require distinct snapped cells WITHIN each twelve-site portfolio. This avoids treating duplicate model cells as independent locations. Do not require different portfolios to be disjoint.

For each group, select two portfolios. **Nearby:** order eligible cities by great-circle angular distance of their snapped cell to the center, breaking ties by increasing GeoNames ID; take the first twelve distinct cells. **Dispersed:** start at that same nearest eligible cell, repeatedly choose the city maximizing its minimum great-circle angular distance to selected cells, tie by increasing ID, and skip cells already selected, until twelve. This is a geography-only design, not a sample of actual resource allocation or user query frequency. Do not present it as representative of all cities.

If a group has fewer than twelve eligible distinct cells, record the failure and omit its city portfolios without lowering the cutoff, adding countries or selecting replacements after viewing forecasts. Original regular-grid portfolios remain. Save all candidate/selected data and selection diagnostics. Freeze and commit the realized `design-v4.json` (points, portfolios, scheduled dates/leads) BEFORE stage2 weather acquisition. Place selection is therefore reproducible and does not use forecast temperature values.

If readily obtainable, extract the public IFS land-sea mask at selected snapped cells to describe coastal/mixed cells. Do not filter cities using observed temperature or silently remove coastal cells. Label mask provenance/system and missing mask values; it is not a validation of urban microclimate or of AIFS's surface classification. Failure to obtain this diagnostic is reported, not grounds to alter the city sample.

## Weather acquisition and derived data (stage2)

Use the v2 bounded public-range transfer procedure and the same ECMWF CC BY4.0/general terms and attribution as v1. Store the new selected site vectors separately from v1, with complete indexes, metadata, URLs/ranges, times and hashes. Reuse a byte-identical saved index when applicable and explicitly record its original source rather than pretend to download it again. Global transport fields outside selected points need not be retained. No new model API, paid account, cloud compute or participant study.

Derive two endpoint arrays for each horizon: the12UTC snapshot and the memberwise maximum of its four fields. Save derived arrays with hashes of ALL contributing source arrays, method, units, member IDs and point identities. Validate elementwise maximum>=snapshot, time/member alignment, finite values and all binary-mask/count round trips. These checks are expected by construction, not substantive findings.

For paired exploratory inference, a date must have all2models x2horizons x4times complete, each with all fifty members. Keep partial/unmatched data and descriptive availability outputs. No replacement dates. Max two acquisition invocations per new unit, including one cached-data resumption, as in v2; original v1 failed/excluded units retain their original status. Failures do not count as negative weather results. Match cities/regular points and endpoints within the same dates/models; do not count repeated original snapshots as independent replications.

## Analysis, uncertainty and reporting

For each complete derived array, use exactly v1's binary exceedance and LP conditions, n=12 and capacities3/6/9; thresholds25/30/35C and c=0.1/0.25/0.5. Smaller-n query products are not required in this extension; v3 retains that separate comparison on the original universes. Group portfolios as regular versus city, and their specified geometry/selection rule. Describe differences in spatial extent and source definitions alongside comparisons; do not rank regions or interpret equal site counts as equal population demand.

Report mean widths and paired width differences for snapshot versus four-time maximum in all cases and the common informative stratum, with all denominators and floor/ceiling counts. Report original-style informative strata separately too. Show system/horizon and portfolio-type breakdowns; no post-result exclusions or optimally chosen threshold. Use date-clustered circular moving-block resampling, block length2 of the twelve scheduled v4 dates,2000 replicates,seed20261026. These are descriptive resampling intervals for a convenience sample, not true-weather probability or calibration intervals. If fewer than eight dates are fully matched, mark the boundary comparison undersized/unfinished. Do not claim independent confirmation of v1: dates/products overlap.

Record all failures, code/plan commits, input hashes, commands and start/end times under the existing runner. At most two experiment workers, each<=1800seconds; split acquisition into date/model/horizon groups that fit. Check actual runtime from early units before increasing batch size. Monitor total directory storage. Do not start new long acquisition within sixty minutes of the current manifest deadline. If incomplete, preserve/report it and prioritize paper/verification rather than changing definitions to manufacture completion.

This extension is exploratory in the paper and abstract if it changes interpretation. Ground-truth weather verification, clinically appropriate heat thresholds, real resource loads, human usability, actual provider traffic and adoption remain unmeasured. Public-data safety rule12.5 applies. No security/privacy/disclosure issue is indicated; do not collect individual-level data or make named-city performance rankings.
