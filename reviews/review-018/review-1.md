REVIEW-1
- Review ID: review-018-1
- Target: tag submission-1 (tag object 5f7fc5286a15f189f1f45c4592dc5d6a89298f59), commit 739117262e02cdbec90900446e14776ce1f12624
- Reviewer's model: confirmed from the execution environment: Claude Code runtime 2.1.311 (AI_AGENT=claude-code_2-1-311_agent), CLAUDE_EFFORT=xhigh. The environment does not expose the serving model ID, so it could not be confirmed. / Name given in the conversation: Opus 5.5 (claude-opus-5-5), reasoning effort xhigh, as specified by the human.
- Review period: start 2026-10-28T08:28:17Z (17:28:17 JST), end 2026-10-28T09:41:39Z; excluded usage-limit stop time: 0 s (no stop occurred)
- Scope of verification carried out: on a clone of the tag, I ran the VERIFY.md single entry point in both modes, `--refit primary` and `--refit polygonC`. Both passed 101/101 checks, regenerated the whole manuscript and claims.jsonl byte-identically, and refitted their models with identical predictions. I refitted six archived control or exploratory conditions with the submitted code: constant column at seed 0, permutation 2, seed 1000, boosted trees on corrected inputs, whitened boosted trees, and 2021 embeddings. All were identical to the archive. I independently recomputed the primary results from saved predictions and checked the timeline for all 142 experiment records. I checked the existence of 8 of 17 references, ran a bounded novelty search and checked the AI API records. The remaining supplementary conditions were checked only in reduced form (recomputed from archived predictions, not refitted).

## 1. Summary of the paper
The paper asks whether adding annual satellite-embedding distance (AlphaEarth Foundations 2024 or TESSERA v1.1) to a random-forest pair model built on 30 public terrain, surface-water (JRC) and HAND covariates improves the screening of wetland "reference" candidates. Improvement is measured as fewer mismatches in the published NWI water-regime class (temporarily, seasonally or semipermanently flooded) among the half of queries the model is most confident about. The test uses 3,667 wetlands in three vegetation subclasses in 12 convenience windows (16 km × 16 km) in the United States, with spatially blocked query/reference/training roles. In the prespecified comparison, both augmentations lower window-mean mismatch by about 3 points against the hydrological pair model (AlphaEarth −2.95 pp, 95 % window-bootstrap −6.81 to −0.01; TESSERA −3.72 pp, −8.23 to +0.08), meeting the descriptive 2-point benchmark against both baselines. The paper then reports many further controls and exploratory analyses: forest seeds, a constant column, random scalars, boosted trees, polygon sampling, whitened distances, other-window training, alternate embedding years and budget allocation. From these it concludes that an increment attributable to the satellite measurement is not established by the primary comparison alone, while some configurations favour the embeddings. The endpoint is inventory-label agreement, not field hydroperiod or practitioner benefit.

## 2. Overall verdict
Major revision.
The computations are reproducible. A re-run on a clean clone regenerated the whole manuscript and claims file byte-identically and refitted the primary and polygon-C models with identical predictions; six archived control or exploratory refits also matched exactly (see §4). The research process is unusually well recorded: all 142 experiment records cite plan and code commits that predate the run. The main problem is how the result is interpreted and presented. On the primary (window-mean) metric, the headline increment is the same size as the changes produced by planned null perturbations (permuted embeddings, other forest seeds) and by a constant column. Under the plan's own rule (plan-v6), the incremental claim should therefore be qualified. In addition, more than half of the AlphaEarth gain comes from one query in a window with 5 retained queries. The abstract gives the prespecified estimates and eight exploratory or post-hoc results, but no answer to the research question. The planned permutation control appears only in the appendix. These problems can be fixed within the response period by re-analysing the archived outputs and rewriting.

## 3. Scores (1–5, one line of reason each)
- Correctness of claims: 3 — every number checked matches the outputs and the scope statements are careful, but the primary contrast is presented as if it were evidence of an increment even though, under the planned decision rule, it is indistinguishable from the null perturbations (R1-1, R1-2).
- Verifiability: 5 — a single offline entry point regenerates every table, figure, the full manuscript text and claims.jsonl from bundled raw inputs, and the refits I ran reproduced the archived predictions exactly. Inputs, plans, failures and timelines are linked by commit and hash. The minor bytecode-cache issue (R1-10) affects only the optional refit procedure.
- Novelty: 3 — within the range I searched, I found no controlled evaluation of embedding distance for wetland reference screening against an NWI water-regime endpoint. However, embedding similarity for hydrological donors (Qu et al. 2026) and AlphaEarth-based mapping of wetland inundation regimes (an uncited 2026 conference abstract, R1-6) already exist, and the paper itself states a narrow contribution.
- Generality: 2 — 12 convenience windows, two of which retain fewer than 20 queries; one inventory-label endpoint; and the conclusions change with seed, learner, aggregation (window-mean vs pooled) and embedding year.
- Usefulness to readers: 3 — the evaluation design (null-feature, permutation, fixed-query decomposition) and the warning against before/after comparisons with stochastic learners are useful to method developers. Practitioners' judgment would hardly change (field hydrology remains necessary, as the paper says), and the take-home answer is currently hard to extract.
- Clarity: 2 — the background section is written for wetland practitioners and is good, but the abstract has 332 words, about 35 numerical values and 7 "exploratory" mentions, and gives no answer. Many internal terms are left undefined for the target readers ("pair model", "category model", "nontrivial matchable pool", "physical comparator", "measurement operator", "pp", "window-bootstrap").

## 4. Verification results
"Re-run" means a re-run by another agent (this reviewer) on the same machine, on a fresh `git clone --no-hardlinks` of tag submission-1 in the review directory with a dedicated venv (`requirements-lock.txt`, Python 3.13.7, GDAL 3.12.2 / PROJ 9.8.1 / GEOS 3.14.1, the same versions as recorded). It is not an independent reproduction.

Legend:
- **P** = `code/reproduce.py --refit primary` (VERIFY.md single entry point) on the clone. It regenerated raw-derived features, polygon samples and features, all saved-decision summaries, tables, figures, the manuscript and claims.jsonl, and refitted all 18 primary methods at all four rotations. Result: `passed: true`, 101/101 checks, 1,210.7 s, no network, no API calls. The regenerated paper.md and claims.jsonl are byte-identical to the submitted ones, and the source copy was unchanged.
- **R** = the reduced part of P. Values are recomputed from the archived supplementary predictions and compared with expected values at 1e-12; those models are **not refitted** by P.
- **O** = my own recomputation with separate code.
- **X** = my refit of an archived control with the submitted code, outside the source copy.

| claim_id | Claim (shortened) | Procedure run | Result | Record path |
| --- | --- | --- | --- | --- |
| C01 | Both single distances meet 2-pp benchmark vs both comparators (seed-0 forest); each has an interval crossing zero vs ≥1 comparator | P (full refit) + O | match (risks, contrasts, intervals; refit predictions identical) | verification/run-primary/results/verification-report.json; verification/recompute/primary_recompute.json |
| C02 | Pool accounting 30 / 204 / 59 (26) / 3,374 | P + check of summary.json | match | verification/run-primary/results/analysis/primary-corrected-summary/summary.json |
| C03 | Zero column changes forest choices/confidence/screens with 0 splits; boosted trees unchanged | R (constant audits, including the zero-split counts) + X (constant-corrected-seed-0 refit, 4 rotations, 3.3 min) | match: the refit predictions equal the archived ones (reference and mismatch exactly, confidence within 1e-12); contrast −3.38 pp identical. The split counts were checked only by R | verification/run-extra/constant-compare.json |
| C04 | Raw-distance gains not consistent across seeds, boosted trees, recent panel | R + X (refits of seed-1000, of the boosted-tree learner on corrected inputs, and of permute-2, a planned control bearing on the same question) | match. All three refits are identical to the archive (seed-1000: pair 32.57 %, AlphaEarth 31.84 %, TESSERA 33.94 % window-mean; boosted trees 40.61 / 38.96 / 37.72 %; permute-2: −3.81 / −4.53 pp). The seed-2000 and recent-panel fits were checked only in reduced form | verification/run-extra/seed1000-compare.json; hgb-compare.json; permute-compare.json |
| C05 | Own-screen gain = ranking + selection components | P (from refitted primary) | match | verification/run-primary/results/analysis/report-data/screen-decomposition.csv |
| C06 | Scalar controls comparable at 0.7; small at all-feature | R | match (reduced: not refitted) | verification/run-primary/results/verification-report.json |
| C07 | Polygon cohort 3,624 (43 exclusions); shared raw pixels agree after repair | P (polygon pixel selection R01–R12 and conditions A–D regenerated from raw) | match | same |
| C08 | Averaged physical maps change which physical comparator is lower | R + `--refit polygonC` (features regenerated from raw; all 18 methods refitted at 4 rotations) | match: `passed: true`, 101/101, 1,232.5 s. My first polygonC run failed only at its final source-immutability check, because of my own concurrent refit (R1-10); the re-run, done alone, passed | verification/run-polygonC-2/results/verification-report.json; verification/run-polygonC/stderr.txt |
| C09 | Whitened boosted-tree augmentations ≥2 pp vs both comparators | R (+ 32 whitening vectors via separate SVD) + X (whitened boosted-tree refit, original panel) | match: the refit is identical to the archive (34.18 / 33.98 vs 40.61 / 36.63 %). The polygon-C whitened conditions were checked only in reduced form | verification/run-extra/c09-compare.json |
| C10 | Shared-query nontrivial and omission diagnostics; AlphaEarth benchmark changes in 1 omission | R + O (leave-R07-out −1.40 pp) | match | verification/recompute/pooled_bootstrap.txt |
| C11 | Budget-allocation policy changes which 2-pp contrasts are met | R | match (reduced: not refitted) | verification/run-primary/results/verification-report.json |
| C12 | 2021 AlphaEarth augmentation lower than 2024; physical decisions unchanged | R (annual features regenerated from raw; physical invariance audit) + X (2021 refit, all 18 methods × 4 rotations) | match: the 2021 refit is identical to the archive (AlphaEarth 30.96 %, pair 36.98 %). The 2023 fits were checked only in reduced form | verification/run-extra/c12-compare.json |
| C13 | Other-window boosted trees: raw TESSERA ≥2 pp vs both, intervals cross zero | R (strong-transfer invariants) | match (reduced: not refitted) | same |

## 5. Findings

### R1-1
- Severity: Critical
- Type: Insufficient evidence
- Target: paper.md Abstract, §4.1, §4.5, §5 Discussion, Appendix (rows "Within-window/vegetation/role embedding shuffle"); claims C01, C04, C06; protocol/plan-v6-robustness.md
- Content:
  - Observed (archived summaries, collected in `verification/recompute/perturbation_table.txt` and `synthesis_null_vs_real.txt` in the review directory): at the primary forest setting (max_features 0.7), the real augmentations change half-coverage window-mean mismatch against the same-seed hydrological pair model as follows. AlphaEarth: −2.95 (seed offset 0, primary), −0.73 (1000) and −1.42 (2000) pp; mean −1.70. TESSERA: −3.72, +1.37 and −2.87 pp; mean −1.74. The pair baseline itself is 36.98 / 32.57 / 37.42 % across these three seeds.
  - Observed: in the same setting, 12 null perturbations give −3.38, +3.92 and −2.50 pp (constant column, three seeds), −4.56, −1.24 and −1.02 pp (independent scalar), −0.29, −2.76 and −3.81 pp (permuted AlphaEarth vectors) and −1.55, −1.78 and −4.53 pp (permuted TESSERA vectors). Their range is −4.56 to +3.92 pp and their mean −1.96 pp. The six planned permutation controls alone range from −4.53 to −0.29 pp (mean −2.45 pp), which brackets the primary −2.95 and −3.72 pp.
  - Observed: the seed and permutation controls and the boosted-tree learner were fixed in plan-v6 (commit 322f723, 2026-10-27T17:04:05Z), before the first aggregate inspection (events.jsonl E0175, 17:18:57Z). Plan-v6 states: "Main incremental claims should be qualified if they disappear under the second learner or are comparable to the null-feature perturbations." The permutation results, and the seed-1000/2000 results for the primary 0.7 forest, appear only as Appendix rows (paper.md lines 468–472). Neither is given in §4.5, Figure 4 or the Discussion, and the abstract mentions the seeds only in general words.
  - Inference: by the study's own prespecified rule, the primary window-mean contrast does not support an increment attributable to the embeddings. The abstract leads with the seed-0 estimates and an interval that excludes zero (−6.81 to −0.01), and it calls the planned controls "exploratory". It does not tell readers that the planned null controls produce changes of the same size. The Discussion's sentence "an increment attributable to the satellite measurement is not established" is correct but does not reach the abstract or the claims records. The window-bootstrap intervals do not include this model-randomness variance.
- Requested action (priority 1):
  1. In the abstract and at the start of §4.1, state the answer plainly. One possible wording: "On the prespecified metric, the increment was not distinguishable from planned null perturbations (permuted embeddings, other forest seeds) and is therefore not established."
  2. Add the permutation results and the 0.7-forest seed results to §4.5 and Figure 4, next to the constant-column results, or overlay the null range on Figure 2.
  3. Report the three-seed mean, as well as seed 0, for each primary contrast.
  4. Relabel the seed, permutation and boosted-tree controls as planned secondary analyses (they were fixed before outcome inspection), and keep "exploratory" for the later additions.
- Feasibility of the action: can be done within the research environment (archived outputs only).

### R1-2
- Severity: Moderate
- Type: Insufficient description
- Target: paper.md Abstract, §4.1, §4.2, §4.3, §4.6, §4.9; claims C01, C08, C10, C13
- Content:
  - Observed (own recomputation from `analysis/main-corrected/r*/predictions.csv`, `verification/recompute/per_window_diffs.txt`): retained queries per window at half coverage are R07 = 5 and R08 = 14, i.e. 19 of 1,804, or 1.1 %. For AlphaEarth minus the pair model, R07 is −20.00 pp, which is one query changing from mismatch to match. Under equal window weights this contributes −1.67 of the −2.95 pp headline; R07 and R08 together contribute −2.27 pp (77 %). For TESSERA, R08 (−21.43 pp) contributes −1.79 of −3.72 pp.
  - Observed: on the planned pooled scale, the differences against the pair model are −0.67 pp for AlphaEarth (my window-bootstrap of pooled counts: −2.47 to +1.20) and −2.44 pp for TESSERA (−5.03 to −0.32), `verification/recompute/pooled_bootstrap.txt`. Without R07, the AlphaEarth window-mean difference is −1.40 pp; without R07 and R08 it is −0.82 pp.
  - Observed: window-mean and pooled disagree in several places. Geographic nearest reference vs hydrological pair: 35.73 vs 36.98 % window-mean, but 39.58 vs 34.15 % pooled. Other-window forest, AlphaEarth vs pair: 39.69 vs 40.64 % window-mean, but 42.96 vs 40.41 % pooled. Other-window boosted trees, TESSERA vs category model: 34.39 vs 38.83 % window-mean, but 37.86 vs 36.92 % pooled. Polygon condition C (dispersed embeddings with averaged physical covariates), from `analysis/polygon/C-*-summary` via supplementary-half-coverage.csv: §4.6 concludes that "neither [raw distance] beat both corresponding physical comparators", and this holds on window-mean. On the pooled scale, however, TESSERA beats both: forest 29.28 % vs 33.03 % (pair) and 30.01 % (category); boosted trees 31.24 % vs 34.32 % and 35.78 %.
  - Observed: in the recent-image panel, AlphaEarth pooled mismatch equals the pair model's exactly (37.52 %).
  - Observed: the paper does mention the 18-query window and reports single-window omissions (−3.64 to −1.40 pp). It does not say that one query in one window supplies more than half of the AlphaEarth headline, and the abstract reports only window-mean values.
  - Inference: the equal-window mean was prespecified and is legitimate, but on this panel it is a high-variance estimator dominated by two tiny windows. Readers need the pooled values to judge the size of the effect.
- Requested action (priority 2): report pooled differences next to the window-mean ones in the abstract and in §4.1, and for every contrast quoted in the abstract. State the R07/R08 contributions explicitly. In §4.1, note that on the primary metric the hydrological pair model does not beat the geographic nearest reference. Wherever a conclusion holds on only one scale (geographic vs hydrological, other-window training, polygon condition C), give both values and qualify the statement.
- Feasibility of the action: can be done within the research environment.

### R1-3
- Severity: Moderate
- Type: Overclaim
- Target: paper.md Abstract ("An everywhere-zero input changed corrected-input mismatch by −3.38 pp, showing pipeline sensitivity to an uninformative feature"), §4.5, §5; claim C03
- Content:
  - Observed: the primary forest samples 70 % of the features at each split with a fixed random_state (plan-v1, item 3; scikit-learn RandomForestClassifier).
  - Observed: consistent with this, the boosted-tree learner, which does no feature subsampling, is exactly unchanged (0 changed references). The all-feature forest changes little (121 references; +0.92 pp). The 0.7 forest changes as much as a re-seed does: the pair baseline spans 32.57–37.42 % across seeds.
  - Inference: with the same random_state, appending any column changes the random feature draws at each split. With 70 % subsampling this gives a forest roughly as different as a re-seeded one; with all features, the random feature order still changes, which explains the smaller effect. The constant-column result is therefore a predictable consequence of the learner's randomization, not a separate finding about the pipeline. The substantive finding is that seed-level Monte Carlo variability of the window-mean endpoint, a range of about 4.9 pp, is as large as the effect being tested.
- Requested action (priority 3):
  1. Reframe C03 and the abstract sentence as model-randomness variability, and quantify it from the available seeds (for example, the spread of the baseline and of each contrast).
  2. Optional, if time allows: refit hydro_pair, pair_aef, pair_tessera and hydro_decoder at five or more further seed offsets and report seed-averaged contrasts. The control-seed-1000 record took about 10 minutes for this set of methods; with two processes in parallel, five seeds take about 25 minutes. Alternatively, average predictions over seeds.
- Feasibility of the action: can be done within the research environment (the re-analysis certainly; the refits within the 2-hour period at lower priority).

### R1-4
- Severity: Moderate
- Type: Insufficient description
- Target: paper.md §4.3 (decoder table), §4.5, §5 Discussion; claims C04, C06, C09
- Content:
  - Observed (`analysis/report-data/decoder-information.csv`): query log loss is 0.780 for the hydrological decoder, 0.729 for AlphaEarth only, 0.723 for hydrology + AlphaEarth, 0.741 for TESSERA only and 0.731 for hydrology + TESSERA. Balanced accuracy is 0.502 for the hydrological decoder and 0.539–0.543 for the others. No uncertainty is reported.
  - Observed (my exploratory window-level paired re-analysis of the saved probabilities, `verification/recompute/decoder_logloss.txt`): log-loss change against the hydrological decoder is −0.047 nats for hydrology + AlphaEarth (95 % window-bootstrap −0.073 to −0.019; better in 9 of 12 windows), −0.038 for hydrology + TESSERA (−0.075 to −0.003; 8 of 12) and −0.052 for AlphaEarth only (−0.083 to −0.016; 11 of 12).
  - Observed (archived, exploratory all-feature forest): on the pooled scale, TESSERA augmentation lowered mismatch by 2.22, 2.16 and 3.55 pp across three seeds and AlphaEarth by 0.83–1.11 pp, while the null features changed it by −0.28 to 0.00 pp.
  - Inference: there are signs that the embeddings carry NWI-regime information that the 30 covariates lack, but the top-1 match, 50 %-screen endpoint on 12 unequal windows is too noisy to turn this into a stable gain in screening. The current Discussion moves between "pipeline sensitivity" and a list of favourable cases, so readers cannot tell which of these is supported.
- Requested action (priority 2):
  1. Add window-level paired uncertainty for the decoder log-loss and balanced-accuracy differences, labelled exploratory.
  2. Add one compact table of real vs null changes, on both the window-mean and pooled scales, by learner setting and seed.
  3. Rewrite the first two Discussion paragraphs to separate (a) whether the embeddings carry regime information beyond the covariates from (b) whether an improvement in screening is established.
- Feasibility of the action: can be done within the research environment (saved outputs only).

### R1-5
- Severity: Moderate
- Type: Insufficient description
- Target: paper.md Abstract, §5, terminology throughout
- Content:
  - Observed: the abstract has 332 words and about 35 numerical values, and quotes eight separate exploratory or post-hoc results: the seed/learner/recent-panel controls, the constant column, polygon sampling, whitened distances, the all-feature forest, the 2021 embeddings, other-window training and the nontrivial-pool fixed screen. No sentence answers the research question.
  - Observed: "exploratory 2021 AlphaEarth distance augmentation yielded 30.96%, further limiting generalization across embedding years" describes a result that is better than 2024. The phrase cannot be interpreted without further explanation, and the 2024 vs 2021 difference (3.1 pp) lies within the seed-level range (R1-1).
  - Observed: terms such as "pair model", "category model", "nontrivial matchable", "pool", "physical comparator", "measurement operator", "pp" and "window-bootstrap" are not defined in words that wetland practitioners would use.
- Requested action (priority 1):
  1. Restructure the abstract as: problem and why it matters (1–2 sentences); design; the answer; primary values (window-mean and pooled); what the planned controls show; at most one or two exploratory observations, labelled as such; scope.
  2. Move the remaining exploratory results to Results.
  3. Define the core terms at first use and add a short plain-language summary for practitioners.
  4. Remove or explain the "further limiting generalization" sentence.
- Feasibility of the action: can be done within the research environment.

### R1-6
- Severity: Moderate
- Type: Insufficient description
- Target: paper.md §2 Prior work, §6 Limitations
- Content:
  - Observed (my bounded search, `verification/refs/reference_checks.md`): the following close work is not cited.
    - Abrahamson, J. & Stegen, J. (2026), "Mapping Wetland Inundation Regimes using Google's AlphaEarth Embeddings: A Case Study in the Florida Everglades", Society for Freshwater Science 2026 Annual Meeting, poster #222. It trains a random forest on AlphaEarth embeddings to map annual inundation regimes (seasonal, permanent, ephemeral) for 2018–2021, uses ground truth from the gauge-based Everglades Depth Estimation Network, and compares against Sentinel-2 NDWI composites. This is a conference abstract.
    - arXiv:2602.10354 (2026). AlphaEarth embeddings reconstruct 26 environmental variables over the conterminous US, including terrain and hydrology, with R² above 0.90 for 12 of them. This bears directly on how far embeddings duplicate the physical baseline.
    - The remote-sensing literature on mapping wetland surface-water regimes and hydroperiod in support of NWI updates: DeVries et al. 2017 (Landsat sub-pixel water fraction, Remote Sensing); the SWaRe multi-source Surface Water Regimes product (AGU 2018 abstract); and Lang et al. 2008 (SAR hydroperiod compared with NWI). I found these only in search listings and did not read them in full.
  - Observed: the paper's novelty statement is already limited ("No novelty claim follows from this bounded search"), so this finding does not overturn a claim. It does change what readers can learn about where this study sits: embedding-based mapping of inundation regimes against gauge truth already exists, and SAR-based inundation frequency is the standard physical predictor for water under vegetation. The paper's physical baseline lacks it (JRC is optical, as §2 notes).
- Requested action (priority 3): cite and position these works. In Limitations, state that the physical comparator contains no SAR-derived inundation information, so "beyond public hydrological covariates" refers to this specific optical/terrain set.
- Feasibility of the action: the citations and the limitation can be added within the research environment. Adding a SAR-based baseline is not feasible within 2 hours (new acquisition), so narrow the claim instead.

### R1-7
- Severity: Minor
- Type: Inconsistent records
- Target: paper.md Abstract ("Exploratory controls ..."), claims.jsonl C04 (`exploratory: true`), VERIFY.md (timeline paragraph)
- Content:
  - Observed: the seed, permutation and boosted-tree controls were fixed before outcome inspection (see R1-1), and §3.5 says so, but the abstract and C04 label them exploratory. C04 also mixes in the recent panel, which is exploratory.
  - Observed: VERIFY.md gives the first author inspection of matching-loss results as 2026-10-27T17:16:36Z, whereas events.jsonl E0175 (primary_results_observed) has 17:18:57Z. The primary-summary run ended at 17:16:34Z. Both times come after the plan-v6 commit (17:04:05Z), so the ordering conclusion is unaffected.
- Requested action: unify the labels (split C04 into a planned part and an exploratory part) and correct or explain the time.
- Feasibility of the action: can be done within the research environment.

### R1-8
- Severity: Minor
- Type: Insufficient description
- Target: protocol/plan-v1.md line 80 (planned boundary conditions); paper.md §4.8; analysis/primary-corrected-summary/subgroups.csv
- Content:
  - Observed: plan-v1 lists the following among planned boundary conditions: small (≤1 ha) vs larger polygons, vegetation subclass, and image-date groups. The paper does not report them.
  - Observed: descriptive values exist in subgroups.csv. For example, half-coverage pooled mismatch of the hydrological pair model is 29.5 % for ≤2014 source images (1,378 retained), 48.4 % for 2015–2019 (376) and 56.0 % for ≥2020 (50). For hydrology + AlphaEarth the figures are 28.5 / 49.6 / 52.1 %.
  - Inference: the image-date pattern bears on the inventory-age explanation the paper discusses, although it is confounded with window.
- Requested action: report these planned subgroup results with their denominators and the window confounding, or state that they were not analysed and why.
- Feasibility of the action: can be done within the research environment.

### R1-9
- Severity: Minor
- Type: Suggestion
- Target: paper.md §1 Introduction (last paragraph), §5
- Content:
  - Observed: the paper states correctly that where NWI regimes are known, filtering on them is enough, so the label-masked workflow has no demonstrated operational advantage.
  - Inference: readers working on the problem need a concrete setting in which the question matters, for example areas without current inventory regimes or projects that check outdated mapping. They also need to be told that transfer to such settings was not tested (other-window training gave no stable gain, §4.9).
- Requested action: add two or three sentences naming such settings and the corresponding limit on the evidence.
- Feasibility of the action: can be done within the research environment.

### R1-10
- Severity: Minor
- Type: Unverifiable
- Target: VERIFY.md ("Optional supplementary model refits"); code/run_rotation_batch.py
- Content:
  - Observed: I ran two optional refits with the copy's own code, as VERIFY.md describes (inputs from the copy, outputs outside it). `run_rotation_batch.py` starts `analyse_controls.py` as a child process without `-B`, and VERIFY.md does not say to set `PYTHONDONTWRITEBYTECODE`.
  - Observed: as a result, Python wrote `code/__pycache__/analyse_matching.cpython-313.pyc` and `records.cpython-313.pyc` into the source copy (08:53:19Z). My concurrent `--refit polygonC` run then failed its final "source copy unchanged" assertion (`verification/run-polygonC/stderr.txt`).
  - Inference: the main entry point protects the copy (it sets `PYTHONDONTWRITEBYTECODE`), but the documented optional refit procedure does not. I attribute this run failure to my own operation; the research directory was never written to.
- Requested action: add `-B` to the child commands in `run_rotation_batch.py`, or tell users in VERIFY.md to export `PYTHONDONTWRITEBYTECODE=1` for the optional refits.
- Feasibility of the action: can be done within the research environment.

## 6. Value to readers
(Summary of reader_value.md. This is my self-report, not a measurement of how readers actually change their behaviour.)
- As I expected: a small point reduction of about 3 pp, wide intervals, heterogeneity across windows, a high error floor (all methods 31–42 % mismatch; a uniformly random reference gives 45 %), and no stable gain under geographic transfer.
- Not as I expected:
  - The planned null perturbations (permuted embeddings, other seeds) produce changes of the same size as the real embeddings (R1-1).
  - One query in a 5-query window supplies more than half of the AlphaEarth headline (R1-2).
  - In the recent-image panel, where label dates are closest to the embedding year, the AlphaEarth gain disappears.
  - The probabilistic decoder diagnostic shows clearer signs of regime information than the matching endpoint does (R1-4).
- Judgment that could change:
  - Method developers (C03–C06, C10): a before/after comparison of a stochastic learner with an added embedding feature needs seed, permutation and fixed-query controls. I trust these numbers highly because they were reproduced, but the underlying mechanism is predictable.
  - Wetland-reference researchers (C01, C02, C05): on this panel, raw embedding distance does not give a robust improvement in matching NWI water regimes beyond these covariates. I give this moderate trust, given the convenience panel, the tiny windows and the label endpoint.
  - Practitioners: little change, because field hydrology and HGM reasoning remain necessary, as the paper says.
  - The exploratory favourable cases (C09, C12, C13) should not change judgment.
- The abstract's numbers are accurate, but the abstract does not answer the question and does not apply the planned qualification. Its scope statements do not overgeneralize: there are no national, field or user-benefit claims.

## 7. Points that can be supported
- Reproducibility (C01, C02, C05, C07, C08 and the reduced checks of all claims): both VERIFY.md modes passed with no network or API use, the regenerated paper.md and claims.jsonl are byte-identical to the submitted ones, and the refits of the primary models, the polygon-C models and six control or exploratory conditions (constant column, permutation 2, seed 1000, boosted trees, whitened boosted trees, 2021 embeddings) reproduced the archived predictions exactly.
- My own independent recomputation of the half-coverage primary results from the saved predictions (pure csv logic, not the authors' summarizer) matches all 18 window-mean values in the §4.1 table, all pooled values, and the four primary contrasts with their bootstrap intervals (`verification/recompute/primary_recompute.json`).
- Sampled abstract and Results numbers match the archived outputs: the pool counts (30 / 204 / 59 / 26 / 3,374), the fixed-screen nontrivial-pool value of −0.62 pp (1,644 queries, 11 windows), the whitened boosted-tree values 34.18 / 33.98 vs 40.61 / 36.63, the all-feature forest value of 32.78, the 2021 value of 30.96 and the other-window values 34.39 vs 41.01 / 38.83. All 60 evidence_paths in claims.jsonl exist.
- Timeline: for all 142 `experiments/*/record.json`, the plan and code commits exist, are committed before the recorded start time, and the plan is an ancestor of the code commit. All 140 plan SHA-256 values that are given match the plan file at the plan commit (the two pilot records have no hash). The primary protocol (plan-v1, commit 1a0e119) precedes acquisition, and the seed, permutation and boosted-tree plan (plan-v6) precedes the first aggregate inspection. Failed runs (8 non-zero exits) are retained. I found no contradiction with the recorded order. Git times are self-reported, so this does not prove the order.
- The paper states the endpoint honestly. It is inventory-category agreement, with no claims about field hydroperiod, function, restoration outcome or user benefit, and the convenience nature of the panel is stated.
- The fixed-query decomposition (C05) is a useful and correct diagnostic. It shows that most of the AlphaEarth own-screen gain (−2.42 of −2.95 pp) comes from which queries are retained rather than from better references (−0.52 pp on the fixed hydrological screen).
- AI API use follows §2.3. There was one topic-candidate critique (gpt-6-astra, 1 call, USD 1.99 of the USD 20 budget, with a prior plan and price sources), and its request and response are saved. It was not used for code, analysis or writing. A scan for key-like strings found only the ordinary word "task-appropriate" in a saved source; no key value was found.
- Public data only, no individuals, data terms documented (including the TESSERA licence ambiguity). No §12 safety concern was identified.

## 8. What could not be confirmed / limitations of this review
- All my re-runs were done by another agent on the same machine, using the authors' code and archived inputs; they are not an independent reproduction. Network acquisition (NWI, AlphaEarth, TESSERA, JRC, 3DEP, HAND) was not repeated, so the archived raw inputs were taken as given. Their hashes match the submitted SHA-256 list.
- Not refitted by me: seed-2000, permutations 0 and 1, the independent-scalar and all-feature-forest controls, the boundary conditions, the recent panel, transfer and stronger-transfer, polygon conditions A, B and D, the polygon-C whitened conditions, the 2023 embeddings and the budget policies. For these, the reduced mode only checks that the archived predictions reproduce the reported tables and claims; whether a refit gives the same predictions was not tested. The zero-split counts for the constant column come from the authors' audit, which the reduced mode checks; I did not recount splits.
- My own analyses — the pooled-scale synthesis of real vs null contrasts, the R07/R08 contributions and the window-level decoder log-loss bootstrap — are post hoc and descriptive. They use archived predictions without refitting and should be read as prompts for the authors' re-analysis, not as results of this review.
- References: 8 of 17 were checked for existence (Crossref, arXiv pages, search index). Their content was checked only through abstracts or search summaries. The Sharma et al. preprint page could not be loaded with curl, so its content was not checked. The novelty search consisted of a few web searches; absence of other close work means "not found within the range searched".
- Timeline: Git and record times are self-reported. The checks show no contradiction with the recorded order; they do not prove the absence of tampering. The human-confirmed usage-limit stops on the research side (4 effective records I0001/I0004/I0005/I0006 — I0002 was invalidated by I0003 — totalling 22,875 s of excluded time; submission at 08:24:46Z before the extended deadline of 08:44:45Z) could be checked only against interventions.jsonl and manifest.json, not against runtime logs.
- The topic critique (gpt-6-astra) was evaluated only from its saved request and response; no API was called. The research side's session history was not viewed.
- Target state: at the start of the review, the working tree of run-018 already differed from the tag in events.jsonl (2 appended lines, E0789/E0790, the post-commit submission receipt declared in review/submission-1/preparation.json). At the end of the review (09:41:15Z), the state was identical to the start: HEAD and the tag still point to 739117262e02; `git status` still shows only events.jsonl modified, with the same SHA-256 as at the start; the SHA-256 list gives 23,865 matches, 1 mismatch (events.jsonl), 0 missing and 0 unlisted files. My operations caused no difference. Writes made by my runs went only to the review directory. The one unintended write, a bytecode cache in my own clone (R1-10), was removed before the polygon-C re-run.
- Reviewer's tooling: WebSearch was used for discovery; pages were read with curl rather than WebFetch, so that page content would not be summarized by another model. GNU timeout is not installed, so a perl `alarm` wrapper (verification/tlimit.sh) enforced the per-run limits.
