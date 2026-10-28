# Topic selection — chronological working record

Started after reading the full copied skill. No topic has yet been adopted. All twelve initial technology-derived candidates and three obvious candidates are in `research_log.md`. No past trials were consulted. Dates below come from `events.jsonl`.

## Six-point checks of all twelve technology-derived candidates

The numbered points correspond to step 2.6, in order. These are pre-selection assessments, not results. Constraint origin for every initial candidate: **no**; feasibility constraints subsequently screen the ideas.

### C1 — joint heat warnings

1. Existing numerical ensembles suffice for generic heat warnings; the question is retained only about *learned* joint forecasts and their decision utility.
2. GenCast and FGN already test pooled spatial fields and cyclone joint probabilities. The potential difference is sustained, concurrent heat; a generic “marginals are insufficient” claim is already known.
3. Joint dependence matters by definition, but comparative event reliability and its size cannot be computed without forecasts and observations. Shuffling is a diagnostic, not the only baseline.
4. ERA5/HRES are public verification targets, not mortality observations; heat-event skill must not be called health benefit.
5. Local full inference is infeasible; published historical forecasts require an access check.
6. Positive: retain and validate joint trajectories for surge planning. Negative: do not infer event reliability from instantaneous CRPS alone.

### C2 — nutrient-application windows

1. The generic weather-window study can be done with old ensembles; learned forecasting is not necessary unless the question explicitly compares the new joint distributions.
2. Runoff-risk tools and rainfall-based fertilizer scheduling already exist, including a 2025 SWAT evaluation.
3. Without observed runoff, a constructed weather-window metric risks making the main result a property of the chosen threshold.
4. Precipitation can be verified, nutrient losses cannot be validated with these data.
5. Same uncertain access as C1.
6. Either result could affect window-selection methods, but cannot yet justify changed nutrient advice. **Discard initial formulation: capability decoration and unvalidated pollution proxy.**

### C3 — ecological reference comparisons

1. Bad post-treatment controls can be demonstrated without new technology, making the initial formulation too close to known causal bias. **Revise**, rather than claim that known bias as a discovery.
2. BACI already handles natural variation. Heiman (2026) proposes cosine similarity to secondary-forest references in annual learned embeddings. This suggests a narrower measurement question below.
3. Reference-year dependence is mathematically possible, but its size and sign relative to observed forest-recovery trajectories are not fixed by the metric.
4. No AI annotation is needed; independently published burn history and land-cover maps can define disturbance and stable-class controls. Stable class does not prove no ecological change.
5. Published annual embedding subsets are available without inference; access must be piloted. A second public embedding system may test whether the result is limited to one representation.
6. Positive sensitivity: report reference-year uncertainty or use same-year controls. Negative sensitivity: fixed references may be adequate under the tested conditions.

**C3 revision before pilots/main plan:** How stable are directions and magnitudes of satellite-embedding forest-recovery scores to the reference forest's calendar year, and can contemporaneous controls remove common temporal variation without removing the disturbance/recovery signal? Method: annual forest embeddings around independently mapped fires, stable-class controls, all fixed reference years, concurrent references, and conventional vegetation indicators. This is a measurement study, not a causal evaluation of restoration programs. It tests a proxy that restoration researchers are beginning to use. Reason: the full-text methods/results of Heiman (2026) exposed a concrete reference-choice question; the initial post-treatment-matching claim was too predictable and already addressed by BACI logic.

### C4 — persistent versus transient flood water

1. Event radar images and long-established surface-water histories can do most of the study without embeddings.
2. Sen1Floods11 explicitly distinguishes permanent and flood water; foundation-model flood mapping has already been evaluated.
3. Annual summaries cannot be expected to recover short event timing; a failure is largely predictable from aggregation.
4. Labels are public and verifiable, but may share satellite inputs with embeddings.
5. Data subsets potentially runnable.
6. Could constrain the use of annual embeddings for recovery mapping, but largely reconfirms a known resolution limit. **Discard initial formulation: known concern and technology decoration.**

### C5 — ramp slopes

1. Sparse uncalibrated geometry is the proposed new instrument; calibrated stereo already provides a strong comparison.
2. DUSt3R benchmarks cover geometry, and access standards specify surveyed slopes; a ramp-specific abstention test may differ.
3. Absolute scale/gravity ambiguities predict some failures; they cannot themselves be the empirical discovery. Slope relative to a defensible vertical reference is needed.
4. Surveyed ramps are required; generic depth benchmarks are inadequate ground truth for access.
5. No licensed ramp-specific longitudinal geometry found; running on generic ETH3D would answer a different question.
6. Results could change triage decisions in either direction. **Do not advance without genuine ramp ground truth.**

### C6 — heritage surface loss

1. Uncalibrated reconstruction enables archival-photo comparisons; calibrated surveys remain essential truth.
2. Photogrammetry and scanning are standard heritage recording methods (Remondino 2011).
3. Lack of physical scale makes certain absolute-loss comparisons underidentified; avoid presenting that fact as an experimental finding.
4. Repeated independent surveys would validate change.
5. No suitable repeated, licensed geometry obtained at this stage.
6. Both outcomes affect use of archival photos. **Discard: no validated change dataset and ambiguity at the core of the claim.**

### C7 — variant reassessment

1. New context-based scores create a new ranking option, but temporal variant reassessment as a question is not new.
2. ReVUS (July 2026) directly addresses the uncertain-to-resolved transition, gene-level circularity and imbalance-aware evaluation. EVEE supplies a newer probe, not a new problem.
3. Relative ranking cannot be hand-calculated; using a ClinVar-trained score after the outcome freeze can contaminate the evaluation.
4. Variant-level ClinVar transitions are checkable; a public label is not disease ground truth.
5. EVEE data are 35 GB but column projection may fit; original Evo scores are not present in the unscored EvoEval release.
6. Both outcomes affect reassessment-priority validation. **Do not adopt initial formulation: close prior work already asks it, and changing only the predictor is insufficient.** Retain for explicit prior-work comparison/critique because it was a high-potential candidate before the 2026 search.

### C8 — conservation genetic load

1. Long-context likelihood is a new option; generic assembly-error bias can be studied without it.
2. Genome erosion reviews already discuss reference, annotation and demographic confounding.
3. Degrading sequences by construction would make some score shifts predictable; real fitness consequences remain unknown.
4. Independent load/fitness labels for threatened taxa are not available here.
5. Suitable public scored variants were not located.
6. Might change score comparability, but not defensible conservation actions. **Discard: no validation and capability partly decorative.**

### C9 — acoustic species accumulation

1. Open vocabulary changes the set of possible outputs; generic false-positive accumulation is already studied for fixed classifiers.
2. NatureLM evaluates identification/detection, while BirdNET field evaluations show species-specific false positives. The difference would be unbounded taxonomy under increasing effort.
3. The possibility of false-richness accumulation is obvious; relative size, saturation and verification priorities are empirical.
4. Fully labelled soundscapes could verify emitted labels; incomplete annotations can turn genuine secondary species into apparent errors.
5. The released model needs gated Llama 3.1 8B access; the full benchmark is about 180 GB. No saved per-record predictions were found in the public repository tree. No gated model access will be requested for this optional candidate.
6. Both outcomes affect allocation of annotation versus recording effort. **Currently not feasible; no adoption without reusable outputs.**

### C10 — welfare and detectability

1. Broad descriptions are the new instrument, but welfare inference remains a distinct supervised problem.
2. Briefer's 2012 review details vocal-emotion mechanisms and the need for independent affect validation.
3. Recordings lacking animals cannot establish absence of distress; that is a definitional non-identifiability, not a novel finding.
4. No synchronized, independently validated welfare labels located.
5. Same gated/inference issues as C9.
6. Both outcomes might affect screening design, but the desired property is not measured. **Discard: unvalidated proxy and predictable ambiguity.**

### C11 — reservoir threshold passage

1. First-passage forecasting predates foundation models; the new option is transferring a learned sequence distribution without local fitting.
2. Water4Power forecasts reservoir volumes; classical reservoir first-passage probabilities were studied by Fujita et al. (1996); recent Chronos hydrology applications exist. The possible difference is calibrated warning probabilities under transfer, versus point-score claims.
3. Marginal accuracy does not imply first-passage calibration, but the amount of useful warning and comparison with domain baselines are empirical.
4. Public daily storage validates crossings; statistical low-storage thresholds do not automatically equal operational drought rules.
5. Small public models and government daily series appear feasible; pilot needed.
6. Positive: assess transferred path forecasts as screening support. Negative: require domain models and action-specific calibration. **Retain, with modest novelty.**

### C12 — SNAP caseload warnings

1. Transferable forecasting creates a cold-start option; reporting delay and revision effects can be measured with older models.
2. State-level caseload models and official forecast-risk reports already address policy changes; a 2026 panel-data SNAP forecasting paper is close.
3. Without policy covariates, predictable errors at known rule changes could dominate; a constructed shortage proxy would not establish unmet need.
4. Aggregate counts are checkable; need consistent archived vintages rather than present tables pretending to be contemporaneous.
5. Data/model access plausible, vintages not confirmed.
6. Results could change update schedules, but would not alone change assistance policy. **Discard current formulation: capability decoration and scope too close to generic forecasting.**

## Step 3: top-five prior-work checks

The five candidates selected for detailed comparison are C1, C3 (revised), C7, C9 and C11. This list reflects potential scientific value; C7 and C9 already have serious novelty/feasibility objections. It is not a claim that all are eligible for adoption. Search range: public scholarly and primary sources, including 2025–2026 papers/preprints, official dataset/tool documentation, and older field standards. Synonyms searched include joint/spatiotemporal extremes, pooled forecast verification, BACI, reference ecosystems, temporal measurement invariance, temporal holdout, variant reclassification/circularity, species accumulation/imperfect detection/false positives, reservoir first passage/low storage/drought warning.

| Candidate | Three closest named works and difference |
|---|---|
| C1 | Price et al., *Probabilistic weather forecasting with machine learning* (2024): includes joint pooled and wind-power tests, but not this sustained/concurrent heat decision. Alet et al., *Skillful joint probabilistic weather forecasting from marginals* (2025): directly addresses joint structure; proposed difference is health-warning events rather than generic pooling. Hajat et al., *Heat–Health Warning Systems: A Comparison of the Predictive Capacity of Different Approaches to Identifying Dangerously Hot Days* (2010): establishes trigger sensitivity, not learned-ensemble joint skill. Closest two full texts: GenCast methods/results and FGN Sections 3–5 checked. |
| C3 | Heiman, *Characterizing Brazilian Atlantic Forest Restoration Outcomes with Geospatial AlphaEarth Embeddings* (2026): proposes cosine reference trajectories; our revised question tests reference-year sensitivity and negative controls rather than proposing another success score. Meroni et al., *Remote sensing monitoring of land restoration interventions in semi-arid environments with a before–after control-impact statistical design* (2017): explicitly controls natural variability; our contribution must be the empirically unresolved behavior of learned reference geometry, not the need for controls. Brown et al., *AlphaEarth Foundations: An embedding field model for accurate and efficient global mapping from sparse label data* (2025): mapping/representation evidence, not reference-conditioned recovery validation. Closest two full texts: Heiman Sections 2–5 and appendices; Meroni Sections 4–6 checked. |
| C7 | Gür, *ReVUS: A Temporal-Holdout Benchmark for the Reclassification of Variants of Uncertain Significance* (2026): directly overlaps question and gene-disjoint validation; difference currently only the score family, insufficient. Pearce et al., *EVEE: Interpretable variant effect prediction from genomic foundation model embeddings* (2026): reports cross-sectional and functional-assay performance; temporal queue comparison would differ, but overlap with ReVUS remains. Deignan et al., *Points to Consider in the Reevaluation and Reanalysis of Genomic Test Results* (2019): establishes actual curation decision. ReVUS full methods/results checked; EVEE initially abstract-only because full-text request returned 403/429; no access restriction will be bypassed. Need a legitimate public full-text copy or record this check incomplete. |
| C9 | Robinson et al., *NatureLM-audio: an Audio-Language Foundation Model for Bioacoustics* (2025): open identification/detection benchmarks, not survey-effort accumulation. Kahl et al., *BirdNET: A deep learning solution for avian diversity monitoring* (2021): fixed species classes, not open-vocabulary taxonomy. *Evaluation of an autonomous acoustic surveying technique for grassland bird communities in Nebraska* (2024): field false-positive/detectability assessment, making generic concern non-novel. NatureLM methods/results read from downloaded full PDF; acoustic field study full-text retrieval requires checking content (one downloaded PMC page may be an access interstitial). |
| C11 | Ansari et al., *Chronos: Learning the Language of Time Series* (2024): zero-shot probabilistic trajectories and broad benchmark, not reservoir warning calibration. Kuzma et al., *Using a Deep Learning Framework to Forecast Reservoir Water Availability in India* (2023): 90-day reservoir-volume forecasts; proposed difference is transferred first-passage risk rather than site-specific meteorological modelling. Fujita et al., *Numerical Analysis of Storage-Level Probability Distribution and First Passage Probability in a Reservoir with Correlated Inflows* (1996): establishes first-passage as an old water-resource problem, limiting conceptual novelty. Chronos framework/evaluation full text checked. WRI technical-note full methods/results must be downloaded from the link, not inferred from landing-page summary. |

Sources and check ranges will be completed in `sources.jsonl`; not-found claims apply only to this search range. No assertion of novelty is made.

## Step 4: pilot plan fixed before pilot results

Pilot candidates: C1, revised C3 and C11, chosen for remaining plausible differences and testable data routes after the initial gates. Each pilot has a strict 900-second process timeout (less than the 30-minute overall experiment limit). At most two pilots run concurrently. They only check access, scale and a small technical calculation, not main hypotheses.

- C1: inspect documented historical-output access and public catalogue; do not use paid BigQuery, account credentials or generate a full forecast. End if reusable outputs cannot be obtained without new permissions.
- C3: retrieve public embedding metadata and one small geographic subset for two years; check dequantization, vector norms, masks, repeatable coordinates, and whether a second embedding dataset is accessible. No recovery effect will be claimed from the pilot. If pilot pixels are used later, identify them explicitly in the main plan or exclude them.
- C11: retrieve one public daily reservoir series and check time/units/missingness; run a tiny pretrained model only if dependencies and weights fit; no main risk estimates. End rather than request new accounts.

Pilot outputs and commands go under `experiments/pilot-*/`; all failures remain. The scoring table is not fixed yet, and no critique call has been sent.

## Pilot outcomes and further narrowing (before scoring)

- **C1:** no adequate anonymous historical ensemble archive obtained. FGN full text points to Earth Engine/BigQuery; no paid query, new account or local forecast generation attempted. `experiments/pilot-c1/` records an access audit, not a forecast experiment.
- **C3:** the first asynchronous read failed on the local CA configuration; a retry with the installed trusted certificate bundle retrieved valid 64-dimensional AlphaEarth vectors for two years. The second dataset, TESSERA v1.0/vultr, also returned finite 128-dimensional vectors for two years, but writing its metadata summary failed on a non-JSON Dataset object. The vectors were saved; a recovered summary was computed without another download. All failures and exit codes remain. Total actual pilot process time is far below 15 minutes; all C3 access and scale decisions ended by 08:52:36 UTC, within 15 minutes of the first C3 process start at 08:38:01 UTC. The pilot forest coordinate and its 10 km neighborhood will not enter the main study. Annual vectors are not identical, but this is not evidence of a recovery-score problem.
- **C3 labels/scale:** the public, licensed AlphaEarth supplemental evaluation archive contains explicit before/after human-interpreted LCMAP labels for 2,320 adjacent-year pairs, including 803 pairs involving tree-dominated cover. This permits a stronger direct check of a score against real class transitions. Full original ScienceBase history could not be accessed (403); it will not be reconstructed or assumed from the paired derivative. The data are benchmark samples, enriched for change, not prevalence estimates for US forests. Original-source and derivative licences are checked in the metadata and embedded READMEs. The full TESSERA licence passage was checked after its pilot retrieval; this sequencing deviation is recorded in E0027. Use is permitted by CC0, and no unlicensed reuse occurred.
- **C11:** a public RISE query returned 365 observed daily elevation values for a bounded 2020 date range, with unit/provisional-data documentation. This confirms access, not storage-model inference or first-passage calibration. No pretrained forecast was run, so model feasibility remains an estimate.

**C3 refinement after pilot scale check, before critique or main results:** Test whether concurrent forest references and BACI-style control adjustment improve the validity of embedding reference scores for *labelled tree-cover transitions* while reducing calendar-reference sensitivity. Include fixed first-year and last-year references, a pooled reference, concurrent references, control adjustment and a supervised discrimination baseline. Do not call tree-cover gain ecological restoration success. Stable tree-dominated cover is a measured negative-control class, not proof of ecological invariance. Calendar anchoring has an algebraic component, so its existence cannot be presented as an unexpected empirical discovery. The nontrivial test is whether corrections retain discrimination of real transitions across two different embedding systems, years and spatial holdouts. This narrows the original multi-year post-fire recovery idea to the actual, verified paired-label evidence while preserving the reference-measurement question.

## Step 5: original scoring table, fixed before critic

Each cell gives score (1–5) and a reason. Primary total = impact + novelty + non-obviousness + generality + unpredictability; feasibility and verification are constraints/additional assessments. These are this session's self-assessments, not external evaluation. For candidates without an actual pilot, feasibility is explicitly an estimate. Gated candidates remain in this record and in the top-five critique so their weaknesses are explicit; scores do not override the step-2 exclusion reasons.

| ID | Impact | Novelty | Non-obviousness | Generality | Unpredictability | Feasibility | Verification | Primary total |
|---|---|---|---|---|---|---|---|---|
| O1 | 4: cooling access matters to resource allocation | 1: familiar accessibility audit | 1: obvious first idea | 3: transferable spatial design | 3: actual coverage unknown | 4: estimate, public layers likely | 4: public locations and census summaries | 12 |
| O2 | 3: changes accessibility-data priorities | 2: missingness audit is familiar | 2: obvious candidate | 4: feed semantics generalize | 3: network effect uncertain | 3: estimate, validation uncertain | 3: records need physical truth | 14 |
| O3 | 4: monitoring priorities matter | 1: surveillance gaps known | 1: obvious first idea | 3: context-dependent administrative definitions | 3: observed association unknown | 3: estimate, linkage difficult | 3: exposure proxy and missingness confounding | 12 |
| C1 | 4: surge planning depends on joint hazards | 2: joint-skill concern already established | 3: sustained regional warning differs from pooling | 4: joint-distribution question durable | 4: relative event skill unknown | 1: pilot found no adequate accessible outputs | 3: public weather truth if forecasts available | 17 |
| C2 | 4: pollution and farm timing decisions | 1: weather-based application tools already exist | 2: familiar window comparison | 3: general sequencing principle | 2: threshold construction drives outcome | 1: estimate, same forecast access gap | 2: no observed nutrient loss | 12 |
| C3 revised | 4: tests interpretation of restoration-monitoring proxies | 3: close work found, reference/calibration validation not found in searched range | 3: joins reference geometry, controls and human class transitions | 3: two embedding systems, limited ecological endpoint | 4: correction can improve or damage real transition validity | 4: two public embedding reads and paired labels verified | 4: human labels, held-out controls, strong comparisons planned | 17 |
| C4 | 3: constrains disaster-recovery mapping | 1: transient/permanent water distinction already studied | 2: annual aggregation mismatch is familiar | 3: temporal-resolution lesson general | 1: event timing lost by design | 3: estimate, subsets likely feasible | 4: public labelled water events | 10 |
| C5 | 4: inspection triage could improve access | 2: threshold validation could differ from depth benchmarks | 3: geometry-to-action abstention less routine | 3: projection ambiguities durable | 2: known ambiguities dominate | 1: estimate, no actual ramp survey data found | 2: generic depth data inadequate | 14 |
| C6 | 3: archival evidence useful to conservators | 2: opportunistic change validation may differ | 3: varied photographs are less conventional | 3: geometry principle durable | 2: scale ambiguity predicts failure modes | 1: estimate, no paired change truth | 1: no independent loss measurements | 13 |
| C7 | 4: reassessment priorities are clinically relevant | 1: ReVUS already asks the question | 2: new predictor alone is not a new study | 3: temporal validation durable | 3: predictor ranking empirical | 2: estimate, remote column reads possible but untested | 3: public labels, potential outcome contamination | 13 |
| C8 | 4: load estimates influence conservation | 2: reference-quality confounding known | 3: long-context likelihood comparison less obvious | 3: taxon-dependent validity | 2: perturbation can manufacture effects | 1: estimate, scored taxa/fitness truth unavailable | 1: desired property unmeasured | 14 |
| C9 | 4: changes recording-versus-verification effort | 2: false-richness accumulation already known | 3: open vocabulary adds taxonomic uncertainty | 3: detection observation model general | 4: magnitude and saturation unknown | 1: estimate from public metadata; gated weights and no saved outputs | 3: annotations may omit real secondary species | 16 |
| C10 | 4: welfare screening consequential | 1: non-detection ambiguity already known | 2: prompt task alone not distinctive | 3: detectability principle durable | 1: unobservable welfare state dominates | 1: estimate, no suitable labels/model access | 1: welfare proxy unvalidated | 11 |
| C11 | 4: warning calibration matters to water planning | 2: first passage and pretrained hydrology already studied | 2: action-specific forecast validation is expected | 4: transfer/path-risk problem durable | 4: out-of-domain warning utility unknown | 3: data pilot passed, model runtime untested | 4: observed series and domain baselines | 16 |
| C12 | 4: staffing and food assistance planning | 1: caseload forecasts/reporting risks already studied | 2: standard vintage comparison | 3: administrative specifics limit transfer | 3: benefit of transfer unknown | 3: estimate, archived vintages not confirmed | 3: caseload is not unmet need | 13 |

Close-work follow-up: NatureLM methods/results and Schuster et al. (2024) methods/results pp. 5–12 were checked in full text, with its 2025 correction located. WRI's full 24-page technical note was downloaded and its data/model, train/test and results sections read. For C7, ReVUS full methods/results were checked; EVEE full text remained inaccessible after ordinary requests returned 403/429, so only its abstract, the authors' detailed methods/results blog and public figure/data repository were checked. This is an incomplete closest-two paper check for an already rejected candidate; no EVEE paper-specific finding will support the selected study. No access restriction was bypassed.

The scoring table is now fixed. It must be committed before generating the single authorized critic request. No main experimental plan has been fixed and no main experiment has run.

Bibliographic correction after the scoring freeze: the 1996 reservoir paper is by Sheng Yue and Michio Hashino, DOI 10.2208/prohe.40.335, as confirmed from the publisher page. Earlier working entries attributing it to Fujita were mistaken. The unconfirmed author attribution was removed from the critique prompt before the call. The Meroni paper DOI was likewise corrected before sending. These corrections do not change scores or scientific comparisons.

## Step 6 complete: candidate critique

One Responses API request completed, with the requested model/reasoning and web search. Returned model identifier `gpt-6-astra`. The exact template and candidate-only entries were committed before the call. The complete original response, requests, status snapshots and source metadata are saved. The critique contains no ranking used for selection. Point-by-point decisions are in `protocol/critique-decisions.md`; original scores are retained unchanged.

The final response reports 115,237 input tokens (including 6,120 cache-write tokens and zero cached reads), 14,443 output tokens including 9,680 reasoning tokens, and 13 web-search items. Computed charge is USD 2.01982 at the checked standard/default rates, including cache writes. A first accounting formula omitted automatic cache writes; a correction was appended from saved response data without a second API request. The response exposes a legacy retention field and no write-lifetime breakdown; the calculation uses the documented GPT-6 default 30-minute write rate. No invoice is visible. No more paid calls are planned for the study. This is a documented accounting caveat, not a reason to hide observed usage.

## Step 7: final selection

**Adopt revised C3.** Research question: *Do concurrent reference forests or control adjustment improve the transfer of satellite-embedding tree-cover transition screening to later years and held-out regions, compared with fixed-reference scores and supervised comparators?*

The primary five-axis score is 17. C1 also scored 17 but failed access feasibility; C11 scored 16 and has a less distinctive question given established first-passage/hydrological transfer studies. C3 is chosen for its unresolved interpretation of a newly proposed restoration-monitoring proxy and direct validation route, not for an expectation of a positive correction result. The correction can succeed, harm sensitivity, or add nothing. The study will report all of these possibilities and will not claim ecological restoration success from class transitions. Finding a general need for controls or a predictable anchoring inequality is not the proposed empirical contribution.

Disposition of every other candidate at selection: O1 not adopted (familiar access audit); O2 not adopted (missingness alone insufficient validation); O3 not adopted (known surveillance-gap question and confounding); C1 not adopted (member-level historical data access infeasible here); C2 not adopted (capability decorative, unvalidated pollution proxy); C4 not adopted (known aggregation/permanent-water issue); C5 not adopted (no actual ramp ground truth); C6 not adopted (no repeated heritage change truth, scale ambiguity); C7 not adopted (direct ReVUS overlap and predictor provenance); C8 not adopted (no independently validated conservation fitness endpoint); C9 not adopted (incomplete labels, gated model and no reusable outputs); C10 not adopted (welfare property unmeasured); C11 not adopted (useful but less distinctive question and untested pretrained runtime); C12 not adopted (generic forecasting/vintage issue, unconfirmed archives). These are final contemporaneous selection reasons, not retroactive candidates.

Selection took approximately an hour of actual research time. Exact start and completion times are recorded in events; no idle work was inserted to meet the skill's time guide. Feasibility was checked after problem/capability divergence and did not generate the initial candidate list.

## Step 8: pre-mortem

**One-sentence successful claim:** A specified reference/control rule, with thresholds calibrated only on earlier years outside the test region, retains more true tree-cover transitions at a comparable false-flag burden than the fixed-reference score in both public embedding systems. This is a conditional claim to test, not a result.

**Usefulness:** Researchers currently considering proximity-to-reference scores would learn whether the score is a transferable screening signal, which normalization deserves further field validation, or whether a small supervised classifier should remain the preferred benchmark. A null result limits the interpretation of smoother trajectories. No effect on practitioners or field-check workload is measured.

**Why the exact question might be under-studied:** Dense annual precomputed embedding products and reference-trajectory proposals are recent (2025–2026), while the controlling ideas of reference ecosystems, BACI and radiometric normalization are old. The opportunity lies in connecting their measurement logic to independent labelled transitions across two embedding spaces. The literature search did not establish the absence of prior work or a novel normalization principle.

**Likely first reviewer objections and responses to build into the main plan:**

1. *Dominant tree cover is not ecological recovery, and 10 m features do not exactly match 30 m labels.* Scope the endpoint to class-transition screening; keep ecological recovery as the motivation. Preserve class/scale definitions, quantify gains separately, and check support/aggregation sensitivity. Do not label unchanged classes ecologically unchanged.
2. *The apparent calendar effect is algebraic, and control subtraction may leave rankings identical.* Show the identity explicitly. Make out-of-time/region false flags and missed transitions the empirical endpoints, include a supervised comparator, count identical-score/ranking cases and non-negligible sign changes, and report a correction that fails.
3. *Contemporary control selection can leak test labels, and US benchmark transitions may be unrepresentative.* Select fixed reference cohorts using only labels available before the later test period, prohibit test transition labels in tuning, separate screening from forecasting, and report enriched-sample rather than population rates. Preserve failures and evaluate spatial/temporal transfer with actual denominators. If later time permits, broaden within this question using another independent label source or stronger boundaries, rather than adding loosely related topics.

**Metric/property check:** The desired measured property is correctness of tree-cover transition flags at a threshold transferred from earlier labelled data; this can be checked directly against public human-interpreted before/after classes. Cosine proximity, smoothness and small temporal variability are proxies and cannot validate themselves. Pairwise class labels provide a sample check of the proxy, but not a check of native biodiversity, biomass, ecosystem function, causal restoration effects or social benefit. Those properties are outside the empirical claim.

## Step 9: safety pre-check

This is passive use of public environmental data and local statistical analysis of published representations. It does not involve security testing, vulnerabilities, manipulation, human participants or biological sequence design. No disclosure decision is required under §12.3. Social/environmental-data provisions of §12.5 apply: use permitted licences, avoid identification and rankings of people/households/businesses, do not link land-cover coordinates to owners, publish aggregate scientific results, respect ordinary retrieval limits and distinguish observations from policy judgments. No contact with data providers, authors or affected organizations is authorized. All changes from here on require a pre-execution main plan and later deviations must be recorded.

The required topic-selection procedure is now complete, subject to the explicitly documented incomplete full-text check for rejected C7 and pilot record/term-check sequencing deviations. No main experiment has yet run.
