# Spatial temperature-exceedance probabilities from ensemble summaries: an empirical partial-identification study

<!-- Working manuscript template. Numerical blocks are generated from analysis
outputs by the rendering script; this is not a submitted or completed paper. -->

## Abstract

Planning heat preparedness across locations can require a joint-event probability that individual probability maps do not specify; here fixed dry-bulb thresholds are stylized examples, not health-warning criteria. We bound an ensemble's probability that at least k of twelve sites exceed a threshold using individual probabilities, those probabilities plus one aggregate second binomial moment, and all pairwise co-exceedance probabilities. The target is the empirical forecast law. Primary bounds permit arbitrary probability weights; known-size equal-weight ensembles are checked separately. {{ABSTRACT_PRIMARY}}

{{ABSTRACT_SENSITIVITY}}

{{ABSTRACT_EXPLORATORY}}

## 1. Introduction

Heat–health action plans connect warnings to actions, responsibilities and available response capacity. The World Health Organization's guidance stresses local warning criteria and coordination between health and other services; dry-bulb temperature alone does not validate a health-warning trigger [1]. If an organization can prepare a limited number of locations, the probability that several locations cross a threshold may matter alongside each location's probability. This study examines that information requirement using simplified portfolios of locations. It does not estimate actual staffing needs or show that the portfolios correspond to an existing response network.

Ensemble forecasts provide multiple possible weather fields. Member identifiers preserve which local outcomes occur together. Reducing these fields to a probability at each location removes that association. This is an established problem in multivariate forecast post-processing: ensemble copula coupling restores dependence using the raw ensemble's ranks [2]. It matters to distinguish information retained from forecast accuracy. A summary can reproduce an inaccurate ensemble exactly; conversely, a calibrated local probability does not identify the dependence needed for a joint event.

The information problem arises at a delivery interface that supplies only per-location probabilities: for example, a probability-map dashboard, a map image, or a downstream table exporting one exceedance probability per cell. These are illustrative delivery situations, not evidence that a named service restricts access to members. ECMWF's official Open Data client documentation describes both perturbed members and ensemble probability products (`type="ep"`) [19, relevant documentation sections checked]. Our source distributes members, so a recipient retaining them can calculate joint counts directly. The experiment asks what remains answerable after a chosen summary, rather than claiming that source users lack the original information.

Practical warning products also require events defined for the intended decision. Ponzano et al. describe co-designed ensemble products, including heat-related applications using the wet-bulb globe temperature and explicit cost–loss considerations [3]. Our temperature thresholds and capacity fractions are deliberately simpler experimental definitions, not replacements for those applications. A recent conference abstract reports operational compression of large rainfall ensembles into histograms that sacrifice spatial correlation [4; **complete abstract checked, no full study assessed**]. That report motivates examining retained joint-event information, but supplies no evidence that this study's queries represent users of that service. Numerical compression also has application-specific effects, including effects on nonlinear spatial threshold diagnostics [5]. We investigate exact low-order summaries of binary events rather than an alternative numerical-field compressor.

The practical question is not whether dependence can matter in principle. It is how much ambiguity remains in actual forecast states after particular information is released, and how often a decision can be certified despite that ambiguity. A cheap aggregate moment might retain much of what a larger pairwise table provides. Conversely, pairwise summaries might look adequate because most locations are certain, because finite ensembles imply exact zero cells, or because the chosen event is far from a decision boundary. These alternatives require explicit denominators and sensitivity checks.

**Research question.** For fixed portfolios in operational forecasts, how tightly do individual, aggregate-second-moment and pairwise summaries bound the probability that at least a specified number of locations exceed a temperature threshold, and how often do those bounds certify an illustrative binary action? Exploratory extensions ask whether the answer changes for subset queries, city-based locations and a four-time maximum. The intended readers are ensemble-product designers, researchers in multivariate forecasting, and practitioners assessing whether a delivered forecast product supports their joint-event query.

## 2. Prior work and scope of contribution

Dependence reconstruction in weather ensembles predates this study. Schefzik, Thorarinsdottir and Gneiting [2] separate calibrated margins from an empirical dependence template. Lakatos et al. [6, methods §§3.2.1–3.2.5 checked] compare several template-based approaches. Their Schaake shuffle uses historical **observations**, whereas our baseline uses ranks from earlier **forecast ensembles**. We therefore call it a historical forecast-rank reconstruction, not a Schaake shuffle or a calibrated climatology.

The European Centre for Medium-Range Weather Forecasts (ECMWF) Forecast User Guide already explains why separate event probabilities cannot generally be combined without dependence information and describes counting joint events in coherent members [12]. It also cautions that a finite ensemble's zero or one is not real-weather certainty. Our study quantifies compatibility with exact empirical summaries; it does not discover those general principles or interpret an empirical zero as absence of weather risk.

Bounds on probabilities from incomplete event probabilities are also established. Ramachandra and Natarajan [7, §1.1] review general bivariate-information linear programs and aggregated moments. Their paper's specialized pairwise-independence results do not apply to our empirically dependent events; we use the general finite-event linear-program formulation. Hoppe [8] discusses hybrid moments and the influence of redundant events on bounds. Neither the linear program, nested tightening under additional constraints, nor the fact that pairwise information need not determine higher-order events is a new result here.

Padmanabhan and Natarajan [13, §§1.2–1.3 in the checked preprint] state the same general count-tail program with given marginal and bivariate probabilities and review the sorted-marginal bound. Their specialized tree-graph results address computational tractability with partial bivariate information. Here the complete pair table is retained for small portfolios, and the research concerns its empirical information retention. This closer mathematical precedent further confines the contribution to the measured forecast cases and comparisons.

The classical literature is broader still. The checked general discussion in [7, §1.1, equations (1.5)–(1.7)] attributes the atom-based LP to Hailperin [14] and gives the Boros–Prékopa closed-form bound from the first two binomial moments [15]. Those closed forms provide a route without a full atom LP when only the two aggregate moments are retained. Our aggregate condition additionally keeps every individual probability, a stronger information set; the two are not interchangeable. The original Hailperin article was checked bibliographically only, and the original Boros–Prékopa and Prékopa [16] articles at publisher-abstract/bibliographic level only. The substantive formulation and formula statements here rely on the relevant full passage of [7], rather than an unexamined original theorem.

There is also an empirical precedent outside weather: Giglio [17, relevant full passages in §§3.1–3.2, §4.1 and §4.2.1 checked] minimizes and maximizes the probability that at least r banks default using individual and pairwise default probabilities inferred from financial prices. The empirical implementation allows inequality and linear-combination constraints inferred from prices; it is a precedent for the same count-tail LP framework, rather than an exact replica of our fully observed pair table. In a related continuous-risk setting, Bernard, Rüschendorf and Vanduffel [18] study Value-at-Risk bounds with known marginal distributions and portfolio variance; **only the institutional abstract and bibliographic record were checked**, so we do not assess their theorems or numerical results. The contribution of the present study is the application and comparison on operational ensemble temperature products, not a new probability-bounding method or the first empirical use of this LP.

Decision-specific cost–loss analysis and compound weather events are likewise established; Olivetti et al. [9] evaluate weather forecast value in a decision-specific framework. Our losses are expectations under a retained empirical ensemble law, with no observation-based verification. They must not be read as economic benefits in practice.

Within the recorded literature-search range, we did not find the same empirical comparison of these information releases for the count-tail queries studied here. This is a bounded search statement, not a claim of novelty or absence. The contribution sought is a reproducible empirical audit of ambiguity, including cases where apparently sufficient summaries owe their performance to simple or finite-sample conditions. Exact task-specific count distributions and coherent binary masks are included because a comparison only with independence would give an incomplete picture of available information products.

## 3. Methods

Plain-language terms used below:

| Term | Meaning in this study |
| --- | --- |
| Release | The summary delivered to the recipient. |
| Compatible interval and width | The smallest and largest tail probabilities possible under the delivered constraints; width is their difference. |
| Numerically identified | That interval has width at most 10⁻⁷ in the floating-point calculation. |
| Coherent binary mask | One 0/1 value per member and site, with rows aligned so each row preserves which sites exceed together. |
| Second binomial moment | The expected number of site pairs that both exceed the threshold. |
| Lattice-equivalent | A tolerance admits exactly the same integer moment counts; with fifty equal-weight members, probabilities change in steps of 0.02. |

### 3.1 Data and fixed sample

{{DESIGN_AND_AVAILABILITY}}

We use public ECMWF Open Data forecasts on the 0.25° grid. The operational products are the Artificial Intelligence Forecasting System ensemble (AIFS ENS) and Integrated Forecasting System (IFS) ensembles initialized at 00 UTC; perturbation member identifiers 1–50 are retained and the control member is excluded. Product names, valid steps, parameter, units, member identifiers and point coordinates are checked against the GRIB messages. The official operational calendar lists IFS Cycle 50r1 and AIFS ENS v2 from 12 May 2026 [10], before the sampled season. These labels are documentary attributions from the calendar, not independently decoded cycle identifiers in every GRIB message. The data period, operational product paths and retained field metadata define the measured scope.

For each center, a compact portfolio uses three latitude offsets and four longitude offsets; a dispersed portfolio uses a wider set of offsets. Exact coordinates, subset indices and the fixed calendar are in `protocol/design-v1.json`. Smaller portfolios use fixed nested locations, so size comparisons also change spatial selection and density. Portfolios may overlap and their sites are not independent observations. They are experimental spatial configurations, not a probability sample of regions or a mapping of actual service demand. Fixed absolute thresholds permit a common information comparison but do not represent equally unusual or equally harmful heat in different climates.

The archive is accessed anonymously through bounded byte-range reads of indexed public GRIB messages. Complete global transport fields are decoded, then selected site vectors are retained losslessly with source URLs, ranges, field hashes, metadata and timestamps. A small set of full temperature messages is additionally retained solely for offline decoder validation; other global values outside the selected sites are not retained, and none are analyzed as scientific variables. Offline verification starts from the bundled selected vectors and those validation fixtures; optional network re-extraction is separate. Failed transfers and partial vectors remain recorded. The cause of HTTP errors and truncated transfers is not assigned to the data provider.

Later extractions can reuse nearest-point indices only when GRIB grid-definition bytes match exactly across members. Decoded values at those indices are checked against the original nearest-point routine for the first newly decoded member and member50 of each raw unit. The retained full-message fixtures allow those checks to be repeated offline. This implementation change preserves the fixed coordinates, member identities and selected values; no controlled speed comparison is claimed.

### 3.2 Target and released information

Let \(X_{mj}=1\) when member \(m\)'s temperature at site \(j\) meets or exceeds threshold \(t\). The empirical distribution assigns mass \(1/M\) to each of the \(M\) coherent binary rows. For a portfolio of \(n\) sites, let \(S=\sum_j X_j\) and \(q_k=P(S\geq k)\). “Probability” below means this empirical ensemble probability unless explicitly stated otherwise.

Here \(k\) is an activation threshold measured in locations. If an application instead specifies a literal capacity of \(C\) locations, the event of exceeding that capacity would use \(k=C+1\). The studied fractions do not assert an existing service's capacity.

We compare three nested releases:

1. Individual probabilities \(p_j=E[X_j]\).
2. Those probabilities and the scalar \(a=E[\binom{S}{2}]\).
3. Those probabilities and every \(b_{ij}=E[X_iX_j]\).

The scalar is the second binomial moment, half the second factorial moment. The aggregate scalar equals \(\sum_{i<j}b_{ij}\). When deterministic sites are removed computationally, their contributions are determined by the fixed margins and are accounted for exactly. We minimize and maximize \(\sum_x w_x1\{\sum_j x_j\geq k\}\) over binary states \(x\in\{0,1\}^n\), subject to \(w_x\geq0\), \(\sum_xw_x=1\) and the corresponding released equalities. The interval \([L_k,U_k]\) is sharp within this finite-state class up to numerical tolerance. Marginal-only endpoints use the classical sorted-marginal expression reviewed in [13, §1.2], checked against the equivalent linear program on validation fixtures.

The primary feasible class permits arbitrary real probability weights. It is larger than the class of exactly \(M\) equally weighted coherent rows. This is a substantive distinction, tested by the prespecified integer sensitivity rather than hidden in the word “ensemble.” The binary-state class imposes no further atmospheric dynamics or spatial-smoothness constraints. Its extrema describe compatibility with the released information; they need not describe equally plausible meteorological scenarios. Exact zero pair cells exclude states because probabilities are nonnegative; deterministic sites are removed. Such reductions preserve the feasible set for exact inputs. The perturbation sensitivity restores all binary states and relaxes the individual and pairwise equalities.

We use SciPy/HiGHS dual simplex with per-solve time limits and verify primal residuals, nonnegative mass, dual feasibility and the primal–dual gap. The numerical identification tolerance is \(10^{-7}\). These checks are floating-point certificates, not formal exact-arithmetic proofs. Analytic fixtures, random binary examples, permutations, complements, integer cases and round trips are checked separately from weather results.

### 3.3 Evaluation and comparisons

The primary metric is interval width \(U_k-L_k\), reported across all cases and in a stratum fixed in advance: at least four sites have empirical probabilities strictly between zero and one, and \(0.1\leq q_k\leq0.9\). This stratum exposes uncertainty hidden by floor and ceiling cases; conditioning on it changes the target population of queries. It is not an observed-weather verification set. We count \(q_k=0\), \(q_k=1\), deterministic portfolios and portfolios with at most two uncertain sites. In particular, an empirical tail at zero or one need not imply that a coarse summary determines it.

For an illustrative protective action with cost–loss ratio \(c\), acting has normalized expected cost \(c\), and not acting has expected loss \(q_k\). A weakly optimal action is certified when \(U_k\leq c\) or \(L_k\geq c\), with ties and the numerical tolerance explicit. The fixed cost ratios are illustrations, not measured practitioner preferences. Interval width also equals the length of cost ratios in \([0,1]\) where neither action is certified. This identity is an interpretation of the metric, not an experimental discovery or an assumption that real cost ratios are uniform.

Point reconstructions include independence via a Poisson-binomial distribution, the pair-interval midpoint, and a historical forecast-rank template. The latter uses up to six earlier complete initialization dates for the same product and lead, requires at least three, resolves temperature-rank ties by member identifier, and applies each earlier rank template to the current exceedance counts. It reproduces the current margins exactly but is not guaranteed to reproduce current dependence. Comparisons with this baseline use a common availability set. These methods consume different information: the comparison measures the combined release and reconstruction. Point error and illustrative decision regret are computed against the original ensemble, not against observations.

A full distribution of \(S\) exactly answers every capacity threshold for the known portfolio, so it is an essential reference. We do not propose pairwise tables as a preferable delivery format for that task. A coherent binary mask also answers every query for that fixed temperature threshold, including subset queries. Its sufficiency follows by construction and is checked by round trips.

### 3.4 Repetition, uncertainty and prespecified sensitivities

The fixed sample crosses initialization dates, forecast products, lead times, centers, geometries, temperature thresholds and capacity fractions. We preserve those paired conditions when resampling dates. Circular moving-block resampling uses three scheduled date slots per block and the fixed seed, with 2,000 repetitions. Reported intervals describe resampling variation within this convenience sample. They do not measure calibration uncertainty, population representativeness, or independent variation among every site, member or query. Missing scheduled dates remain slots in the resampling design; replicates with no eligible query have undefined means and are omitted from the quantiles.

Prespecified sensitivities use one seeded nested member subset of sizes 10 and 25 per forecast. A deterministic hash ordering selects up to 120 informative primary cases for integer-weight extrema and moment perturbation. Integer solves have a five-second limit per endpoint; unresolved cases are reported. The pairwise perturbation analysis allows each individual and pairwise probability to differ from its released value by at most 0.005 or 0.02. These are mathematical sensitivity neighborhoods, not simultaneous statistical confidence sets or estimated measurement errors.

### 3.5 Exploratory extensions

The subset extension was planned after the initial primary result was available and is explicitly exploratory. For fixed queries containing four or eight sites from a twelve-site universe, it compares all universe pairwise information with the full universe count distribution plus individual probabilities. These information sets are not nested. A query-only pairwise table is a diagnostic; a query-specific count distribution and the coherent binary mask are exact references. Queries were fixed without selecting for outcome differences. The informative subset stratum additionally requires at least two uncertain sites outside the query. The count distribution determines a shifted subset count if every outside site is individually deterministic; a constant outside count observed only in the original ensemble is not the same released-information guarantee.

The city/time extension was fixed before acquiring its new coordinate vectors. Natural Earth's public-domain populated-place layer supplies a geography-only eligibility filter and selection, using metropolitan population estimates only for eligibility, not burden weights or rankings. Twelve distinct snapped cells are selected near each center and by a dispersed maximin rule. The original proposed gazetteer was abandoned when its robots policy prohibited retrieval; it was not obtained from a mirror. The replacement source and exact realized coordinates were committed before new weather extraction. These are cartographic city samples, not complete city censuses or verified urban microclimates. Their changed locations and spacing do not isolate an urban land-use effect.

The schedule contains twelve fixed dates. For each completed product/horizon combination, four six-hourly fields on the forecast day are aligned by member ID. The sitewise maximum over those four samples is compared with the 12 UTC snapshot. It is not the continuous daily maximum, and a threshold crossed at different sites need not be crossed simultaneously. The original regular portfolios are re-extracted alongside the city portfolios to check extraction consistency. The extension shares dates and forecasts with the primary study and is not independent confirmation. Its resampling uses two scheduled dates per block. Common informative queries under both time definitions are reported alongside each definition's own stratum.

Further exploratory checks address interpretation. For an exact pair constraint matrix \(A\), full column rank is a sufficient condition for unique binary-state weights; an event vector \(e=A^Ty\) has probability \(y^Tb\) fixed by the released moments. We count constant events after zero-cell pruning, full-column-rank cases, numerical event row-space membership and remaining cases separately. Rank uses a relative singular-value threshold of \(10^{-10}\), row-space residual tolerance \(10^{-8}\). These are numerical sufficient-condition diagnostics; rank deficiency does not prove that nonnegative feasible weights are nonunique. Separately, marginal- and aggregate-interval midpoints provide additional point controls with the same error/regret outcomes, leaving the originally planned methods intact.

After the prespecified member-size summaries revealed different informative denominators, an exploratory saved-data comparison holds query identities fixed using the M50 informative set and the intersection informative at all three member sizes. The same nested member selections are retained. This controls query composition, while the empirical laws still change; it does not identify a causal effect of ensemble size or provide repeated-sampling uncertainty.

{{REPEATED_MEMBER_METHOD}}

After the all-moments perturbation result, controlled precision comparisons keep individual probabilities exact, then keep their aggregate second binomial moment exact as well, while allowing pairwise moments the original tolerances. The frozen sensitivity cohort, full binary-state space and LP tolerances remain unchanged. These additions are exploratory and do not model a measured publication error.

{{INTEGER_PRECISION_METHOD}}

Coverage diagnostics use all observed complete-unit outputs, including units on otherwise unmatched dates. If \(N\) scheduled widths include \(K\) missing values and observed sum \(T\), the safe full-schedule mean envelope is \([T/N,(T+K)/N]\), using width bounds \([0,1]\). Unknown informative eligibility is treated conservatively. Equal-center weighting, leave-one-center-out estimates and block lengths one and five are additional sensitivities. These envelopes and weighting choices are exploratory and do not imply random missingness or representative sampling.

An optional exploratory coverage check can reuse the already scheduled overlapping city extraction for the exhausted original unit. It requires agreement with every retained original member's values and field hash and with the original index. Its separately derived regular-site input and recovered-calendar summary preserve the original missing flag and primary sample. It introduces no extra retrieval and no independent forecast sample.

### 3.6 Reuse terms and research process

ECMWF data are used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and the applicable general terms. **This document is based on data and products of the European Centre for Medium-Range Weather Forecasts (ECMWF).** © 2026 ECMWF. We extracted locations, thresholded members and computed new summaries; ECMWF has not endorsed these analyses. Natural Earth data are public domain. Source-specific reuse records and retrieval dates are included with the data.

Plans and revisions, source passages, failed experiments and Git commits are bundled. Git dates are self-reported and hashes establish file consistency, not independence or tamper-proofness. One authorized topic-candidate critique used the API model identifier `gpt-6-astra`, reasoning effort `xhigh`, on 25 October 2026 UTC; its original request, output and usage are retained. It was topic-selection consultation, not experimental data, paper authorship or peer review. No AI API was used to write or debug the analysis. The model carrying out the study is presented in the session as GPT-6/Codex; an exact runtime model identifier was not observable. No human participants or individual-level records were used.

## 4. Results

{{RESULTS_PRIMARY}}

{{RESULTS_DECISIONS}}

{{RESULTS_SENSITIVITIES}}

{{RESULTS_EXPLORATORY}}

## 5. Discussion

{{DISCUSSION_RESULTS}}

The general lesson is to specify the query before deciding that a forecast summary is sufficient. For a fixed portfolio, the count distribution is an exact compact answer to every capacity threshold. For changing subsets at a fixed temperature threshold, preserving coherent binary scenarios is another exact option. Pairwise tables may support a wider range of queries than a single total-count curve, but that does not make them universally sufficient or the preferred encoding. Our fixed-width payload accounting excludes headers, optimal coding and general compression; it cannot establish actual download savings or a provider deployment recommendation.

{{PRACTICAL_ENCODING}}

The admissible probability laws and the precision of the release must also be specified together. A continuous moment neighborhood allows probabilities unavailable to a known equal-weight ensemble. In the fixed-size check, an allowance smaller than one moment-count increment leaves the integer constraints unchanged. This qualifies any interpretation that a small decimal tolerance necessarily destabilizes an exact finite-ensemble release. Larger tolerances can allow changed counts; the new integer solves measure that regime while retaining bounds for unresolved endpoints. Neither neighborhood estimates the precision of a particular forecast product.

The results describe compatibility under released empirical moments. They do not justify replacing a coherent forecast with an independence reconstruction, nor do they show that the original joint forecast is correct. A practitioner would still need a locally meaningful event definition, calibrated forecasts, realistic capacity costs and evaluation with observations. Those requirements are separate from checking whether the delivered information can answer the desired query.

## 6. Limitations

The spatial configurations and calendar are convenience designs from a limited season and two operational products. Absolute temperature thresholds have different climatological meanings across locations; no region or product is ranked for public-health performance. Site counts are not population exposure, workload or simultaneous peak demand. City coordinates are snapped to coarse model cells, and the cartographic source's population definitions and dates differ. The four-time maximum misses between-sample extremes and is defined on a UTC day rather than each location's local warning day.

All reference probabilities come from finite raw ensembles. Exact zero probabilities and exact pair cells can make partial identification appear stronger than it would be for a smoothed or population forecast law. Moment perturbation probes that sensitivity but does not estimate the true uncertainty in moments. The main LP allows arbitrary weighted laws; the integer comparisons cover a selected cohort. Exact optima and bounds for unresolved integer endpoints have separate denominators. Larger portfolios, different ensemble sizes, additional thresholds, weights for unequal site burdens, changing portfolio membership and other hazards are not established by these results.

Complete-case matching may introduce selection if transfer failures depend on archive or field properties. Partial and unmatched data are retained; their absence is not evidence of weather performance. Historical templates use a short archive and are not an optimized or calibrated dependence model. Midpoint comparison does not estimate the optimal practical reconstruction. Numerical tolerance can affect very small widths and boundary ties. Resampling intervals cannot repair the sample's lack of representativeness or make correlated queries independent.

No human usability, adoption, health benefit, realized economic benefit or actual network traffic was measured. The exploratory extensions were added after an early primary result; they are not independent confirmatory tests. The trial is one AI-led study. {{CRITIC_IDENTIFICATION}} {{REVIEW_STATUS}} Neither the critique nor the author’s verification constitutes independent human peer review or independent reproduction.

## 7. Reproduction and availability

`VERIFY.md` gives a single offline entry point, a reduced numerical replay and the full replay procedure. Saved selected-temperature arrays and original responses suffice without an AI API or external network. Reproduction writes to a caller-supplied output location outside the checked source copy. Optional fresh data extraction and the original topic-critique API call are separate from recomputation. `claims.jsonl` maps main claims to artifacts, commands and expected results. {{VERIFICATION_RESULT}}

## References

1. WHO Regional Office for Europe (2026). *Heat–health action plans: guidance, second edition: executive summary.* [Official publication](https://www.who.int/europe/publications/m/item/heat-health-action-plans--guidance--second-edition--executive-summary).
2. Schefzik, R., Thorarinsdottir, T. L., & Gneiting, T. (2013). Uncertainty quantification in complex simulation models using ensemble copula coupling. *Statistical Science*, 28, 616–640. [doi:10.1214/13-STS443](https://doi.org/10.1214/13-STS443).
3. Ponzano et al. (2025). Bridging the gap between ensemble forecasting and end-user needs for decision-making on high-impact events. *Advances in Science and Research*, 22, 39–52. [doi:10.5194/asr-22-39-2025](https://doi.org/10.5194/asr-22-39-2025).
4. Cooper, F., Nath, S., Weisheimer, A., & Palmer, T. (2026). Histogram compression of large ensemble forecasts. EGU26-15706. **Conference abstract only.** [doi:10.5194/egusphere-egu26-15706](https://doi.org/10.5194/egusphere-egu26-15706).
5. Tintó Prims, O., Redl, R., Rautenhaus, M., Selz, T., Matsunobu, T., Modali, K. R., & Craig, G. (2024). The effect of lossy compression of numerical weather prediction data on data analysis: a case study using enstools-compression 2023.11. *Geoscientific Model Development*, 17, 8909–8925. [doi:10.5194/gmd-17-8909-2024](https://doi.org/10.5194/gmd-17-8909-2024).
6. Lakatos, M., Lerch, S., Hemri, S., & Baran, S. (2022). Comparison of multivariate post-processing methods using global ECMWF ensemble forecasts. [arXiv:2206.10237v2](https://arxiv.org/html/2206.10237v2).
7. Ramachandra, A. K., & Natarajan, K. (2023). Tight probability bounds with pairwise independence. *SIAM Journal on Discrete Mathematics*, 37(2), 516–555. [doi:10.1137/21M1408294](https://doi.org/10.1137/21M1408294). General LP discussion used; pairwise independence not assumed here.
8. Hoppe, F. M. (2009). The effect of redundancy on probability bounds. *Discrete Mathematics*. [doi:10.1016/j.disc.2007.12.052](https://doi.org/10.1016/j.disc.2007.12.052).
9. Olivetti, L., Messori, G., Avner, P., & Hallegatte, S. (2026). Assessing the real-world economic value of weather forecasts under compounding extremes: a decision-specific framework. World Bank Policy Research Working Paper 11407. [Official report](https://documents.worldbank.org/curated/en/099836006022622606/pdf/IDU-3d41fc50-bb68-481a-ae9f-95c258fb251c.pdf).
10. ECMWF. *AIFS data specification; operational cycle calendar and joint upgrade announcement; Open Data and general terms.* Relevant official pages and retrieval records are archived in `literature/` and `sources.jsonl`. {{ECMWF_OFFICIAL_LINKS}}
11. Natural Earth. *1:10m cultural vectors: populated places; terms of use.* [Populated places](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/), [public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/). Archive version and SHA-256 are recorded with the realized design.
12. ECMWF (2022). *Forecast User Guide, 7.1 Consideration of Probability*, version 15, 14 November 2022. [Historical version](https://confluence.ecmwf.int/pages/viewpage.action?navigatingVersions=true&pageId=298956912). Relevant full sections on time intervals, areas, combined events, finite ensembles and calibration checked. No current interface capability is inferred from this historical page.
13. Padmanabhan, D., & Natarajan, K. (2021). Tree bounds for sums of Bernoulli random variables: a linear optimization approach. *INFORMS Journal on Optimization*, 3(1), 23–45. [doi:10.1287/ijoo.2019.0038](https://doi.org/10.1287/ijoo.2019.0038). Relevant full passages checked in [arXiv:1910.06321v1](https://arxiv.org/pdf/1910.06321v1), the 2019 preprint.
14. Hailperin, T. (1965). Best possible inequalities for the probability of a logical function of events. *American Mathematical Monthly*, 72(4), 343–359. [doi:10.1080/00029890.1965.11970533](https://doi.org/10.1080/00029890.1965.11970533). Original bibliographic record only; historical attribution checked through the full general discussion in [7].
15. Boros, E., & Prékopa, A. (1989). Closed form two-sided bounds for probabilities that at least r and exactly r out of n events occur. *Mathematics of Operations Research*, 14(2), 317–342. [doi:10.1287/moor.14.2.317](https://doi.org/10.1287/moor.14.2.317). Original publisher abstract/bibliography only; relevant formula checked in the full text of [7].
16. Prékopa, A. (1990). Sharp bounds on probabilities using linear programming. *Operations Research*, 38(2), 227–239. [doi:10.1287/opre.38.2.227](https://doi.org/10.1287/opre.38.2.227). Publisher abstract and bibliography only.
17. Giglio, S. (2016). *Credit default swap spreads and systemic financial risk.* ESRB Working Paper No. 15, June 2016. [Official full paper](https://www.esrb.europa.eu/pub/pdf/wp/esrbwp15.en.pdf). Relevant full formulation and empirical-comparison passages checked (see §2 and source notes).
18. Bernard, C., Rüschendorf, L., & Vanduffel, S. (2017). Value-at-Risk bounds with variance constraints. *Journal of Risk and Insurance*, 84(3), 923–959. [doi:10.1111/jori.12108](https://doi.org/10.1111/jori.12108). [Institutional abstract and bibliography only](https://researchportal.vub.be/en/publications/value-at-risk-bounds-with-variance-constraints/); full paper not assessed.
19. ECMWF. *ecmwf-opendata: official client documentation.* [README](https://github.com/ecmwf/ecmwf-opendata/blob/main/README.md). Sections “Stream and type”, “Download the ensemble probability products” and “ECMWF open data license” checked 26 October 2026; archived copy bundled.

## Appendix: additional descriptive analyses

{{APPENDIX_RESULTS}}

## Revision history

Revised after one review by an AI agent (REVIEW-1). The abstract now answers both width and action-certification questions and states the exact-moment, finite-member and geometry limits. Table 2 includes all prespecified decision strata; Appendix L displays the prespecified product × geometry × lead strata. Appendix M adds clearly labelled post-review diagnostics from saved cases. Prior-work positioning now names the classical binomial-moment literature and the empirical financial-risk precedent, with access levels stated. A glossary, delivery examples, encoding comparison and spacing corrections improve readability. Primary data, cohort, LP endpoints and reported primary numbers are unchanged. The original failed diagnostic record is preserved with an appended index correction. See `review/response-1.md` for pointwise decisions and verification.
