# Response to REVIEW-1

Review ID: review-018-1. The original review by an AI agent is preserved verbatim in `review/review-1.md`. Reviewer identities and reruns are reported by the human and were not directly observed by this session. Same-machine reruns are not independent reproduction.

The primary conclusion is revised: an increment attributable to embedding distance is not established on the prespecified equal-window metric under plan-v6’s qualification rule. Predictive label information, screening performance and field hydrological validity are distinguished. No primary data, metric, acceptance rule or first-draft snapshot was replaced.

Plan v23 was fixed before the added analyses and seed fits at commit `bd204416000b4998b8c97882aff9e7d866670f8f`. Saved-output analysis code was fixed in `ef2002070c203075b87d2c4dd6effedb93789e8a`; the main revision modules were added in `194021a33309efad54f7b893e1372c5fb1e1b471`. Subsequent exact file revisions and the final verification source commit are listed below before finalization.

## R1-1

**Decision: partly adopted.** State the primary answer, show the planned null/seed controls prominently, report homogeneous three-seed means, and apply plan-v6 qualification.

The attribution claim is not established under the planned descriptive rule. We avoid a formal “indistinguishable” claim because three permutations and heterogeneous perturbations do not define a calibrated null distribution. A narrow factual correction: submitted Figure4 already included all planned seeds/permutations; the revision clarifies its labels/caption and adds the full paired-scale table to the main text.

Changes: Abstract; §§4.1,4.5,5; Figure4; C01/C04/C06; code/review_manuscript.py and review_claims.py.

Added experiment references: `review-reanalysis-v1`, `review-reanalysis-v2`.

## R1-2

**Decision: adopted.** Report both weightings and small-window contributions.

The accepted sets can differ, so the one-error difference is described as one fewer mismatch among five accepted queries rather than one same-query prediction corrected. No window is excluded from the primary result. Polygon-C and other-window conclusions are explicitly restricted when pooled results differ.

Changes: Abstract; §§4.1–4.4,4.6,4.9; C01/C08/C10/C13/C15.

Added experiment references: `review-reanalysis-v1`, `review-reanalysis-v2`.

## R1-3

**Decision: adopted.** Frame zero-column changes as fitting randomness and add the fixed five further corrected-input seed fits.

Changing feature dimension can change randomized trees even at the same random-state integer. The zero-column result is a diagnostic of effect size relative to fitting variability, without a uniquely demonstrated tree-level mechanism. Homogeneous initial three-seed and corrected six-seed summaries are kept separate.

Changes: §4.5; Discussion; C03/C17; analysis/review-seeds/.

Added experiment references: `review-seed-3000`, `review-seed-4000`, `review-seed-5000`, `review-seed-6000`, `review-seed-7000`.

## R1-4

**Decision: adopted.** Add paired uncertainty for decoder log loss/recall and a compact real/null table on both scales.

Decoder prediction and accepted-reference mismatch answer different questions. Better probabilities from these fitted models do not establish conditional information absent from every possible physical model, field hydroperiod, or screening benefit. The new uncertainty is explicitly exploratory.

Changes: §§4.3,4.5,5; C16; decoder-contrasts.csv and real-null.csv.

Added experiment references: `review-reanalysis-v1`, `review-reanalysis-v2`.

## R1-5

**Decision: adopted.** Shorten the abstract around the answer, define the core terms, and give a plain-language practitioner interpretation.

The abstract retains the primary paired-scale contrasts, the small-window caveat and planned control range, with one exploratory decoder observation. The ambiguous claim about the earlier embedding year is removed from the abstract; alternate years remain in Results with fixed-label and model-randomness limits.

Changes: Abstract; Introduction; Methods glossary; Discussion; paper-template.md.

Added experiment references: no model fitting added specifically for this point.

## R1-6

**Decision: partly adopted.** Position the close inundation studies and specify that no explicit SAR inundation predictor is in the physical baseline.

We checked the complete SFS conference abstract and relevant full-text passages of Rahman2026, DeVries2017 and Lang2008. The conference abstract reports methods without numerical outcomes and is labelled accordingly. The related2018poster was confirmed only in the author bibliography; no SWaRe abstract/product validation was located in the bounded search, so no unverified method or performance claim is added. The saved input inventory contains terrain, optical surface-water and HAND maps plus embeddings, but no explicit SAR inundation map or gauge series. The multisensor embeddings themselves do not supply an independent physical SAR comparator. No new SAR acquisition was added within this response; we narrow the claim rather than claiming such a study is impossible.

Changes: §2; §6; references.md; sources.jsonl; sources/review-*.

Added experiment references: no model fitting added specifically for this point.

## R1-7

**Decision: adopted.** Split planned secondary controls from the exploratory recent panel and correct the inspection timestamp.

C04 is planned; the recent-panel result is C14 and exploratory. VERIFY now names E0175 at17:18:57Z as the first explicitly logged aggregate inspection, distinguishing summary completion at17:16:34Z and the imprecise earlier clock note. An append-only correction event preserves the earlier record. Both times follow plan-v6.

Changes: §3.5; §4.5; C04/C14; VERIFY.md; events.jsonl.

Added experiment references: no model fitting added specifically for this point.

## R1-8

**Decision: adopted.** Report the planned size, vegetation and source-image-date subgroups with available/accepted counts and windows represented.

The own-screen subgroup figures are descriptive and confounded with window. No rescreening, causal image-age explanation or age-adjusted effect is claimed.

Changes: §4.8; planned-subgroups.csv.

Added experiment references: `review-reanalysis-v1`, `review-reanalysis-v2`.

## R1-9

**Decision: adopted.** Name outdated-inventory auditing and locations without current regime labels as possible applications and state the deployment gap.

The present closed, inventory-delineated, label-masked experiment does not test either deployment or open-set mapping. Other-window training is a limited retrospective comparison that changes training size, seeds and indicators as well as geography.

Changes: Introduction; Discussion; Limitations.

Added experiment references: no model fitting added specifically for this point.

## R1-10

**Decision: adopted.** Disable bytecode writes in the optional batch parent and every child, and document the environment safeguard.

run_rotation_batch.py sets sys.dont_write_bytecode and PYTHONDONTWRITEBYTECODE before importing local helpers, and invokes child scripts with -B. VERIFY also instructs optional refits to use both protections. The additional seed batches exercise this launcher; source immutability is checked again by the final end-to-end run.

Changes: code/run_rotation_batch.py; VERIFY.md; final verification.

Added experiment references: no model fitting added specifically for this point.

## Status of additions and final checks

The actual completed additions and the end-to-end result are recorded below. The archived preliminary reanalysis remains distinct from the final reanalysis.


### Completed fixed additions

All five fixed seed groups completed successfully; no seed was replaced. The final saved-output reanalysis is `analysis/review-reanalysis-v2/`; the preliminary version remains preserved. Against the physical pair model, corrected six-seed mean changes (equal-window / pooled, percentage points) are pair_aef: -2.49 / -0.60; pair_tessera: -4.49 / -1.92. These favourable means are reported prominently and do not erase the original planned seed reversal; no matched repeated-permutation fits were added for these five seeds.

The model-continuity audit compared ten exact code/input files with complete pre-review verification source commit `d3926e3337cca22e6668d038c8fc1bb08e27a8db`; all agree. It links the existing polygon model refit to unchanged inputs/code, without calling this a new polygon refit. The final revision code is fixed in commit `92bc95fee1193cf8eebf4b4014370e653c27a2fa` and later Git revisions; the end-to-end source commit will be appended after its run.


### Final end-to-end result

The author ran the VERIFY.md entry point on a fresh immutable Git archive of `f394f535cca460a605dc124d707ae73e1e4f2146`, with full four-rotation primary refitting. It passed 108/108 checks in 1176.107529seconds. The complete revised paper and claims regenerated byte-identically; primary predictions matched the archive and source contents/file list remained unchanged. The run used no network or AI API. This is an author re-run, not independent reproduction. The primary/polygon model and saved-result scopes remain distinct in `analysis/verification-status.json`.

The scientific-file versions for every response point are those in commit `f394f535cca460a605dc124d707ae73e1e4f2146`. The bytecode fix for R1-10 was introduced in `bd204416000b4998b8c97882aff9e7d866670f8f`; final manuscript/claims were generated in the verified source commit. Exact per-file history is available with `git log -- <path>`. Subsequent changes are verification receipts, administrative records and final submission metadata; no scientific code, manuscript or claim changed after this run.
