# Topic selection (append-only decisions)

No main experimental plan is fixed by this document. Source-access failures and rejected candidates remain part of the record. The technology/capability/field divergence and first three obvious candidates are in `research_log.md`.

## Twelve divergent candidates, recorded before pilots or main results

The first four use coherent cheap physical-environment samples (T1, including published hybrid learned/physical ensembles as well as diffusion ensembles); the next four use reusable annual satellite representations (T2); the last four use conditional periodic-structure generation (T3). There are four per technology, at most four in any outside-CS field, and four each of information/data audits, tool/method evaluations, and reproductions/refutations. Technology is a route to a question, not a requirement to pretend older methods cannot answer it.

### C01 — Public information needed for shared emergency capacity (information/data audit)

- Question: When can site-level weather exceedance probabilities certify whether to activate shared surge capacity, and how often does unreported spatial dependence prevent that judgment on real forecast cases?
- Users/judgment: emergency and climate-service planners deciding whether a public forecast product is sufficient for a pooled-capacity decision; data publishers deciding which joint summaries to release.
- Capability/origin: many coherent alternative physical futures, T1 (generative/hybrid ensembles). The revised question studies the decision information that survives their public summarisation, rather than claiming a new weather model is more accurate.
- Data: open WeatherBench ensemble archives (learned NeuralGCM and physical IFS), public forecast-product specifications, reanalysis only if evaluating realised outcomes. No unavailable GenCast outputs are assumed.
- Why the capability matters: cheap ensembles and public marginal products increase the gap between available internal joint forecasts and accessible summaries. The mathematical question could be studied before 2024; the new capability is motivation and supplies a second class of real forecasts, not an invented prerequisite. Initial model-performance framing is rejected as technology decoration; the information/decision framing is the candidate evaluated here.
- Six checks: (1) Older ensembles can answer the mathematical part; retain only with modern public product context and cross-model empirical tests. (2) Copula reconstruction, sharp bounds and forecast value are established; novelty must be in decision certification and real-case frequency, not dependence loss itself. (3) Non-identifiability can be proved without data; its frequency, decision relevance and efficacy of stronger comparisons cannot. (4) No AI judgment; finite ensemble probabilities are exact ground truth for information retention, not truth about actual weather. (5) Public small subsets appear runnable; pilot required. (6) If summaries often certify decisions, practitioners can use them under explicit bounds; if they do not, publishers/users need a joint aggregate or scenarios.
- Origin from execution constraints: no; motivated by what information public warning products let practitioners act on. Data access narrows comparisons.

### C02 — Repeated-confirmation rules for anticipatory action (method evaluation)

- Question: At a matched false-alarm or resource budget, does requiring forecasts to confirm a heat event on successive updates sacrifice useful lead time compared with calibrated single-update and optimal-stopping policies?
- Users/judgment: anticipatory-action planners choosing confirmation rules and action deadlines.
- Capability/origin: coherent temporal uncertainty trajectories, T1.
- Data: successive archived ensemble initialisations and reanalysis; operational warning-rule documents.
- Why capability matters: compare dynamically updated uncertainty at many sites; older archives may already suffice, so a modern-model label alone cannot justify the study.
- Six checks: (1) Yes, conventional forecasts suffice; retain as a possible refutation of confirmation-rule reasoning only if a clear empirical gap remains. (2) Lagged-forecast consistency/optimal stopping literature is close and must be checked. (3) The trade-off direction is predictable, but whether a calibrated rule reverses the policy ranking is not. (4) Reanalysis checks forecast events; protection outcomes remain unmeasured. (5) Public initialisations seem available; pilot needed. (6) Either improved operational robustness supports confirmation, or lost lead time supports a different policy; no claim about actual health effects.
- Origin from execution constraints: no; operational commitment/revision dilemma.

### C03 — Frost-protection duration (reproduction/refutation)

- Question: Do per-night frost warning scores preserve the ordering of forecasts for protection against consecutive frost nights during a crop's vulnerable period?
- Users/judgment: agronomic advisory services deciding whether night-level validation is sufficient.
- Capability/origin: joint temporal samples, T1.
- Data: WeatherBench temperatures; public crop-stage calendars and experimental frost-injury thresholds, if validated.
- Why capability matters: cheap trajectory samples permit duration-risk estimates, but the question predates the technology.
- Six checks: (1) Yes; high decoration risk. (2) Duration/compound-event verification is established. (3) Ranking changes cannot be calculated without forecasts, but the mismatch is known. (4) Air temperature is not crop-tissue injury; public validation not secured. (5) Weather data runnable, biological endpoint not. (6) Both signs affect score selection, but field-specific practical value is weak without crop-stage data.
- Provisional disposition: reject at screening for known question and unvalidated injury proxy.
- Origin from execution constraints: no; biological duration requirement.

### C04 — Reservoir action from published quantiles (method evaluation)

- Question: Can quantile-only rainfall products support robust staged reservoir releases without reporting trajectory dependence?
- Users/judgment: water operators deciding whether marginal forecasts suffice for release schedules.
- Capability/origin: coherent physical trajectories, T1.
- Data: ensemble precipitation, public catchment hydrology and reservoir constraints (CAMELS/benchmark reservoir cases), expected research/open licences.
- Why capability matters: stochastic forecast trajectories motivate information needed for decisions.
- Six checks: (1) Existing stochastic dynamic programming can study it; technology is not essential. (2) Multistage stochastic optimisation and hydrological ensemble postprocessing are mature. (3) Dependence matters by construction; operational frequency may be informative. (4) No AI judge, but rainfall-to-inflow proxy requires validation. (5) Input access possible, calibrated hydrology not yet secured. (6) Answers change product choice, but the gap from prior work is currently unclear.
- Provisional disposition: reject; too close to established reservoir uncertainty work and a hydrological calibration study would dominate.
- Origin from execution constraints: no; sequential water-allocation problem.

### C05 — Temporary fallow versus persistent abandonment (information/data audit)

- Question: Can annual reusable satellite representations distinguish temporary crop interruption from persistent abandonment under spatial and temporal holdouts, and how much does a history of representations add beyond one-year land-cover labels?
- Users/judgment: agricultural land-use researchers choosing evidence sufficient to count abandonment, with consequences for land-restoration estimates.
- Capability/origin: compact multisensor annual descriptions, T2.
- Data: TESSERA/AlphaEarth; multiannual USDA Cropland Data Layer or public European agricultural labels (terms to verify); exclude individual-farm reporting.
- Why capability matters: repeated regional sparse-label tests without recreating the raw optical/radar pipeline. Older multiannual cover data can test simpler versions, so novelty requires comparison to those strong baselines.
- Six checks: (1) A simpler study can be done without embeddings; retain only the question of incremental evidence beyond label histories. (2) Abandonment/fallow mapping and phenology methods are very close. (3) Multi-year histories should help by definition; incremental accuracy on honest future/spatial holdouts is not guaranteed. (4) Label histories are a reference, not verified farmer intent; must narrow endpoint to persistent mapped interruption. (5) Embeddings/labels public in principle; pilot required. (6) Positive result justifies sparse-label representation histories; null result favours established map histories and avoids overstating abandonment.
- Origin from execution constraints: no; temporary interruption can be mistaken for land availability.

### C06 — Disturbance-specific forest recovery (reproduction/refutation)

- Question: Do annual representation-based forest recovery measures assign the same recovery ordering after fire and harvest as public canopy/disturbance reference products, after accounting for pre-disturbance state?
- Users/judgment: restoration and carbon-accounting researchers deciding whether a generic representation-distance measure is evidence of ecological recovery.
- Capability/origin: annual general-purpose pixel descriptions, T2.
- Data: open embeddings, Landsat-derived disturbance histories, government fire perimeters and canopy products; all analysed at regional scale.
- Why capability matters: representations offer a new low-cost generic monitoring route; the measured latent change is a proxy whose validity is the question.
- Six checks: (1) Classical spectral recovery studies exist; question concerns validity of a new generic surrogate. (2) Remote-sensing recovery/metric sensitivity literature is close. (3) Neither agreement nor disturbance-specific reversal follows from definitions. (4) Public canopy estimates are imperfect and not independent field recovery; proxy gap must be stated. (5) Available outputs appear adequate; pilot optional if not top three. (6) Agreement supports a limited monitoring use; disagreement requires disturbance-specific validation before interpreting distances as recovery.
- Origin from execution constraints: no; ecological recovery differs from greenness.

### C07 — Concurrent annual representations as disaster controls (method evaluation)

- Question: Does matching on a representation that includes the disaster year attenuate estimated crop-disruption contrasts relative to pre-disaster matching, and can a simple temporal guard prevent this without sacrificing pre-event balance?
- Users/judgment: disaster-evaluation researchers selecting remote-sensing covariates and reference years.
- Capability/origin: ready-to-use annual multisensor vectors, T2.
- Data: public disaster footprints, annual representations before/during the event, annual crop/vegetation outcomes at aggregated scale.
- Why capability matters: new convenient vectors can silently incorporate post-event information; the causal principle itself is old and cannot be claimed as new.
- Six checks: (1) The causal warning exists without embeddings; retain only if empirical effect and practical guard outperform an established pre-event baseline. (2) Post-treatment bias/bad controls and remote-sensing causal inference are close. (3) Attenuation is plausible, not guaranteed because vectors can also improve confounding control; observed attenuation alone is not evidence of causal bias. (4) No AI judge; no public true causal effect, so use constructed outcomes/negative controls plus observational demonstration. (5) Data available in principle; pilot needed. (6) Stable estimates support cautious use; attenuation/negative-control failure supports enforcing reference-year constraints.
- Origin from execution constraints: no; misuse of available covariate summaries motivates it.

### C08 — Wetland stress versus drainage (information/data audit)

- Question: Can annual representations distinguish temporary drought from persistent wetland drainage without treating every dry-year change as habitat loss?
- Users/judgment: wetland-monitoring practitioners deciding which changes require follow-up.
- Capability/origin: reusable multisensor summaries, T2.
- Data: public wetland inventories, annual water maps, drought indices, embeddings; reuse expected with attribution.
- Why capability matters: cross-sensor annual context might disambiguate physical mechanisms.
- Six checks: (1) Hydrological time-series methods already address the issue. (2) Wetland hydroperiod/change mapping is close. (3) Directions not tautological. (4) Drainage ground truth is not obtained by a dry-pixel label; independent infrastructure/management evidence absent. (5) Input maps available but the outcome is not validated. (6) Both answers affect surveillance, but would not be trustworthy with the current reference.
- Provisional disposition: reject for ground-truth failure and technology decoration.
- Origin from execution constraints: no; distinguishing reversible stress from habitat conversion.

### C09 — Low-risk magnetic designs (reproduction/refutation)

- Question: Does excluding rare-earth elements from generated magnetic structures reduce broader material-supply exposure at matched predicted magnetic performance?
- Users/judgment: materials designers deciding whether an element-exclusion constraint is sufficient.
- Capability/origin: jointly conditioned new periodic structures, T3.
- Data: MatterGen generated candidates/property tables, public criticality indicators.
- Why capability matters: candidates expose trade-offs beyond known catalogues.
- Six checks: (1) Can be studied in enumerated known materials but generated designs add a distinct search space. (2) MatterGen itself reports magnetic density plus supply-chain-risk conditioning; this is very close. (3) Rare-earth-free is not equivalent to low-risk by definition; exact frequency is empirical. (4) Predicted magnetic density is not a functioning permanent magnet. (5) Tables available, physical testing unavailable. (6) Both signs affect screening, but this is likely only re-confirming the paper's rationale.
- Provisional disposition: reject; direct close prior work and proxy limitation.
- Origin from execution constraints: no; resource substitution can shift burdens.

### C10 — Designs compatible with recycled feedstocks (method evaluation)

- Question: Do generated low-supply-risk structures remain plausible when impurity combinations representative of recycled metal streams are imposed?
- Users/judgment: circular-metallurgy researchers deciding which designs warrant synthesis.
- Capability/origin: structure generation under compositional constraints, T3.
- Data: generated structures, public scrap-composition distributions and physical stability calculations.
- Why capability matters: noncatalogued candidates broaden impurity-compatible designs.
- Six checks: (1) Conventional alloy design can ask it; require genuinely new structures. (2) Impurity-tolerant alloy design literature is close. (3) Stability under substitution is not analytic. (4) Formation-energy surrogate cannot establish processing tolerance without validated data. (5) Reliable relaxation plus realistic scrap distributions cannot be secured from released outputs alone. (6) Both results affect synthesis priority, but would overclaim without experiments beyond this environment.
- Provisional disposition: reject for endpoint and execution feasibility, not because the underlying problem is unimportant.
- Origin from execution constraints: no; recycling compatibility motivates the question, constraints rule it out.

### C11 — Chemical novelty versus useful alternatives (reproduction/refutation)

- Question: How much reported generative-crystal novelty survives comparison within chemical/prototype neighbourhoods that already provide equivalent supply-diversification choices?
- Users/judgment: materials researchers interpreting discovery counts and prioritising synthesis.
- Capability/origin: large generated candidate sets, T3.
- Data: released candidates, public structure databases, composition/prototype matching.
- Why capability matters: more candidate structures make novelty accounting operationally important.
- Six checks: (1) Existing database matching can answer a simpler question; the generator is mostly a data source. (2) Crystal-generation baseline/novelty critiques are already extensive. (3) Stricter equivalence necessarily reduces novelty counts; useful diversification would need functional validation. (4) No verified functional equivalence benchmark. (5) Structure matching runnable; core endpoint not. (6) A smaller count alone would not change a well-informed reader's judgment.
- Provisional disposition: reject; definitional result and weak decision endpoint.
- Origin from execution constraints: no; synthesis-priority decision, not a cheap benchmark chosen for convenience.

### C12 — By-product co-dependence in material substitution (information/data audit)

- Question: Do individually diversified generated compositions still concentrate on metals co-produced from the same host supply chains?
- Users/judgment: resource-economics/material-design teams deciding whether element-wise risk objectives are adequate.
- Capability/origin: property-conditioned structure candidates, T3.
- Data: generated composition/property tables; USGS and public host/by-product production relationships.
- Why capability matters: design candidates permit a search-space comparison beyond current commercial materials.
- Six checks: (1) Same issue is analysable for known materials; new generation is a stress-test source. (2) Companion-metal criticality and supply-chain network studies are close. (3) Co-dependence magnitude is empirical but omitting it is a known limitation. (4) Production linkage is checkable; property predictions do not demonstrate substitutability. (5) Data analysis feasible but candidate-level supply substitution is not validated. (6) Positive concentration supports joint supply constraints; a null result would merely vindicate the chosen candidate set with narrow scope.
- Provisional disposition: reserve, lower priority than C01/C02/C05/C06/C07 because of overlap with known criticality concerns and weak functional endpoint.
- Origin from execution constraints: no; co-production links are the mechanism.

## Next checks

Top five for close-prior-work screening: C01, C02, C05, C06, C07, in candidate-ID order. Top three pilot checks will be selected after that screening. This is not the final scoring or adoption decision. The obvious candidates O1–O3 remain recorded and are not silently relabelled as divergent candidates.

## Pilot procedures fixed before running (step 4)

After the prior-work screen (`protocol/literature-screen.md`), the top three feasibility pilots are C01, C05 and C06. Each runs for at most 900 seconds using `scripts/run.py`, and all outputs/failures are retained. They test access and endpoint plausibility, not a main hypothesis. Their actual start/end times come from the runner.

- P01 / C01: Download an ordinary HTTP byte range for up to 50 surface-temperature member fields from one advertised open AIFS ensemble initialisation (2026-07-01 00 UTC, 168-hour lead). Decode with ecCodes and save a small predeclared set of regional points. Check finite values, member count, units, coordinate conventions, and whether there is any ensemble uncertainty around fixed temperature thresholds 25, 30 and 35 °C. This one date is a pilot and will be excluded from the main inferential sample if adopted. Re-run on a second date only if the first fails on access, not to search for a favourable effect. Input indexes already downloaded are access-screening evidence, not result-driven case selection. No model API is involved.
- P02 / C05: Open the public v1.1 dClimate TESSERA store and sample a small regular spatial grid in a broad agricultural region for 2022 and 2023. Save numeric vectors, dataset identity, coordinate conventions and finite-value counts; do not interpret a vector change as abandonment. Inspect the existence and licence of a corresponding public annual cropland reference. If intent/persistence reference is not available, report that weakness rather than manufacture an abandonment endpoint. No individual-farm analysis or map will be published.
- P03 / C06: Sample a small regular grid in a broad forested region from the same public annual representation store for 2021 and 2023. Inspect finite values and whether a public disturbance/reference product can be paired in space/time. Vector changes alone are not recovery evidence. No attempt to obtain parcel ownership or participant data.

Pilots P02/P03 may share a cached public representation-store metadata read, but their numeric samples and access records remain separate. If the final topic is C01, P02/P03 are not part of its evidence. If either satellite topic is adopted, pilot points/years are excluded from its main test or explicitly declared in the main plan. Theoretical examples used to check a solver are not empirical evidence.

## Pilot results and initial scores (before external critique)

Recorded at 2026-10-25T22:37:47Z. The whole C01 pilot window was 22:23:13–22:34:49 UTC (less than 15 minutes), including failures and repairs. The initial date yielded ten complete raw member fields across failed attempts but no completed summary; transfers repeatedly returned HTTP 503 or truncated bodies. The permitted second date (2026-07-02) completed a ten-member, eight-region, twelve-site sample with all 960 values finite. Its fixed 25/30/35 °C checks found ensemble uncertainty at 19/30/8 of 96 sites respectively. This is an access/uncertainty sign, not a decision result. Both pilot initialisation dates will be excluded from the main sample if C01 is selected. Fifty members were indexed, but a full fifty-member data extraction was not piloted.

P02 read 25 finite representation vectors in each of 2022 and 2023, then failed only on JSON metadata serialization; P02b repaired metadata using saved raw vectors. P03 read 25 finite vectors in each of 2021 and 2023 and completed. These show access, not abandonment or recovery validity. No reference labels were obtained in the pilot, and the dClimate catalogue licence differs from model authors' CC0 advertisement; conservative share-alike attribution and no external distribution were recorded.

The initial score table is generated from candidate-scores.json. These are this agent's judgments; feasibility without a topic-specific pilot is explicitly an estimate. The primary selection criterion sums the first five axes, leaving feasibility and verification visible.

| Candidate | Impact | Novelty | Non-obviousness | Generality | Unpredictability | Feasibility | Verification | Primary sum |
|---|---|---|---|---|---|---|---|---|
| O1 | 4 | 1 | 2 | 4 | 2 | 4 | 4 | 13 |
| O2 | 4 | 2 | 2 | 4 | 3 | 3 | 3 | 15 |
| O3 | 4 | 3 | 2 | 4 | 4 | 2 | 2 | 17 |
| C01 | 5 | 3 | 3 | 5 | 4 | 4 | 5 | 20 |
| C02 | 4 | 2 | 2 | 4 | 3 | 3 | 3 | 15 |
| C03 | 3 | 1 | 2 | 3 | 2 | 2 | 2 | 11 |
| C04 | 4 | 1 | 2 | 4 | 2 | 2 | 3 | 13 |
| C05 | 4 | 2 | 2 | 4 | 3 | 3 | 3 | 15 |
| C06 | 4 | 3 | 3 | 4 | 4 | 3 | 3 | 18 |
| C07 | 4 | 2 | 3 | 4 | 3 | 3 | 2 | 16 |
| C08 | 4 | 2 | 2 | 4 | 3 | 2 | 2 | 15 |
| C09 | 4 | 1 | 2 | 3 | 2 | 3 | 2 | 12 |
| C10 | 4 | 3 | 3 | 4 | 4 | 1 | 1 | 18 |
| C11 | 2 | 1 | 2 | 3 | 1 | 4 | 2 | 9 |
| C12 | 4 | 2 | 3 | 4 | 3 | 3 | 2 | 16 |

One-line reasons for every score:

### O1

- Impact: 4 — Cooling-service schedules are a real preparedness decision.
- Novelty: 1 — Hot nights and duration are already established heat-health concerns.
- Non obviousness: 2 — An obvious first candidate; skill cap applies.
- Generality: 4 — Duration matters across warning tools.
- Unpredictability: 2 — Maxima can miss hot nights by definition.
- Feasibility: 4 — Estimated: public temperatures available; no pilot.
- Verification: 4 — Meteorological events checkable; service effects unmeasured.

### O2

- Impact: 4 — Transfer protection can affect usable accessible journeys.
- Novelty: 2 — Reliability-based accessibility is a mature topic.
- Non obviousness: 2 — Obvious first candidate; skill cap applies.
- Generality: 4 — Connection fragility extends across transit systems.
- Unpredictability: 3 — Real connection-slack patterns need data.
- Feasibility: 3 — Estimated: public timetables likely, reliable disruption data uncertain; no pilot.
- Verification: 3 — Timetable reachability is checkable but actual journeys are not.

### O3

- Impact: 4 — Renewal calendars determine service workloads.
- Novelty: 3 — Precise public-data causal gap not established within the range searched.
- Non obviousness: 2 — Obvious first candidate; skill cap applies.
- Generality: 4 — Renewal bunching generalises across administrations.
- Unpredictability: 4 — Workload dynamics need empirical calendar data.
- Feasibility: 2 — Estimated: relevant public aggregate mechanism data not secured; no pilot.
- Verification: 2 — Annual counts do not verify the proposed timing mechanism.

### C01

- Impact: 5 — Climate-service publishers and pooled-resource planners can decide which summary information is sufficient for a specified action.
- Novelty: 3 — Dependence/bounds are known; decision certification frequency and scalar-moment versus full-pair information comparison were not found in the targeted search.
- Non obviousness: 3 — Publishing one aggregate co-exceedance moment instead of a full spatial pair matrix is less immediate than the usual retain-dependence warning, but no uniquely AI-origin claim is made.
- Generality: 5 — Information bounds apply to arbitrary binary hazard portfolios and both physical/data-driven ensembles; empirical prevalence remains sample-specific.
- Unpredictability: 4 — Real forecast ambiguity, exact low-order moment identification, and practical reconstruction accuracy cannot be obtained from the definitions.
- Feasibility: 4 — Pilot decoded a complete ten-member second-date subset; fifty members are indexed; first-date transfer failures and retrieval cost limit sample size.
- Verification: 5 — Saved raw selected values, exact empirical joint law, LP dual/primal checks and stronger summary/coupling comparisons can verify information-retention claims; no real health gain claimed.

### C02

- Impact: 4 — Would guide anticipatory-action confirmation rules.
- Novelty: 2 — Act-now-or-wait and lagged consistency literature is very close; closest decision paper not obtained in full.
- Non obviousness: 2 — A common concern about waiting for confirmation.
- Generality: 4 — Sequential commitment occurs across forecast systems.
- Unpredictability: 3 — Magnitude/rule ranking empirical; basic trade-off predictable.
- Feasibility: 3 — Estimated: archive available but multi-update calibration and observed outcomes not piloted.
- Verification: 3 — Can verify event timing; behavioural/health benefit remains unmeasured.

### C03

- Impact: 3 — Could affect agronomic score selection.
- Novelty: 1 — Compound-duration verification is already known.
- Non obviousness: 2 — Obvious temporal aggregation concern.
- Generality: 3 — Relevant to duration-dependent crop injury, but biological settings differ.
- Unpredictability: 2 — Night-level versus consecutive-event mismatch is foreseeable.
- Feasibility: 2 — Estimated: crop stage/injury reference not secured; no pilot.
- Verification: 2 — Air temperature is an unvalidated injury proxy.

### C04

- Impact: 4 — Reservoir release decisions matter for water management.
- Novelty: 1 — Very close to mature multistage stochastic reservoir optimisation.
- Non obviousness: 2 — Dependence in inflow trajectories is an established consideration.
- Generality: 4 — Would apply to many reservoirs if hydrology were validated.
- Unpredictability: 2 — Information loss is built into the comparison.
- Feasibility: 2 — Estimated: calibrated rainfall-to-inflow model not obtained; no pilot.
- Verification: 3 — Formal decision checks possible, operational validity weak.

### C05

- Impact: 4 — Could prevent counting temporary crop interruption as reusable abandoned land.
- Novelty: 2 — Reviews already stress duration, fallow and multisensor methods; embedding increment is a narrow gap.
- Non obviousness: 2 — Multiple-year evidence for persistence is immediately expected.
- Generality: 4 — Endpoint distinction extends across agricultural monitoring systems.
- Unpredictability: 3 — Increment beyond existing annual label histories is unknown.
- Feasibility: 3 — Pilot obtained 25 finite vectors in both years; public labels exist but intent/persistence ground truth and exact dClimate licence version remain unresolved.
- Verification: 3 — Mapped persistence checkable; abandonment intent not verified.

### C06

- Impact: 4 — Could change whether generic latent distance is treated as restoration evidence.
- Novelty: 3 — Within searched sources, explicit disturbance-specific recovery validation for annual representations was not found; spectral recovery validity is already well studied.
- Non obviousness: 3 — Distinguishing representation return from ecological recovery is useful but has clear precedents in spectral metrics.
- Generality: 4 — Surrogate validation matters across models, disturbance types and monitoring systems.
- Unpredictability: 4 — Disturbance-specific agreement or reversal is not determined by definitions.
- Feasibility: 3 — Pilot obtained finite vectors for both years; matched independent canopy/recovery labels still need a full test.
- Verification: 3 — Public reference products permit comparison but do not establish full ecological recovery.

### C07

- Impact: 4 — Would guide covariate-year choices in disaster evaluation.
- Novelty: 2 — Post-treatment bias and rich-representation treatment leakage are already studied directly.
- Non obviousness: 3 — Annual support-period contamination is easy to miss operationally.
- Generality: 4 — Applies to compressed covariates beyond satellite data.
- Unpredictability: 3 — Observed attenuation is plausible but confounder control can move estimates either way.
- Feasibility: 3 — Estimated from shared satellite access pilot; a known-effect construction is feasible but true observational effect is not available.
- Verification: 2 — Cannot infer causal bias from attenuation alone; synthetic validation may dominate contribution.

### C08

- Impact: 4 — Could distinguish reversible wetland stress from habitat loss.
- Novelty: 2 — Hydroperiod and drainage distinctions are established.
- Non obviousness: 2 — Dry years versus drainage is an obvious monitoring ambiguity.
- Generality: 4 — Broad ecological relevance if outcome labels existed.
- Unpredictability: 3 — Embedding discrimination would need testing.
- Feasibility: 2 — Estimated: independent drainage reference not secured; no pilot.
- Verification: 2 — Dry-pixel labels cannot verify drainage.

### C09

- Impact: 4 — Supply-risk screening affects synthesis priorities.
- Novelty: 1 — MatterGen itself jointly conditions magnetic density and supply risk.
- Non obviousness: 2 — Rare-earth-free is not equivalent to low-risk is well known.
- Generality: 3 — Candidate-space conclusions need functional comparability.
- Unpredictability: 2 — Broader-risk substitution trade-offs are expected.
- Feasibility: 3 — Estimated: released tables usable; no pilot.
- Verification: 2 — Magnetic density is not verified permanent-magnet performance.

### C10

- Impact: 4 — Recycled feedstock compatibility is a real design decision.
- Novelty: 3 — Generated-structure perturbation might add a gap, but recent impurity-tolerant design is close.
- Non obviousness: 3 — Joining inverse structure design to realistic scrap mixtures is less immediate.
- Generality: 4 — Physical impurity tolerance extends beyond one generator.
- Unpredictability: 4 — Stability and processing tolerance are not analytic.
- Feasibility: 1 — Estimated: validated relaxation and realistic feedstock mixture endpoints not available; no pilot.
- Verification: 1 — Cannot verify processing tolerance from released pristine structures.

### C11

- Impact: 2 — A stricter novelty count alone is unlikely to change an informed synthesis decision.
- Novelty: 1 — Generative-crystal novelty/baseline critiques are already extensive.
- Non obviousness: 2 — Changing equivalence definitions is an obvious benchmark concern.
- Generality: 3 — Matching logic extends across generators, functional equivalence does not.
- Unpredictability: 1 — Stricter equivalence necessarily reduces novelty.
- Feasibility: 4 — Estimated: structure matching runnable; no pilot.
- Verification: 2 — No ground truth for equivalent functional alternatives.

### C12

- Impact: 4 — Could alter joint supply-risk screening.
- Novelty: 2 — Companion-metal and co-production dependence are established concerns.
- Non obviousness: 3 — Applying host-metal links to generated compositions is less routine.
- Generality: 4 — Supply-network dependence extends beyond models.
- Unpredictability: 3 — Magnitude in generated candidates is empirical.
- Feasibility: 3 — Estimated: composition and public production data likely accessible; no pilot.
- Verification: 2 — Functional substitute performance is not validated.

Top five sent for critique, in candidate-ID order: C01, C02, C05, C06, C07. This preserves the candidates chosen for close-work screening, including weaker candidates so the critique can expose their core weaknesses. No candidate is yet adopted. C10's high primary sum cannot override feasibility 1; it is rejected unless narrowed to an endpoint that can actually be verified.

Eligibility clarification before critique: “top five” refers to the five surviving screened candidates whose endpoints can be bounded or checked with available references. C12 is now rejected at the six-point screen because composition co-production analysis cannot establish functional substitution; its numeric primary score is kept. O3 likewise lacks the public timing mechanism data needed for a test. C10 is infeasible at its core endpoint. Scores do not override these screening exclusions. No score or preference is sent to the critic.

## Critique assessment and final selection (2026-10-25T22:50:27Z)

The complete point-by-point classification is in `protocol/critique-assessment.md`. Original scores above remain unchanged. After the critique, C01 impact is revised 5→4 (actual product demand and delivery constraints are not measured), feasibility 4→3 (full fifty-member extraction still not piloted), verification 5→4 (continuous-law bounds must not be confused with fixed-size empirical ensemble bounds). Its revised score vector is [4,3,3,5,4,3,4], primary sum 19. All other score vectors remain at their original values. C01 remains the highest primary sum among eligible candidates; C06 has 18, C07 16, C02/C05 15. This is a self-assessment, not a ranking by the critic.

**Adopt C01, revised question:** On equally sized operational machine-learned and physics-based weather ensembles, when do reusable site and pairwise co-exceedance summaries determine pooled temperature-exceedance capacity decisions for user-chosen regional portfolios, and when is a portfolio-specific count distribution or member-coherent forecast still required?

The empirical object is the width of the set of compatible capacity-tail probabilities, including its decomposition into the information in one aggregated second factorial moment and the additional spatial arrangement of all pairs. The study does not propose that a moment beats a count distribution for a known portfolio. Count distributions are the exact, compact query-specific comparator. It will not claim that dependence loss, bound nesting, LP methods, count-distribution sufficiency, or cost-loss thresholds are discoveries. A machine-learned stochastic joint forecast is essential to the revised comparison with physical ensembles; the generic mathematical problem itself predates these technologies. The introduction must make this distinction clear.

The study risks the skill's avoided type of applying existing evaluation methods to a new target. It is adopted because the question is empirical adequacy of reusable dependence products for flexible decisions, including whether pair arrangement adds much over aggregate variance, rather than merely confirming that dependence matters. If the data yield only the known concern with no useful adequacy boundary, report that weak outcome plainly. The new capability makes the physical-versus-machine-learned comparison possible; it does not make the known mathematics new.

**Other actual candidates:** reject C02 (operational cost/episode endpoint not secured and directly close decision literature); C05 (no independent persistence reference and availability constraint); C06 (best alternative, but structural recovery/measurement independence not secured); C07 (known bad-control principle and unknown real effect). Earlier dispositions of C03/C04/C08–C12 and O1–O3 stand; no unrecorded candidates were added after scoring. C10 cannot be made feasible without replacing its core physical endpoint; C12/O3 lack a verifiable core endpoint.

Topic selection was completed in less than 60 minutes of confirmed active research time. The exact elapsed calculation is in the selection event. It was not shortened to reserve a predetermined experiment: three bounded data pilots, recent and classic close-work searches, the permitted critique, and its assessment have supplied enough evidence to distinguish the candidates. Further waiting solely to reach a time target would not add evidence. Remaining close-literature checks will continue during the study and before submission.

### Pre-mortem before adoption

- Successful paper's one-sentence claim: In the specified real ensemble portfolios, pairwise summaries leave a measured amount of uncertainty about pooled capacity, with identifiable settings where an aggregate moment suffices and where a query-specific count distribution is necessary to preserve the forecast decision. The directions and magnitudes are unknown.
- Reader change: forecast-data providers can judge what a pairwise interface can certify for these queries and whether count-query or coherent-member access remains necessary; researchers can distinguish probability reconstruction error from information that no reconstruction can recover from the released summaries. This has a path to a real data-service decision, but actual provider adoption and user benefit will not be measured.
- Why possibly not studied in exactly this form: moment bounds and dependence reconstruction are long established in reliability/operations research and meteorology separately. Modern operational stochastic machine-learning ensembles make the cross-system information comparison timely. No assertion of uniqueness or novelty follows from this rationale or the targeted search.
- Likely weakness 1, artificial portfolios/thresholds and trivial probabilities: prespecify geometries, sizes, thresholds, times and all-case plus nontrivial strata; count floors/ceilings; add realistic boundary checks if time permits. Fixed temperature is a meteorological endpoint, not a validated heat-health trigger.
- Likely weakness 2, count products dominate or pair matrix costs ignored: distinguish reusable marginal/pair summaries from portfolio-specific count summaries, include the latter exactly, report schema size, and make no unobserved bandwidth or demand claim.
- Likely weakness 3, solver/finite-ensemble artefacts and insufficient independent dates: validate LP primal/dual bounds against known constructions and marginal formulas; explicitly specify arbitrary probability laws versus exactly fifty equally weighted members; check integer feasibility on a sample; resample by initialization date, not by site/member/threshold.
- Metric versus claim: compatible-tail interval width directly measures identification of the empirical forecast law's capacity event. It is not a proxy for forecast calibration, medical demand, observed heat harm or social benefit. Those outcomes will not be claimed.

### Safety pre-check

This is a passive public-weather-data and local numerical study. It is not vulnerability, attack, privacy, dual-use or human-participant research; no disclosure decision is indicated. Section 12.5 applies to its social-problem framing and public geographic data. Use permitted ECMWF open data with attribution and bundled selected measurements; no person, household, business, target ranking or blame. No model API will be used for experiments, coding, literature interpretation or paper writing. No new paid service or account is needed. The archive's ordinary anonymous HTTP range requests are within its documented access mechanism; limit concurrency and preserve failures.
