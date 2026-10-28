# Deviations and implementation corrections

2026-10-25T09:39:15Z: Two simultaneous retrieval starts each wrote E0051 because the initial logger assigned IDs without a lock. The original lines are retained. Disambiguate by artifact path: E0051/fetch-aef-000 and E0051/fetch-tessera-000. The logger now locks the event file while allocating IDs. This recording defect does not change the sampling, plans or measurements. The failed optional process-list command was sandbox-restricted; run logs and child PIDs suffice, so no permission was requested.

2026-10-25T10:11:36Z: Added protocol/interpretation-clarification.md before empirical score inspection. Temporal holdout concerns downstream readouts; later-produced encoders and retrospective manual labels prevent a claim of historically deployable or prospective validation. No methods change. V2–V4 are additive pre-analysis extensions and v3 scheduling change; original v1 is retained.

2026-10-25T11:30:14Z: Additional-control fetch-controls-aef failed to save raw arrays because a relative tasks path was used with absolute relative_to. Preserved all95 failed attempts for32 taskIDs and stopped only its child group. Recording restored by validating/resolving the path before requests. V8 allows one fourth cumulative attempt only for this specific software failure; no newsample, no observedscore selection. The unsaved arrays of the failedrun are unavailable and cannot supportclaims.

2026-10-25T11:32:52Z: Correction to the previous technical-stop wording: the signal attempt failed with PermissionError and did not stop the process. Its existing1800second timeout will end it; no alternate signalling route or permission request is used because waiting under the authorized limit suffices. The fixed path conversion passed a local check. Old failed-run arrays remain unavailable.

2026-10-25T12:25:54Z: Library inspection found a GeoTessera read_patch internal concurrency override of32, so the intended outer bound2 was not enforced. Actual request concurrency unknown. V9 explicitly pins its module setting to2 for subsequent jobs, with smaller batches; existing job ends under configured timeout. No scientific outcomes inspected.

2026-10-25T12:35:05Z: V10 isolates input-cohort availability/hashes per analysis; optional extra-control retrieval no longer affects the original main artifact. No empirical outcomes inspected or score rules changed.

2026-10-25T12:47:05Z: V11 permits the already-prespecified AlphaEarth model-specific analysis after its own original retrieval is closed, before slower TESSERA finishes. The paired primary analysis and all sampling/scoring rules remain fixed. Separate inputs/results and an offline re-run preserve this scheduling change.

2026-10-25T12:52:20Z: Resource-limit breach: an unconditional launch of fetch-nlcd-aef-012-015 at12:50:47UTC preceded the end of fetch-nlcd-aef-008-011 at12:51:08UTC while fetch-tessera-033 was active. Registered experiment overlap was21seconds, peak3 rather than permitted2. These are recorded process times, not instrumented HTTP concurrency. The predecessor ended normally before the breach was inspected, leaving2 active jobs. No record is erased and no limit is relaxed. The wrapper now locks launch registration and refuses a new child when2 run records are active; run records are written atomically. The breach must appear in self-check and final resource tallies. Scientific sampling and scoring are unchanged.

2026-10-25T12:58:02Z: V12 fixes exploratory calibration, semantic-control-matching, baseline-only labelled-cohort readouts and a saved partial-label audit after the first AlphaEarth scores. These additions do not change primary comparisons or sample selection.

2026-10-25T13:30:58Z: V13 fixes an exploratory stable-only gain-negative counterfactual and before/after scalar diagnostic after paired results. Grass↔Shrub negatives are excluded only from this secondary calibration/test condition; original sampling, fitting, primary output and failed/negative results are retained.

2026-10-25T13:37:11Z: V14 fixes an exploratory same-plots-before/after reference completeness sensitivity after discovering differing valid-reference counts in8/40 primary groups. Original per-year-valid reference means remain primary; no source case or label is changed.

2026-10-25T13:46:21Z: V15 fixes a3-patch byte-equivalence/operational-timing pilot for the library-documented gateway route to the same public TESSERA v1 data. Future route switch is conditional on exact values and the fixed timing rule; no sample, score or resource limit changes.

2026-10-25T13:53:28Z: V15 transport pilot saved all3 raw patches but failed relative-path reporting after each save. Original error records and false decision remain. Resolve output paths before requests; separate offline recovery compares preserved raw arrays and metadata, with logged elapsed including bookkeeping as an upper bound. No re-fetching.

2026-10-25T14:14:27Z: V16 restores up to4 source batches/job for the same TESSERA NLCD queue after measured gateway batch durations, within the original v3 cap. V9 one-batch reduction is superseded for timing only. All trial limits, cutoff and sample remain fixed.

2026-10-25T14:29:10Z: V17 fixes exploratory initial-vector input diagnostics after strong state-readout results and transfers all added readouts to the still-unanalysed NLCD endpoint. Primary contrasts remain unchanged. This does not establish forecasting or isolate static context, and uses after-vector availability for comparable complete cases.

2026-10-25T14:53:31Z: V18 fixes exploratory coordinate-only controls after initial-vector associations. Same data partitions/availability and thresholds are used; no embedding values enter the three learners. The construction is established prior work, and causal/forecasting interpretations are excluded.

## 2026-10-25T15:09:19Z — v19 initial-class alternative explanation
Post-primary exploratory comparison fixed before subgroup metrics or class-rate scores. All original scores, thresholds and primary claims retained. No test-based selection.

## 2026-10-25T15:27:52Z — v20 baseline reference access
Exploratory change permits baseline R/C plots inside held-out region, motivated by already-saved very large nearest-reference distances. Target fitting/calibration and original primary condition unchanged. No claim of equal geographic information access.

## 2026-10-25T15:32:29Z — v21 paired native target input cases
Additional exploratory16-pair stratified case check fixed before native agreements/results; target inputs alone change, original mosaic fitting/R/C/calibration retained. Retrieval ends17:00UTC even if incomplete. No general native-performance claim.

## Usage-limit stop and incomplete native acquisition
Observed on resume2026-10-25T17:12:29UTC. The fixed17:00retrieval cutoff passed while the model was stopped for a confirmed usage limit. Original native slots113/120were obtained; v21additional acquisition never launched, and only1/32point-years from an earlier v5query is available (0/16completepairs). No missing slot is replaced and no post-cutoff acquisition occurs. The point-year diagnostic remains evaluable; paired-native decision stability is untested. Availability analysis and saved-data verification do not convert this unfinished test into a success.

## 2026-10-25T17:19:18Z — v22saved-data alternative
After finding0complete native pairs anywhere in saved original target data, fix an availability-selected single-date substitution case series using only existing native measurements. Unmeasured dates remain mosaic, so this does not complete or replacev21. Explicit v21status fields clarify empty counts without changing any score/flag CSV. All acquisition remainsclosed.

## 2026-10-25T17:55:34Z — v23matched direct input comparison
After first complete numerical self-rerun, address algorithm/training-target confounding in before-versus-after interpretation with fixed direct learners on four input choices. Both endpoints already inspected, so all new estimates exploratory and Forest data reuse explicit. Original results and native-pair failure retained; new end-to-end rerun required.

## 2026-10-25T18:41:07Z — v24 fitting/calibration partition sensitivity
Remaining conditional-on-fits uncertainty is examined using ten fixed earlier cell assignments. All prior results have been seen; this is exploratory and does not replace the original partition or estimate independent training variance. No data acquisition; all split outcomes and missing conditions retained. Expanded verification2 remains scoped to its earlier numerical candidate and a final expanded self-rerun will be required. Event E0553.
