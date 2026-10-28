# Revisiting reference locations for changes in Swiss declared crop-group diversity: a resampling benchmark

<!-- Manuscript source: numerical fields are filled from recorded analysis outputs. -->

## Abstract

{{REVISED_ABSTRACT}}

## 1. Introduction

Crop diversity describes both the crops present in an agricultural landscape and their relative areas. Researchers and policy staff use spatial indicators of this composition to study agricultural landscapes and support monitoring of agricultural programs. Public crop maps and harmonized declarations now make repeated measurement possible, but the suitability of a map for a diversity indicator depends on its errors at the scale of the intended application. A recent assessment using administrative declarations found that conventional crop-map accuracy summaries did not by themselves establish fitness for local landscape-heterogeneity measurement [CROP-FITNESS2026]. The practical decision is whether a monitoring programme should revisit reference locations and whether its evidence supports reporting an annual increase or decrease rather than an unresolved change.

Annual satellite embedding products offer a convenient source of predictors for such monitoring. They summarize remote-sensing observations in numerical vectors that can be used by relatively small downstream classifiers [TESSERA2025; AEF2025]. This makes it feasible to hold a classifier fixed and apply it to later years. It does not establish the precision of an area-composition change estimate. A monitoring system still needs a probability-based reference sample and an assessment of uncertainty [OLOFSSON2014].

One choice is whether to revisit the same reference locations or draw a new sample each year. Repeated and rotating samples have a long history in crop-acreage estimation [ROTATION-SAMPLE1981]. Their benefit depends on dependence between measurements at the same locations over time. For a model-assisted estimate, the relevant dependence is that remaining after prediction. Crops can also move between fields while landscape proportions change little. Consequently, neither label persistence nor pixel classification accuracy alone supplies the answer for a nonlinear diversity indicator.

We ask: **At a fixed annual reference-label budget, how reliably can model-assisted estimates based on frozen classifiers of annual satellite embeddings identify changes in the diversity of declared crop groups, and does revisiting reference locations improve inference relative to independent samples?** We compare established sampling and estimation procedures on public annual declarations. The target is change in spatial area composition. Crop rotations, crop species diversity, ecological outcomes and policy effects are separate quantities.

## 2. Prior work

The components of the comparison are established. Probability-sampled reference information and reference-based area estimation are central recommendations for land-change assessment [OLOFSSON2014]. Remote-sensing area-estimation studies have compared confusion-matrix adjustments, regression estimators and direct sampling at different sampling fractions [LI2014]. Estimating class proportions rather than predicting individual labels is also studied as quantification and label-shift estimation. Source-confusion correction relies on conditions such as stable class-conditional predictions and adequate source support [LIPTON2018]. Those conditions differ from obtaining fresh probability-sampled target references.

Repeated-sample theory already explains why covariance affects the variance of a change estimate [ROTATION-SAMPLE1981]. Design-based model-assisted change estimation for permanent and temporary forest-inventory plots, including external prediction models and first-phase sampling variance, is also established [MASSEY2015]. We use that principle as an interpretation and validation tool, rather than presenting the covariance identity as a new result.

Crop-map fitness for Shannon-based heterogeneity measurement is already an explicit research subject [CROP-FITNESS2026]. Cross-year crop classification with annual embeddings is also studied [SENEGAL2026]. The present empirical target is the behavior of a fixed reference budget, including uncertainty and abstention, when the estimate is a change in diversity rather than a single-year map or class area. A targeted search covered crop diversity, temporal transfer, quantification, model-assisted area estimation, permanent/rotating samples, and uncertainty in entropy, including recent work. The recorded search scope and unresolved full-text leads are in protocol/ and sources.jsonl; the search does not establish the absence of another study.

Entropy estimation introduces its own problems. Plug-in estimates can be biased, and normal or resampling intervals can be unreliable in small samples or near probability-simplex boundaries [PANINSKI2003]. We therefore measure interval coverage rather than assuming that a nominal level guarantees reliable reports.

Prediction-powered inference provides a related formulation of prediction correction, and PPI++ estimates a prediction weight to improve efficiency under its stated asymptotic assumptions [PPI-PLUS]. Stratified prediction-powered inference combines stratum-specific prediction weights and sampling allocation [STRAT-PPI2024]. Cluster-robust prediction-powered inference addresses dependence within independently sampled clusters and partially labeled clusters [CLUSTER-PPI2026]. These results motivate stronger comparisons; they do not directly guarantee finite-sample coverage for projected entropy changes. We do not propose a new estimator or sampling theorem.

Jessen’s agricultural sampling investigation compared matched with independent samples for year-to-year change and also examined interview error [JESSEN1942]. The expected direction of the main precision result therefore follows from classic successive-occasion sampling, rather than constituting a new principle. Operational examples already use repeated observations: Eurostat’s Land Use and Coverage Area frame Survey (LUCAS) has a mixed panel [LUCAS-METADATA2024]; USDA NASS area-frame surveys rotate portions of their segment samples [NASS-AREA2009]; and Swiss ALL-EMA (Arten und Lebensräume Landwirtschaft – Espèces et Milieux Agricoles) surveys sample squares in repeated cycles [ALL-EMA-METHODS]. These programmes have different units and ecological targets; the present pixel benchmark does not reproduce their designs or costs.

Van der Velde and colleagues calculate Shannon-based crop diversity from an Earth-observation crop map and farmers’ declarations and examine declaration-based changes over time [POLICY-DIVERSITY2025-READ, relevant full-text sections 2.1–2.3 checked in the indexed publisher article body]. That is direct current-practice context for this study; our comparison concerns fixed-budget reference sampling and reporting uncertainty, not a first demonstration of crop-diversity change monitoring. Lu and colleagues combine a small reference sample with remote-sensing map predictions for regression estimation, with related area-estimation material in their versioned appendices [LU-MAPS-V7]. Their inferential targets and assumptions differ from our fixed finite-population entropy change.

The failure of Wald intervals near rare-event boundaries is established; Brown, Cai and DasGupta’s author preprint documents erratic binomial interval coverage even beyond extreme boundaries [BROWN-WALD1999, introduction, pp. 1–2]. Our zero-width intervals are an application-specific manifestation, not a newly discovered general failure. Further reviewer-identified bibliographic leads—Patterson (1950, successive sampling), Basharin (1959, entropy estimation), Hutcheson (1970, comparing Shannon diversity) and Cochran’s sampling textbook—were not checked in full text in this study and are not cited as supporting evidence. Their recorded access limitations remain in sources.jsonl and review/response-1.md.

## 3. Data and methods

### 3.1. Reference declarations and spatial populations

SwissCrop25 provides annual labels from the Agricultural Cultivated Areas dataset (Landwirtschaftliche Nutzfläche, LNF), which compiles cantonal agricultural land-use declarations, together with a published agronomic hierarchy [SWISSCROP25]. Its country coverage is complete from 2021 onward. Declarations describe the intended primary crop; the reference is not an independent observation of realized harvest use. The public dataset contains no personal or farm-identifying attributes [SWISSCROP25-CARD].

We use the pinned dataset revision {{SWISS_REVISION}} and years {{YEAR_RANGE}}. Fractional source-code coverage is aggregated to the published fine hierarchy before assigning the category with largest fractional coverage, then mapped to its published broader parent. Unknown coverage competes with known categories and can produce a missing label. The primary hierarchy includes declared arable, grassland and permanent agricultural groups. {{TAXONOMY_COUNTS_SENTENCE}}. The outcome is diversity of these groups, rather than a count of biological species.

Candidate landscapes are 5.12 km squares containing 4×4 dataset tiles, separated by one tile-width gaps. A fixed seed orders candidates, and 25.6 km supercells define spatial training, calibration and test pools. Eligibility requires label-tile coverage in all years and at least 10% stable agricultural support. Selection does not use diversity changes or classifier output. The complete candidate order, exclusions and failed attempts remain in data/selection-results.jsonl. {{SELECTION_COUNTS_SENTENCE}}.

For each landscape, a uniform sample of 4,096 distinct 10 m agricultural reference pixels is taken from the support that remains agricultural throughout the five years. This is the finite population for the main reference-sampling experiments. Common valid features are required in both representations: in 2021 for source training/calibration, and across all five years for test locations. {{FINAL_POPULATION_SENTENCE}}. The primary estimand is conditional on that stable support and sampled population, and is not a national estimate. The complete declarations are used as a benchmark reference against which simulated limited samples can be evaluated; where these declarations are already available, this experiment does not establish a need to replace them with a small audit. The five-year agricultural mask is supplied to every method and its construction is outside the annual audit-label budget.

A possible application is map-based crop-diversity monitoring where complete declarations are unavailable, or an independent check of declared versus observed crops using a small photo-interpreted or field reference sample. There, one reference label would classify the crop group at a sampled point in one year, and revisiting would retain that point. It would not necessarily mean one parcel, one farm visit or one independent interpreter decision. Here a label is a database reading at a 10 m point within a fixed finite population of approximately 4,000 locations per landscape, with error-free repeatability and a five-year agricultural frame supplied in advance. Field/photo errors, parcel clustering, changing eligibility, travel, interpretation time and frame construction would require additional designs and costs. Where complete trustworthy declarations already exist, this benchmark does not establish a need to sample them.

### 3.2. Annual predictors and fixed classifiers

The representations are {{TESSERA_IDENTIFIER}} and {{AEF_IDENTIFIER}}, with {{REPRESENTATION_DIMENSIONS}} dimensions respectively. We use native 10 m pixels, published dequantization and correct raster orientation. Numerical input extracts and their provenance are retained. Coordinates are interpreted from the public tile geometry as pixel corners and shifted to cell centers; decoder and raster-index checks are documented in protocol/implementation-notes.md. {{INPUT_VALIDATION_SENTENCE}}.

Separate multinomial logistic classifiers use 2021 training landscapes, source-only standardization, L2 regularization C=1, a maximum of {{LOGISTIC_MAX_ITER}} iterations and tolerance 10^-5. Their parameters are then frozen for later years. Calibration landscapes supply a held-out 2021 class-conditional prediction matrix for a zero-new-label comparison. Test landscapes never train or calibrate the classifier. Classes absent from training receive zero predicted probability and remain in the target reference; their mass is reported. Initial source fits used {{INITIAL_LOGISTIC_MAX_ITER}} iterations; {{INITIAL_NONCONVERGED_FITS}} of {{SOURCE_FIT_COUNT}} reached that limit. A recorded numerical revision increased the limit without changing regularization, tolerance or data, before inspecting target changes. All revised source fits converged and the originals remain available. This is a retrospective evaluation using releases available in October 2026.

Zero-new-label point comparisons are hard class counts, average predicted probabilities, constrained source-confusion adjustment with a 10^-6 prior regularizer, and no change. These point estimates have no claimed 95% reporting interval. “Zero new labels” means zero additional target-audit labels, conditional on the fixed reference frame and previously trained/calibrated models; it does not mean zero total reference information. {{CLASSIFIER_DIAGNOSTICS_SENTENCE}}.

### 3.3. Reference sampling and estimation

For a fixed landscape population, p_tc is the proportion of reference group c in year t. Shannon entropy is H(p_t)=−Σ_c p_tc ln(p_tc), with 0 ln 0=0. The change is ΔH=H(p_b)−H(p_a). Its exponential is the ratio of effective numbers of the specified groups.

Primary contrasts are 2022→2023, 2023→2024 and 2024→2025. Each annual sample contains n∈{32,64,128,256,512} reference observations. The revisited design uses the same uniformly sampled locations in both years; the independent design samples separately without replacement each year. A two-year contrast uses 2n labels. We simulate 500 samples per condition with saved common random draws. These are resampling experiments on public data, not measurements of human auditors or travel costs.

The direct estimator uses sample proportions. The model-assisted difference estimator adds the sample mean prediction residual to the full finite-population prediction mean:

\[
\widehat p_{tc}=N^{-1}\sum_{i\in U}\widehat q_{itc}
 +n^{-1}\sum_{i\in S_t}\{1(Y_{it}=c)-\widehat q_{itc}\}.
\]

With predictions fixed before sampling, the unprojected proportion estimator is design-unbiased. If a vector lies outside the probability simplex, Euclidean projection is used before taking entropy. Projection frequency and magnitude are retained. Neither projection nor the entropy transformation preserves exact unbiasedness.

Numerical cleanup is applied consistently; the projection flag counts a raw component outside [0,1] by more than10^-10. The0.01 change and0.05 entropy context cutoffs are descriptive, not established policy-relevance thresholds.

The original nominal 95% intervals use an estimated entropy gradient at the projected proportions, with the prespecified 10^-6 numerical floor. This rule does not apply the projection Jacobian; a later exploratory comparison does. A sample influence value is the gradient dotted with the observed label minus prediction; direct estimation uses zero prediction. The revisited-design standard error uses the sample variance of the difference between year-specific influences. Independent-design variances are added. Both use the finite-population correction (1−n/N)/n. A direction is reported only when its whole interval excludes zero, with a 10^-10 numerical comparison tolerance. Coverage, reporting frequency and incorrect-direction reporting are measured against the saved reference change.

For interpretation, we also compute population influence variances using known reference proportions and the same clipped gradient. The paired variance equals the sum of marginal variances minus twice their covariance. This diagnostic concerns a fixed linearized proxy and is not an exact entropy variance at a simplex boundary. It is not used in an operational interval. The reported minimum-detectable-change diagnostic uses a normal approximation for 80% power and is not a measured power guarantee. Exact enumeration on a saved six-point fixture checked the proportion and variance code, including census recovery and constant-predictor equivalence. This was a same-session software validation.

### 3.4. Summaries and checks

Each test landscape and transition receives equal weight. Monte Carlo standard errors describe simulation precision on this benchmark. Repeated transitions from one landscape are not treated as independent geographic replications. We retain all eligible cases, including near-zero changes, single-group populations, absent source classes and degenerate influence variances.

The reference values and predictions are treated as fixed; randomization is the probability-sample draw. This design-based calculation does not assume that neighboring agricultural pixels are independent biological observations. Sampling fields or clusters of pixels would require the corresponding design variance, and was not measured here. The original simulations draw each two-year contrast separately; their intervals are pointwise and do not establish simultaneous annual-monitoring coverage. The no-change point baseline is assessed under the same squared-error loss, without interpreting a zero prediction as evidence that change is absent. Conditional wrong-direction frequency among reported intervals is descriptive; a nominal95% confidence interval is not a95% posterior probability of a correct direction.

{{COMPLETED_ROBUSTNESS_METHODS}}

{{ADDITIONAL_GEOGRAPHY_METHODS}}

{{PROJECTION_METHODS}}

{{REVIEW_METHODS}}

The original plan was committed before main data acquisition. A prospective revision removed unnecessary future-feature requirements from source-only training/calibration before any outcome analysis. A further prospective supplement specified full native-pixel population checks to assess the main finite-population approximation. The timeline and all changes are retained in Git and protocol/. {{DEVIATIONS_SENTENCE}}.

## 4. Results

{{RESULTS_GENERATED_TABLES_AND_TEXT}}

## 5. Discussion

{{DISCUSSION_WRITTEN_AFTER_RESULTS}}

## 6. Limitations

The reference measures declared primary use, with known uncertainty about realized harvest use. Classification of subpixel mixtures, unknown coverage and registration can affect the reference and predictors. The original coverage deficit and size of the revisiting gain condition on perfectly repeatable declaration labels. The post-review synthetic sensitivity is not an estimate of field or photo-interpretation error and does not validate an interval under measurement error. A fixed agricultural support omits changes in declared extent. The main experiments condition on sampled finite populations; {{CENSUS_LIMITATION_SENTENCE}}. The landscapes are a seeded convenience benchmark from available complete data and do not constitute a representative probability sample of Switzerland or other agricultural systems.

Only the specified representations, downstream models, taxonomy levels, released data and period are evaluated. Both representations share Earth-observation inputs. Their pretraining exposure to geography and years is not established as held out, and the public mirror does not expose a complete production-model training history. Training data and fitted maps are fixed for reference-sampling inference; uncertainty from possible alternative training datasets is not estimated. The experiment supplies a stable agricultural frame defined with all five reference years. Its cost and availability are not included in the audit budget, so a practical application that must estimate changing agricultural extent needs an additional design. Pixel observations also differ from field visits or parcel annotations; their information and costs need not scale as 2n.

Changing the agricultural support changes the estimand, the class composition, turnover and signal magnitude together. The stable-arable supplement therefore establishes a boundary of the aggregate observation, not a causal attribution of every coverage difference to permanent grassland. The selected arable subset also has fewer landscapes. Simulations conditional on these references cannot establish calibrated inference for another country, reference product, sampling design or future period.

Approximate entropy intervals can fail at small class proportions or simplex boundaries. Empirical coverage and projection diagnostics are therefore central to the results. Topic selection consulted one critique by another model ({{CRITIC_MODEL}}), under the recorded trial procedure. No measured effect on users, field-visit cost, ecological outcome or policy result follows from this computational study. {{REMAINING_UNFINISHED_CHECKS}}.

## 7. Reproduction

VERIFY.md gives a single entry point that regenerates the main numerical tables and figures from saved data without network access or AI API calls. It also describes source/input checks, optional refitting and retrieval, expected claim values, the timeline, deviations, and the clean-copy verification performed by this session. That rerun is not independent reproduction.

## References

{{REFERENCES_FROM_VERIFIED_SOURCES}}

## Appendix

{{APPENDICES_AND_PROCESS_DISCLOSURE}}


{{REVISION_HISTORY}}
