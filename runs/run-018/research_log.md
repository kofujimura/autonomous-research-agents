# Research log

Start: 2026-10-27 14:23:30 UTC. Deadline: 2026-10-28 02:23:30 UTC.

No past-trial subjects, methods or results are present in the visible context; none were sought. No user profile was used. The record is a concise decision index, not a complete record of internal reasoning.

## First three obvious candidates (before divergence)

1. Correlated weather forecast error and whether heat-relief capacity plans miss simultaneous demand. Potential users: emergency planners.
2. Whether canopy-height maps change where urban shade interventions are prioritized compared with canopy area. Potential users: urban forestry teams.
3. Whether three-dimensional building information changes flood evacuation route assessment. Potential users: flood planners.

These are the first three recorded candidates, not yet selected. Their non-obviousness will be capped at 2 if adopted. The recent-capability divergence follows separately.

## Divergence record, 2026-10-27T14:41:50.496162+00:00

# Topic divergence, recorded before selection

These are prospective candidate questions, not findings. This file preserves the intermediate lists required by the research-question skill. The decision record in `topic-selection.md` will be appended after prior-work checks and pilots. No prior-trial files or personal projects were consulted. Execution constraints were assessed after generating the problem questions.

## Recent technologies and capabilities

| ID | Computer-science area; technology | First demonstrated capability, source and date | Access in this environment |
|---|---|---|---|
| T1 | Multimodal representation learning; AlphaEarth Foundations | Globally aligned, annual 10 m embedding fields assimilating optical, radar and other observations; Brown et al., *AlphaEarth Foundations: An embedding field model for accurate and efficient global mapping from sparse label data*, July 2025, https://arxiv.org/abs/2507.22291 | Published 64-channel outputs, CC BY 4.0, available without model training via Source Cooperative. |
| T2 | Generative physical simulation; GenCast | Learned stochastic global medium-range weather trajectories, rather than a deterministic prediction; Price et al., *Probabilistic weather forecasting with machine learning*, December 2024, https://doi.org/10.1038/s41586-024-08252-9 | Code/weights public; local generation likely unsuitable; published evaluation forecasts must be checked. The 2023 preprint means 2024 is practical publication, not an assertion of first invention. |
| T3 | Structural bioinformatics; AlphaFold 3 | Joint prediction across proteins, nucleic acids, small molecules and ions; Abramson et al., *Accurate structure prediction of biomolecular interactions with AlphaFold 3*, May 2024, https://www.nature.com/articles/s41586-024-07487-w | Published evaluation structures potentially usable. Local generation/access terms not yet established. Included for the new interaction capability, not simply the version number. |
| T4 | Audio signal processing; SAM Audio | General sound separation conditioned jointly by text, image masks or time spans; Shi et al., *SAM Audio: Segment Anything in Audio*, December 2025, https://arxiv.org/abs/2512.18099 | Public evaluation methods; weights require approved authenticated access according to upstream README. No credentials will be obtained. Published outputs must suffice or candidates will be discarded. |
| T5 | Automated theorem proving; AlphaProof | Reinforcement learning that generates machine-checkable Lean proofs at olympiad level; official announcement, July 2024, https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/ | Published proofs available; no general local system established. Legal applications probably do not need this capability; checked below. |
| T6 | Transfer learning for numerical sequences; Chronos | Pretrained probabilistic forecasts transferred to unseen time-series domains without local model fitting; Ansari et al., March 2024 preprint / October 2024 TMLR, https://arxiv.org/abs/2403.07815 | Small public checkpoints can run locally. This is a new deployment capability, not a claim that transfer learning or forecasting began in 2024. |
| T7 | Dense computer vision; global metre-scale canopy-height inference | Public global 1 m maps resolving individual trees rather than only coarse forest pixels; Meta/WRI release, April 2024, https://sustainability.atmeta.com/blog/2024/04/22/using-artificial-intelligence-to-map-the-earths-forests/ | Published maps are public; local range-window reads likely practical. |

The areas are diverse in application and representation but several share deep learning; this is a limitation of the divergence. T1/T6 and T2/T6 overlap in methodology. No claim is made that every underlying algorithm was invented after 2024.

## Generalized capabilities, without technology names

| Capability | Newly possible | Much cheaper/faster | Constraint removed | Fields and difficult judgments |
|---|---|---|---|---|
| K1 (T1) | Compare fine-scale annual land states across sensors and regions in one representation | Repeated multi-sensor preprocessing and feature extraction | Need to assemble/fit a sensor-specific representation for every place | Wetland restoration: selecting reference sites with the same water regime; agricultural monitoring: deciding whether apparent rotation changes reflect farming or representation drift. |
| K2 (T2) | Sample coherent alternative future global weather trajectories with learned dynamics | Producing large trajectory ensembles | Cost of repeated numerical integration | Power systems: whether geographically pooled backup is sufficient; heat response: whether regions can rely on each other's relief resources. |
| K3 (T3) | Represent heterogeneous biomolecular partners in a joint structural hypothesis | Screening plausible interactions before expensive structural work | Need for separate specialized pipelines for each partner type | Wastewater biotechnology: whether cofactor-dependent treatment candidates are structurally credible; crop nutrition: whether mineral-binding structural screens survive altered ionic context. |
| K4 (T4) | Extract broadly described sounds in realistic mixtures using several prompt types | Creating targeted sound streams without training a separator per sound | Closed lists of supported source types | Conservation monitoring: whether separated calls preserve occupancy evidence; environmental acoustics: whether separated rail impulses preserve exceedance counts. |
| K5 (T5) | Search for a proof and have a kernel verify the result | Exploring formal derivations | Reliance on unverified informal reasoning | Social insurance: whether benefit schedules have unintended boundary discontinuities; electoral law: whether quota rules preserve stated invariants. |
| K6 (T6) | Obtain predictive distributions for a newly observed series without fitting a domain-specific model | Deploying forecasts across many small public-service series | Large local training histories and bespoke fitting | Water supply: choosing reserve margins from short records; public transport: distinguishing closures from lost underlying demand. |
| K7 (T7) | Represent canopy geometry at the scale of individual trees globally | Surveying heights outside local lidar coverage | Availability of costly local height inventories | Forest carbon: whether threshold-based eligibility misses low-stature recovery; urban heat: whether canopy-area priority maps omit shade from adjacent trees. |

## Fields, standard methods and classic/established studies

These are candidate-screening references; search/full-text status is tracked separately. They are not automatically evidence for the eventual paper.

- Restoration: reference ecosystems and reference models; Gann et al. (2019), *International principles and standards for the practice of ecological restoration*, confirmed through the Society for Ecological Restoration archive, https://www.ser.org/page/Standards_2nd_ed_archive. Wetland water regimes need evidence beyond vegetation appearance.
- Agricultural monitoring: supervised crop mapping and annual land-cover comparison; USDA Cropland Data Layer is a standard source. Boryan et al. (2011), *Monitoring US agriculture: the US Department of Agriculture, National Agricultural Statistics Service, Cropland Data Layer Program*, is to be checked in the closer search.
- Energy forecasting: ensemble probabilities and multivariate postprocessing; ensemble copula coupling (Schefzik, Thorarinsdottir and Gneiting, 2013) is to be checked alongside GenCast.
- Heat response: percentile/threshold heat-warning criteria and duration-based events; official heat-health warning guidance and the field's standard exposure measures require a closer search before adoption.
- Wastewater and crop structural screening: molecular docking, with Trott and Olson (2010), *AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading*, confirmed at https://vina.scripps.edu/. A structural pose is not treatment efficacy or nutrient uptake.
- Conservation acoustics: point counts, passive acoustic monitoring, occupancy accounting for imperfect detection. Kahl et al. (2021), *BirdNET: A deep learning solution for avian diversity monitoring*, confirmed from the author-hosted full paper and official publication list, https://birdnet.tu-chemnitz.de/publications/. Environmental acoustics: equivalent sound level and event/exceedance counts; official definitions need checking if adopted.
- Social insurance and electoral rules: executable formal specifications/invariant checking; Merigoux, Chataing and Protzenko (2021), *Catala: a programming language for the law*, https://doi.org/10.1145/3473582. This is direct evidence that the new proof-search capability may be unnecessary. Voting apportionment has long-established mathematical methods; no claim of a new problem is warranted.
- Public-service forecasting: seasonal naive, exponential smoothing/ARIMA, and quantile forecasts; Croston (1972), *Forecasting and stock control for intermittent demands*, confirmed through the field's book/review references. Forecasting is distinct from estimating demand censored by closure or capacity.
- Forest carbon: field inventory and allometry; Chave et al. (2014), *Improved allometric models to estimate the aboveground biomass of tropical trees*, https://doi.org/10.1111/gcb.12629. Canopy height alone does not measure additional carbon.
- Urban heat: measured thermal exposure and radiative/microclimate models; Meili et al. (2021), *Vegetation cover and plant-trait effects on outdoor thermal comfort in a tropical city*, https://doi.org/10.1016/j.buildenv.2021.107733. The abstract confirms that geometric/trait effects beyond cover are already established.

## Public data combinations considered

| Capability/field | Candidate public inputs and expected terms | Preliminary availability |
|---|---|---|
| K1/wetlands | Annual published embeddings (CC BY 4.0); US Fish and Wildlife Service National Wetlands Inventory (US government public data); JRC Global Surface Water (open with attribution) | Plausible, must verify labels, licence and local reads. |
| K1/agriculture | Same embeddings; annual USDA Cropland Data Layer (US government data) | Plausible; labels and dates must align. |
| K2/power | Published forecast ensembles; WeatherBench 2 ERA5 and ENS, each under its own bucket licence; aggregate synthetic wind portfolios | Forecast-output access unconfirmed. |
| K2/heat | Same weather ensembles and reanalysis, aggregate regions | Same obstacle; humidity and subdaily timing may be missing. |
| K3/wastewater | Public structural benchmarks and PDB structures, terms checked if used | Relevant environmental pairs not yet located; efficacy ground truth absent. |
| K3/crop nutrition | Same structural data, crop mineral-binding proteins | Relevant paired conditions not located; functional ground truth absent. |
| K4/conservation | Public bird sound benchmarks with event labels; published separation outputs | Weights gated, no appropriate saved outputs located yet. No human voices will be retained. |
| K4/environmental acoustics | Public labelled environmental sound clips and benchmark outputs | No validated regulatory-level amplitudes identified; likely invalid proxy. |
| K5/social insurance | Public statutory texts and existing Catala examples | Data exist, but capability unnecessary and legal correctness requires expert validation. |
| K5/electoral rules | Public apportionment rules and aggregate populations | Data exist, but ordinary solvers suffice. |
| K6/water supply | Aggregate municipal demand or public river-flow records, plus public model checkpoints | Relevant sufficiently long/licensed aggregate demand data must be located. Household data excluded. |
| K6/public transport | Aggregate system ridership from government open data | Closure/capacity-censored demand is not observed; causal test likely unavailable. |
| K7/carbon | Published canopy maps; open forest plot/land-cover data | Height available, additionality/eligibility outcomes need verification. |
| K7/urban heat | Published canopy maps; public lidar for validation and open land-cover/roads | Geometry feasible; no measured pedestrian outcome established. |

## Fourteen candidate questions

1. **C01, wetland restoration (problem discovery):** Do nearest neighbours in annual satellite embeddings preserve wetland water regimes when selecting geographically separate reference sites, and can explicit hydrological constraints prevent mismatches? Users: restoration teams deciding whether a retrieved reference site is suitable. K1/T1; embeddings plus wetland water-regime labels and surface-water history. The object being assessed is the new globally shared representation; traditional local imagery cannot provide the same cross-sensor pretrained-neighbour operation. Not generated from execution constraints.
2. **C02, agricultural monitoring (method proposal):** Can cross-year consistency constraints distinguish crop-rotation changes from changes in an annually updated satellite representation without fitting a new crop classifier each year? Users: agricultural monitors deciding when a rotation alert warrants checking. K1/T1; embeddings and annual crop labels. Transfer of one representation across years is central. Not generated from execution constraints.
3. **C03, power-system resilience (problem discovery):** Does improved marginal weather skill translate into useful estimates of simultaneous low-wind events across a regional backup portfolio? Users: power planners deciding whether geographically pooled backup is reliable. K2/T2; published coherent ensembles, reanalysis, and fixed wind-power conversion. Cheap coherent alternative futures are central, although analogous questions predate the technology. Not generated from execution constraints.
4. **C04, heat response (problem discovery):** Do coherent weather ensembles alter how often nearby regions can safely count on mutual aid during persistent heat with little overnight recovery? Users: emergency planners deciding whether relief capacity can be shared. K2/T2; ensembles and reanalysis. New ensembles permit many joint trajectories, but the broad question can be asked with numerical forecasts. Not generated from execution constraints.
5. **C05, wastewater treatment (replication/refutation):** Are structural confidence scores informative about cofactor-context sensitivity for publicly benchmarked environmental treatment enzymes? Users: environmental biotechnology researchers deciding what a structural screen can rule out. K3/T3; published heterogeneous-complex predictions and experimental structures. Joint heterogeneous context is central. Not generated from execution constraints.
6. **C06, crop nutrition (replication/refutation):** Do publicly released joint molecular predictions preserve known mineral-binding geometry across plant proteins, or is confidence decoupled from the context relevant to nutrient transport? Users: crop researchers deciding whether to trust structural triage. K3/T3; public structure pairs. New joint predictions are the object; function remains unmeasured. Not generated from execution constraints.
7. **C07, conservation monitoring (dataset construction):** Does general sound separation preserve the presence/absence and timing of faint bird calls across naturally varying competing sounds? Users: ecologists deciding whether separated recordings support occupancy analysis. K4/T4; public event-labelled bird soundscapes and separated outputs. Broad target extraction without species-specific training is central. Not generated from execution constraints.
8. **C08, noise regulation (replication/refutation):** Can general sound separation preserve counts of impulsive transport-noise exceedances rather than merely perceptual clarity? Users: environmental acousticians deciding whether separated audio supports event counting. K4/T4; amplitude-calibrated public soundscapes would be required. Not generated from execution constraints.
9. **C09, water supply (method proposal):** Can short-record transferable probabilistic forecasts support municipal demand reserve decisions during unusual peaks, and does calibration with longer seasonal history change the decision? Users: water operators deciding how much reserve is supported by the evidence. K6/T6; aggregate demand and public pretrained models. Deployment without local fitting is central but conventional short-history forecasts remain a strong comparison. Not generated from execution constraints.
10. **C10, transport access (replication/refutation):** Do zero-shot ridership forecasts mistake closure-induced zeros for persistent demand loss, and can explicit closure information correct the inferred recovery? Users: transport planners deciding whether service demand has recovered. K6/T6; aggregate ridership and closure calendars. New transfer is convenient rather than necessary; likely discard. Not generated from execution constraints.
11. **C11, forest restoration (dataset construction):** How much low-stature woody recovery falls outside canopy-height threshold screens used to locate potential restoration areas? Users: restoration/carbon teams deciding what to inspect. K7/T7; metre-scale canopy maps and longitudinal plot/land-cover labels. Fine-scale public heights enable a broader audit, but threshold exclusion is partly definitional. Not generated from execution constraints.
12. **C12, urban heat (problem discovery):** How often do canopy-cover priorities for shade investment change after accounting for adjacent-tree geometry, and does global metre-scale height data reproduce those changes seen in lidar? Users: urban forestry teams choosing areas for detailed assessment. K7/T7; global heights and public lidar/land cover. Cheap heights outside lidar coverage are central; actual thermal benefit is not observed. Not generated from execution constraints.
13. **C13, social insurance (method proposal):** Can machine-checked proofs expose benefit-schedule boundary discontinuities missed by example-based checks? Users: policy implementers deciding which boundary rules need review. K5/T5; public statutory examples. Existing verification methods already address this; likely discard. Not generated from execution constraints.
14. **C14, electoral administration (dataset construction):** Which public apportionment rule statements can be accompanied by checkable invariants across population changes? Users: election administrators deciding which guarantees a rule actually has. K5/T5; aggregate populations and statutory rules. Ordinary proof/solver methods suffice; likely discard. Not generated from execution constraints.

No technology supplies more than two of fourteen candidates; no field supplies more than two. Types: problem discovery 4, method proposal 4, dataset construction 3, replication/refutation 3 (all at most half). The three earlier obvious candidates remain separately recorded in `research_log.md`; they were not relabelled as divergence candidates.

## Six checks per candidate

The six positions below are: capability necessity; close known application; analytic/definitional result; independently checkable target if AI measured; runtime/output access; changed judgment for either outcome. These are screening judgments, not a literature-completeness claim.

- **C01:** (1) The retrieval operation needs published aligned embeddings, although reference selection itself is old. (2) Closely related embedding interpretation/hydrological prediction exists; water-regime preservation in restoration reference retrieval needs checking. (3) Mismatch frequency and benefit over hydrologic baselines cannot be deduced from definitions. (4) Public wetland classifications can check agreement, but are imperfect proxies for actual regimes; the plan must distinguish this. (5) Published windows appear accessible. (6) Good agreement supports using retrieval for triage; poor agreement supports requiring independent hydrologic constraints. Retain for closer check.
- **C02:** (1) Cross-year representation consistency is specific to the available annual fields. (2) Crop mapping and change detection with embeddings likely close; search explicitly. (3) Rotation alerts are not mechanically determined by the representation. (4) Annual crop labels check semantic stability, subject to label error. (5) Published outputs accessible. (6) Stable transfer supports reuse; unstable transfer demands year-specific checks. Retain provisionally.
- **C03:** (1) New ensembles reduce production cost, but the scientific question can be tested with old ensembles: revise to isolate dependence versus marginal skill, not claim a newly possible question. (2) Ensemble copula coupling and energy drought studies are close. (3) Empirical joint-event calibration is not analytic. (4) Reanalysis checks weather events, not actual power adequacy. (5) Saved ensemble access unconfirmed. (6) Good joint skill supports pooled planning inputs; weak joint skill requires separate verification. Retain only if a nonredundant difference and data exist.
- **C04:** (1) Same study possible with numerical ensembles. (2) Heatwave spatial concurrence and mutual-aid dependence are established concerns. (3) Scarcity under synchrony is predictable; frequency is empirical. (4) Weather validation cannot validate relief demand. (5) Timing/humidity data uncertain. (6) Both outcomes matter, but the core proxy is weak. Discard: technology decoration plus unverified demand proxy.
- **C05:** (1) Heterogeneous joint context is newly accessible. (2) Binding-confidence audits exist. (3) Confidence/geometry relation needs actual pairs. (4) Structural geometry is checkable; treatment efficacy is not. (5) Relevant environmental paired outputs not identified. (6) Both outcomes alter structural triage, but no outcome validates treatment. Discard unless a relevant open paired benchmark appears; do not infer efficacy.
- **C06:** (1) Same joint-context benefit. (2) Broad binding benchmarks likely cover the method. (3) Geometry fidelity not definitional. (4) Experimental structure can check geometry but not uptake. (5) Paired plant/mineral outputs not established. (6) Limited practical action without functional validation. Discard: missing relevant paired data and central proxy gap.
- **C07:** (1) General target extraction is central. (2) Bioacoustic source separation and detection are well studied; occupancy preservation differs from perceptual separation. (3) Call deletion/insertion and context dependence are empirical. (4) Event annotations or isolated source channels can verify timing/presence. (5) Upstream weights gated and saved appropriate outputs not yet located. (6) Faithful extraction supports detector preprocessing; unfaithful extraction rules it out for occupancy. Discard for current access unless published outputs solve it; do not substitute an unapproved service.
- **C08:** (1) Separation is central but older methods suffice. (2) Environmental sound separation exists. (3) Amplitude changes make regulatory threshold changes partly predictable. (4) Public calibrated ground truth not found. (5) Gated weights and missing calibrated outputs. (6) Either result concerns counting, but not regulatory compliance without calibration. Discard.
- **C09:** (1) Transferable priors are central to no-fitting deployment; the domain problem is older. (2) Water-demand deep forecasting and zero-shot forecasting are close. (3) Peak losses and calibration improvements are empirical, but short-context failures may be obvious; include strong seasonal methods. (4) Aggregate observations check demand, not unobserved consumer welfare. (5) Small checkpoints feasible, licensed demand not yet established. (6) Good performance supports rapid provisional reserves; weak performance requires historical calibration. Retain for closer check.
- **C10:** (1) Technology is decoration: censored demand needs explicit modelling regardless of predictor. (2) Demand censorship and service-disruption recovery are established. (3) Observed ridership cannot identify latent unmet demand. (4) Ground truth missing. (5) Public observations feasible but wrong target. (6) Either answer would not resolve the planning judgment. Discard.
- **C11:** (1) Scale changes, not the basic question. (2) Forest definitions/threshold exclusions well studied. (3) Below-threshold omission is definitional, only prevalence empirical. (4) Height does not establish additional carbon or recovery. (5) Heights accessible, independent outcomes uncertain. (6) Main conclusion largely predictable. Discard.
- **C12:** (1) New maps permit outside-lidar assessment; canopy geometry could be studied before. (2) Shade geometry and cover limitations are known; the difference must concern decision transfer under height error, not rediscover shading. (3) Priority changes under height error are empirical. (4) Lidar checks geometry; no measured heat-health outcome. (5) Range windows plausible. (6) Agreement supports a screening use; disagreement requires lidar or conservative priorities. Retain only with a sharply narrowed transfer question.
- **C13:** (1) New proof search unnecessary. (2) Catala and concolic computational-law testing already do this. (3) Constructed boundaries could make results tautological. (4) Kernel checks formal claims but not statutory interpretation. (5) AlphaProof general system unavailable. (6) Could improve rule checks, but this study adds no established difference. Discard.
- **C14:** (1) New proof search unnecessary. (2) Formal apportionment analysis is classic. (3) Many invariant violations follow analytically. (4) Proof checks formal model, not legal meaning. (5) General system unavailable. (6) Old methods answer the actionable issue. Discard.

Top five for close checks, in ID order: C01, C02, C03, C09, C12. No candidate is selected yet. Data access and prior work may overturn these provisional choices.

Correction: candidate-type tallies in the prose above were miscounted: problem discovery 4, method proposal 3, dataset construction 3, replication/refutation 4. Each is at most half. Candidate labels themselves are unchanged.

## Data interpretation checks, 2026-10-27T15:07:17.111874+00:00

The wetland inventory is reconnaissance-level, imagery-based biological classification, not current measured hydrographs or regulatory delineation. The official 2013 standard defines non-tidal regimes with reference to growing seasons and typical years. Any later study must measure label agreement and treat suitability/current hydrology as unmeasured. TESSERA is a possible second representation, but its distribution has inconsistent licence naming (all inspected statements permit this noncommercial research); keep source copies and conservative attribution/share-alike. No restricted weather forecasts, gated weights, participant data or additional billing routes were accessed.

## Final selection 2026-10-27T15:23:20.278327+00:00

Selected refined C01, incremental embedding contribution to vegetation-controlled wetland inventory-regime matching. Critique point decisions, revised scores, pre-mortem and safety check are preserved in protocol/topic-selection.md. Full Brinson text now confirms the baseline practice and the limitations of remote indicators. No main data have been collected or analysed.

## Input-vintage finding 2026-10-27T15:47:48.081129+00:00

All12 fixed windows acquired. {'observed_at_utc': '2026-10-27T15:47:48.081129+00:00', 'polygons': 3667, 'regions': 12, 'image_year_groups': {'2015–2019': 770, '<=2014': 2756, '>=2020': 141}, 'matching_outcomes_observed': False}
This is a data-quality observation, not a model result. The prescribed recent-label subgroup is small; an explicitly exploratory recent-source expansion would address a core alternative explanation, while retaining all original windows and primary results. No matching model has been fitted.

## Confirmed usage-limit resumption

{
  "stop_start_utc": "2026-10-27T16:26:05+00:00",
  "resume_utc": "2026-10-27T16:39:37+00:00",
  "excluded_seconds": 812.0,
  "basis": "Human resume message explicitly confirms AI usage limit; last explicit live clock query before interruption and first live clock query after receipt. Exact runtime cutoff not directly observable.",
  "human_message": "Resuming after a stop caused by the AI usage limit.",
  "original_deadline_utc": "2026-10-28T02:23:30+00:00",
  "extended_deadline_utc": "2026-10-28T02:37:02+00:00",
  "processes_with_end_times_in_bookkeeping_gap": [
    {
      "experiment_id": "aef-panel-2024-b",
      "start_time_utc": "2026-10-27T16:26:03.991754+00:00",
      "end_time_utc": "2026-10-27T16:35:04.168896+00:00",
      "exit_code": 0
    },
    {
      "experiment_id": "input-audit-initial",
      "start_time_utc": "2026-10-27T16:28:27.448278+00:00",
      "end_time_utc": "2026-10-27T16:28:35.107581+00:00",
      "exit_code": 0
    }
  ],
  "process_timing_note": "AEF acquisition continued to completion during the gap. The input audit also ended in the gap; exact cutoff relative to its end is not directly observable. Bounded processes were not relaunched automatically."
}

## First primary aggregate 2026-10-27T17:18:57.295665+00:00

Read analysis/primary-summary after allfour primary rotations finished. Distances reduce region-macro mismatch relative to the specified learned hydrology comparators, but intervals are wide and many includezero; pooled and region-macro magnitudes differ. No claim of field hydrology validity or robust general superiority. Pre-fixedv6 controls will address stochastic/learner/transfer explanations. Recentpanel remains exploratory.

## Second-learner check 2026-10-27T17:35:41.512937+00:00

The predefined HGB check weakens a broad incremental-value interpretation: at50% coverage, neither single-distance augmentation beats both hydrological comparators in region-macro risk. No tuning or replacement of this negative result. Combined-distance secondary result is reported separately. Next execute all null-feature and forest-seed controls.

## Recent-panel result 2026-10-27T17:48:24.028343+00:00

The exploratory recent-source panel fails to show incremental single-distance value over both hydrological comparators at50% coverage. Preserve all6windows, no search for substitute sites. This further limits the preliminary original-panel means; it does not identify inventory age as a causal explanation.

## Tile-edge extraction correction 2026-10-27T19:34:56.503445+00:00

Polygon preflight failed, preserved at analysis/polygon-features. All overlapping validAEF values and allTESSERA values agree; only formerly missing pixels differ. Exhaustive initial-patch audit finds12missing inside-polygon pixels in4wetlands (1original,3recent), all outside the centre-owned tile. Current repair fetches all9pixels of affected patches, checks oldvalid values exactly and writes separate overrides, preserving originals. Main comparisons will be refitted; initial controls retain precise initial-input provenance. No polygon matching has run.

2026-10-27T19:40:51.537469+00:00 — Strict scalar controls inspected: at max_features=.7, scalar rep0 −4.56 percentage points vs hydrological pair, reps1/2 −1.24/−1.02; at1.0 the three scalar differences +0.07/+0.47/−0.13pp. Actual distances at1.0 AEF+0.07pp and TESSERA−0.79pp. These are paired archived initial-extraction comparisons, exploratory after the primary fits; no formal randomization inference. Canonical manuscript paths now explicitly point to pending corrected-input fits, while controls retain initial-input provenance.

## Polygon support, metric refinement and verification — 2026-10-27T22:50:40.552304+00:00

The tile-edge omission was repaired without replacing the initial study: previously valid raw values agreed exactly; corrected feature arrays changed one original and three recent AlphaEarth rows. All four polygon sampling conditions and both learners are now fitted on the same3624wetland cohort. The factor-isolation audit verifies identical physical-only decisions where physical inputs were held fixed and identical embedding-only decisions where embedding inputs were held fixed. See analysis/polygon-condition-audit/result.json and the preserved failure/correction events.

The common-polygon comparison changes interpretation. Wider embedding sampling produces a favourable full-vector forest case, while averaging the existing physical maps at those locations strengthens the physical category comparator. Neither raw-cosine augmentation beats both physical comparators for the original forest/HGB settings in that matched-location condition. This is inventory-code evidence, not field hydrological validation; NWI geometry remains an input.

A reduced author verification on a fresh Git archive of d7485efcf8760027e0eccfb898e933b0e1f6c090 passed54recorded checks in212.726564seconds, including regenerated raw features, polygon point selection, all32then-complete saved-decision summaries, constant/factor audits and unchanged source contents. No network/API calls. Primary and critical polygon model refits are still pending; the entry point now supports separate bounded refits for both. This is not independent reproduction.

The favourable planned whitened-cosine diagnostic motivates an explicitly exploratory transformed-distance augmentation, fixed in plan-v16 before its fits. It reuses the original training-only whitening rule, checks maxima against archived cosine outputs, and tests fixed HGB/all-feature forests on original and averaged-physical polygon inputs. Do not generalize a raw-distance failure to every metric or representation. HGB fits are complete; forest/stronger-baseline fits are under way.

Geographic transfer is running in fixed window order, with one target window per bounded group after the first two-window batch. Target-window labels and indicators are withheld, but training size/geography/seeds also differ, so this does not isolate a causal effect of local labels. Plan-v17 fixes a common2024/2023/2021cohort before alternate-year retrieval; those data have not yet been retrieved. Remaining boundary checks and the fixed random-frame panel remain unexecuted.

A distinct confirmed usage-limit resume at21:40:37UTC excluded6052seconds, after the earlier812seconds. The unsupported duplicate interpretation after compaction was withdrawn; it adds no time. Current research deadline04:17:54UTC. No other AI calls or subagents were used; actual API cost remains1.98624USD. A brief report-builder overlap with two fits was conservatively disclosed as a possible process-count deviation; later numerical reporting uses a free bounded slot.

### Final verification 2026-10-28T08:08:45.462175+00:00

All57completedconditions and13claims are included. The final all-condition pool audit, centre-pixel boundary and expected constant replay completed. The candidate3 numerical/model refits exposed a manuscript-path verification gap; candidate4 fixes it and verifies the entire paper exactly plus full primary refits. The critical polygon refit uses identical model code/inputs from candidate3. All processes ended. Final records/hash/snapshot preparation follows; wider-frame matching remains unexecuted.
