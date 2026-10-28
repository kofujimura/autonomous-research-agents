# Topic divergence, written before selection

The first three obvious candidates are recorded in research_log.md. No earlier trials are visible. This file records the intermediate search space, not selected claims.

## Technology list (step 2-1)

| ID | CS subfield and new capability | Existence and practical date checked | Local access assessment |
|---|---|---|---|
| T1 | Scientific machine learning: diffusion-generated global probabilistic weather trajectories | Price et al., GenCast, public code December 2024; https://deepmind.google/blog/gencast-predicts-weather-and-the-risks-of-extreme-conditions-with-sota-accuracy/ . Preprint December 2023; practical public release roughly 2024. | Training/inference not realistic locally; archived outputs and WeatherBench2 are potential inputs. Need confirm actual ensemble availability. |
| T2 | Remote-sensing representation learning: globally reusable, annual per-pixel multimodal embeddings and generation of missing modalities | TerraMind April 2025 (https://arxiv.org/abs/2504.11171); TESSERA June 2025 (https://arxiv.org/abs/2506.20380); AlphaEarth July 2025 (https://arxiv.org/abs/2507.22291). This is the released representation-as-data capability, not a model version update. | Published embedding windows can be accessed without credentials; raw global processing cannot run here. TerraMind small inference may run locally. |
| T3 | Time-series sequence modeling: pretrained probabilistic forecasting on unseen series without fitting each series | Chronos, public release March 2024, https://www.amazon.science/blog/adapting-language-model-architectures-for-time-series-forecasting/ . | Small open weights can run on CPU; data available from Monash and original public agencies. |
| T4 | Computational structural biology: unified prediction of joint protein/ligand/nucleic-acid structures | Abramson et al., 8 May 2024, https://www.nature.com/articles/s41586-024-07487-w . Unified interaction prediction is the new capability, rather than protein folding alone. | Full inference too large; benign environmental-enzyme published predictions may be usable if paired ground truth exists. No pathogen or toxin work proposed. |
| T5 | Computer graphics: editable, object-grouped explicit 3D reconstructions from ordinary multiple views | Ye et al., Gaussian Grouping, code December 2023, masks January 2024, ECCV 2024; https://github.com/lkeab/gaussian-grouping . | Existing reconstructed scenes and masks usable; training requires CUDA and may be infeasible. Late-2023 code is a boundary case for “roughly 2024.” |
| T6 | Verifiable data systems: publicly usable sub-second proofs of SQL over committed data | Proof of SQL open-source release 12 June 2024, issuer announcement https://chainwire.org/2024/06/12/space-and-time-releases-sub-second-zk-prover-under-open-software-license/ and https://docs.rs/crate/proof-of-sql/0.105.1/source/README.md . Earlier concept predates 2024; public performant prover is the practical change. | Local Rust implementation potentially usable; no chain transactions or paid services. Licence must be checked. |

Search records: sources/search-technology-1.json, search-technology-2.json, search-divergence-1.json through search-divergence-3.json. OSWorld (2024) was checked as an additional HCI candidate technology but is not used in the six-way divergence: ordinary desktop agents and this study's lack of human testing make its social applications harder to ground.

## Capability generalization (step 2-2, no technology names)

| Capability | Newly possible | Cheaper/faster | Constraint relaxed |
|---|---|---|---|
| C1 | Sample geographically coherent possible future environmental states | Many whole-world trajectories at minutes rather than large weather-center compute | Access to many joint counterfactual weather scenarios |
| C2 | Query a compact representation of each place's whole year, even across sensors | Reuse precomputed descriptors instead of processing image archives repeatedly | Raw imagery volume and bespoke feature engineering; not absence of ground truth |
| C3 | Obtain forecast distributions for an unfamiliar demand series immediately | Thousands of short histories without separately fitting complex models | Model fitting overhead and scarcity of task-specific training histories |
| C4 | Jointly represent heterogeneous molecular interactions | Screen structural hypotheses before experiments | Crystallographic structures required for every candidate; not proof of biological function |
| C5 | Remove, group, or measure scene objects while retaining a 3D context | Interactive rendering and local changes | Dense manual 3D segmentation; not reliable metric geometry automatically |
| C6 | Verify an aggregate query independently of the machine executing it | Verification of a large computation with a compact proof | Trust in remote query execution; not trust in source truth or definitions |

## Fields, judgments, and data leads (steps 2-3/2-4)

These are leads to be checked before selection. “Expected terms” are not a licence clearance for experiments. Standard methods/classic works will be linked to checked sources in the subsequent prior-work table.

| Capability | Field; user and judgment | Standard method / classic work lead | Public data and expected terms |
|---|---|---|---|
| C1 | Disaster preparedness; mutual-aid coordinators judge whether distant regions can share emergency capacity | Cost-loss forecast value; Richardson (2000), Using the economic value of ensemble prediction systems | WeatherBench2 ensembles, ERA5; dataset-specific research terms |
| C1 | Electricity adequacy; system planners judge the reserve value of geographic diversification | Loss-of-load and weather-year simulation; Bloomfield et al. weather-dependent demand/renewable generation | WeatherBench2 plus ERA5-derived power proxies; research terms and Copernicus licence |
| C2 | Ecological restoration; ecologists judge whether apparent recovery is measurable across years and disturbed places | Before-after/control-impact; Underwood (1994), On Beyond BACI | MTBS burn severity, stable land-cover controls, annual embeddings; US public domain and CC BY / product-specific |
| C2 | Agriculture; monitoring agencies judge whether crop-diversity trends reflect changing fields or mapping resolution/support | Design-based area estimation; Olofsson et al. (2014), Good practices for estimating area and assessing accuracy of land change | USDA Cropland Data Layer / LUCAS / AAFC crop inventory, embeddings; US public domain / CC BY / Open Government Licence |
| C3 | Food distribution; inventory planners judge whether a probabilistic model supports a specified shortage tolerance | Croston (1972), Forecasting and Stock Control for Intermittent Demands; newsvendor quantile | Public intermittent demand benchmarks, London food-demand open aggregates if identifiable-free; original licences must be checked |
| C3 | Public transport; operators judge whether pooled rolling forecasts keep rare service disruptions visible | Seasonal forecasts and queue/capacity planning; Gneiting & Raftery (2007), Strictly Proper Scoring Rules | Public bike rental trip counts aggregated before use, city counts or UCI bike sharing; CC BY / agency terms |
| C4 | Plastic waste treatment; enzyme researchers judge which benign degradation candidates need wet-lab validation | Structure-based screening and kinetics; Tournier et al. (2020), An engineered PET depolymerase to break down and recycle plastic bottles | Published PET enzyme structures and kinetics, PDB CC0; predicted interactions only if explicitly redistributable |
| C4 | Food processing; formulation researchers judge transfer of structure confidence to starch-active enzymes | Michaelis-Menten kinetics and docking; classic enzyme-kinetics literature | CAZy-linked PDB structures and open benchmark outputs; mixed licences, reject if unavailable |
| C5 | Built-environment accessibility; facility planners judge whether a navigable route survives uncertain clutter | Wheelchair clearance / geometric path planning; ADA accessibility standards and established access audits | Replica/ScanNet reconstructions; dataset agreement/licence check needed, avoid images of persons |
| C5 | Cultural heritage preservation; conservators judge which visibility gaps need a resurvey | Photogrammetric survey / multiview geometry; Remondino & El-Hakim (2006), Image-based 3D Modelling | Public cultural heritage scans, Europeana/Sketchfab openly licensed only; exclude personal interiors |
| C6 | Climate finance accounting; public auditors judge whether compact computation verification leaves material accounting ambiguity | Transaction reconciliation / audit sampling; IPCC accounting guidance | Public national inventory totals and open budgets; government reuse terms |
| C6 | Circular-economy material accounting; certifiers judge comparability across batch aggregation definitions | Material flow analysis; Brunner & Rechberger, Practical Handbook of Material Flow Analysis | Eurostat waste/material accounts, EU reuse notice |

No combinations are discarded merely for being computationally expensive at this stage. Data scarcity, absent ground truth, foreseeable analytical answers, and existing close work will determine rejection.

## Twelve question candidates (step 2-5)

These questions were generated from the capability/field combinations above, before scoring and before the critic. They are not additions made after selecting a winner. Each technology and field occurs in 2/12 candidates, below one third; empirical studies 5/12, method proposals 4/12, benchmark/data designs 2/12, and re-examination 1/12, below one half each.

| ID/type | Question; reader's possible changed judgment | Capability / data / necessity |
|---|---|---|
| Q01 empirical | When heat-response capacity is shared across regions, can medium-range joint weather forecasts identify days on which the usual mutual-aid partners are simultaneously unavailable, and does forecast-aware reservation improve on fixed geographic pooling? Emergency planners decide whether a mutual-aid pool is adequate or needs external reserve on each date. | C1/T1; public ensemble hindcasts and verifying temperature fields. Need many coherent future fields to evaluate date-dependent joint scarcity; fixed historical correlations cannot answer the forecast-value question. |
| Q02 method | For low-wind electricity episodes, can a warning rule that accounts for forecast recovery time reduce premature reserve release compared with warnings based only on daily low-wind probabilities? Power adequacy analysts decide when to release backup capacity. | C1/T1; ensemble wind hindcasts and verifying reanalysis. Joint trajectories supply recovery-time uncertainty unavailable from independent marginal probabilities. |
| Q03 empirical | Can annual satellite representations support claims of ecological recovery after wildfire when movement toward a pre-fire state is judged against matched stable vegetation rather than against the fire-year embedding alone? Restoration ecologists decide whether an observed trend supports recovery or merely loss of a transient disturbance signature. | C2/T2; annual embeddings from at least two families, MTBS and stable land-cover controls. Multiple years and multisensor compact descriptors make matched trajectory checks possible at broader scale. Conventional indices remain a necessary comparator. |
| Q04 method | Can crop-diversity change be estimated without annual relabeling when crop rotations alter the performance of a map trained in one reference year, and does a rotation-aware area adjustment preserve the direction of change? Agricultural agencies decide whether a diversity trend needs new reference sampling. | C2/T2; embedding fields plus multi-year public crop maps/reference labels. Transferable descriptors support a frozen representation and explicit separation of input drift from label/rotation shift. |
| Q05 empirical | For intermittent food/supply procurement, do probabilistic forecasts that are well calibrated for each future day give reliable total-demand reserve quantities over the delivery interval, and can dependence-only correction improve service risk without altering daily distributions? Distribution planners decide whether daily quantile accuracy is adequate evidence for procurement. | C3/T3; public intermittent-demand data, with genuinely public nonprofit supply data preferred if found. Many forecast trajectories without per-series fitting enable the cross-series test; temporal copula comparisons isolate joint risk. |
| Q06 benchmark/data | Can a public transport availability benchmark distinguish a genuine demand collapse from demand displaced to nearby service points using only information available before the forecast, and does that distinction alter surge planning conclusions? Operators decide whether a route/station-level model is learning lost service or shifted demand. | C3/T3; aggregate public station counts and closure/service-status metadata. Broad pretrained distributions enable replay across sparse histories; clear metadata is essential. |
| Q07 empirical | Across benign PET-degrading enzymes, do accurate predicted enzyme–substrate contact geometries identify which laboratory assays transfer across temperature and substrate crystallinity, rather than merely ranking the assayed enzymes? Recycling researchers decide where structural predictions support process comparison. | C4/T4; open published structures/predictions and kinetic assays. Joint interaction prediction supplies otherwise absent substrate-contact descriptors. No new enzyme designs or hazardous biological targets. |
| Q08 benchmark/data | Is there enough paired open structural-prediction and enzyme-kinetics evidence to validate predictions of starch-processing robustness across assay conditions, and which assay strata remain unidentifiable? Food-processing researchers decide what a structural benchmark can establish. | C4/T4; public PDB and open benign enzyme assay tables. Heterogeneous interaction descriptors allow condition-specific comparison, if released predictions and metadata actually exist. |
| Q09 method | Can a clearance assessment that propagates object-boundary uncertainty avoid falsely certifying a wheelchair route from a visually convincing 3D reconstruction? Accessibility auditors decide whether a scene supports certification or requires physical measurement. | C5/T5; public person-free reconstructions and metric geometry. Editable object representations allow structured occlusion and boundary tests, beyond rendered-image quality. |
| Q10 empirical | Do cultural-heritage resurvey priorities change when 3D uncertainty is measured on surfaces revealed by object removal rather than by ordinary camera visibility? Conservators decide what must be resurveyed before relying on a virtual restoration. | C5/T5; openly licensed site reconstructions and original viewpoints. Object-level reconstruction permits controlled revealed-surface tests. |
| Q11 re-examination | For public climate-budget aggregates, how much substantive disagreement between accepted accounting definitions remains after execution is cryptographically verified? Auditors decide whether a verified total warrants a comparable-emissions claim. | C6/T6; public inventories and budgets, local prover. Proofs distinguish arithmetic/execution correctness from accounting-definition correctness in actual queries. |
| Q12 method | Can a compact, verifiable material-flow reconciliation expose which circular-economy comparisons depend on incompatible aggregation units without revealing unnecessary input rows? Material-accounting practitioners decide which circularity comparisons are supportable. | C6/T6; public Eurostat material accounts. Verifiable relational queries could support reproducible unit-aware reconciliation. |

## Six checks for each candidate (step 2-6)

### Q01
- Capability necessary: historical pooling can be studied without it; the proposed incremental value of time-varying *forecast-conditioned joint* availability requires joint ensembles. Keep that as the central contrast.
- Prior measurement overlap: cost-loss forecast evaluation, correlated disasters, and crew deployment exist; exact pooling/reservation comparison needs the top-five search.
- Predetermined result: correlation makes pooling risky in principle, but neither whether forecast-conditioned reservation helps out of sample nor its lead-time/cost boundary follows from definitions.
- Ground truth: temperature exceedances are publicly verifiable; actual response demand is a proxy and must not be claimed as measured.
- Execution: public archived ensembles may suffice; check with pilot and reject if only unavailable model inference works.
- Judgment in either direction: positive value supports testing forecast-conditioned reserve; null/negative value favors fixed pools or climatology at tested costs. Origin in execution constraints: no, started from mutual-aid availability.

### Q02
- Capability necessary: recovery time could be estimated historically, but testing forecast-conditioned trajectory information requires the ensemble.
- Prior measurement overlap: duration-based energy droughts and ensemble copula coupling are established; search exact reserve-release context.
- Predetermined result: duration-aware rules can trivially hold capacity longer; compare at matched reserve-days/cost to avoid that result.
- Ground truth: reanalysis wind/power proxy is checkable, but grid shortfall and price effects are unmeasured.
- Execution: needs joint time trajectories, not just ensemble means; pilot required.
- Judgment in either direction: positive value supports duration-aware release; failure favors simpler marginal warnings. Origin in execution constraints: no.

### Q03
- Capability necessary: NDVI/NBR studies of recovery already possible; question must isolate whether the newly released *representation product* adds defensible recovery evidence beyond these methods.
- Prior measurement overlap: very close 2026 work on wildfire signals and decomposable embedding recovery was found (sources/search-data-prior-1.json); likely reject unless a clear difference survives full-text checks.
- Predetermined result: matching stable controls need not remove or retain a recovery trend; but detecting a known transient is not sufficient novelty.
- Ground truth: MTBS severity and stable controls are not biological recovery measurements; direct ecological validation is a core risk.
- Execution: two families of annual windows appear accessible, no credentials; licences differ across mirrors and must be resolved.
- Judgment in either direction: distinguish support for recovery measurement from mere disturbance detection. Origin in execution constraints: no.

### Q04
- Capability necessary: ordinary crop mapping/area adjustment predates embeddings; keep only if fixed-representation temporal transfer offers a distinct question, otherwise decoration.
- Prior measurement overlap: crop rotation, temporal domain shift, and area estimation all have close literatures; integrated change-direction check needs search.
- Predetermined result: classification bias can change diversity estimates, but direction/frequency under actual rotations cannot be inferred from class accuracy alone.
- Ground truth: public classified crop maps are imperfect reference proxies and may overlap pretraining; independent labels needed for strong claims.
- Execution: windows plus public crop labels feasible, contingent on obtaining label metadata.
- Judgment in either direction: evidence for/against skipping annual sampling. Origin in execution constraints: no.

### Q05
- Capability necessary: older probabilistic models can also supply trajectories; do not claim the question was impossible before 2024. Revised focus is whether immediate transferable distributions remove fitting overhead *without removing the need for temporal-dependence validation*.
- Prior measurement overlap: aggregation, lead-time demand, and probabilistic inventory scores are established; if only target replacement, reject.
- Predetermined result: daily marginal calibration does not imply total-demand calibration mathematically; useful result must be out-of-sample decision benefit of a nontrivial repair, not this implication.
- Ground truth: realized public demand sums directly checkable; observed sales may be censored and are not latent demand.
- Execution: small local pretrained model feasible; full trajectory versus quantile-output distinction must be checked.
- Judgment in either direction: use of direct lead-time forecasting/repair versus daily forecasts unchanged. Origin in execution constraints: no; local scope may narrow it later.

### Q06
- Capability necessary: demand displacement can be studied with standard models; foundation capability risks being decorative.
- Prior measurement overlap: bike-sharing demand under closures, spatial substitution and lost sales are established; metadata-based benchmark must be a new distinction to retain.
- Predetermined result: a local closure mechanically reduces observed rentals; must evaluate neighboring change and future predictive effect, not detect the zero itself.
- Ground truth: public aggregate counts and dated closure records could verify; absent a clean closure inventory, do not infer causal displacement.
- Execution: public aggregate counts accessible, closure metadata uncertain; reject if causal labeling unavailable.
- Judgment in either direction: decide whether local demand series are adequate for rebalancing; null supports no extra displacement layer. Origin in execution constraints: no.

### Q07
- Capability necessary: interaction predictions supply unmeasured contacts but older docking can supply competing descriptors; must compare.
- Prior measurement overlap: enzyme structure/function and assay dependence well studied; exact cross-condition transfer needs search.
- Predetermined result: structural accuracy need not predict kinetics; the answer is empirical.
- Ground truth: published assays checkable, yet temperature/substrate confounding and too few aligned measurements are major risks.
- Execution: without paired released predictions, local model cannot fill gap; expected feasibility low.
- Judgment in either direction: specify whether structural screens can prioritize process conditions. Origin in execution constraints: no.

### Q08
- Capability necessary: a catalogue of assays alone does not need the capability; only paired prediction validation could justify it.
- Prior measurement overlap: enzyme databases and structural benchmarks already exist.
- Predetermined result: identifying missing metadata is a catalogue result, likely small and predictable.
- Ground truth: assay outcomes available, alignment to predicted complexes uncertain.
- Execution: too little aligned released data expected; reject if pilot cannot secure it.
- Judgment in either direction: which benchmark claims are supportable; weak result if all it shows is missing data. Origin in execution constraints: no.

### Q09
- Capability necessary: ordinary mesh geometry may solve clearance better; compare, and reject if grouped graphics adds no distinct uncertainty information.
- Prior measurement overlap: robotic traversability and reconstruction uncertainty may already cover the question.
- Predetermined result: visual quality does not imply metric accuracy; that alone is known, so threshold-decision error versus geometric baseline must be measured.
- Ground truth: metric reference scenes could check clearance; wheelchair users and actual accessibility outcomes unmeasured.
- Execution: reconstruction training not feasible without CUDA; existing reconstructions plus reference geometry needed.
- Judgment in either direction: a defensible abstention/certification rule versus physical audits. Origin in execution constraints: no.

### Q10
- Capability necessary: traditional visibility/occlusion geometry may already do this; new representation may be decoration.
- Prior measurement overlap: photogrammetric completeness and virtual restoration established.
- Predetermined result: hidden surfaces are uncertain by construction; likely an obvious reconfirmation.
- Ground truth: complete reference surfaces absent for actual sites; no invented completeness labels.
- Execution: downloadable real scene examples limited and licence-sensitive.
- Judgment in either direction: resurvey priorities, but no clear distinct decision likely. Origin in execution constraints: no.

### Q11
- Capability necessary: verified execution does not verify definitions by construction; numerical case study does not require proving queries.
- Prior measurement overlap: accounting comparability and cryptographic correctness distinction established.
- Predetermined result: yes; a proof certifies only its encoded query, so the central contrast follows from definitions. Reject.
- Ground truth: published accounting definitions checkable; do not characterize institutions as faulty.
- Execution: local code may run, but not worth a main experiment on this question.
- Judgment in either direction: likely no change for knowledgeable auditors. Origin in execution constraints: no.

### Q12
- Capability necessary: unit-aware reconciliation can be done in ordinary SQL; compact verification is a deployment feature, not the substantive social question.
- Prior measurement overlap: material-flow consistency and unit-aware query systems established.
- Predetermined result: incompatibility of selected units can be established analytically. Reject current formulation.
- Ground truth: Eurostat metadata checkable, but benchmark intentionally incompatible rows would be artificial.
- Execution: possible local proof library, no paid chain; feasibility not the rejection reason.
- Judgment in either direction: no defensible new comparison claim yet. Origin in execution constraints: no.

Interim assessment: Q11/Q12 rejected on analytical/decorative grounds, Q08/Q10 on weak capability need and evidence, Q06 on capability need/closure ground truth unless new evidence appears. Q03 is under close-prior-work challenge. Top-five detailed search provisionally Q01, Q02, Q03, Q04, Q05. This is not a selection or final scoring.
