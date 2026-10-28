# Response to review-017-1

Written 2026-10-27T13:15:48.700191Z. Original review: `review/review-1.md`; target `submission-1` (`8ff25a6335b4ec3aee0b998032633a6948f840b9`). All six findings are adopted with evidence-specific qualifications below. No result, fit, failure or first-draft snapshot was deleted. Review-prompted analysis plan v11 was committed before E68. No new model fitting or AI API call was used.

## R1-1 — adopted

Reason: The largest original-split interaction was numerically correct but its prominence understated split dependence and optical gains. The bootstrap conditions on fitted training sets, thresholds and maps; it does not resample split selection.

Changes: paper.md Abstract, §§3.4,4.1,4.5,5; claims C01 implication and C06 text/implication; code/review_manuscript.py and code/write_claims.py.

Evidence and limits: All-split embedding gain 8.4 pp [4.5, 12.1]; optical gain 3.9 pp [1.6, 6.2]; interaction 4.5 pp [0.3, 8.3]. Original interaction 11.6 pp [4.9, 18.5] retained as planned, not substituted. Text explicitly says optical gained in every new split and two of three new interaction estimates fall below the original lower interval endpoint. Four test-core clusters per region and fixed training cores are explicit.

Change commits: `36bc480627ec5dd0455fd08b4eaa4e86a71c94b7`. Added scientific analyses: E68.

## R1-2 — adopted

Reason: Preplanned conditions were computed but inadequately reported. Complete reporting changes the reader’s interpretation, particularly coverage and validation replay. Expanded tables/intervals are labelled review-prompted while the underlying preplanned definitions retain that status.

Changes: paper.md §4.2, Discussion, Appendices E–G; analysis/review-response/summary.json; five new generated tables; claims C11; code/review_sensitivities.py and VERIFY.md.

Evidence and limits: All16 fixed rows are shown (original/four-split × six >=50%-coverage operating conditions plus any/75%). Existing >=50% blocks supply conditional intervals; any/75% are point estimates explicitly. Original pooled validation replay interaction 4.5 pp [-2.4, 12.0]. Without-Vermont interaction 12.8 pp (point only). All rotation replays, medium/large patch counts/results, balanced accuracy, per-fit pooled AP averaged across seeds and the size/isolation figure are now reported. Optical any-overlap exceeds embedding any-overlap in pooled arms; >=50% ordering reverses. We do not infer a smoothness cause or ecological completeness. No requested condition was omitted.

Change commits: `9509e2e690025eab85e7df7f7d0e2fe31b726c28`, `36bc480627ec5dd0455fd08b4eaa4e86a71c94b7`. Added scientific analyses: E68.

## R1-3 — adopted

Reason: The planned other-project-threshold transfer is more decision relevant than held-project test-standardized thresholds alone. Negative recovery differences accompany FPR differences, so they cannot be interpreted as matched-error causal effects.

Changes: paper.md Abstract, §4.3 and Discussion; analysis/tables/review-transfer-replay.md; C04 text, scope, implication and expected fields.

Evidence and limits: Planned pooled transfer embedding gain -3.6 pp [-7.0, -0.6], optical gain -0.6 pp [-3.1, 1.7], interaction -3.0 pp [-7.3, 0.9]. All four regional rows and achieved FPRs appear next to the standardized-transfer table. Regional five-seed mean FPR range 0.1%–15.2% is distinguished from the individual-seed range. The former broad “small and uncertain” characterization is restricted to held-project-standardized interactions.

Change commits: `36bc480627ec5dd0455fd08b4eaa4e86a71c94b7`. Added scientific analyses: E68.

## R1-4 — adopted

Reason: The first abstract was too dense for practitioners and did not explain the stable decision or its practical limits.

Changes: paper.md Abstract (about200words), Introduction, §§3.3–3.6 and Discussion; paper-template.md and code/review_manuscript.py.

Evidence and limits: The revised abstract explains patch-first allocation and the fraction of reference-upland area predicted positive, identifies16primary test cores and2,000positions, reports both predictor gains and the planned test, labels pooling exploratory, and states transfer/calibration limits and a practical recommendation. Geometry, constant-map and mechanism-control counts remain in Results rather than the abstract; no entire primary comparison is a floor, ceiling or identical-map case. Oracle is glossed as privileged access to inventory boundaries/identities. Duplicate3.5 is corrected to3.6 and the deviations section now summarizes actual changes.

Change commits: `36bc480627ec5dd0455fd08b4eaa4e86a71c94b7`. Added scientific analyses: none.

## R1-5 — adopted

Reason: Classic training-allocation and point/object studies are close precedents. The sampling principle was expected; the contribution is the quantified held-out representation × allocation comparison.

Changes: paper.md §2 and References; sources S046/S047 and supplemented S039; data/literature/*-2015-review-notes.md.

Evidence and limits: Checked relevant full-text methods/results/discussion and CC BY4footers in primary publisher-provided public copies for Millard & Richardson, Colditz and Corcoran after direct publisher429 responses were stopped. Colditz’s heterogeneous-pixel precedent is related to the interior arm without asserting identical mechanisms; between-class area objectives differ from equal-patch recovery. Corcoran’s forested-site benefit and coarser agricultural-site tie are qualified by its changed predictor aggregation/output unit. Relevant passage ranges and public URLs are recorded; original PDF/HTML bytes are not bundled and notes are not presented as source transcriptions.

Change commits: `36bc480627ec5dd0455fd08b4eaa4e86a71c94b7`. Added scientific analyses: none.

## R1-6 — adopted

Reason: The v9 launch pointer and identical source IDs were imprecise descriptions of cumulative coverage and evidence roles, despite not changing numbers.

Changes: protocol/implementation-clarifications.md review-017-1 subsection; every claim source_ids_role; VERIFY.md revision subsection.

Evidence and limits: Original E61–E67 run.json files remain unchanged. The clarification says those runs cover cumulative v1–v10, including v10 alignment; final v11 verification includes all of them plus review summaries. source_ids explicitly denote data-provenance/access documents only, whereas evidence_paths and experiment_ids support numerical findings.

Change commits: `9517bf40fa7c930405c310aea1ed12a408ccf00d`, `36bc480627ec5dd0455fd08b4eaa4e86a71c94b7`. Added scientific analyses: none.

## Verification and tally

```json
{
  "generated_at_utc": "2026-10-27T13:15:48.699678Z",
  "review_id": "review-017-1",
  "points": 6,
  "decisions": {
    "adopted": 6
  },
  "existing_claims_revised": [
    "C01",
    "C04",
    "C06"
  ],
  "claim_statuses_changed": [],
  "claims_withdrawn": [],
  "claims_added": [
    "C11"
  ],
  "analysis_batches_added": [
    "E68"
  ],
  "verification_batches_added": [
    "E69",
    "E70"
  ],
  "new_model_fits": 0,
  "new_ai_calls": 0
}
```

Latest full self-rerun: **PASS**, revision `36bc480627ec5dd0455fd08b4eaa4e86a71c94b7`, 1498.153s. See `review/offline-verification.json` for exact scope/time and `VERIFY.md` for the single entry point. This same-session numerical rerun shares the saved probability bytes; it is not independent reproduction.

The human reports that the AI-agent reviewer also reran saved-prediction verification on the same machine. That report is preserved, not independently inspected or described as human peer review/independent reproduction. Reviewer model/runtime labels are human-reported, not directly observable by this session. Final amendments and the completed verification receipt appear in the final tagged tree.

Final manuscript/claim consistency check **PASS** (E70, 1.252s): all25numeric tables, all11claim records and the full manuscript agree with rendering from the fresh E69 numerical outputs, tolerance1e-12. Report `review/final-manuscript-check/comparison.json`; code/presentation commit `e186eb6a41c24a5ac2f34b823081233d6837a33e`.
