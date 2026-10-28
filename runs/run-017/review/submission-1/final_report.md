# First-draft research report: free-research-017

Report generated at 2026-10-27T11:51:03.462411Z. This is the research-period report; the planned review by an AI agent has not yet been received. No external publication, upload or contact occurred.

## Scope and question

**Training Point Allocation and Recovery of Small Wetland Patches from Satellite Embeddings.** How does allocation interact with annual embeddings versus seasonal optical predictors at a common reference-upland false-positive area rate, and can image-derived allocation recover an oracle object-frame benefit?

The study selected one topic through the supplied research-question skill, bounded prior-work searches, pilots, recorded scoring and one permitted model critique. Main data contain 64 separated cores in four convenience NWI projects. Original test data have 227 eligible mapped palustrine patches of 0.2–1 ha; all fixed split rotations together have 978. These counts describe the retained inventory, not true ecological completeness or a national probability sample.

The completed analysis includes **465 final local classifier fits**, with all five fixed seeds in every reported fitted cell. It contains the 285-fit priority grid plus 100 exploratory weighting/proposal/query fits, 60 added split fits and 20 geographical-quota fits. `analysis/completed-cells.csv` records the exact conditions. The original protocol's entire possible cross-product was not run: decoder, alternative-budget, hybrid and transfer sensitivities were prioritized to the main area–oracle contrast. Missing cells are not presented as completed experiments.

## Findings

- The original planned interaction is **11.6 pp [4.9, 18.5]**. Embedding recovery changes from 44.8% to 57.6%; optical recovery from 36.4% to 37.6%. The original optical-derived proposal rule does not reproduce the embedding oracle gain. This is a result about fitting allocation from an existing reference resource.
- The planned budget and linear-decoder checks retain the interaction's direction. Entire-held-region cases have small, uncertain interactions; their equal-region pooled exploratory summary is 0.9 pp [-2.6, 4.0]. Threshold replay exposes calibration transport rather than establishing a deployed 5% FPR guarantee.
- Exploratory pooled split rotations attenuate the interaction to **4.5 pp [0.3, 8.3]**. New split intervals, undefined bootstrap replicates and constant/empty cases remain visible. Overlapping training sets do not provide independent replication.
- Exploratory same-position inverse-size loss weights, stronger embedding-guided uncertainty and oracle-core-quota controls recover part of the benefit. They do not establish that additional patch coverage alone causes it, or that an oracle frame is necessary. The weighted decoder disables bootstrap in matched controls; effects are not a causal decomposition of the primary forest.
- The deterministic reference-shift stress test retains 166 of 227 original small patches in a shared cohort and gives positive conditional interactions for all cardinal shifts. Its 61 excluded patches are outside that robustness claim. It is not an estimated inventory-error distribution.

All original and exploratory results, including weaker transfer and split results, remain in the paper and machine-readable outputs. Interval estimates condition on the fixed fitted models and reference maps; secondary/exploratory intervals do not correct for multiple comparisons.

## Limitations and unverified matters

The reference is NWI agreement, with omissions, boundary uncertainty, differing project procedures and nominal source-year matching. Public project reports document older/ancillary inputs as well as 2020 imagery. AEF production v2.1 inputs and global pretraining differ from the fixed seasonal optical summary; architecture or spatial context is not isolated. No independence from related pretraining products is guaranteed. No human annotation labour, ecological completeness, later-year updating, legal wetland determination or conservation outcome was measured.

The dense labelled pool already contains information from which geometry can be reconstructed; sampler restrictions are algorithmic restrictions, not proof that object information is independently unavailable or costly. Uniform-initialization query simulations still receive an inventory-derived land domain. We did not compare every modern segmentation model or input stack. The field-reference alternatives checked (WetSAM point annotations, NWCA site/assessment-area schemas and the new area-weighted-loss paper's request-only data statement) did not supply a verified dense independent patch reference in the searched range. This is not proof none exists. No request/contact was made.

The final literature repeat found direct prior size-aware loss weighting (full relevant method checked) and a recent small-pond embedding search hit (secondary abstract only). No new weighting principle, first small-feature embedding study or absence of close prior work is claimed. All literature used as supporting evidence was checked at the relevant full-text passage; abstract-only hits are marked and not used for findings.

## Failures and recording limitations

There are 5 failed experiment-process runs among 70 completed runs at this report time: E02, E03, E07, E38, E62. E02/E03 encountered source orientation/construction problems; E07 retained a partial input batch after HTTP503; E38 retained measured outputs before an analysis-table handoff failure; E62 had a syntax error before analysis. Corrected runs and original logs are kept. No failed study was replaced by a different successful topic.

An empty initialization helper file was accidentally created in the parent directory and immediately removed (E0004); the recorded correction states no user file was read or changed.

E03 and E62 also have explicit code-provenance timing corrections: execution began while a code commit was pending. A later matching snapshot is not claimed to precede the run. E62 did no scientific computation and its compiled retry passed. E64 also has a presentation-helper addendum: a lazy import loaded prose/table-generation code edited during the running job, so its entrypoint commit alone does not describe that helper. No import-time hash is claimed. E65 verified all numeric rows/intervals, E66 recomputed all numeric tables from immutable committed code, and E67 checked the final manuscript on those fresh outputs. All main classifier batches link to their fixed dataset, plan/code commits and input hashes. Git dates are self-reported; records/hashes do not prove absence of tampering. Session identifier, exact runtime session model/build/settings and session-wide token charges are not exposed.

## Verification and outputs

The clean selected-copy offline run reports **PASS**, in 1471.200 seconds, using committed revision `5d222f64614fa2de18d68f54492d676a16e11c8b`. It checks 879 copied committed files unchanged, recomputes all final-fit measurements/intervals and checks the frozen numeric table hashes. The probability bytes and dedicated environment are shared with the original bundle; this is a self-rerun, not independent reproduction.

Main files: `paper.md`, `claims.jsonl`, `VERIFY.md`, `analysis/`, `figures/`, `review/self-check.md`, `review/offline-verification.json`, `README.md`, the output SHA-256 list and `HASH_SCOPE.md`. Raw prediction arrays outside Git remain bundled with per-fit hashes. Verification working copies and environments count toward storage; working-copy inputs/caches are excluded from output hashes, while regenerated verification measurements/logs are included. See `VERIFY.md` for a single offline entry point, optional rebuilding/refitting and timeline checks.

## Interventions, usage and end state

- I0001: runtime_resume at 2026-10-27T07:14:25.085086Z; Resume research; exclude confirmed stop interval.
- I0002: runtime_resume at 2026-10-27T09:43:24Z; Exclude confirmed usage-limit stop interval.

Tally by type: `{"runtime_resume": 2}`. No permission request, unplanned scientific advice or peer review was received during this research period. The candidate critique is a separate pre-authorized model use. The review round remains pending.

AI API: **1 distinct call** (1 call to gpt-6-astra for topic_candidate_critique). Observed usage is 116078 input tokens, including 6113 cache-write tokens and 0 cache-read tokens; 12786 output tokens include 7851 reasoning tokens. The saved response has 13 search-call items, while provider tool usage reports 11 web requests. No retries or failed AI API calls occurred. A cost-correction row is not a second call.

Exact invoice-priced cost is **unknown** because the returned cache-write lifetime breakdown is missing and a legacy 24h retention label does not match current documented tiers. The recomputed charge range, using the prescribed search-item count and confirmed current write tiers, is $1.9453625–$2.0217750; original under-accounting was corrected append-only. Budget is $20. Pricing source: [official price list](https://developers.openai.com/api/docs/pricing.md), checked 2026-10-27T04:55:55.986246Z, preserved in `data/literature/openai-pricing.md` and `data/literature/prompt-caching.md`. No further API calls are planned. Session/search-tool allowance use and charges remain unknown; no new paid billing route was added.

Research began 2026-10-27T04:34:15Z; original first-draft deadline 2026-10-27T16:34:15Z; extended deadline 2026-10-27T17:37:35.523723Z. Two human-confirmed usage-limit stops are documented in manifest/events/interventions, including processes that completed during the first stop. Latest measured directory size is 9938110210 bytes (including dependencies/history and working copies); limit is 10737418240 bytes. Active experiment runs at the tally time: `[]`.

The original grid was deepened after completion with mechanism controls, more realistic initialization, all-core rotations, geographical mixture checks and reference stress tests. The experimental phase ends with those checks complete and storage approaching its ceiling; remaining space is reserved for verification and retained artifacts. The first draft will be frozen under tag `submission-1`, then no research work will occur until human-supplied `REVIEW-1`. SessionID to preserve: unknown; preserve this directory and local Git history. This report will be updated after review response.
