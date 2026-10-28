# Evaluation phase: amendment 1 (counting run-014)

Written 2026-10-27, after run-015, run-016 and run-017 had finished and their results had been seen, and before run-018 was started. The decision is the human author's. The management agent wrote this text. `preregistration.md` is left unchanged (SHA-256 980193992912a3ff…, the value recorded when it was written).

## 1. Change

- The pilot run-014 is counted as the first of the five evaluation runs.
- The series is therefore run-014 to run-018: v1.10, then v1.10.1 to v1.10.4.
- run-019 (v1.10.5) is not run as part of the series.
- This replaces two statements in §2 of `preregistration.md`: "Five consecutive runs: run-015 to run-019" and "The pilot run-014 is not counted".

## 2. Basis

- **The human's stated basis.** The instructions of run-014 are the same as those of the evaluation runs. In the human's words: 「run-14が1回目です」, 「指示書は同じですよね？」, and then 「run-014を1回目として数えて、変更を記録してください」.
- **What the management agent checked on 2026-10-27:**
  - `prepare_run.py --version 1.10 --run 014 --check` passes against the frozen files listed in §1 of `preregistration.md`. The filled instructions of run-014 are exactly what the frozen package produces.
  - The filled research and review instructions of run-014 and run-015 differ only in the version number and the run number (`diff`).
  - The copied skills `run-014/input_skills/research-question` and `review-014/input_skills/peer-review` are identical to the workspace's `skills/` (`diff -r`).
  - The models, reasoning efforts, launch settings, time limits and resource limits are the ones listed in §3 and §5 of `preregistration.md`. They were set for the pilot and kept.
  - The Codex CLI version was 0.164.0 for run-014 to run-017.
  - v1.10 was frozen after run-014 without any change.

## 3. Known differences between run-014 and the later runs

- **Freeze decision.** run-014's result was seen before v1.10 was frozen, and the freeze followed that result. Had a defect been found, v1.10 would have been changed and run-014 would not represent the frozen system. No defect was found and nothing was changed.
- **Workspace.** At run-014 the research workspace held no earlier `run-*` or `review-*` directories. From run-015 on, it holds the earlier ones. The instructions forbid reading them.
- **Reviewer's prior expectation.** In review-014 the reviewer saw the abstract before writing its prior expectation. This also happened in review-016.
- **Reviewer software.** The reviewer used Claude Code 2.1.310 for run-014 and run-015, and 2.1.311 for run-016 and run-017.

## 4. Relation to the inclusion rules

- §4 of `preregistration.md` says: "No run is excluded, replaced or repeated after its result has been seen."
- This amendment adds a run whose result had been seen. It also ends the series one run earlier than planned.
- It is reported as a deviation from the pre-registration, together with this record.
- No run already counted is excluded.

## 5. Unchanged

All other parts of `preregistration.md` are unchanged:

- §1, the system under evaluation;
- §3, the models and settings;
- the other inclusion rules in §4;
- §5, no changes during the series;
- §6, what is recorded.
