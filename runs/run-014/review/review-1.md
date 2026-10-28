REVIEW-1
- Review ID: review-014-1
- Target: tag submission-1 (annotated tag object 17f82ae9dfae7f8b0e65142444682d236e790a32), commit e459b6c0ba39032e1a8069ccc882717d2fac2d71 of /Users/fujimura/Research/ai-free-research-en/run-014
- Reviewer's model: identifier confirmed from the execution environment: no environment variable names the model. The runtime's system prompt states model ID `claude-opus-5-5`, the environment has `CLAUDE_EFFORT=xhigh`, and the Claude Code CLI executable path is `.../claude/versions/2.1.310`. Name given in the conversation: Opus 5.5, reasoning effort xhigh.
- Review period: start 2026-10-25T19:21:35Z (2026-10-26T04:21:35+09:00 JST); end 2026-10-25T19:49:38Z; excluded usage-limit stop time: 0 s (no stop occurred)
- Scope of verification carried out:
  - Ran the full VERIFY.md entry point (`scripts/reproduce.py`, not reduced) once, on a `git clone --no-hardlinks` copy of submission-1 inside the review directory, in a dedicated venv built from requirements-analysis.txt. It returned PASS: 245 checks, 36 stages, 963 s wall time, no network, no AI calls, and no writes to the source copy.
  - Ran `audit_saved.py` (PASS) and `hash_outputs.py --check` (PASS, 8891 hashes).
  - Compared every `expected` record in claims.jsonl with the regenerated outputs using a reviewer-written matcher; all matched.
  - Independently recomputed (reviewer-written code) the operating points, AUROC and paired contrasts of paper Tables 1–3 from the saved predictions (36/36 rows match). Recomputed cosine-change scores from raw embedding arrays for 120 sampled targets (match to ≤5.6e-16).
  - Ran reviewer-written exploratory diagnostics on saved data: similarity of corrected vs uncorrected scores, results by year pair and region, and reference-centroid drift.
  - Checked the timeline of all 108 experiment records against Git, the existence of all 82 evidence paths, and the existence of all 19 references (18 via Crossref/DataCite/arXiv/HTTP/search; one only through the research side's saved copy). Checked the content of the passages from Heiman (2026), Brown et al. (2025) and Ball et al. (2026) that the paper relies on, plus a novelty search.
  - Did not do: live re-acquisition of embeddings, any AI API call, a re-run of the topic critique, or a full-text check of every cited paper.

## 1. Summary of the paper
The paper asks whether two corrections improve the screening of tree-cover gain and loss with public annual satellite embeddings (AlphaEarth Foundations V1, read from an unofficial geographic mosaic, and TESSERA v1): (a) recomputing the reference-forest vector every year ("concurrent reference"), and (b) subtracting the mean change of separate stable-tree control plots. Alert thresholds are calibrated on earlier years outside each held-out US region. The comparisons are against a fixed start-year reference and against supervised classifiers. On 446 LCMAP test pairs (24 gain and 124 loss positives), the eight planned correction contrasts in Youden's J range from −0.037 to +0.011 with mixed signs. A direct supervised classifier has higher J in all four product/task conditions, and the unsigned cosine change magnitude flags 0/24 gains. A pre-planned separate Annual NLCD Forest test gives similar patterns. Many exploratory checks follow. Among them, initial-date-only learners retain gain discrimination, and every correction contrast changes sign across ten fixed fitting/calibration partitions (the original plus nine perturbations). The paper concludes that the corrections are not evidence of improved screening, and that endpoints, input periods and transferred thresholds need validation.

## 2. Overall verdict
Major revision.

Every number I checked reproduces exactly, the process records are unusually complete, and the claims are carefully hedged. The problems are in interpretation and presentation, not computation:
- The main answer ("no consistent benefit") is largely predictable from the design. The corrected scores are almost the same ranking as the uncorrected one, and the paper never quantifies how much year-to-year drift there was to correct.
- The gain results rest on essentially one year pair.
- A documented AlphaEarth training detail that bears on several claims is not mentioned.
- The abstract is so dense with paired counts and internal terms that the results most useful to practitioners are hidden. These are: the near-chance reference score for AlphaEarth gains, and the inverted ranking of gains by cosine change magnitude.

All requested actions can be done in the 2-hour window with text changes and analyses of saved data.

## 3. Scores (1–5, one line of reason each)
- Correctness of claims: 4. All numbers in the abstract and tables, and all claims.jsonl expected values, reproduce. Some interpretations omit documented alternative explanations (R1-1, R1-3) and the year-pair concentration (R1-2).
- Verifiability: 5. A single offline entry point re-ran to PASS on another copy. Plan and code commits precede every run record, and no contradiction was found between Git and the experiment records.
- Novelty: 3. I did not find this exact comparison within my search. But the main null result is largely predictable, the loss-easier-than-gain pattern is known for operational change products, and the newest-looking result (gains change *less* than unchanged non-tree plots) is not developed.
- Generality: 2. The study covers CONUS only, adjacent-year intervals only, 24 gain positives (21 in one year pair, 13 five-degree cells), one AlphaEarth access path, and a CONUS-wide centroid of 58 reference plots. The text mostly states these limits, but the question and title read more broadly.
- Usefulness to readers: 3. It contains decision-relevant evidence for users of embedding change maps and reference-similarity scores, but this evidence is not stated in their terms.
- Clarity: 2. The abstract has 337 words and 28 "x/y" counts, the term "readout" appears 44 times, internal names such as "start-fixed" are used throughout, and 11 post-result exploratory amendments (v12–v14, v17–v24) are presented in the main text.

## 4. Verification results
All runs listed are "a re-run by another agent on the same machine", not an independent reproduction. "Full run" means `reproduce.py` (PASS, 245 checks). "Claims matcher" means my comparison of every claims.jsonl `expected` record with the regenerated outputs.

| claim_id | Claim (shortened) | Procedure run | Result | Record path |
| --- | --- | --- | --- | --- |
| C001 | 8 primary correction contrasts, mixed signs, no consistent benefit | Full run; claims matcher (8/8 records); reviewer recomputation of ΔJ and changed flags from predictions | match | verification/full_reproduce/, verification/independent/main_contrasts.csv, claims_check_regenerated.json |
| C002 | Direct classifier J > start-fixed in 4/4 | Full run; matcher (4/4); recomputation (ΔJ 0.410, 0.309, 0.285, 0.118) | match | same as above |
| C003 | Magnitude flags 0/24 gains, both products and supports | Full run; matcher (8/8); recomputation; raw-array magnitude for 120 targets | match | verification/independent/raw_magnitude_check.csv |
| C004 | Initial class supplied; denominators 24/85, 124/213 | Full run; matcher (4/4); read task definitions in plan-v1 | match | verification/independent/main_operating_points.csv |
| C005 | Stable-negative counterfactual keeps the gain floor | Full run; matcher (4/4) | match | new-results/endpoint-v13/ |
| C006 | Same-reference-plots check changes TESSERA gain contrast −0.012→+0.024 | Full run; matcher (12/12) | match | new-results/reference-completeness-v14/ |
| C007 | Partial later labels 109/166, 0 known disagreements | Full run; matcher (JSON summary) | match | claims_json_regenerated.json |
| C008 | Cohort/matched-control readouts condition-dependent | Full run; matcher (12/12) | match | new-results/robustness-paired-v12/ |
| C009 | Initial-vector readouts retain gain discrimination | Full run; matcher (48/48 + permutation summary) | match | new-results/initial-vector-v17/ |
| C010 | Coordinate-only learners show some discrimination | Full run; matcher (6/6) | match | new-results/geography-v18/ |
| C011 | Class-rate baseline flags no gains; subgroups | Full run; matcher (10/10) | match | new-results/initial-class-v19/ |
| C012 | NLCD Forest: concurrent ≤0 in 8/8, direct higher in 7/8 | Full run; matcher (32/32); manual check of 7/8 from Appendix B | match | new-results/nlcd-v4/ |
| C013 | Native co-location 113/120, 49 equal centres | Full run; matcher (3/3) | match | new-results/native-v5/ |
| C014 | Reference access inside region: 1071→579 km; contrasts change | Full run; matcher (48/48 + JSON) | match | new-results/reference-access-v20/ |
| C015 | Paired-native test not tested (0/16 pairs) | Full run; matcher (JSON) | match (the not_tested status reproduces; there is no scientific result to verify) | new-results/native-pairs-v21/checks.json |
| C016 | Single-date native substitution: 5/20 pairs change a flag | Full run; matcher (96/96 + JSON) | match | new-results/native-single-date-v22/ |
| C017 | Difference-only J lower in 6/6 gain, higher in 6/6 loss | Full run; matcher (96/96) | match | new-results/direct-inputs-v23/, nlcd-direct-inputs-v23/ |
| C018 | All 8 correction contrasts change sign across 10 partitions; TESSERA loss direct 6/10 | Full run (partition stage 341.7 s, not reduced); matcher (52/52 + JSON) | match | new-results/partition-sensitivity-v24/ |
| P001 | Process peak 3 for 21 s | Read three run.json intervals | match (12:50:47–12:51:08Z overlap) | verification/independent/p001_p002.stdout.txt |
| P002 | 486 errors / 162 task IDs, arrays lost | Recounted data/aef-retrievals.jsonl | match | verification/independent/p001_p002.stdout.txt |

## 5. Findings

### R1-1
- Severity: Moderate
- Type: Insufficient evidence
- Target: paper.md Abstract, §4.2, §5, §6; C001, C014, C018
- Content:
  - Observed facts, from reviewer-written checks on the saved data:
    - On the test rows, the concurrent and tree-control scores have Spearman rank correlations of 0.947–0.996 with the start-fixed score. The control adjustment is an exact constant within each held-out region and year pair (maximum within-group SD of the difference ≈6e-18). The corrections change at most 9% of decisions (3–19 changed flags per condition, the largest share being 10/109). Source: verification/independent/score_similarity.stdout.txt and main_contrasts.csv.
    - The reference scores being corrected are near chance for AlphaEarth gains: AUROC 0.556 (start-fixed), 0.510 (concurrent), 0.533 (tree controls). For TESSERA gains they are 0.61–0.66. Table 1 gives no AUROC for these rows (verification/independent/main_operating_points.csv).
    - Reviewer computation from raw arrays (58 reference plots, CONUS-wide centroid, centre pixels; not identical to the paper's per-fold, per-year valid sets), in verification/independent/reference_drift.stdout.txt:
      - The AlphaEarth reference centroid moves very little between adjacent years (1−cos 0.0034–0.0076; at most 0.0124 between 2017 and 2022).
      - TESSERA shows a large 2017→2018 shift (0.0616, against 0.0083–0.0416 for other adjacent pairs). Its stable cohort plots change more in 2017→2018 (median 1−cos 0.140, against 0.076–0.120 in other pairs).
      - By comparison, the median change of loss-positive targets is 0.19–0.40.
    - Only adjacent-year pairs are tested. The motivating application (Heiman, 2026, §3.2) uses multi-year trajectories, s_T − s_0 from restoration start.
  - Inferences:
    - For AlphaEarth there was little year-to-year reference drift to correct, so "no consistent benefit" is close to what the design guarantees. Readers cannot tell from the paper whether the corrections failed or had nothing to correct.
    - For TESSERA, the 2017→2018 shift falls inside the calibration years, so there was something to correct. That is where the corrections are most informative, and the paper does not show it.
- Requested action:
  1. Priority 1: report the per-product, per-year-pair drift of the reference centroid, and the change of stable cohort plots, next to typical target change magnitudes. Use the paper's own fold- and year-specific definitions.
  2. Priority 1: state in the results and the abstract, in plain words, that the corrections leave rankings nearly unchanged (rank correlation, share of changed alerts).
  3. Priority 1: add AUROC for the primary reference rows of Table 1.
  4. Priority 2: state in the abstract and limitations that only one-year intervals were tested, so the conclusions do not cover multi-year reference trajectories. If time allows, add a descriptive multi-year drift table from the saved reference/control embeddings for 2017–2023.
- Feasibility of the action: can be done within the research environment (saved arrays and predictions; well under one hour).

### R1-2
- Severity: Moderate
- Type: Overclaim
- Target: paper.md §1 research question ("in later years"), §4.1, Abstract; C001–C003, C009, C017
- Content:
  - Observed facts:
    - In analysis/main-v1/strata.csv (and my recount), 21 of the 24 LCMAP gain positives are in the 2019→2020 pair and only 3 in 2020→2021 (negatives 46 and 39).
    - 2019 is also the end year of the earlier calibration pairs, as §3.3 notes.
    - The gain positives lie in 13 five-degree cells. Held-out regions 2 and 4 have only 4 and 1 gain negatives (verification/independent/gain_by_region.stdout.txt).
    - The NLCD 2022–2023 gain test has 7 positives.
  - Inference: for gains, "later years" is effectively a single year pair adjacent to the calibration period. Temporal transfer of gain screening is tested for one year pair only, and the 2020–2021 gain results rest on 3 cases.
- Requested action:
  1. Priority 2: report positives and negatives by year pair and by held-out region in §4.1, and the 21/3 split in the abstract.
  2. Phrase the gain conclusions as holding for that pair. Avoid "later years" and "held-out regions" in the plural for gains unless the counts support it.
- Feasibility of the action: can be done within the research environment (text and existing strata files).

### R1-3
- Severity: Moderate
- Type: Insufficient evidence
- Target: paper.md §3.2, §4.6, §4.9, §5, §6; C003, C005, C009, C012, C017
- Content:
  - Observed facts:
    - Brown et al. (2025, arXiv v2, Supplement S1.9 and the source/loss tables S1–S2) list the NLCD land-cover map as a training target for AlphaEarth, with cross-entropy loss, weight 0.5, "target (@50%)". "We use the 2021 release for the year 2021, and the 2019 release for all other years … all samples are associated with the nearest mapped year."
    - The research side's bundled sources/alphaearth-full.txt contains this passage (around lines 1702–1710), but the recorded range_checked for S002 does not include S1.9, and the paper does not mention it.
    - TESSERA is trained self-supervised (Barlow Twins on Sentinel-1/2) without land-cover targets (Feng et al., abstract).
  - Inferences:
    - AlphaEarth vectors for 2017–2020 were partly trained toward one static 2019 land-cover map. This could (a) damp year-to-year change, relevant to the AlphaEarth magnitude floor, and (b) give 2017–2018 vectors information from a map made after the represented year, relevant to the AlphaEarth before-only gain association and to the training pairs.
    - The NLCD Forest endpoint is not independent of AlphaEarth's training targets. The Annual NLCD reference labels are a different product from the NLCD maps, but they share the class system.
    - TESSERA shows similar before-only and magnitude patterns, so this cannot be the only explanation. It does mean the two products are not equivalent replications on these points.
- Requested action:
  1. Priority 2: describe this training design in §3.2 and §6.
  2. Add it to the list of possible explanations in §4.6/§5 and in the scopes of C009, C012 and C017.
  3. State that the AlphaEarth/TESSERA contrast partly separates it from other explanations.
- Feasibility of the action: can be done within the research environment (text; the source is already bundled).

### R1-4
- Severity: Moderate
- Type: Insufficient description
- Target: paper.md Abstract, §4.3, §4.7, §5; C003, C005, C012
- Content:
  - Observed facts:
    - For gains, cosine change magnitude has AUROC 0.287 (AlphaEarth) and 0.318 (TESSERA), well below 0.5 (paper Table 3). In my recomputation, the median magnitude of gain plots is below that of non-tree negatives in both test year pairs and both products (e.g., AlphaEarth 2019→2020: 0.033 vs 0.044; TESSERA: 0.090 vs 0.130; verification/independent/magnitude_by_year.stdout.txt).
    - For losses, the start-year reference score is much weaker than plain magnitude: AlphaEarth AUROC 0.696 vs 0.968, sensitivity 0.52 vs 0.90.
    - For the NLCD Forest endpoint, start-fixed J is negative in 3 of 4 gain conditions (§4.7 table).
    - None of these is discussed in the text: the AUROCs and the negative Forest J values appear only in tables, and the magnitude comparison by year pair is not reported. The abstract reports only differences between corrections and the "0/24" count.
  - Inference: these are the results most likely to change practitioners' judgments. On these plots, a year-over-year embedding change map ranks tree gains *below* unchanged grass/shrub plots, and the reference-direction score does not detect most gains. Without them, readers learn only that the corrections did not help.
- Requested action:
  1. Priority 1: report these facts in the results and in one or two plain sentences in the abstract.
  2. Discuss the inversion (gains being more stable in embedding space than unchanged non-tree plots), keeping it scoped to this labelled sample.
- Feasibility of the action: can be done within the research environment (existing outputs).

### R1-5
- Severity: Moderate
- Type: Insufficient description
- Target: paper.md §1, §2, §5; sources.jsonl
- Content:
  - Observed facts: close prior work and primary sources that the paper does not mention (my search; "not found in the paper" is not a claim that the list is complete):
    - (a) Manikandan et al. (2026), "Foundation-Model Embeddings for Land-Cover Mapping and Annual Change Detection in a Hyper-Arid Region", Remote Sensing 18(18), doi:10.3390/rs18183163. This is in the authors' own sources.jsonl as S026 (abstract only, noting "reference-area threshold sensitivity"), but not in the paper.
    - (b) Yao et al., CaGIS 2026 extended abstract "Cartographer in the Loop". It computes exactly the paper's comparator d = 1 − v_t·v_{t+1} between consecutive AlphaEarth years, with a default threshold τ = 0.15, and compares it with LandTrendr across 15 sites. The AlphaEarth gain medians here (~0.03) are far below τ.
    - (c) Google Earth "Detect change (Experimental)" documentation (developers.google.com/maps/documentation/earth/detect-change). It describes a deployed tool that uses the AlphaEarth embeddings to map year-to-year change at 10 m.
    - (d) The USGS validation of LCMAP Collection 1.0 (Stehman et al., 2021, Remote Sensing of Environment; USGS publication 70223301; I read the abstract only). It reports change agreement on the same LCMAP reference sample of UA 13% / PA 16% for the exact year and 28% / 34% within ±2 years, with class-specific gain and loss mostly below 30% and tree-cover loss the best mapped.
    - Standard annual change algorithms (LandTrendr; CCDC, which is LCMAP's own algorithm) are not named. Change vector analysis is attributed to Wang et al. (2018) rather than a classic CVA source.
  - Inferences:
    - The narrow novelty statement remains valid.
    - Readers need (b) and (c) to see who is affected.
    - (d) shows that weak exact-year detection, and loss being easier than gain, are known for operational products. The ±2-year improvement gives a concrete, citable timing explanation for the gain floor.
- Requested action:
  1. Priority 2: add (a)–(d) with their access ranges.
  2. Present the gain/loss asymmetry as consistent with known results.
  3. Name the standard algorithms in §2.
- Feasibility of the action: can be done within the research environment (public web; abstract-only use must be marked as such).

### R1-6
- Severity: Moderate
- Type: Insufficient description
- Target: paper.md Abstract, whole text (terminology), §3.5–§4.10 structure
- Content:
  - Observed facts:
    - The abstract has 337 words and 28 "x/y" counts, in forms such as "AlphaEarth V1 mosaic: 3/9 of 109 gain cases, 19/6 of 337 loss cases".
    - It reports at least four groups of exploratory results: matched direct inputs, partitions, native single-date input, and Forest counts by horizon.
    - "Readout(s)" appears 44 times. "Start-fixed", "tree controls", "operating point" and "conditional transition screening" are not standard terms in restoration ecology or in land-cover change accuracy assessment.
    - §8 of the research instructions asks that the abstract give planned main results first, and include only those exploratory results that change their interpretation.
  - Inference: a target reader cannot extract the main message or the scope from the abstract.
- Requested action:
  1. Priority 1: rewrite the abstract in about 250 words, in this order:
     - problem and why it matters;
     - data and scope (CONUS, LCMAP plus a separate NLCD test, two products, one-year intervals, 24 gains of which 21 in one pair);
     - the planned answer in one sentence, with the range and the share of changed alerts;
     - absolute detection by the reference score, and magnitude 0/24 with the ranking inversion;
     - the supervised comparison;
     - one sentence on the partition instability.
  2. Move the native single-date check and the per-horizon Forest flag listing out of the abstract.
  3. Use established terms, defined once, alongside sensitivity and FPR: "change score", "alert threshold", omission/commission error or producer's/user's accuracy.
  4. Priority 3: consider moving the coordinate-only, initial-class, reference-access and native-input amendments to an appendix.
- Feasibility of the action: can be done within the research environment.

### R1-7
- Severity: Minor
- Type: Insufficient description
- Target: paper.md §1
- Content:
  - Observed fact: the introduction does not say in which current systems or workflows these scores are used, or whose decisions they affect. Its only example of current use is one workshop paper (Heiman, 2026).
  - Inference: the importance is plausible but not tied to confirmable use.
- Requested action: Priority 3. Add 3–5 sentences with sources: the Google Earth tool and the Earth Engine dataset documentation for year-to-year change, reference-trajectory restoration monitoring, and what a screen would be used for (for example, choosing plots for field or imagery verification). Do not claim effects on users.
- Feasibility of the action: can be done within the research environment.

### R1-8
- Severity: Minor
- Type: Insufficient description
- Target: paper.md §3.1–§3.4, §6; C001
- Content:
  - Observed facts:
    - The reference/control pool has 116 plots for all of CONUS (58 reference, 58 control; data/prepared/references.csv).
    - Each fold's "global" reference is the mean of the reference plots outside one region, spanning very different forest types.
    - The paper reports the 1,071 km eighth-nearest median distance but not the pool size per fold.
  - Inference: the tested construction is a continental "forest-likeness" axis rather than a local reference ecosystem. This further limits transfer of the C001 conclusion to restoration practice.
- Requested action: Priority 3. Report the number of valid reference and control plots per fold and year, and say explicitly in §6 that conclusions apply to this pooled construction.
- Feasibility of the action: can be done within the research environment.

## 6. Value to readers
I wrote the prior expectation after accidentally seeing the abstract, so the comparison is biased toward "as expected". As expected: the corrections gave no consistent benefit, supervised classifiers did better, loss was easier than gain, and transferred thresholds missed the nominal 10% false-positive rate (test FPR 0.035–0.329). In my view, the null for the corrections was largely predictable from the design (R1-1).

Not expected, and the most useful for practitioners: cosine change magnitude ranks LCMAP tree gains *below* unchanged non-tree plots in both products (AUROC 0.29/0.32), and the start-year reference score is near chance for AlphaEarth gains (R1-4). Initial-date-only learners also detect gains about as well as two-date learners (C017).

Users of year-over-year embedding change maps (for example the Google Earth Detect change tool, or cosine-dissimilarity thresholds) and restoration researchers using reference similarity could revise their judgment: a change map is unlikely to flag gradual tree gain, and year-matched references or control subtraction are not a validation. I trust the observed counts highly, since they were re-computed exactly. I trust their generality only moderately (24 gains, 21 in one year pair, CONUS, one-year intervals, an AlphaEarth training detail in R1-3).

The abstract is numerically accurate and heavily hedged rather than overgeneralized, but it buries these messages (R1-6). This is the reviewer's self-report, not a measurement of reader change.

## 7. Points that can be supported
- All numbers in the abstract and Tables 1–3 reproduce exactly from the submitted code and bundled data, and all claims.jsonl expected values match the regenerated outputs (re-run by another agent on the same machine).
- C001 as worded: the eight planned correction contrasts have mixed signs and small magnitudes, and do not establish a consistent benefit or equivalence. C018 strengthens this, since all eight change sign across partitions.
- C002 as worded (point estimates, unequal label resources), with the C018 boundary for TESSERA loss.
- C003 and C005: zero gain flags for magnitude in this sample, persisting without the Grass/Shrub transitions.
- C012 as a pre-planned separate test. plan-v4 was committed (E0105) before any score outcome, and it excludes plots within 1.28 km of LCMAP plots. Subject to R1-3 for AlphaEarth.
- C013, C015 and C016 are reported honestly as diagnostics or as not tested. The paired-native failure is not presented as robustness evidence.
- Process:
  - No contradiction was found between Git and the 108 experiment records. Every plan and code commit exists, precedes its run, and the plan is an ancestor of the code.
  - Exploratory amendments are labelled, and each states what had already been seen.
  - The single AI API call (topic critique, USD 2.02 of the 20 budget) follows §2.3 and the skill's step-6 exception, and all generations are recorded.
  - The concurrency breach and the lost arrays are disclosed and match the records (P001, P002).
  - 130 of 131 commit IDs are recorded in events.jsonl (the exception is the submission commit itself), and every commit-message event ID exists.
- Safety and data terms (§12.5): the study uses only public environmental data (LCMAP and Annual NLCD reference data, public domain; AlphaEarth, CC BY 4.0, with the required attribution in §7 of the paper; TESSERA, CC0). No personal or owner linkage, no ranking of named regions, and licence check dates are recorded. I found no issue.
- References: all cited works exist. The passages I checked (Heiman 2026 §2–3; Brown et al. 2025 unsupervised change d = (1−e·p)/2 with a validation-selected threshold; Ball et al. 2026 §3.5 and Table 5) are described accurately.

## 8. What could not be confirmed / limitations of this review
- The re-run used the same machine and the bundled data. It confirms determinism and internal consistency, not correctness of the external inputs. Live re-acquisition from the AlphaEarth mosaic and the TESSERA store was not attempted, so the agreement of bundled arrays with the public sources was not checked beyond the authors' hashes.
- The reviewer drift numbers in R1-1 use a simplified global centroid of the 58 reference plots, not the paper's exact per-fold, per-year valid sets. They are exploratory and indicative only.
- The R1-3 mechanism is an inference from the AlphaEarth documentation. I did not test it.
- Stehman et al. (2021) was checked at abstract level only (USGS publication page). For Manikandan et al. (2026) I confirmed only the Crossref metadata; its content is described from the research side's record S026. The Burns (2026) article could not be opened (HTTP 403) and was not found by my search; its existence rests on the research side's saved copy.
- My novelty search was limited to web and arXiv searches on embedding change detection, reference similarity and temporal transfer. Absence from my results does not mean absence.
- The prior expectation was not blind (see prior_expectation.md).
- I did not view the research side's session history.
- Target state: checked at the start (19:22Z) and the end (19:48Z). Both times HEAD and submission-1 point to e459b6c0ba39032e1a8069ccc882717d2fac2d71, `git --no-optional-locks status` is clean, and all 8891 SHA-256 entries in review/submission-1/SHA256SUMS.txt match (0 mismatched, 0 missing). No difference was found, and my operations did not change the research directory.
