# Topic selection: pre-critique record

Recorded before the required critic call. Selection is not yet fixed. Intermediate lists and twelve six-point checks are preserved in divergence.md and screening.md, which are included by reference in research_log.md.

## Search scope and closest work (step 3)

Searches used the ordinary web search tool and public primary sources on 2026-10-27. Search terms included the candidate formulations and established alternatives: multivariate verification, ensemble copula coupling, Schaake shuffle, spell duration, energy drought, Dunkelflaute, geographic object-based image analysis, minimum mapping unit, patch fidelity, landscape context, rare-class accuracy, spatially blocked validation, temporal hierarchies, forecast reconciliation, contextualized table extraction, table structure recognition and censored/nondetect measurements. Recent searches explicitly included 2025 and 2026. Saved search returns and checked passages are indexed by sources.jsonl and data/searches/. Search results alone are not supporting evidence for the paper.

### C01: sustained hot-night forecasting

1. Price et al., *Probabilistic weather forecasting with machine learning* (Nature, 2024; doi:10.1038/s41586-024-08252-9; author manuscript arXiv:2312.15796). Full-text methods and results checked, including marginal extreme-event verification, joint/spatial wind power, REV and bootstrap methods. Difference: matched-marginal multi-night run probabilities and heat-protection activation, rather than an overall AI-versus-NWP score comparison.
2. Schefzik, Thorarinsdottir and Gneiting, *Uncertainty Quantification in Complex Simulation Models Using Ensemble Copula Coupling* (2013; doi:10.1214/13-STS443; arXiv:1302.7149). Full-text methods and results checked. Difference: evaluate a health-protection spell decision using new learned trajectories; retaining dependence itself is already known and cannot be claimed as new.
3. Wessel et al., *Probabilistic AI models outperform numerical weather prediction models on record breaking heat extremes* (2026; arXiv:2610.20519, Oct 14). Abstract/search checked only at selection; it shows very close current work on probabilistic heat verification. Difference potentially remains in multi-night persistence under equal marginal information; not established by abstract alone.

Standard approaches: heat-health warning thresholds and distributed-lag temperature studies; Brier score, cost-loss/REV, ECC and Schaake shuffle. Much of the original candidate is known. Novelty is therefore low; no claim of a new dependence principle.

### C02: prolonged low-wind reserve risk

1. Price et al. (above). Full text checked. Already compares regional wind-power forecasts and dependence-sensitive outcomes. Difference: cumulative deficit and reserve scheduling, rather than spatially summed instantaneous power.
2. Bracken et al., *Standardized benchmark of historical compound wind and solar energy droughts across the Continental United States* (Renewable Energy 220, 119550, 2024; doi:10.1016/j.renene.2023.119550). Full methods and results checked: simulated hourly power under historical weather, standardized drought indices, duration and coincidence with load. Difference: evaluate forecast-conditioned decisions, not recreate the already published drought climatology.
3. Bracken et al., *Seasonal compound renewable energy droughts in the United States* (2025; doi:10.1088/2753-3751/adc8ad). Abstract/search only. Difference: short-range forecast trajectories rather than seasonal drought climatology; neither novelty nor method details inferred from abstract.

Standard methods: reliability/adequacy replay, power-curve sensitivity, energy drought indices and storage-sizing models. Close prior work substantially reduces value of a simple AI forecast application.

### C03: small wetland fidelity in smooth maps

1. Ryan, Powell, Ling and Wen, *Streamlining Wetland Vegetation Mapping with AlphaEarth Embeddings: Comparable Accuracy to Traditional Methods with Cleaner Maps and Minimal Preprocessing* (Remote Sensing 18, 293, 2026; doi:10.3390/rs18020293). Full paper obtained from the publisher's public static PDF after the ordinary HTML route returned 429; no authentication, user-agent rotation or access-control bypass was used. Methods pp. 4–7 and results/discussion pp. 8–14 checked. It selects homogeneous clusters/inliers, uses random point holdout and describes smoother/larger patches as useful. Difference: a spatially held-out, object-sensitive evaluation of small isolated wetland retention under equal training budgets, matched spectral and smoothing controls, and alternative sampling designs. The present candidate must not claim that small-wetland remote-sensing difficulty is newly discovered.
2. Brown et al., *AlphaEarth Foundations: An embedding field model for accurate and efficient global mapping from sparse label data* (2025; arXiv:2507.22291v2). Full text, sections 4–5, S17–S19 and S22.3 checked. It uses sparse pixel labels, balanced accuracy, broad mapping tasks, and strong EO baselines, with minimum 1.28 km spacing. Public production embeddings use v2.1 whereas paper evaluations use v2.0. Difference: patch retention and validation/sample selection as a conservation decision, rather than generic representation quality or a new-target leaderboard.
3. Halabisky, Moskal and Hall, *Object-based classification of semi-arid wetlands* (Journal of Applied Remote Sensing 5, 053511, 2011). Full methods/results checked: NAIP-based object classification, point validation, and errors concentrated in very small wetlands. Difference: modern reusable representations, equal-budget sample allocation, and patch-level rather than point-only acceptance criteria. This classic is direct evidence that size-related errors are already known.

Additional standard/review source: Dronova, *Object-Based Image Analysis in Wetland Research: A Review* (2015; Remote Sensing 7, 6380–6413), initially search-checked; Olofsson et al., *Good practices for estimating area and assessing accuracy of land change* (2014; doi:10.1016/j.rse.2014.02.015), identified as an accuracy-assessment standard, full relevant passage still to check before citing in the paper. No directly matching factorial comparison of sampling design, embedding/spectral representation and small-object fidelity was found in this search range. This does not establish absence or novelty.

### C06: temporal aggregation of zero-shot demand forecasts

1. Ansari et al., *Chronos: Learning the Language of Time Series* (2024; arXiv:2403.07815v2). Full methods and benchmark results checked. Difference: explicit aggregation of forecast uncertainty at planning intervals, rather than usual per-step zero-shot accuracy.
2. Jeon, Panagiotelis and Petropoulos, *Reconciliation of probabilistic forecasts with an application to wind power* (2018 author preprint arXiv:1808.02635; related published title: *Probabilistic forecast reconciliation with applications to wind power and electric load*, EJOR, 2019). Full sections 3.2–3.3 and 5 checked; stacked/ranked/permuted sampling, temporal hierarchy, CRPS and point accuracy results. Difference is principally the use of zero-shot foundation forecasts; the generic aggregation/dependence insight is already known.
3. Nystrup et al., *Temporal hierarchies with autocorrelation for load forecasting* (2020; doi:10.1016/j.ejor.2019.07.061). Abstract and introduction checked through primary publisher text; full author manuscript download returned 403/404, so not treated as full-text evidence. Difference again largely model class. Recent 2025 *Long-Term Multi-Resolution Probabilistic Load Forecasting Using Temporal Hierarchies* was searched and abstract checked only.

Standard methods: seasonal/ETS/ARIMA baselines, probabilistic reconciliation, empirical copulas, CRPS and planning-loss evaluation. Candidate has an executable route but weak conceptual novelty.

### C08: interval-valued environmental table extraction

1. Wei et al., *General OCR Theory: Towards OCR-2.0 via a Unified End-to-end Model* (2024; arXiv:2409.01704). Full methods and experimental results checked. Difference: relation/interval decisions in public environmental tables, not merely text/formula recovery scores.
2. Smock, Pesala and Abraham, *PubTables-1M: Towards Comprehensive Table Extraction From Unstructured Documents* (CVPR 2022). Full methods/results checked: canonicalized cell/header annotation, structure recognition and functional analysis. Difference: uncertainty-preserving measurement interpretation, but table structure alone is already thoroughly studied.
3. Ouyang et al., *OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations* (CVPR 2025). Official benchmark repository and publication metadata checked; no claim from its paper's uninspected methods/results. It includes formulas, tables, text and reading order, with 2026 evaluation revisions documented in the official repository. Difference: targeted environmental interval-decision validation against source data.

Standard field practice: preserve detection limits/censoring and propagate intervals; substituting exact values for nondetects is a known problem. Main risk is measuring a known OCR concern using handpicked examples rather than changing a real QA decision.

## Pilot outcomes (step 4)

- P01 completed in 72.989 seconds. A public unauthenticated range read produced a 64×128×128 embedding array; all 16,384 pixels were valid and median decoded vector norm was 1.000084. The reference query returned 500 polygons and explicitly reported truncation. Main retrieval must paginate or retrieve a complete ID list. No mapping outcome was compared, and the pilot window will be excluded from main evaluation. The public index/metadata may be reused. Full-state archive HEAD showed 4,144,885,064 compressed bytes; it was not downloaded because selective public queries fit the storage limit better.
- P02 completed in 0.966 seconds as an access check. Official GenCast documentation states deprecation and that Earth Engine/BigQuery routes were deprecated July 29, 2026. No usable unauthenticated archive was established. No forecast was run; this is a failed feasibility check, not evidence about forecast performance.
- P03 completed in 2.595 seconds as an access-only check. OPSD data-package and tiny Chronos configuration were obtained. The package did not expose a top-level `licenses` entry in this check. Data reuse terms require further verification. No model inference or energy experiment was run. Feasibility is an estimate beyond these access facts.

P01/P02/P03 raw outputs, commands and plan/code commits are under experiments/. All three were capped at 900 seconds. No more than two ran concurrently.

## Original scoring (step 5, before critique)

Axes are impact (I), novelty within searched scope (N), non-obviousness (O), generality (G), unpredictability (U), feasibility (F) and verification strength (V), all 1–5. Main selection criterion is I+N+O+G+U; F/V are safeguards. Each following line explains all seven scores. Obvious candidates are capped at O=2. Unpiloted feasibility is explicitly an estimate.

| Candidate | I | N | O | G | U | F | V | Main total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| O1 | 4 | 2 | 2 | 4 | 3 | 2 | 2 | 15 |
| O2 | 4 | 2 | 2 | 4 | 2 | 3 | 3 | 14 |
| O3 | 4 | 3 | 2 | 3 | 3 | 2 | 2 | 15 |
| C01 | 5 | 2 | 3 | 4 | 3 | 2 | 4 | 17 |
| C02 | 5 | 2 | 2 | 4 | 3 | 2 | 4 | 16 |
| C03 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 21 |
| C04 | 4 | 1 | 2 | 4 | 3 | 2 | 3 | 14 |
| C05 | 4 | 1 | 2 | 4 | 3 | 2 | 2 | 14 |
| C06 | 4 | 2 | 2 | 4 | 3 | 4 | 4 | 15 |
| C07 | 4 | 2 | 2 | 3 | 3 | 2 | 2 | 14 |
| C08 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 17 |
| C09 | 4 | 2 | 2 | 3 | 1 | 2 | 2 | 12 |
| C10 | 3 | 2 | 2 | 3 | 3 | 2 | 2 | 13 |
| C11 | 4 | 2 | 3 | 3 | 3 | 1 | 2 | 15 |
| C12 | 3 | 2 | 2 | 3 | 2 | 1 | 2 | 12 |

- O1 — I4: heat-protection resources; N2: known infrastructure vulnerability; O2: first-look idea; G4: multi-system issue; U3: location-dependent interactions; F2: linked public outage/protection evidence unconfirmed (estimate); V2: action proxy needs validation.
- O2 — I4: evacuation access; N2: shared-route failure is established; O2: obvious network question; G4: route topology generalizes; U2: bottleneck effect predictable; F3: local/public simulation plausible (estimate); V3: real flood/route truth difficult.
- O3 — I4: continuity of food support; N3: joint calendars might reveal gaps; O2: obvious temporal audit; G3: programme-specific definitions; U3: real calendars unknown; F2: authoritative entitlement truth unavailable (estimate); V2: dates alone are inadequate.
- C01 — I5: multi-night protection decisions; N2: ECC and current heat-verification work are close; O3: equal-marginal persistence focus less obvious; G4: dependence beyond one model; U3: observed skill not predetermined; F2: pilot found no usable unauthenticated archive; V4: observed weather and strong copula controls if data secured.
- C02 — I5: adequacy decisions; N2: energy drought and wind forecast work already close; O2: straightforward energy extension; G4: cumulative risk broad; U3: empirical scheduling differences; F2: shared archive obstacle; V4: observed/reanalysis-based outcomes if archive secured.
- C03 — I5: map acceptance for small habitat protection; N4: precise factorial/object-fidelity comparison not found within search; O4: asks whether appealing smoothness plus pure-sample validation conceals habitat omission; G4: sampling/representation/patch-scale interaction beyond version, though direct data limited; U4: representation may help or harm small patches and intervention may fail; F4: actual embedding/reference pilot succeeded, spectral match still untested; V4: published aerial/lidar reference and matched controls, with known reference errors.
- C04 — I4: water-model updating; N1: close 2026 hydrology application already found; O2: straightforward embedding transfer; G4: broad catchment issue; U3: update gains uncertain; F2: full hydrology pipeline unpiloted estimate; V3: public streamflow but disturbance attribution difficult.
- C05 — I4: supply buffers; N1: recent accuracy/service and censored-demand work close; O2: standard inventory replay; G4: general censoring issue; U3: empirical effects; F2: no appropriate food-need truth (estimate); V2: sales/need mismatch.
- C06 — I4: energy planning interval; N2: probabilistic temporal reconciliation established; O2: expected forecast extension; G4: aggregation broadly applies; U3: exact rankings empirical; F4: data/model configurations accessible but full runtime/licence untested; V4: observed aggregate load and strong classical comparators possible.
- C07 — I4: entitlement continuity; N2: relation extraction established; O2: routine calendar audit; G3: policy definitions local; U3: real gaps unknown; F2: policy validation unpiloted (estimate); V2: no independent entitlement ground truth.
- C08 — I4: avoid incorrect environmental screening; N3: interval-specific decision audit not found in exact form; O3: relation risk rather than character accuracy; G4: information loss general; U3: real relative error empirical; F3: local model plausible, paired table data unpiloted estimate; V3: source-grounded comparisons possible, manual/source pairing bottleneck.
- C09 — I4: accessible routes; N2: geometry/access research close; O2: obvious route composition; G3: benchmark-specific geometry; U1: local versus path success follows definitions; F2: route truth not secured (estimate); V2: generic depth is an invalid proxy.
- C10 — I3: heritage monitoring; N2: reconstruction applications exist; O2: conventional feature-fidelity test; G3: artifact/imagery dependence; U3: empirical feature losses; F2: compatible before/after scans not secured (estimate); V2: imagery timing confounded.
- C11 — I4: benign environmental enzyme assay selection; N2: confidence/activity distinction known; O3: cross-family matching useful; G3: benchmark limitations; U3: correlation empirical; F1: no usable predicted-output/assay intersection (estimate); V2: missing negative assays.
- C12 — I3: recycling assay triage; N2: evidence-aware triage known; O2: routine evidence scoring; G3: domain-specific; U2: withholding unsupported claims partly tautological; F1: usable safe outputs not secured (estimate); V2: no outcome ground truth.

All scores are the session's self-assessment. No external evaluation has yet occurred. Candidates with F≤2 are not eligible for adoption without narrowing and re-evaluation. The next step is the one permitted critic call, after committing this file.

## Post-critique verification and score revisions (appended; original scores unchanged)

The required critique completed using `gpt-6-astra` on 2026-10-27. It introduced no ranking and none is used. Point-by-point adoption decisions are in critic-response.md. Its most consequential C03 concern was that object-aware sampling can receive a complete polygon frame for free. The final question treats oracle sampling as conditional on an already available frame and requires an imagery-derived proposal control. Equal pixel labels will never be called equal labour cost.

New sources personally checked: Yuan et al. (2026), *Wetland mapping from sparse annotations with satellite image time series and temporal-aware segment anything model*, arXiv:2601.11400 (full methods, experiments, label-density sensitivity and limitations); Maier-Hein et al. (2024), *Metrics Reloaded: Recommendations for image analysis validation*, doi:10.1038/s41592-023-02151-z (full relevant framework and small-object/metric/aggregation passages); Perez-Diaz et al. (2025), *Foundation Model Forecasts: Form and Function*, arXiv:2510.19345 (full aggregate/path-dependence/evaluation sections). Olofsson et al. 2014 and Dronova 2015 were also checked in full relevant passages. Small-object loss, MMU effects and point-versus-object validation are established facts, not this study's discovery.

| Candidate | Revised I | N | O | G | U | F | V | Main total | Reason |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| C01 | 5 | 1 | 3 | 4 | 3 | 2 | 4 | 16 | Close current probabilistic heat work and classic dependence methods; no usable archive. |
| C02 | 5 | 1 | 2 | 4 | 3 | 2 | 4 | 15 | Stronger operations-research overlap and missing adequacy inputs. |
| C03 | 5 | 3 | 3 | 4 | 4 | 4 | 4 | 19 | Generic size/metric concern is already known, so novelty and non-obviousness reduced. A factorial interaction with an explicit frame-information control remains decision-relevant and uncertain. Matching 2020 public reference/predictor data is available. |
| C06 | 4 | 1 | 2 | 4 | 3 | 4 | 4 | 14 | Recent forecast-form framework directly covers the main conceptual claim. |
| C08 | 4 | 2 | 3 | 4 | 3 | 3 | 3 | 16 | Review/abstention framing is established; a real paired corpus remains unsecured. |

## Selection (step 7)

Adopt C03, narrowed to: **How does training-point allocation interact with annual satellite embeddings versus seasonal optical predictors in recovering small mapped wetland patches at a common reference-upland commission-area constraint, and does the benefit require an oracle object sampling frame?**

Intended readers are wetland-mapping researchers and conservation/mapping agencies selecting training examples and acceptance criteria for inventory-based mapping. The decision is whether equal numbers of labels should be spread over pixels, homogeneous interiors, or candidate objects, and whether the extra object information is indispensable. The result does not establish wetland jurisdiction, actual population of omitted wetlands, human annotation cost, ecological benefit or current condition of an individual site.

Reason for adoption: the highest revised main-criterion total among considered questions, an actual data-access pilot, a precise factorial comparison with strong counterfactual controls, and a path to changing map validation and sample-allocation practice. Feasibility does not by itself determine the choice. C01/C02 are rejected for close known mechanisms and unavailable forecast trajectory evidence; C06 for directly matching conceptual prior work; C08 for a smaller and more predictable result with no verified corpus. O1/O2/O3 and remaining divergent candidates retain their original recorded rejection/screening reasons; none is silently substituted for a failed study.

The emerging question stays within C03: reference-vintage matching, oracle-frame disclosure and proposal-frame sampling refine its method, not its field or core problem. Source checking found four public 2020 image-reference projects: Prairie Pothole Watersheds 2 NRCS, VT Winooski Otter Creek, GLRI NY Area 1, and WI One Map. They are selected for contemporary reference coverage and contrasting landscapes, not observed mapping outcomes. Project geometries and selection data are preserved. The original Minnesota pilot region is excluded from evaluation. No main experiment has run.

Selection took less than the skill's 60-minute guide. Reason: the actual access pilots, closest-work full-text checks for all five finalists (with shared sources where appropriate), recent-paper search, and the complete different-model critique were finished promptly using batched tools. Extra elapsed time alone would add no evidence. The original scores, reductions after newly checked prior work, access failures and all rejected candidates remain preserved. Main experimental planning begins only after committing this selection.

## Pre-mortem (step 8)

Possible successful claim in one sentence: **Under the tested public wetland inventories, the apparent value of annual embeddings for retaining small patches depends on how training labels are allocated; a deployable proposal-based allocation either recovers the oracle improvement at a similar commission burden or exposes that the improvement relies on unavailable object information.**

Usefulness: agencies could alter label allocation and add mapped-patch recovery to map acceptance, or avoid paying for a proposed allocation that only works with an oracle frame. Either direction matters. This is not a promised positive result or an assertion that the issue has never been studied.

Why this exact comparison may be uncommon: the public reusable annual embedding fields are recent, and representation benchmarks usually use sparse pixel labels while wetland practitioners use object-based inventory concepts. The question lies at that interface. Classic small-wetland and image-validation work already covers much of the generic concern; that limits the contribution.

Three likely reviewer objections and planned response:
1. **Free oracle information / unrealistic labels.** Explicitly separate an oracle polygon-frame allocation from an imagery-derived proposal allocation, restrict both to training geography, count the initial proposal labels, and report annotation counts rather than labour cost. If only the oracle works, the operational claim fails.
2. **Reference error, dates and patch-definition artifacts.** Match 2020 imagery and embeddings to project-year metadata, dissolve touching wetland sub-polygons, count rasterization/erosion floors, evaluate boundary tolerance and partial patches, and claim agreement with mapped reference objects only. Report omission and map age limitations rather than infer true ecological recall.
3. **Known concern or one-representation benchmark.** Primary target is a pre-specified representation-by-allocation interaction, with matched sample positions, seasonal spectral predictors, conventional smoothing and multiple decoders. If all representations respond equally or the interaction is weak, report that result. No claim of universal embedding failure or a new statistical principle.

Metric/property check: mapped-patch coverage is a property of inventory agreement, not ecological completeness, object existence, labour cost or conservation outcome. Reference-upland commission area is an observable disagreement proxy for review burden, not measured human inspection effort. The plan will include actual validation-threshold replay and achieved test commission rates to expose the difference between standardized operating-point scores and deployable decisions.

## Safety pre-check (step 9)

This is public environmental mapping, not security, privacy, adversarial AI, biological intervention or dual-use testing. §12.5 applies. No personal/household/business records are used; outputs will be aggregate scientific measures and generic patch illustrations, with no named-and-blamed sites, organizations or rankings. Public inventories are planning references with known limits, not legal wetland delineations. AEF CC BY 4.0 attribution is required. USFWS metadata states access/use constraints are none and requests acknowledgement; Sentinel reuse is free/full/open with Copernicus attribution. Exact metadata, terms and dates will be recorded. No human participants or external publication. No matter requiring security disclosure has been identified.
