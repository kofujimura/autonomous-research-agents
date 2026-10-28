# Self-check before first-draft submission

Observed 2026-10-27T11:38:55.688522Z. This is the author's self-assessment, not external peer review, human review or independent reproduction. The planned review by an AI agent has not happened.

## Numerical and process checks

- Full numerical offline entry point: **PASS**, 1471.200 seconds. Prepared committed revision: `5d222f64614fa2de18d68f54492d676a16e11c8b`. All 879 selected committed files remained unchanged; saved probability inputs were shared by links and used for reading. It recomputed all 465 final models' measurements, intervals, reference shifts, allocation/weight checks and twenty numeric tables without network/API/refitting. Report: `review/offline-verification.json`; raw outputs and logs: `verification-work/run-1/`.
- Earlier aggregation was optimized for the process deadline. E63 checked the full original 75 fits plus four boundary cases; E65 compared all reported scalar rows and intervals from E61 against canonical E64 outputs, tolerance 1e-12. `review/aggregation-full-comparison.json` is PASS. The original slower outputs remain intact.
- After prose-only edits and a paragraph reporting already planned pixel metrics, current manuscript generation was rerun on the clean numerical outputs. **PASS**: the entire manuscript bytes, 20 numeric tables and 10 claims agree; values use tolerance 1e-12. `review/manuscript-check/comparison.json` records the manuscript hash. This is still the same session's self-check.
- Every final fitted cell has all five original seeds. Fitting positions are unique, training-only, label-consistent and shared across representations/decoders when specified. Oracle-quota negatives/counts and saved weight vectors were recomputed and checked. `analysis/completed-cells.csv` and the allocation audit state exactly what ran; omitted cross-products are not counted as complete.

## Close prior work and citations

The post-result literature searches in `protocol/close-prior-work-update.md` repeated wetland training, area/object sampling, embeddings, small objects, model-guided acquisition and weighting queries. Full relevant passages supporting the paper were checked: the NWI guide, small-wetland/object-based literature, AEF v2 paper and production access documentation, Ryan2026 wetland-embedding methods, WetSAM's checked arXiv version, map-validation/metric guidance, the boundary-aware2026 preprint, WIP2023 training and transfer methods, Radoux/Bogaert2017 polygon sampling, and Zhou2025 size-aware loss equations. Source-specific ranges, versions and retrieval limits are in `sources.jsonl`.

The final search revealed closer precedents than the initial screen. Weighting smaller water bodies is not new; the manuscript explicitly calls its weighting arm a diagnostic, not a new algorithm. Corcoran2015 and Liu2026 small-pond embedding hits remain abstract/bibliographic-only in the checked range and supply no claimed findings. A thesis size-stratification passage remains search-only and is not cited as evidence. The publisher rate-limited routes were stopped, not bypassed. A legally public publisher-provided full-text copy supplied Zhou's method. The preprint is identified as not peer-reviewed. No absence of prior work or guaranteed novelty is asserted. Exact overlap with inaccessible close papers remains unresolved.

## Readability and strength

The introduction starts with wetland inventories and their planning uses before representations/classifiers. It uses National Wetlands Inventory, palustrine wetlands, mapped patches, minimum mapping unit, producer/user accuracy and false-positive rate in their established senses. FPR is explicitly FP/(FP+TN), distinct from commission error. AEF production v2.1 differs from the source paper's principal v2.0 evaluation. Original mapping reports qualify the nominal 2020 match and regional differences; regional tables are in fixed order and are not rankings.

The abstract reports the original planned result first, the negative original proposal finding and transfer/calibration boundaries, then labels the attenuated pooled-rotation estimate and mechanism checks exploratory. Original conditional interaction is not presented as a universal benefit. The frame necessity question is narrowed to tested alternatives in the reported wording; original question/plan remain retained. The paper says no ecological completeness, field accuracy, human annotation effort, legal wetland extent or conservation effect was measured. Dense inventory pools make information restrictions algorithmic; geometry is not proved independently unavailable or costly.

## Alternative explanations addressed

| Concern | Evidence/check | Remaining interpretation |
| --- | --- | --- |
| Class-composition difference in practical samplers | Exact matched-count controls, retained initial labels | Stronger uncertainty gain persists descriptively; not cheap acquisition |
| Region/core mixture | Equal-region quotas and original-oracle quota matching by region/core | Core mixture recovers part; residual is not a full causal decomposition |
| RF-only behavior | Linear decoder and matched no-bootstrap controls | Only these learner/settings tested |
| Weighting versus exposure of new training patches | Inverse-size loss weights on identical positions | Same-position improvement in no-bootstrap setting; original forest mechanism not identified |
| Weak optical proposal teacher | AEF proposal/uncertainty and uniform-initialization simulations | Partial gains; supplied land domain and simulated labels remain |
| Pooled FPR redistributes regional errors | Region-specific evaluation and validation replay, regional FPR tables | Original pooled point is not a deployable threshold |
| Threshold estimation uncertainty | Exact reselected-threshold block bootstrap | Still fixed fitted models/reference maps/convenience regions |
| Favorable original split | All-core fixed rotations, separate new splits and pooled summary | Attenuated effect, not independent replication |
| Unmatched transfer cohort | All-core and original-test-subgroup summaries with actual FPR | Subgroup retains wider-cohort thresholds; no matched-FPR claim |
| Fine-grid alignment | Cardinal integer shifts on shared reference-only cohort | Only 166/227 patches retained; not an error model |
| Appearance versus correctness | Optical smoothing/edge metrics beside coverage | Smoothness is not accuracy; descriptive, no new validation principle |

Original primary maps are not trivial: 0 all-positive and 0 all-negative among 1200 fit–test-core cases; zero macro floor/ceiling fits. All 85 main audited probability/decision pairs differ. Across all 550 audited pairs there are 0 identical probability maps and 0 identical decisions. Other scopes do contain constant/empty core cases, disclosed in the abstract and complete comparison-case table. Five and ten undefined bootstrap replicates in new rotations are reported, not treated as defined.

The missing 20 m interiors are predictable geometry restrictions, not discovered model defects. All 227 original small test patches meet the ≥90% valid sensitivity, so that sensitivity is an identical cohort and supplies no independent robustness. The pooled and regional standardized threshold conditions coincide by construction for each single-held-region model; this duplicate is not counted as independent evidence. Same-position weighted fits intentionally have identical fitting positions but different losses. Area/oracle overlap and all negative-position sharing are reported, not treated as independent samples.

## Remaining weaknesses and routes checked

NWI omissions and true ecological extent cannot be learned from the same saved inventory. WetSAM's checked labels are sparse points; NWCA's checked schemas provide sites/assessment areas, not a verified complete patch-reference bundle in this search; Zhou's data statement requires a request, and no external contact is allowed or made. These checks do not prove no independent dataset exists. We did not claim that the environment makes independent validation universally impossible.

AEF and optical inputs differ in sensors, summaries, native band resolutions and pretraining. Public NLCD access/prior-dependence checks did not establish an independent pretraining reference. Saved embeddings cannot identify architectural context separately; the claim is correspondingly limited. More derived predictors or other algorithms could be tried, but the work does not claim a best possible wetland mapper. The available context, hybrid, decoder, budget, stronger-frame and geographical controls address the specified comparison, while further expansion is deferred as directory usage approaches the ceiling. Four convenience projects cannot support nationwide inference. Human labour/outcomes remain unmeasured under the trial's no-participant rule.

## Record exceptions and finalization

E02/E03/E07/E38/E62 failed runs are retained. E03 and E62 code-launch/commit timing exceptions are explicitly corrected; E62 has an addendum clarifying that no launch-time code hash was measured. Later code snapshots are not claimed to precede those runs. An empty helper accidentally created in the parent directory was removed immediately and recorded at E0004. Public source PDFs incidentally include author professional contacts; no individual/household/business information was analyzed, and NWCA site/ownership files were not downloaded.

All record times are tool/system timestamps. Original start 2026-10-27T04:34:15Z, current extended draft deadline 2026-10-27T17:37:35.523723Z; confirmed usage stops and continuing processes are documented separately. Exact session identifier/build/settings and session-wide usage are unknown. The one critic API's exact invoice cost is unknown because cache-write lifetime is absent; recomputed bounds and the append-only correction are retained. No other AI agent or research-work API was used.

Before submission: hash raw inputs/measurements, large arrays outside Git, original API artifacts and self-rerun outputs; exclude duplicated working-copy inputs/caches as documented. Snapshot required files, scan for the exact key value without displaying it, commit/tag submission-1, record its receipt, then freeze awaiting REVIEW-1. This self-assessment does not replace that review.

Additional provenance check (2026-10-27T11:51:02.214547Z): E64 imported its presentation helper lazily after that helper had been edited during the running job. `experiments/E64/provenance-addendum.json` limits the start-commit claim accordingly; no import-time hash is invented. The numeric comparison E65, immutable committed-copy recomputation E66, and final manuscript rerender E67 resolve the final outputs without erasing this recording exception. The original selection code/output also specify base seed plus project OBJECTID; this pre-performance derivation is now explicitly cross-referenced in the deviations ledger.
