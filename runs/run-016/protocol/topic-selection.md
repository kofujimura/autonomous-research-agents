# Topic selection — scores fixed before the required critique

Original start: 2026-10-26T14:35:09Z; deadline: 2026-10-27T02:35:09Z. See protocol/divergence.md for all intermediate lists and rejected candidates; protocol/prior-work-top-five.md for the closest-work checks. No final choice has yet been made in this version. The ranking below is a self-assessment, not an external evaluation.

## Pilot checks (step 4)

- **Q01 (P01; also informs Q02):** 2026-10-26T14:52:09Z to the end time in experiments/pilot-weather/result.json, under 15 minutes. Public WeatherBench metadata were readable. The available NeuralGCM ensemble has no 2 m temperature or 10 m wind. Published GenCast access requires a request form; newer raw ensembles have requester-pays egress. No form, paid read, authentication, or workaround was attempted. No physical effect estimate was obtained. Feasibility of the question as formulated is poor. Using upper-air fields as if they were surface fields is rejected.
- **Q04 (P02 and P02b):** 2026-10-26T15:06:30.346105Z to 2026-10-26T15:10:50.321143Z, under 15 minutes including the follow-up crop-label check. A 256×256×128 public TESSERA v1.1 embedding patch was finite everywhere. An anonymous public crop-raster mirror supplied a 333×333 reference window for each of 2020 and 2021. These are actual data/access results, not classification performance. The crop raster contains multiple classes, so the question is not reduced to a single-class ceiling by this example. Terms: official NASS FAQ declares CDL public domain and not revealing/deriving farmer reports; TESSERA's source-specific licence will be pinned in the main plan (the AWS catalogue lists CC-BY-SA while the model-weight card lists CC0; do not conflate weights and embedding data). Pilot location (-93.5, 42.0) and its containing 0.1° neighborhood will be excluded from main test evidence, unless a later plan explicitly marks reuse.
- **Q05 (P03, P03b):** 2026-10-26T15:06:57.956Z (first recorded stderr timestamp; runner start time is more precise in run.json) to 2026-10-26T15:10:46.809327Z, under 15 minutes. Original code failed after loading data and weights because `time` was not imported; the failure and corrected retry remain. Retry on CPU produced finite forecasts of shape 4×20×6, with nonconstant lead-time demand sums. No forecast-accuracy effect was tested. The public car-parts source replaced missing values with zero and overlaps Chronos pretraining; it cannot be claimed to be unseen food-bank demand or used to infer true no-demand episodes. A main study would need a different source or explicit restricted scope.

Pilot outputs will not serve as confirmatory evidence. The main plan must state any reuse. No main experiment has begun.

## Scoring table (step 5)

Axes: I impact, N novelty, O non-obviousness, G generality, U unpredictability, F feasibility, V strength of verification, each 1–5. Selection criterion is I+N+O+G+U, subject to feasibility and the six checks. Feasibility for candidates without pilots is an estimate. Scores are deliberately penalized for an established answer or an enabling technology that may be decorative.

| ID | I | N | O | G | U | F | V | Main sum | Pilot |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| O1 | 4 | 1 | 2 | 4 | 2 | 4 | 4 | 13 | none, estimate |
| O2 | 4 | 2 | 2 | 4 | 3 | 2 | 4 | 15 | none, estimate |
| O3 | 4 | 1 | 2 | 3 | 3 | 3 | 3 | 13 | none, estimate |
| Q01 | 5 | 3 | 4 | 4 | 4 | 1 | 3 | 20 | P01 |
| Q02 | 4 | 3 | 3 | 4 | 4 | 1 | 3 | 18 | P01 access result |
| Q03 | 4 | 1 | 3 | 3 | 2 | 4 | 2 | 13 | none, estimate |
| Q04 | 5 | 3 | 4 | 4 | 4 | 4 | 4 | 20 | P02/P02b |
| Q05 | 4 | 2 | 2 | 4 | 4 | 4 | 4 | 16 | P03/P03b |
| Q06 | 4 | 2 | 2 | 4 | 3 | 2 | 2 | 15 | none, estimate |
| Q07 | 4 | 2 | 4 | 3 | 4 | 1 | 2 | 17 | none, estimate |
| Q08 | 2 | 1 | 2 | 3 | 2 | 1 | 2 | 10 | none, estimate |
| Q09 | 4 | 2 | 3 | 4 | 3 | 2 | 3 | 16 | none, estimate |
| Q10 | 3 | 1 | 2 | 3 | 1 | 2 | 2 | 10 | none, estimate |
| Q11 | 2 | 1 | 2 | 4 | 1 | 4 | 5 | 10 | none, estimate |
| Q12 | 2 | 1 | 2 | 4 | 1 | 3 | 5 | 10 | none, estimate |

### One-line reasons for every axis

**O1:** I4—heat warning coverage can change emergency attention; N1—vulnerability/threshold inequities already widely studied; O2—an obvious first candidate, capped; G4—threshold design matters across systems; U2—some mismatch is foreseeable; F4—public aggregate data plausible, not piloted; V4—official thresholds/temperature records checkable.

**O2:** I4—joint flood risk matters to staging; N2—compound/coherent flood forecasting is established; O2—obvious first candidate, capped; G4—dependence matters beyond one model; U3—empirical magnitude unclear; F2—joint high-resolution archives uncertain, not piloted; V4—public hydrologic observations can verify a suitable case.

**O3:** I4—supply shortages/waste affect distribution; N1—forecast-based intermittent inventory is old; O2—obvious first candidate, capped; G3—nonprofit transfer would be uncertain; U3—ranking on actual data unknown; F3—nonprofit public demand not secured, not piloted; V3—observed sales may censor demand.

**Q01:** I5—whether presumed donors can actually share surge capacity changes reservation policy; N3—exact joint-donor forecast contrast not found, but nearby crew timing work exists; O4—treating donors as forecast-correlated demands is less direct than local alert evaluation; G4—decision structure can apply across forecast families; U4—net value against strong historical copulas cannot be inferred; F1—the required new-model surface ensemble archive is not available under current scope; V3—temperature events checkable, response demand remains a proxy.

**Q02:** I4—early reserve release during persistent scarcity could matter; N3—release timing is a gap in the searched near work, not duration/coherence itself; O3—recovery time is a natural but less routine forecast target; G4—trajectory-versus-marginal contrast generalizes; U4—matched reserve-day comparison may help or fail; F1—same near-surface archive obstacle; V3—physical wind proxy is checkable but power-system outcomes are not.

**Q03:** I4—false recovery interpretations could change restoration assessment; N1—closest new paper already covers persistence and recovery contrasts; O3—comparison to stable controls is sensible but not unusual; G3—only released embedding families and chosen disturbances checked; U2—part of the proposed effect is already demonstrated; F4—public windows and fire maps plausible, unpiloted; V2—remote reference states are not biological recovery.

**Q04:** I5—whether annual labels can be skipped affects the credibility and cost of monitoring crop-diversity change; N3—the aggregate-change/correction-budget contrast was not found in the searched transfer papers, while its components are established; O4—accuracy gains can obscure directional errors in a nonlinear monitoring estimand, a less typical embedding evaluation; G4—compare representations and classic calibration/area-estimation methods, not a single model ranking; U4—actual trend errors and the value of budgeted correction are empirical and could be small; F4—embedding and crop-reference reads succeeded, second representation/reference imperfections remain; V4—fully saved public raster samples permit exact recomputation, though CDL is imperfect reference rather than field truth.

**Q05:** I4—reserve quantities directly affect procurement; N2—lead-time distributions and temporal dependence were already central in 2004, leaving a narrow new-model contrast; O2—natural inventory evaluation, and new technology may be decorative; G4—dependence-only controls span model families; U4—out-of-sample value of repair versus Markov bootstrap is unknown; F4—local model runs, but clean unseen demand data still needed; V4—demand sums and cost rules exactly checkable if the data source is appropriate.

**Q06:** I4—service displacement matters for rebalancing; N2—spatial substitution already studied; O2—foundation capability adds little to the question; G4—closure/displacement issue spans operators; U3—actual neighbor effect uncertain; F2—closure inventory unavailable, unpiloted; V2—causal displacement not established from counts alone.

**Q07:** I4—cross-condition assay transfer matters for recycling research; N2—structure/function/kinetics overlap substantial; O4—condition-transfer rather than enzyme ranking is less usual; G3—few benign enzyme families; U4—structure accuracy need not transfer to kinetics; F1—paired released predictions/assays not secured, estimate; V2—assay heterogeneity confounds the desired interpretation.

**Q08:** I2—benchmark limitations may guide data collection but little immediate process judgment; N1—enzyme benchmark catalogues already exist; O2—missing metadata is expected; G3—protocol alignment extends beyond a model; U2—data scarcity largely foreseeable; F1—aligned public predictions not secured, estimate; V2—partial metadata cannot validate robustness.

**Q09:** I4—route certification errors affect accessibility audits; N2—geometric uncertainty/traversability already studied; O3—decision abstention is more useful than rendered quality; G4—geometry-versus-appearance issue generalizes; U3—actual false certification needs measurement; F2—paired public metric references/reconstructions uncertain, estimate; V3—geometry can verify clearance but actual accessibility is broader.

**Q10:** I3—resurvey priorities can matter; N1—occlusion/completeness already established; O2—hidden surfaces as uncertainty is obvious; G3—limited scene types; U1—central concern follows from visibility; F2—licensed paired scenes uncertain, estimate; V2—true hidden surfaces generally unavailable.

**Q11:** I2—qualified auditors already distinguish query correctness and definitions; N1—the distinction is known; O2—natural caution rather than a new question; G4—definition issue universal; U1—result follows from what proofs certify; F4—local SQL/prover plausible, estimate; V5—query arithmetic exactly checkable but not sufficient reason to study it.

**Q12:** I2—accounting reconciliation useful but current question adds little; N1—unit consistency and reconciliation established; O2—ordinary data engineering idea; G4—unit handling broad; U1—selected incompatible units give the answer analytically; F3—local prover possible, estimate; V5—formal query checks strong but verify the wrong contribution.

## Pre-critique narrowing/rejection notes

Q01 could be narrowed to IFS-only historical sharing; feasibility would rise to 4 but the recent enabling capability disappears, and it risks a target-only application of established decision methods. Q02 could be narrowed to upper-air wind runs; feasibility would rise to 4 but its turbine/backup interpretation would no longer be supported (impact 1). Neither narrowing is adopted. Q06 lacks closure-ground-truth support. Q07/Q08 could be narrowed to a metadata catalogue, but that would lose the main test. Q09 could be narrowed to ordinary meshes, which removes the new capability. Q10–Q12 are rejected for obvious/decorative contrasts even if computationally feasible. These are not successful studies replacing failed main experiments: no main study has been selected or started.

## Required critique (step 6)

Pending at this commit. Top-five candidates Q01–Q05 will be sent in candidate-ID order, without these scores or a preferred choice, using the exact supplied template. Critic classification, revised scores if any, selection, pre-mortem and safety pre-check will be appended after receiving the response. Do not overwrite this pre-critique version or its Git history.

## Post-critique assessment (appended; original scores retained)

The required response is saved verbatim in experiments/topic-critic/A001-output.txt, with the complete provider JSON and request beside it. Returned model: gpt-6-astra, reasoning effort xhigh. Exactly one generation request completed; polling was retrieval, not repeated generation. No other AI helped with the study. The supplied template was used without scores or preference. The response offers criticisms and directions, not a ranking. The classification below is this session's decision.

| Point | Decision and reason |
|---|---|
| Q01 resource/transfer network is not defined by temperature | Adopted as a weakness; do not infer operational capacity from exposure. |
| Q01 pooling and forecast coherence have established antecedents | Adopted; ECC was already checked in full. Eppen is a bibliographic lead, not newly checked evidence. |
| Q01 low value if historical dependence is sufficient or no donors exist | Adopted as a rejection reason alongside the observed surface-data obstacle. |
| Q01 bounded break-even analysis for a documented resource | Not pursued: no main study selected here, and no resource/network data secured. |
| Q02 additive loss may need no temporal trajectories | Adopted as a design flaw; no intertemporal commitment was fixed. |
| Q02 short threshold recovery is not the end of an energy deficit | Adopted as a proxy limitation. New wind-drought references were not used as paper evidence or treated as verified findings. |
| Q02 weak comparator could make a predictable hysteresis gain look novel | Adopted as a reason not to select the vague reserve rule. |
| Q02 concrete contract with recommitment delay | Not pursued because the question lacks an accessible appropriate surface ensemble and a documented contract. |
| Q03 matched remote controls cannot establish biological recovery | Adopted; spectral agreement is not biological validation. |
| Q03 substantial overlap with two recent embedding papers | Adopted; relevant full methods/results had already been checked independently. |
| Q03 a geometric distinction between recovery definitions is predictable | Adopted; not sufficient empirical value by itself. |
| Q03 independent canopy-structure observations | Not pursued: would require a new reference-data pilot while closer overlap already weakens the candidate. The newly suggested synthesis was not adopted as unchecked evidence. |
| Q04 calibration and validation against the same classified map share its errors | Adopted. Replace CDL as the primary reference with public administrative declarations; retain the failed/incomplete US pilot as feasibility history only. |
| Q04 spatial crop diversity differs from rotation | Adopted. Study change in area-composition diversity, not temporal rotational diversity, crop species richness, biodiversity outcomes, or policy impacts. |
| Q04 quantification and reference-based area adjustment are established | Adopted. Olofsson was checked in full before critique; Lipton was independently downloaded and its assumptions and estimator in sections 3–5 checked after critique. Forman is an independently located bibliographic lead, not a claim of a new method. |
| Q04 current-year correction differs from assuming stable source confusion | Adopted; compare them explicitly and document source support and conditioning. |
| Q04 cross-year mapping and phenological alignment already studied | Adopted; the arXiv identifier 2506.12885 now resolves to v5, titled T³S: Think in Thermal Time for Generalizable Crop Mapping from Satellite Image Time Series (2026 revision), rather than the older title quoted by the critic. The current record was checked; no unchecked historical-title claim will be made. |
| Q04 improved proportions may still leave the direction unreportable | Adopted as the main endpoint: uncertainty, wrong-direction claims, and abstention at fixed audit budgets. Do not require a favorable result. |
| Q04 more models alone would be a small benchmark | Adopted; use two representations to test scope, with established estimators and sampling designs as the scientific comparison. |
| Q05 correct marginals do not identify their sum | Adopted; this is an analytical fact, not a possible empirical discovery. |
| Q05 intermittent lead-time dependence has close classic prior work | Adopted; Willemain's relevant full text was already checked. |
| Q05 repaired pretrained forecast may lose to direct interval forecasting | Adopted as a low-value-success scenario; clean holdout and zero semantics remain unresolved. |
| Q05 delivery-interval sweep on genuinely held-out demand | Not pursued: would repair a secondary candidate, while Q04 offers stronger independent references and a more specific unresolved monitoring decision. |

New bibliographic claims were not accepted solely on the critic's authority. Lipton's primary paper was checked independently. The new heat-policy source was opened independently but is unnecessary to the selected study. New references for rejected candidates that were not checked in full remain leads only. The critic was not called again.

### Additional close prior work and reference-data check

While the critic was running, an independent search located Säurich et al. (2026), Are remote sensing-based crop type classifications suitable for calculating a landscape heterogeneity metric? A data-fitness-for-purpose assessment, Ecological Informatics 95, 103660. The full methods, results and discussion were checked. It directly demonstrates that overall crop-map accuracy is insufficient for local Shannon-evenness applications, using administrative declarations as reference. Therefore the general warning is already known; it will not be offered as a new result. The narrower question is what fixed label budgets and sampling arrangements support a direction-of-change claim after model-assisted correction.

Additional searches covered quantification, area estimation, uncertainty in Shannon change, permanent/rotating panels, and crop rotation. A 1981 NASA crop-acreage rotating-sample report confirms that panel sampling is not new. A policy-relevant crop-diversity monitoring paper (DOI 10.1088/1748-9326/ad9d61) is another close lead; its returned PDF URL supplied HTML, so it is not yet full-text-verified. No existing exact experiment on finite-budget diversity-change inference with annual embedding covariates was found within these searches; this is a search statement, not a novelty assertion.

Public SwissCrop25 offers 2021–2025 nationally complete annual crop-declaration labels, a published agronomic hierarchy, and explicit CC BY 4.0 terms. Its full label-origin and preprocessing passages were checked. Labels reflect declared primary planting intent, not independent harvest observations. The card explicitly says there are no personal or farm-identifying attributes. Small class metadata and file-size/index metadata were read; no main-study label arrays, classifier outputs, diversity changes or audit outcomes have been inspected. EuroCrops v2.0 is another licensed multiannual source, but obtaining its harmonization lookup would add avoidable complexity; its public metadata/schema check is retained, not reported as an experiment on diversity.

### Revised scores and choice

Q04's novelty is reduced from 3 to 2 after the closer 2026 fitness-for-purpose paper: I5 N2 O4 G4 U4 F4 V4, main sum 19. The anticipated verification is stronger with declarations but remains conditional on their accuracy. Q01/Q02 remain infeasible as framed. Q03/Q05 retain the earlier penalties, reinforced by the critique. Other candidates and original scores are unchanged.

**Select Q04.** Readers are agricultural monitoring researchers and staff deciding how to maintain a limited annual reference sample. The fixed question is: **At fixed annual reference-label budgets, how reliably can model-assisted estimates based on frozen classifiers of public annual satellite embeddings identify changes in landscape crop-group diversity, and does revisiting the same audit locations improve inference compared with independently resampling locations?**

This retains Q04's crop-diversity-change/annual-labeling question. Sign reporting and abstention adopt the critique's refinement. The paired-versus-independent audit contrast was considered by this session as a concrete way to study how the label budget should be used; it is not a new topic recommended by another AI. Panel variance mathematics is established. Unknown empirical quantities are residual covariance after prediction, interval coverage, and useful versus false direction reports across actual landscape-years. No new estimator or universally optimal design is claimed. The main plan will fix actual sampling units, years, comparisons, repetitions, metrics and stopping rules before measurements.

## Pre-mortem (step 7)

1. **Known result disguised as discovery.** High pixel accuracy need not imply accurate diversity is already established. Remedy: make fixed-budget change inference and repeated-versus-refreshed reference sampling the primary comparison; use strong direct-sample and design-based/model-assisted baselines, and report null or negligible advantages.
2. **Most changes are near zero, or taxonomy/mask choices determine the result.** Remedy: retain all eligible landscapes selected without inspecting changes; count near-zero changes and absent source classes; publish uncertainty and abstention rather than select large movements. Preplan the published broad hierarchy as primary and finer hierarchy plus alternative support masks as sensitivity checks. State that the measurement is crop-group composition, not species diversity or rotation.
3. **Uncertain or inaccessible reference undermines operational interpretation.** Remedy: use independently generated administrative declarations, pin the public snapshot, save the sampled labels/features, and retain all failed reads. Scope conclusions to declared crop groups and selected stable agricultural support. Record planting-intent uncertainty, incomplete labels, spatial alignment, pretraining exposure, and dependence on the two released representations. Do not infer ecological or farmer outcomes.

## Safety pre-check (step 8)

Only anonymous public dataset reads and local CPU computation are planned. No identities, farm ownership, beneficiary data, financial records, contact, participant experiments, exploitation, or external publication. Output units will be landscape aggregates with many parcels, with no field-level examples or rankings of organizations. Do not link parcel locations to ownership or other personal sources. Data reuse is permitted by the checked source licences; retain attribution and indicate modifications. No vulnerability/disclosure workflow applies. No additional paid model calls are planned. Ordinary public retrieval will be rate-limited and bounded by the storage/time limits. If the selected reference cannot be obtained, record the failure and narrow or revise the same study rather than silently replace it.

Topic-selection work is complete with this appended decision; the main plan has not yet been fixed or run.
