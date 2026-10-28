# Do annual satellite embedding distances improve matching of wetland inventory water regimes?

*Revised manuscript following one review by an AI agent. Frozen versions are recorded in the local Git tags.*

## Abstract

Wetland reference assessment needs hydrologically comparable sites to guide restoration targets and evaluation. We tested annual satellite embedding distances against 30 terrain, optical surface-water and drainage covariates using {{primary_wetlands}} wetlands in {{primary_windows}} convenience windows. Published National Wetlands Inventory water-regime labels were masked for query and candidate sites, with spatially separated training. {{primary_abstract_results}} {{pool_abstract_counts}} {{exploratory_abstract_results}} The endpoint is inventory-label agreement; field hydroperiod and practitioner benefit were not measured.

## 1. Introduction

Reference ecosystems provide benchmarks for assessing existing condition, setting targets, designing restoration and evaluating progress. For wetlands and streams, ecological reference assessment considers landscape position, hydrodynamics, geomorphology, hydroperiod and other characteristics that affect how a system functions. The US Environmental Protection Agency's compensatory-mitigation guidance describes this role of reference conditions and the need for comparable physical characteristics (Ainslie, Somerville and Monroe, 2023, p.83). Wetland hydrogeomorphic (HGM) assessment similarly connects geomorphic setting, water source and water movement to ecological processes, while recognising the limits of remotely derived indicators (Brinson, 1993, chapters 2–4).

These requirements matter when researchers or practitioners assemble candidate sites from maps. Similar vegetation or satellite appearance supplies useful evidence, but does not establish the full hydrological comparison. Annual satellite embedding products make another screening measurement widely accessible: a compact vector can summarize multiple satellite observations at each location. AlphaEarth Foundations and TESSERA provide precomputed global representations, reducing the need to build a sensor-processing pipeline for every downstream task (Brown et al.,2025; Feng et al.,2025). Similarity to reference vegetation has also been used to characterise forest-restoration trajectories (Heiman, 2026). This creates a concrete evaluation question for proposed wetland analogue searches: does representation distance add useful matching information beyond explicit public hydrological covariates?

The US National Wetlands Inventory (NWI) supplies a reproducible category endpoint for this question. Its temporarily flooded, seasonally flooded and semipermanently flooded regimes describe different typical growing-season water conditions (FGDC, 2013). These are interpreted inventory classes. The NWI mapping procedures caution that regime assignment is particularly uncertain, that long-term water-level information is often unavailable, and that a single image can reflect unusual wet or dry conditions (Dahl et al.,2020). Therefore agreement with an NWI regime cannot validate current hydroperiod or functional equivalence.

Our research question is: **Does adding annual satellite embedding distance improve wetland reference screening beyond public terrain and surface-water covariate matching, at fixed screening coverage, when vegetation subclass and geographic setting are controlled?** The study is a label-masked retrospective diagnostic. Where the relevant water-regime labels are already known, they can directly define a category filter; no operational advantage from masking them is established here. Potential applications include audits of outdated regime mapping and candidate searches where current inventory regimes are unavailable. Transfer to such settings, independently delineated wetlands and open-set inventories was not tested. Quantifying the increment here helps set evidence requirements, rather than demonstrating an operational benefit.

## 2. Prior work

Hydrological comparability is established reference-assessment practice (Brinson,1993; Ainslie et al.,2023). It is the motivation for the outcome, rather than a discovery of this study. Terrain-informed wetland remote sensing also has a substantial methodological basis. Askew et al.(2025) combined terrain descriptors, including height above nearest drainage (HAND), with multispectral observations and field measurements to study floodplain inundation. Our explicit covariates include HAND to avoid comparing embeddings only with local elevation and slope. The public surface-water product is another informative measurement, although its underlying optical method has documented limitations for small, short-lived or vegetation-obscured water (Pekel et al.,2016; JRC, 2026).

Brown et al.(2025) evaluated AlphaEarth features for mapping and biophysical prediction; Feng et al.(2025) evaluated TESSERA representations for several Earth-observation tasks. Ryan et al.(2026) compared embedding-based and conventional multisensor wetland vegetation mapping. Young and Keshav(2026) investigated the surface events retained by annual embedding products using decompositions and external reference data. Heiman(2026) examined forest-restoration trajectories using similarity to reference forest. These studies motivate the measurements but evaluate different endpoints from choosing a same-vegetation wetland reference with a matching inventory water regime. Vegetation classification, representation similarity and hydrological reference comparability require separate evidence.

A recent preprint by Sharma et al.(2026, version1, sections2.5–2.8 and3.1–3.2) evaluates binary wetland mapping with AlphaEarth, LiDAR and Sentinel predictors after excluding uncertain polygon-boundary pixels. Its endpoint differs from water-regime reference matching. Its boundary treatment also changes the population being evaluated; our common-cohort polygon comparison therefore holds eligible wetlands fixed when comparing sampling operators. The preprint has not been peer reviewed.

Close work also concerns inundation regimes directly. Abrahamson and Stegen (2026, **conference abstract only**) describe AlphaEarth-based classification of Everglades annual inundation regimes against gauge-derived EDEN labels and comparison with Sentinel-2 NDWI, including an unsupervised analysis. The full abstract was checked, but it reports no numerical performance estimates and is not a full empirical paper. It establishes a close research direction already being pursued; it does not supply outcome evidence for this screening task.

Rahman (2026, preprint version1, sections2.3–2.5 and3.1–3.2) evaluates how AlphaEarth predicts environmental variables, including terrain and hydrological maps, with random and spatial-block validation. This supports expecting overlap between representation and physical predictors, rather than assuming that embedding information is independent of the baseline. It does not establish a wetland screening increment.

Wetland inundation mapping predates embedding products. DeVries et al.(2017, sections3.1 and5.1–5.2) estimate sub-pixel surface-water fractions from Landsat, including small and partially inundated wetland features, while discussing remaining optical limitations. Lang et al.(2008, sections3.3–6) compare multi-temporal C-band SAR hydroperiod indicators with field inundation/soil moisture and NWI mapping in forested wetlands. Thus explicit radar-derived inundation is a relevant omitted predictor in our optical/terrain/HAND baseline. A related 2018 dataset poster is listed in DeVries’s author bibliography; only that listing, not its abstract or a SWaRe product validation, was checked, so it is a bibliographic pointer rather than supporting evidence.

The bounded literature and primary-source search is documented in `sources.jsonl` and `protocol/prior-work-candidates.md`. It included wetland reference condition, hydrogeomorphic classification, hydrological analogue/donor selection, satellite embeddings, wetland hydrology and ecological restoration similarity, including 2025–2026 work. {{close_work_search_statement}} This search does not establish absence of prior work outside its coverage.

Basin-scale hydrological prediction is a further important comparison. Ou and Zheng(2026, sections2.1–2.4 and3.1–3.3) combined spatially aggregated, annually changing AlphaEarth features with static catchment descriptors and meteorological forcings in a rainfall–runoff model. They evaluated temporal and held-out-basin prediction with multiple training seeds and related learned similarity to hydrological signatures. That study provides evidence for a hydrological use of satellite embeddings at a different scale, with different inputs and endpoints. Our label-agreement screening diagnostic cannot confirm or refute its streamflow results.

More directly, Qu et al.(2026, version2, section2.3 and ExperimentB) used standardized AlphaEarth cosine similarity to select donor basins for rainfall–runoff models. Their reported advantage for embedding-based donors shows that representation similarity has already been evaluated for hydrological transfer. Liu et al.(2026, sections2.1–2.2 and3.1–3.2) compared annual and multi-year spatially averaged descriptors, including augmentation of conventional attributes, in temporal and ungauged-basin prediction. They found benefits that depended on the evaluation setting. Our contribution is narrower: a controlled wetland inventory-category screening comparison that tests the physical baseline, feature controls and spatial measurement operators. It is not the first use of embeddings for hydrological similarity, and its results do not generalize to donor-basin streamflow prediction.

## 3. Methods

A **pair model** scores how likely a query wetland and a candidate reference are to share a regime from their covariates. A **category model** predicts each wetland’s probabilities for the three regime classes and compares those probabilities. A **candidate pool** is the set of eligible local reference wetlands. A **nontrivial matchable pool** contains both a matching regime and a different regime, as determined retrospectively from masked labels. **Physical comparators** are models using the stated terrain, optical surface-water and drainage covariates. Differences are expressed in percentage points (pp). A **paired window bootstrap** resamples the same geographic windows for both methods to describe uncertainty across this convenience panel. Spatial sampling refers to how existing maps are summarized near a point or across a polygon.

### 3.1 Data and population

The primary panel comprised fixed 16 km squares in {{primary_windows}} contrasting US settings. These are convenience windows, with no national sampling interpretation. The eligible codes were exactly PEM1A/C/F, PFO1A/C/F and PSS1A/C/F: persistent emergent, broad-leaved deciduous forested and broad-leaved deciduous scrub-shrub wetlands with temporarily, seasonally or semipermanently flooded regimes. All nine combinations are permitted by the official NWI code rules. Mixed classes and special modifiers were excluded; Pf denotes Palustrine Farmed and lies outside this population.

Polygons needed projected area 0.1–100 ha and an interior point at least 15 m from the boundary. The point was obtained by polylabel with 2 m tolerance. We retained at most 1200 eligible polygons/window, ordered by a trial-specific SHA-256 hash of their public object identifiers, without balancing regimes. The full eligibility accounting and original responses are archived. NWI imagery-project polygons supplied source-image years, including overlap and missing-date flags. {{input_accounting_results}}

After inspecting the primary panel's image dates, we fixed an **exploratory** supplementary panel of {{recent_windows}} windows using recent-project metadata alone. For six fixed anchors, we selected the nearest qualifying project with IMAGE_YR>=2020, sufficient interior area and separation from original windows; wetland counts, categories and matching outcomes did not choose the new centres. The complete algorithm and selected project records precede supplementary wetland retrieval in Git. The supplementary panel has separate fits and does not replace the original sites. Its landscapes and training sample sizes differ, so comparisons between panels cannot isolate a causal effect of inventory age.

### 3.2 Measurements

We used archived 2024 AlphaEarth Foundations Satellite Embedding V1 annual vectors and TESSERA v1.1-dclimate vectors. The published dimensions are 64 and 128 respectively. The latter identifies checkpoint `tessera_v1_1_aws_encoder.pt`; its public store publishes a specified subset of the model output. The exact AlphaEarth mirror checkpoint was not independently verified; the official catalogue describes production encoder v2.1 and related land-cover supervision. Consequently strict pretraining independence from related map information is not assumed.

For each wetland, we decoded the 3×3 native-grid pixels around its selected interior point, retained pixel centres inside its polygon and required at least five valid vectors. We averaged decoded vectors and normalized the mean for cosine methods. Full-vector decoders retained the magnitude of that mean. Quantization, scales, coordinates and masks are archived so these transformations can be recomputed. A direct-source TIFF transport optimization was adopted only after exact equality with an archived provider-VRT patch set; it changed no scientific input values.

The explicit baseline used {{hydro_feature_n}} covariates: bare-earth elevation, slope and topographic position; JRC water occurrence, recurrence, 2024 seasonality and spatial context; distance to occurrence>=75%; HAND; and polygon area. Numerical source windows and reprojected 30 m grids are bundled. The USGS 3DEP export requested the raw elevation function. The corrected JRC v1.5 release was used, with its documented collection-transition limitations. Its valid zero values are published non-water detections, not proof of absent water beneath vegetation. Physically out-of-range pixels were preserved in source windows and treated as missing in derived grids. HAND derives from a surface DEM and has its own canopy and drainage-model limitations. These measurements do not constitute a field HGM assessment.

### 3.3 Spatial design and matching

Each window was partitioned into 4×4 blocks of 4 km, with fold `(block_x+2*block_y) mod 4`. Across four rotations, one fold supplied queries, the next references and the remaining two nominal training wetlands. Training wetlands within 1 km of any query or reference point in the window were removed. Queries and references did not supply supervised labels, transformations or fitted statistics. Each wetland served as a query once; shared training/reference data mean the rotations are not independent repetitions.

Candidates shared the query's window and exact vegetation subclass and were at least 1 km away. We counted empty pools, single-regime pools, pools without the query's regime and nontrivial pools containing both a matching class and another class. These bounds describe the sampled pools. They do not establish that a real region lacks ecologically acceptable references.

Comparators were geographic nearest neighbour, standardized hydrological distance, a hydrological pair classifier and a hydrological regime decoder. Pair features were symmetric covariate means/differences, missingness indicators, geographic distance and vegetation/window indicators. Training pairs were sampled within training windows and vegetation, at least 1 km apart, with at most 30 partners per training wetland. The augmented pair models added AlphaEarth cosine distance, TESSERA cosine distance or both. The decoder scored reference compatibility by the dot product of predicted class probabilities. This is an uncalibrated compatibility score.

The primary learner was a random forest with 200 trees, max_depth=12, max_features=0.7 and min_samples_leaf=20 for pair learning or 10 for individual decoding. Seeds and pairs were fixed; no query-outcome tuning was performed. Imputation/scaling and representation centring/whitening used retained training data only. Raw, centred and whitened cosine neighbours and full-vector decoders supplied planned information/metric diagnostics. Decoder failure would not prove information absent from a representation.

Physical predictors were imputed with retained-training medians, using zero only where a median was unavailable, then divided by retained-training interquartile ranges. Ranges no greater than 1e-9 were replaced by one; missingness indicators were appended. For embedding transformations, let $v$ be the unit-normalized wetland mean, $\mu$ the retained-training mean and $C=Q\operatorname{diag}(\lambda)Q^\top$ its sample covariance. The centred vector is $v-\mu$. The whitened vector before normalization is $(v-\mu)Q\operatorname{diag}(\max(\lambda_j,\tau)^{-1/2})Q^\top$, where $\tau=\max(0.01\lambda_{\max},10^{-12})$. Cosine scoring normalizes the transformed vectors with a norm denominator at least 1e-12. The floor was fixed rather than tuned on query outcomes.

All individual decoders include the common vegetation and window indicators.
The standalone representation decoders therefore test the specified representation-plus-context
predictor, while hybrid decoders append the full mean vector to physical predictors
and those same indicators. They do not identify the representation's causal information
contribution independently of this model and context.

### 3.4 Evaluation and uncertainty

The risk–coverage distinction is established selective-classification terminology (El-Yaniv and Wiener, 2010, pp. 1606–1607). Here the loss concerns a reference match, and the acceptance set is fixed by a screening budget. We provide empirical conditional losses, without a prospective risk-control guarantee.

Each method first selected its highest-scoring reference, breaking ties by reference identifier. Within each window/rotation it retained the highest-confidence half of queries with nonempty pools, with query-identifier tie breaking. The primary loss was exact inventory-regime mismatch among retained queries. We pooled numerator/denominator across rotations within each window and then averaged window risks. We also report pooled risk, achieved coverage and 20%, 80% and full-coverage results. A two-percentage-point difference was a predefined descriptive benchmark, not a validated benefit or cost-effectiveness threshold.

Primary contrasts compare each single-distance augmentation with **both** the hydrological pair learner and hydrological decoder. A gain over only one comparator does not establish the stated increment. Paired bootstrap intervals resample windows 10,000 times,seed 18018. They describe variation across the convenience panel and omit field-label uncertainty, model-family uncertainty and national sampling uncertainty. We report all contrasts and no uncorrected multiple-comparison significance claims.

To distinguish reference ranking from query selection, we evaluated every method on each hydrological method's fixed 50% query screen, as well as at full coverage. Conditional nontrivial-pool results use the already-selected queries; labels do not trigger rescreening. Uniform-reference expected mismatch and a label-aware oracle are diagnostic bounds. Class-specific coverage, reference-choice overlap and score ties identify cases where majority classes, empty alternatives or identical decisions constrain interpretation.

### 3.5 Additional checks and records

{{robustness_methods_and_timing}}

The complete plans, amendments, source checks, failures, commands and commits are archived. One different model, OpenAI `gpt-6-astra` with requested xhigh reasoning, critiqued topic candidates on 2026-10-27 under the trial's planning exception. It did not write code, analyse data or draft this paper. All experimental measurements use public archived data and local computation. No human participants or practitioner outcomes were studied.

## 4. Results

{{primary_results}}

{{primary_table}}

{{pool_results}}

{{ranking_and_decoder_results}}

{{recent_results}}

{{robustness_results}}

## 5. Discussion

{{discussion}}

## 6. Limitations

The endpoint is interpreted inventory-category agreement, with source-image dates that vary by site. It does not validate current field hydroperiod, water source, groundwater exchange, ecological condition or restoration success. NWI mapping uncertainty and temporal landscape change remain potential explanations. Recent-source sampling reduces one concern but cannot provide field truth or isolate age from landscape and training differences.

Regional update guidance can adopt particular classification definitions and code conventions (Macleod, Paige and Kreiger, 2016, section5.3). We did not audit semantic uniformity across the projects and vintages represented in our windows. This is an additional reason to interpret exact code agreement and geographic transfer as inventory diagnostics rather than field hydrological equivalence.

The primary pool is restricted to selected unmodified codes, size/interior criteria and sampled local candidates. Unmodified codes do not establish an undisturbed reference condition. Geographic buffers concern selected points and do not remove every form of environmental dependence. The convenience panel and region bootstrap support no national ranking or prevalence estimate. NWI also supplies the polygon boundaries and vegetation subclasses used as inputs. Masking the water-regime field does not remove the inventory process that created those geometries, and this closed three-regime population does not test independently delineated, open-set wetland mapping. Conditional subgroup denominators and class-specific screening coverage must accompany aggregate performance.

Agreement with a site's current inventory class does not establish its desired restoration target, especially where current condition is degraded or the restoration objective differs. The diagnostic therefore supplies a measurement comparison rather than an ecological reference-selection recommendation.

Topic selection included one candidate critique by the specified external AI model, as recorded in Methods; the study was not designed without that consultation. The critique did not evaluate the finished paper or independently verify the results.

The comparison concerns the specified public covariates and fitted learners. The physical comparators contain no explicit SAR-derived inundation predictor. Soil properties, gauges, water budgets and a full field-based hydrogeomorphic assessment are also absent. “Beyond public hydrological covariates” therefore refers to this particular terrain, optical surface-water and HAND set. Frozen representations can contain related supervised map information, and their pretraining geography overlaps downstream evaluation locations. Two products are not independent replications of data collection. The conclusions concern the archived versions and years; they do not establish a universal property of all models, periods or locations.

Temporal support also differs. JRC occurrence and recurrence summarize its long observation record, while seasonality and annual embeddings describe particular years (JRC, 2026, release guide). The comparison asks whether an annual measurement adds to these available physical predictors; it does not isolate equal-duration satellite observations or compare sensors with equal information budgets. Holding the physical maps fixed in the alternate-year diagnostic preserves this limitation.

{{remaining_limitations}}

## 7. Data availability and reproduction

All selected raw patches, source raster windows, NWI responses and analysis outputs needed for offline verification are in the research directory. `VERIFY.md` provides the single regeneration entry point, environment setup, expected values, timeline checks and deviations. Network acquisition and the archived topic critique are separate from offline recomputation. {{verification_statement}} This is a re-run by the study author, not independent reproduction.

The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. JRC attribution: Source: EC JRC/Google. NWI/FWS, USGS 3DEP, ASF HAND and TESSERA attributions, reuse terms and the TESSERA licensing ambiguity are documented with retrieval dates in `sources.jsonl` and the data-licence record. The research did not publish data or contact third parties.

## References

{{references}}

## Appendix

{{appendix_results}}


## Revision history

After review by an AI agent (REVIEW-1), the final version applies the planned qualification rule explicitly, distinguishes planned secondary controls from exploratory additions, reports pooled estimates and tiny-window contributions, adds paired decoder uncertainty and five corrected-input seed fits, reports planned subgroups, narrows the physical-baseline claim, and fixes optional-refit bytecode handling. Pointwise decisions and evidence are in `review/response-1.md`. The first draft remains at tag `submission-1` and in `review/submission-1/`.
