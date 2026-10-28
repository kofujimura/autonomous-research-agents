# Free Research014 — tree-cover transition screening

Revised package after review by an AI agent; full verification complete.

Read [paper.md](paper.md), [claims.jsonl](claims.jsonl), [final_report.md](final_report.md) and [VERIFY.md](VERIFY.md). This study compares change scores and classifiers for retrospective one-year tree-cover transitions in CONUS. LCMAP dominant Trees and Annual NLCD Forest are different endpoints. Initial classes are supplied; ecological restoration success and user effects are unmeasured.

The full offline entry point is `python -B /path/to/source-copy/scripts/reproduce.py --output /path/outside/source`. Install requirements-analysis.txt in a dedicated environment outside the source. No live data download or AI call is needed after setup. VERIFY.md gives exact steps, expected checks, stage durations, source-integrity checking and the local Git timeline. The latest self-rerun record is review/self-rerun-4.json; current numerical coverage verified=True.

## Outputs

- analysis/main-v1: paired primary results, model-specific availability, fixed reference/support sensitivities, thresholds, predictions and contrasts.
- analysis/secondary-v2: preplanned additional controls/calendar anchors.
- analysis/robustness-*-v12, endpoint-v13, reference-completeness-v14, initial-vector-v17, geography-v18, initial-class-v19, reference-access-v20: explicitly exploratory checks.
- analysis/nlcd-*: separate Forest/horizon/label-agreement results; matched direct-input additions are exploratory on already-inspected data.
- analysis/partition-sensitivity-v24: ten fixed earlier fitting/calibration assignments; all results and missing conditions retained.
- analysis/direct-inputs-v23 and nlcd-direct-inputs-v23: matched learner/target, four fixed inputs, all results and reconstruction/calibration checks.
- analysis/native-v5: 113/120 point-year input comparisons. analysis/native-pairs-v21: unfinished paired check, 0 complete pairs. analysis/native-single-date-v22: availability-selected single-date substitutions with identity counts, not a native refit.
- figures/, tables/: generated paper visuals/tables. data/: public labels/raw selected measurements. experiments/: actual commands, commits, times, logs, raw/results and retained failures.
- input_prompt.md and input_skills/: finalized original instruction transcription and unchanged copied topic-selection skill. protocol/: original/amended plans and deviations. sources/ and sources.jsonl: bibliographic/access/licence records and checked passages.
- review/: author self-check, candidate self-reruns and first-draft snapshot; human-provided AI-agent review and point-by-point response are preserved.

## Attribution and limits

Analysed LCMAP/NLCD reference labels are public domain; the archive contains unused components with separate terms. TESSERA v1 data are CC0. AlphaEarth V1 data are CC BY4.0: **The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind.** The primary AlphaEarth source is an unofficial geographic mosaic. Native-grid input processing differs; full paired/native performance is unverified.

The records retain a brief experiment-concurrency breach, unknown earlier library request concurrency, lost arrays from a failed acquisition, reporting errors and incomplete native acquisition. No external publication/contact or subagents occurred. The sole API generation was a topic critique, not paper review. Hashes/Git/local logs do not prove independence or untampered chronology. The submission-1 snapshot remains unchanged; final identifies the revised package after review.
