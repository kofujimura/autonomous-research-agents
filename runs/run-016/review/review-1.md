REVIEW-1
- Review ID: review-016-1
- Target: tag submission-1, commit faf7dce40c1a27313b4ae7fb51554fa5d061393b (HEAD of run-016 at start and end of this review)
- Reviewer's model: identifier confirmed from the execution environment: none names the model; confirmed only Claude Code CLI 2.1.311 and CLAUDE_EFFORT=xhigh. Model identifier stated in the runtime system prompt: claude-opus-5-5. Name given in the conversation: Opus 5.5 (human-specified, reasoning effort xhigh).
- Review period: start 2026-10-27T02:25:46Z (11:25:46 JST), end 2026-10-27T02:45:56Z; excluded usage-limit stop time: 0 (no stop occurred)
- Scope of verification carried out:
  - Full VERIFY.md single entry point (`verify.py --all`) on a `git clone --no-hardlinks` copy checked out at submission-1, in a dedicated venv built from requirements-verify.txt; output in review-016/verification/out-full. Result: passed in 802 s (exit 0): 12 input checks including reconstruction of 7,359,539 feature-to-prediction rows from saved coefficients (maximum probability difference 0.0), 88 main CSV tables and 1,530 main raw-array files, 36 supplemental tasks with 93 CSV and 3,291 raw-array files (maximum absolute numeric difference 0.0 in all), the timeline check of 108 experiment records, and exact byte matches of the regenerated paper.md and claims.jsonl. No step wrote to the research directory; the copy's working tree was unchanged afterwards. The research side noted that a fresh minimal installation had not been tested; this run used one and passed.
  - My own code (not the research side's estimator code) recomputing the primary broad direct-sampling results (all 5 budgets, both designs, 90 primary units) from the raw label arrays and saved draw indices.
  - Comparison of the `expected` values in claims.jsonl with the evidence files for C01–C11.
  - Timeline check of all 108 experiments/*/run.json records against Git commit times; API ledger check against the saved response.
  - Existence check of 13 of the 19 cited sources via Crossref, arXiv and NTRS metadata (content checked against abstracts for 2 of them), plus a novelty search.
  - Four reviewer sensitivity calculations on the saved data (labelling error, landscape-level resampling, post-stratified estimator, landscape resampling for C10). These are my own additional analyses, not part of the submitted study.
  - Not carried out: raw data re-acquisition or classifier refitting; hash check of the Git-excluded catalogue/range caches in a copy (I checked the SHA-256 inventory only against the research directory itself); full-text reading of every cited paper.

## 1. Summary of the paper

The paper asks whether, at a fixed number of reference labels per year, revisiting the same reference locations improves estimates of year-to-year change in the Shannon diversity of declared crop groups, and how reliably estimates assisted by frozen classifiers on annual satellite embeddings (TESSERA, AlphaEarth) identify the direction of change. Using SwissCrop25 declarations 2021–2025 as the reference, 30 held-out 5.12 km Swiss landscapes and 90 adjacent-year transitions, it simulates 500 probability samples per condition at 32–512 labels/year. Revisited direct sampling has about 0.27 times the MSE of independent annual samples, but its nominal 95% intervals cover only 83.4% at 128 labels/year (93.1% for independent samples), and a no-change point prediction has lower RMSE (0.0260) than any sampled estimator at 128 labels/year. The preplanned model-assisted intervals are very conservative and rarely report a direction; exploratory analyses show that this depends on a numerical gradient floor and on ignoring the simplex projection, and that the precision gain of revisiting is smaller or reversed on stable arable land.

## 2. Overall verdict

Major revision.
The numerical results are reproducible: the research side's full entry point passed on a clean copy in a fresh environment (all 88 + 93 tables, 1,530 + 3,291 raw-array files, exact regeneration of paper.md and claims.jsonl), and my own independent code reproduced the primary direct-sampling numbers exactly. The process is unusually well recorded and the paper scopes most statements carefully. Revision is needed mainly in interpretation and presentation, not in the numbers: (i) the coverage deficit and the size of the revisiting gain depend on error-free, perfectly repeatable declared labels, which the paper does not test (a cheap sensitivity changes the picture); (ii) the title and abstract give weight to satellite embeddings, whereas the main precision result uses no embeddings and frozen-classifier assistance did not improve revisited estimates; (iii) several decision-relevant numbers that are already in the outputs (arable-dominated ratio, conditional wrong-direction rates, per-landscape coverage, between-landscape uncertainty) are missing from the text; (iv) classic and operational prior work is missing. Most requested actions are text changes plus short analyses on saved data.

## 3. Scores (1–5, one line of reason each)
- Correctness of claims: 4 — every checked number matches; statements are mostly qualified, but C02 is interpreted without the labelling-error alternative and C04 is presented as a model-assistance result although it is mainly an artefact of the interval rule.
- Verifiability: 5 — one offline command regenerated all indexed tables, raw arrays and the paper/claims documents on a copy, and my own code reproduced the primary values; plans, code commits and experiment starts are in a consistent order.
- Novelty: 2 — an application of established estimators and repeated-occasion sampling theory; the direction of the main result follows from classic theory; the specific empirical combination (fixed-budget change in crop-group diversity with embedding-assisted estimators) was not found in my search.
- Generality: 2 — 30 Swiss landscapes, two-thirds grassland-dominated, pixel samples of error-free declarations; the gain shrinks on arable land, and the coverage deficit is sensitive to labelling error.
- Usefulness to readers: 3 — the no-change comparison, the low resolvability of annual change, and the support dependence are useful warnings, but the operational setting the simulation represents is not made concrete and key practical numbers are buried.
- Clarity: 2 — the abstract contains about twenty numbers, many from exploratory checks, and uses terms (entropy units, clipped-gradient rule, soft-logistic, projection derivative) that monitoring practitioners will not follow; results are not expressed on an interpretable scale.

## 4. Verification results
| claim_id | Claim (shortened) | Procedure run | Result | Record path |
| --- | --- | --- | --- | --- |
| C01 | Revisiting lowers direct broad MSE at all five budgets (ratio 0.267–0.278) | verify.py --all; own-code recomputation; expected vs evidence file | match (ratios 0.266728–0.277982 by both; own code n=128 ratio 0.27514) | verification/out-full/verification-result.json; verification/V04_independent_direct/summary-broad.json |
| C02 | n=128 revisited coverage 83.4% vs independent 93.1%; 35 tiny, 4 zero, 0 floor cases | verify.py --all; own-code recomputation; expected vs evidence file | match (0.834244 / 0.930933; 35 / 4 / 0) | verification/out-full/verification-result.json; verification/V04_independent_direct/summary-broad.json |
| C03 | No-change RMSE 0.0260 beats n=128 direct (0.0559) and frozen-model-assisted estimates | verify.py --all; own code (no-change and direct); evidence files for assisted/forest | match (0.026050 / 0.055890; assisted 0.0469–0.0957 all higher) | verification/out-full/verification-result.json; verification/V04_independent_direct/summary-broad.json |
| C04 | Original soft-logistic assisted intervals: coverage 98.8–99.1%, reports 1.1–1.4%, projection ~99% | verify.py --all; expected vs evidence file | match (values match; interpretation qualified in R1-5) | verification/out-full/verification-result.json; verification/V08_claim_evidence_sample.txt |
| C05 | Stable-arable frame (25 landscapes, 75 transitions): coverage 93.07% vs 93.08% | verify.py --all; expected vs evidence file | match | verification/out-full/verification-result.json; verification/V08_claim_evidence_sample.txt |
| C06 | 12.92% zero-change revisited draws; 54.8% of misses; 12 units with ceiling <95%; union 92.5% | verify.py --all (all fields); own code (zero-change fraction) | match (own code 0.1292) | verification/out-full/verification-result.json; verification/V04_independent_direct/summary-broad.json |
| C07 | Gradient floor changes assisted coverage (93.7% at 1e-2 to 99.5% at 1e-10), RMSE unchanged | verify.py --all; expected vs evidence file | match | verification/out-full/verification-result.json; verification/V08_claim_evidence_sample.txt |
| C08 | Half-retained panel: RMSE 0.0864, Bonferroni joint coverage 92.4% vs full revisit 77.8% | verify.py --all; expected vs evidence file | match | verification/out-full/verification-result.json; verification/V08_claim_evidence_sample.txt |
| C09 | Native-grid check: 3 cases, 9 transitions, 2 sign disagreements, discrepancy RMSE 0.0085 | verify.py --all; expected vs evidence file | match | verification/out-full/verification-result.json; verification/V08_claim_evidence_sample.txt |
| C10 | Additional stable-arable broad ratio 1.074 (1.066 at 5,000 reps); fine 0.941/0.913 | verify.py --all; expected vs evidence file; reviewer landscape bootstrap | match for the values; landscape-level 95% interval 0.96–1.19 includes 1 (R1-3) | verification/out-full/verification-result.json; verification/V10_c10_bootstrap/result.json |
| C11 | Projection derivative: assisted paired coverage 93.6–93.7%, reports 8.0–8.2%, point estimates identical | verify.py --all; expected vs evidence file | match | verification/out-full/verification-result.json; verification/V08_claim_evidence_sample.txt |

The entry point regenerated claims.jsonl and paper.md byte-for-byte from the recomputed outputs, so every `expected` value in claims.jsonl is consistent with the re-run outputs. Recomputation was complete, not reduced (all 500 replications, all budgets and conditions indexed in verification-config.json).

## 5. Findings

### R1-1
- Severity: Moderate
- Type: Insufficient evidence
- Target: paper.md Abstract, §4.2, §4.4, §5, §6; claims C01, C02, C06
- Content:
  - Observed: In the benchmark the same declaration database supplies both the "truth" and the audit label, so an unchanged location always gives identical labels in both years. 12.9% of revisited n=128 samples contain no changed label and therefore give a zero-width interval (C06; reproduced by my code, verification/V04_independent_direct/summary-broad.json, zero_change_frac 0.1292). In a reviewer sensitivity check (scripts/label_noise_sensitivity.py; verification/V06_label_noise/result.json), each sampled label was independently replaced in each year, with probability ε, by a draw from that landscape-year's class distribution excluding the true class, while the target remained the error-free population change. With ε = 0 / 0.01 / 0.02 / 0.05 the revisited direct coverage at n=128 was 83.4% / 91.8% / 92.3% / 92.5% (independent: 93.1% / 93.1% / 93.0% / 93.1%), and the revisited/independent MSE ratio was 0.275 / 0.309 / 0.343 / 0.433.
  - Inference: The aggregate coverage deficit of revisited intervals (C02) and part of the precision gain (C01) are properties of error-free repeated labels, not only of the sampling design. In an audit by field visit or photo-interpretation, independent errors of 1% would remove most of the deficit, and larger errors would reduce the gain. Positively correlated errors (same interpreter, same ambiguous parcel) would lie between these cases. My noise model is one simple choice, not an estimate of real error rates. §6 says that pixel observations differ from field visits, but does not state that the two central findings depend on this.
- Requested action: (Priority 1) Add a sensitivity analysis of independent (and, if time allows, partly correlated) annual labelling error at the audited locations for n=128 broad direct estimation, using the saved draws, and report coverage and MSE ratio for several error rates. My script runs in under 20 seconds. State in the abstract and the discussion that the coverage deficit and the size of the gain refer to perfectly repeatable labels, and say what this means for field or photo-interpreted audits.
- Feasibility of the action: can be done within the research environment.

### R1-2
- Severity: Moderate
- Type: Overclaim
- Target: title; Abstract; §4.2 Table 1; §5
- Content:
  - Observed: The headline precision result (C01; Table 2) uses direct sample proportions and no satellite input. At n=128 with revisiting, frozen-logistic assisted RMSE is 0.0605 (TESSERA) and 0.0565 (AlphaEarth) against 0.0559 for direct sampling (Table 1). Frozen forests reach 0.0494/0.0469. With independent samples, logistic assistance gives 0.0947/0.0957 against 0.1066. The abstract reports the model-assisted interval coverage and reporting rates, but not their point accuracy. My post-stratified (hard map class) estimator check (verification/V09_poststrat/) gives the same picture: with revisiting 0.0560/0.0555 against 0.0559 direct; with independent samples 0.0925/0.0923.
  - Inference: For the main design the study recommends, assistance from embeddings with a frozen source-year classifier did not improve point accuracy. This is a substantive finding for readers who consider using embedding products. The title ("…from annual satellite embeddings") and the abstract suggest that embeddings play a central part in the reported gain.
- Requested action: (Priority 1) Put the model-assisted point-accuracy result in the abstract: frozen logistic assistance gave no RMSE gain under revisiting, and forests a modest one. Revise the title so that it names the scope (Swiss declared crop groups, a resampling benchmark) and does not attribute the result to embeddings. Optionally mention that the standard post-stratified map-class estimator gives similar results, or list it as an untested standard comparator.
- Feasibility of the action: can be done within the research environment.

### R1-3
- Severity: Moderate
- Type: Insufficient description
- Target: Abstract; §4.2 Table 2; §4.3; claim C01
- Content:
  - Observed: results/tables/main/pairing-mse-ratios.csv gives, at n=128, a revisited/independent MSE ratio of 0.198 for the 60 grassland-dominated transitions and 0.597 for the 24 arable-dominated transitions. This split was planned in advance (plan-v1 check g). The paper reports only the arable-dominated coverage. The paper's uncertainty statements are Monte Carlo SEs (ratio MCSE 0.003). A landscape-level bootstrap (30 landscapes, 5,000 resamples; verification/V07_cluster_bootstrap/result.json) gives a 95% interval of 0.21–0.36 for the n=128 ratio; per-unit ratios range from 0.00 to 0.97. For C10 (6 additional landscapes) the same resampling gives 0.96–1.19 around 1.066, against a reported MCSE of 0.006 (verification/V10_c10_bootstrap/result.json).
  - Inference: The figure "0.267–0.278 times" is mainly a grassland result. For arable crop-diversity monitoring the prespecified estimate is about 0.6. The landscape-level interval (±0.075) is more than ten times wider than the Monte Carlo interval (about ±0.006), and the C10 "reversal" cannot be distinguished from no difference at landscape level.
- Requested action: (Priority 2) Report the prespecified grassland/arable ratios in Table 2 and in the abstract sentence about the ratio. Add a landscape-level resampling interval (or the range across landscapes) for the main ratio, the coverages and the C10 ratio, labelled as within-cohort variability, not national uncertainty. In the C10 text, state that the 6-landscape interval includes 1.
- Feasibility of the action: can be done within the research environment.

### R1-4
- Severity: Moderate
- Type: Insufficient description
- Target: Abstract; §4.2; §5; claims C02, C03
- Content:
  - Observed (recomputed with my code, verification/V04_independent_direct/breakdown-broad.txt and summary-broad.json): at n=128, among reported directions 868/4,285 (20%) are wrong with revisiting and 1,126/3,513 (32%) with independent samples. For units with |ΔH|<0.01 the shares are 42% and 50%; for |ΔH|≥0.01 they are 14% and 24%. At n=32 and n=64 the per-trial wrong-direction rate exceeds 2.5% (independent 4.4%/3.4%, revisited 3.7%/2.7%). Per-unit revisited coverage at n=128 has a minimum of 8.2% and a 10th percentile of 40.6%, and 32 of 90 units are below 90% (the median and 10th/90th percentiles are also in results/tables/main/unit-performance-distributions.csv and match, but are not given in the paper text). The no-change prediction has a smaller squared error than the revisited direct MSE in 84/90 units at n=128 and 62/90 at n=512. Revisited RMSE at 512 labels/year (0.0268) is still above the no-change RMSE (0.0260).
  - Inference: For a practitioner the decisive question is "when the method reports an increase or decrease, how often is it right?". The abstract gives only per-trial rates (1.9% / 2.5%), which can be read as a low error rate for reported directions. The aggregate coverage also hides very poor coverage in a third of the units. The fact that no tested budget up to 512 labels/year beats the no-change prediction is a clear practical result, but it is stated only for n=128.
- Requested action: (Priority 2) Add the conditional wrong-direction share (with denominators) and the per-unit coverage distribution to the abstract or the first results paragraph, and state that no tested budget (≤512 labels/year) reached the no-change RMSE. Consider reporting the prespecified 2022→2025 secondary contrast against its own no-change baseline, so that readers can see whether longer intervals help.
- Feasibility of the action: can be done within the research environment (the values are in existing output files).

### R1-5
- Severity: Moderate
- Type: Overclaim
- Target: Abstract (sentence on soft-logistic intervals); §4.2; §4.4 Table 5; §4.6 Table 7; claims C04, C07, C11
- Content:
  - Observed: The preplanned model-assisted interval evaluates the entropy gradient at the projected proportions with a floor of 10^-6, but does not differentiate through the simplex projection, which is applied in 98.8–99.7% of logistic-assisted estimates (Table 1). Classes projected to zero receive a gradient of −ln(10^-6)−1 ≈ 12.8 while carrying prediction residuals, which inflates the SE (mean SE 0.118 against 0.058 with the projection derivative; Table 7). The paper's own exploratory results show coverage of 93.6–93.7% and reporting of 8.0–8.2% once the derivative is applied (C11).
  - Inference: The conservative coverage and rare reporting in C04 mainly reflect a mis-specified linearisation in the preplanned rule, not a property of model-assisted inference. The abstract presents C04 first and the correction later, in technical terms, which is hard to interpret. The paper is right to keep the preplanned result, but readers need the conclusion stated plainly.
- Requested action: (Priority 3) In the abstract and §5, state in plain words that the preplanned interval rule for the assisted estimator omitted the derivative of the projection, that this made its intervals too wide, and that with the derivative the assisted intervals behave like the direct ones (with the caveats already given). Keep C04 as a preplanned result, but qualify its reader_implication accordingly.
- Feasibility of the action: can be done within the research environment.

### R1-6
- Severity: Moderate
- Type: Insufficient description
- Target: §1–§2 (background and prior work); sources.jsonl
- Content:
  - Observed: The theory of sampling on successive occasions with partial replacement goes back to agricultural surveys: Jessen (1942, Iowa farm survey), Patterson (1950, JRSS B 12:241–255), and Cochran's textbook chapter. None of these is cited; the paper cites a 1981 NASA contractor report and Massey & Mandallaz (2015). Standard variance and comparison tools for the Shannon index (Basharin 1959; Hutcheson 1970, J. Theor. Biol. 29:151–154) are not mentioned. The zero-width-interval mechanism is the known failure of Wald-type intervals for rare events (e.g. Brown, Cai & DasGupta 2001). Operational panels relevant to the intended readers are not mentioned: EU LUCAS points revisited across campaigns, the rotating segments of USDA NASS area-frame surveys, and the sample squares of Switzerland's ALL-EMA agri-environmental biodiversity monitoring, surveyed in repeated cycles. van der Velde et al. (2024, Environ. Res. Lett., doi:10.1088/1748-9326/ad9d61; Crossref-confirmed) compute Shannon crop diversity from a 10 m EO crop map and from farmers' declarations, compare them, and track diversity change 2009–2021 from declarations. sources.jsonl records it as an unverified lead (POLICY-DIVERSITY2025-LEAD), but the paper does not cite it. Lu, Kluger, Bates & Wang (arXiv:2407.13659; current v7 title "Regression coefficient estimation from remote sensing maps", earlier versions also covered area estimation) apply prediction-powered inference to remote-sensing map products; it is not cited.
  - Inference: The novelty claim is appropriately modest, and within my search I found no study that tests fixed-budget change inference for crop-group diversity with embedding-assisted estimators ("not found in the range searched", not "does not exist"). However, readers working on the problem cannot place the results against the methods and programmes they use. The direction of the main result was predictable from this classic literature, and the paper should say so explicitly.
- Requested action: (Priority 3) Add these works with one sentence each on how the present results relate to them, in particular van der Velde et al. 2024 as the current practice of declaration/EO-based crop-diversity monitoring, and the classic successive-occasion theory as the source of the expected direction.
- Feasibility of the action: can be done within the research environment (bibliographic checks on the public web).

### R1-7
- Severity: Minor
- Type: Insufficient description
- Target: Abstract; §1; §5
- Content:
  - Observed: The abstract has about twenty numbers, including case counts (35, 4, 3, 0, 0, 20, 8) and three exploratory sub-analyses. Results are reported in "entropy units" without translation. The paper notes that exp(ΔH) is the ratio of effective numbers of groups, but does not use it.
  - Inference: Expressed as change in the effective number of crop groups, the no-change RMSE corresponds to about 2.6%, the revisited RMSE at 128 labels/year to about 5.8%, and the independent RMSE to about 11%. Practitioners can relate to this scale; to "0.0559 entropy units" they cannot.
- Requested action: (Priority 4) Restructure the abstract around 3–4 preplanned results and one sentence of exploratory qualifications, move the case counts to the results, and give the main errors also as percentage change in the effective number of groups. Define the readers' decision in one sentence near the start (see R1-8).
- Feasibility of the action: can be done within the research environment.

### R1-8
- Severity: Minor
- Type: Insufficient description
- Target: §1, §3.1, §5, §6
- Content:
  - Observed: The paper states that where complete declarations exist, the experiment does not establish a need for a sample, and that the five-year agricultural mask and source training labels lie outside the budget. It does not say which real monitoring setting the simulated n-label audit represents (e.g. regions without parcel declarations, verification of declared against realised crops, map-based monitoring with a small validation sample), or what one "label" corresponds to there (a pixel visit, a parcel, a photo-interpreted point).
  - Inference: Without this, readers cannot transfer the budget results (e.g. "128 labels/year") to their own costs, and the error-free label assumption (R1-1) is harder to assess.
- Requested action: (Priority 4) Add one paragraph naming the intended operational settings and the corresponding unit of a reference label, and state which assumptions of the benchmark (error-free repeated labels, known stable frame, pixel sampling within one finite population of ~4,000 points) differ from them.
- Feasibility of the action: can be done within the research environment.

### R1-9
- Severity: Minor
- Type: Inconsistent records
- Target: VERIFY.md ("Use tag `final` for the reviewed version"); events.jsonl
- Content:
  - Observed: VERIFY.md instructs use of tag `final`, but the submitted tag is `submission-1` and no `final` tag exists. Two lines (E0539, E0540) were appended to events.jsonl after the tagged commit. They are documented as terminal receipts and covered by the prefix-hash rule, and the inventory check matched (36,535/36,535).
  - Inference: This is harmless for this review, but a reader following VERIFY.md literally would fail at checkout.
- Requested action: (Priority 5) Correct the tag name in VERIFY.md, or state which tag to use for each submission.
- Feasibility of the action: can be done within the research environment.

## 6. Value to readers
(Summary of reader_value.md; this is my self-report, not a measurement of readers' behaviour. My prior expectation was written after I had inadvertently seen the abstract, which weakens the comparison.)
- As expected: revisiting greatly reduces the MSE of direct change estimates where declared use is persistent; the gain is smaller on arable land; annual changes are small relative to sampling error; frozen-classifier assistance adds little; delta intervals can under-cover. The direction of the main result follows from classic successive-occasion theory.
- Beyond expectation: no tested budget up to 512 labels/year beats a no-change prediction (62/90 units still favour no-change at 512); about one in five (revisited) to one in three (independent) reported directions is wrong at 128 labels/year; the preplanned model-assisted interval behaviour is an artefact of the linearisation; there is a possible but statistically unresolved reversal on stable arable land in 6 extra landscapes.
- Judgements that could change: (a) planners of reference panels may expect a large gain from revisiting in grassland-dominated landscapes (about 5×) but a much smaller one on arable land (about 1.7×), conditional on near error-free repeated labels (C01, C05, C10; reproduced, but sensitive to labelling error per R1-1); (b) analysts may stop reporting annual direction-of-change in broad crop-group diversity from a few hundred labels, or report it with explicit conditional error rates (C02, C03; reproduced exactly); (c) users of embedding products may not expect frozen-classifier assistance to improve revisited estimates (Table 1; reproduced, and robust to a post-stratified estimator in my check).
- The abstract is numerically accurate for the values I checked and ends with a scope sentence, but it omits (a)–(c) in the plain form above and is overloaded with exploratory detail.

## 7. Points that can be supported
- All numerical claims C01–C11 match their evidence files and were regenerated by the research side's entry point on a clean copy (passed; maximum numeric difference 0.0). C01, C02, C03 and the C06 zero-change fraction were also reproduced exactly by my own code.
- C01 (revisiting lowers direct MSE at all five budgets on this cohort) is supported. Its size is a grassland-dominated, error-free-label result (R1-1, R1-3).
- C02 (lower aggregate revisited coverage at n=128 under the original interval rule) and C03 (the no-change baseline beats the n=128 direct and frozen-model-assisted estimates) are supported for this benchmark.
- C05, C07, C08, C09 and C11 are supported as exploratory results with the scope already stated in claims.jsonl. C10 is supported as an observed ratio, but not as a difference distinguishable at landscape level (R1-3).
- The research process: plan v1 was committed before main acquisition; for all 108 experiment records the plan and code commits precede the start time; later analyses are labelled exploratory in protocol/deviations.md, claims.jsonl and the paper. No contradiction was found in the order (Git times are self-reported; this does not prove the absence of tampering).
- AI API use was limited to the one required topic critique (call A001). Its cost of 1.94391 USD, recomputed from the usage in the saved response, is within the 20 USD budget, and no other AI did research work according to the records.
- Data licences and attribution are documented; no individual or farm-level information is analysed.

## 8. What could not be confirmed / limitations of this review
- This re-run is a re-run by another agent on the same machine, not an independent reproduction. It used the submitted bundled numerical extracts and archived predictions; raw-data re-acquisition and classifier refitting were not performed, so upstream data provenance and the fitting step were checked only through the stored hashes and the saved-coefficient reconstruction that verify.py performs.
- The SHA-256 inventory (review/submission-1/SHA256SUMS.json) was checked against the research directory itself (36,535/36,535 entries match at start and at end), not against my copy; the Git-excluded catalogues, compressed-label range caches and self-rerun trees were not copied.
- My prior expectation is not blind: my first read of paper.md printed the first 40 lines, so I saw the abstract and §1–§3.1 before writing prior_expectation.md (recorded in that file and in events.jsonl RV0005).
- Reference checks: existence, titles and authors were confirmed from Crossref, the arXiv API and NASA NTRS for ROTATION-SAMPLE1981, MASSEY2015, LI2014, CROP-FITNESS2026, OLOFSSON2014, AUDENAERT2007, FANG-SANTOS2019, SWISSCROP25, SENEGAL2026, CLUSTER-PPI2026, TESSERA2025, AEF2025 and PPI-PLUS (arXiv API). For MASSEY2015 and CROP-FITNESS2026 the content was checked against the abstracts only. LIPTON2018, PANINSKI2003, STRAT-PPI2024, SIMPLEX-JACOBIAN2016, SCIPY-HYPERGEOM and SWISSCROP25-CARD were not individually re-checked. I did not use the runtime's page-summarising fetch tool, because it calls another model; pages were retrieved with curl from public metadata APIs and searched with the web-search tool. The classic works I recommend (Jessen 1942, Patterson 1950, Hutcheson 1970, Basharin 1959, Brown–Cai–DasGupta 2001) were identified from search results and secondary citations, not read in full.
- The novelty search covered PPI/model-assisted estimation with remote sensing and embeddings, crop-diversity monitoring with EO and declarations, Shannon-change inference with repeated samples, and operational panel surveys. "Not found" means not found within this range, not that it does not exist.
- My sensitivity analyses (labelling error, post-stratified estimator, landscape bootstrap) are my own additions with simple assumptions (e.g. the noise model replaces labels by draws from the landscape-year class distribution). They indicate which conclusions are sensitive; they are not estimates of real error rates, and they were not prespecified.
- The model identifier serving this review could not be confirmed from the execution environment (see header).
- No usage-limit stop occurred during this review; excluded stop time is 0.
- Target state, start vs end: HEAD and tag submission-1 both pointed to faf7dce40c1a27313b4ae7fb51554fa5d061393b at the start (02:26:47Z) and at the end (02:44:24Z). `git --no-optional-locks status` showed the same single modification at both times: events.jsonl, with two lines appended by the research side after the tagged commit (E0539, E0540; file mtime 2026-10-27T02:21:31Z, before this review started; 160,374 bytes at start and end). The SHA-256 inventory had 36,535 entries, all matching at start and at end (0 mismatches, 0 missing). No difference arose during the review, and none was caused by my operations.
- Processes: the processes I started (clone, venv installation, full verification, my own analysis scripts, monitors) all finished; none remains running. At most two computational processes ran at the same time. In addition, for about 1.5 minutes before the verification finished, up to three lightweight shell wait loops (sleep polling for the verification's completion file) ran alongside it; I record this as a possible over-count against the two-process limit, depending on whether such wait loops count.
- Review-directory storage at the end: about 8.1 GiB (clone 6.5 GiB, verification output 1.3 GiB, venv), within the 10 GiB limit.
