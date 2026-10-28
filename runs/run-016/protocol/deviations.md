# Deviations and prospective clarifications — maintained during the study

The original topic decision and v1 plan remain unmodified. Times and commit links are in events.jsonl and the corresponding experiment records. This list distinguishes changes from implementation failures; it does not treat an unperformed stage as complete.

## Before classifier and diversity-change outcomes

- **Plan v2:** removed unnecessary future-feature requirements from source training/calibration. Both representations need valid 2021 source features only; test populations require all five years. Five-year reference agricultural support remains fixed for all splits. This correction prevents source selection using future feature availability. The first successful training landscape had already been read for all five years; those inputs are retained. No fitted classifier or change/audit result preceded the revision.
- **Prospective supplement v3:** added at most three native-pixel population checks, selected by original order, baseline arable/grassland category and static geometry. It addresses the scope of conditioning on 4,096 sampled points and documents a first-phase reference variance diagnostic. It does not change main selection or replace main results.
- **Prospective supplement v4:** added a fixed interior subset and 10 m prediction-offset stress tests on exactly those native-grid cases, without new data or refitting. This checks a reference-registration assumption and is a small-case sensitivity analysis with a changed interior estimand.
- **Implementation notes:** resolved raw fractional bands, original LNF-to-published hierarchy mapping, unknown/background competition and tile coordinates. An initial assertion incorrectly rejected negative unmapped residual/background fractions; subsequent failures involved metadata-key parsing and a cell-center assertion. All failures were retained and corrected before any accepted landscape. Mapped crop fractions are not clipped, and overlap diagnostics are retained. A second Zarr decoding path exactly matched the manual decoder; this was a self-check, not independent reproduction.
- **Numerical parameters fixed prospectively:** source-quantifier regularizer 10^-6, SLSQP maximum 1,000 iterations and tolerance 10^-12; gradient floor 10^-6; numerical direction comparison 10^-10; simplex cleanup 10^-12. Additional floor/ceiling, constant-prediction, absent-class and rare-class diagnostics do not exclude units or choose the model. The source-only frozen logistic heads may be fitted while test feature reads continue, with unchanged coefficients/masks and a bitwise source-prediction reconstruction check.
- **Retrieval checks:** direct native COG and public S3 readers matched sampled oriented VRT data but showed no useful speed gain in the observed reads. The primary adapter remains the published VRT. These were data-access implementation checks, not general service-performance experiments.
- **API accounting correction:** added the provider-reported cache-write premium after inspecting the official default retention tariff. The original ledger estimate and correction remain. This did not create another model call.
- **Event identifier correction:** two parallel job starts were both assigned E0103 before locking was introduced. E0104 identifies both originals by time/path. New appends/event allocation use locks and job starts are sequential.

## After outcomes

The following additions retain all original results; every outcome that depends on them is exploratory.

- **V6**, fixed2026-10-26T18:52:36Z, E0171: after two diagnostic target units, added sparse-change diagnostics, exact hypergeometric bounds, jackknife and prediction-stratified sampling. **V6a**, fixed19:02:48Z, E0173, corrected the finite-population jackknife bias scaling before its first run; ordinary jackknife remains a comparison.
- **V7**, fixed19:26:49Z, E0191: added reference-only comparisons on the original unmasked points and complete stable-agricultural grids for all30 fixed test landscapes. This checks dependence on the main feature mask and sampled finite population. Context summaries use the already selected0.01 threshold (E0205).
- **V8**, fixed20:00:59Z, E0204: added bounded same-sample and crossfitted prediction weights at n128 after two diagnostic units and the reference-only full-grid results, before complete main model-assisted results. **V8a**, fixed20:05:47Z, E0208, changed the synthetic noncensus validation fixture from a degenerate six-point setup to seven points; it did not change the benchmark estimator or discard a scientific result.
- **V9**, committed13ce8f5 at the recorded Git/event time after the complete broad n128 summaries: added hard-label auxiliary predictions to check dependence on dense soft predictions. Both representations, all cases and original samples/budgets remain. This was motivated by very frequent projection and conservative soft-prediction intervals; it is not a prospectively selected primary method.
- A suspected reference-context inconsistency was my misreading of a CSV row. Raw counts, the original summary and an exact rerun agreed. No numerical output was changed; correctionE0228 and the extra verification artifacts are retained.

## Unperformed or unfinished checks

Main four logistic conditions and the three native-grid cases are complete (E14/E16). Reference-only full-grid checks and sparse-change diagnostics are complete. Remaining registration, forest/refreshed, other exploratory comparisons and end-to-end verification must be reported according to their actual final status, not treated as complete by this list.

## Source optimization before target outcomes

Plan v5 increases the logistic maximum from 1,000 to 10,000 after three of four source fits reached the original limit. Same source data, C=1, tolerance and optimizer; all initial coefficients/diagnostics retained. No test classification/diversity/audit outcome was used. Revised outputs are separate and must not erase the original warnings.

## After two actual-target diagnostic units

V6 adds exploratory sparse-change diagnostics, an exact hypergeometric entropy envelope/zero-change guard, a delete-one jackknife at n=128, and prediction-based stratified audits. Motivated by low paired-direct interval coverage on two small-change units; original metrics/cohort/models retained. A short unwrapped diagnostic overlapped two acquisition jobs (tool-reported0.7seconds), briefly exceeding the two-experiment limit. The retrospective raw record is preserved and all further statistical calculations use runner slots.

## Resource and record events

- Resource-limit deviation E0170 was recorded retrospectively18:52:36Z, based on the tool-observed0.7-second diagnostic reported18:48:41Z. It briefly made three concurrent experiment processes and had no configured runner timeout. The process exited normally; the record does not pretend the limit was enforced. Limits remain unchanged.
- Confirmed usage-limit stop20:49:18Z–21:12:10Z excluded1372seconds under the original trial rule. E0245 and interventionI0001 record the user's confirmation, computed adjustment and the native-grid job that completed during the stop. The research deadline is2026-10-27T02:58:01Z; this is not discretionary extra time.
- Exact-value precommit secret scanning was accelerated with fixed-string ripgrep, feeding the key only over stdin and suppressing matching contents. Hidden, ignored and binary files remain included; unreadable/error status stops a commit (E0264). No key value is saved or displayed.

## Manuscript-render code provenance

A paper-formatting run E32-manuscript-render-2 started before its asynchronous code commit finished. Its original recorded code revision is retained; the actual renderer is recoverable from874527d. This is recorded as a post-run code snapshot, not a precommit. Main inference outputs are unchanged. The formatting step is rerun from committed code; scripts/run.py now rejects uncommitted script/plan changes and records script SHA-256 values. See the correction event for tool-observed time.

## Completed late checks and second resume

- V10 stable-arable reference frame, v11 coherent panels and v12 numerical-floor checks are complete; the earlier unfinished list is a historical checkpoint, not the final status. Prespecified forest, registration, finer hierarchy and secondary-year checks are also complete.
- All160 later training-feature extracts were obtained; E36 freezes a separate refreshed manifest. E37/E38 completed both refreshed broad logistic fits/inference. They require roughly a full source training sample per later year and are not budget-matched to small audits. E43 verifies identical2021coefficient arrays and matching source calibration, without selecting a new performance metric.
- V13, fixed before additional-label retrieval, targets up to10separate unused test supercells with reference-only analysis; selection cannot use diversity-change outcomes. Actual attained scope remains pending until the separate cohort is frozen.
- Second human-confirmed usage-limit resume observed2026-10-26T23:36:53Z. Latest recoverable preceding tool-recorded time23:33:29.913138Z gives203.086862seconds and extends the deadline to2026-10-27T03:01:24.086862Z. The final preceding standalone clock output is unavailable after compaction, so the interval may include unobserved tool-processing seconds; exact duration is not claimed. No experiment remained active then. Original ledger entries are retained; manifest.json records this uncertainty.

## Final related extensions (recorded 2026-10-27T00:23:04.685958Z)

- V13 attained eight additional landscapes in distinct unused test supercells; acquisition stopped at its128MiBrange-cache growth cap, retaining all nine ineligible and one resource-stopped failed candidate. The cohort was committed before E42inference. The original main population is unchanged. Six additional cases met the stable-arable rule.
- V13a adds post-result covariance summaries after the broad stable-arable MSE reversal was observed; every frame/taxonomy is retained and the linearized proxy is not called exact entropy variance.
- V13b increases Monte Carlo precision to5000replications on all six additional stable-arable cases, preserving both taxonomies/all budgets and the original500results. To bound storage, only new synthetic index containers are omitted; deterministic generation specifications and index-array SHA-256 values, plus every estimate/SE/direction array, are saved.
- V14 adds the established local derivative through projection after the original floor sensitivity, and V14a extends the same rule to every saved broad forest/refreshed control. Both interval rules' raw outputs remain. Original point estimates and uncertainty results are not overwritten. Gradient finite-difference validation and a deliberately nonregular zero-category fixture are separate from coverage evidence.
- E54manuscript rendering failed because a helper argument named frame collided with a table column filter of the same name. E54bfrom committed corrected code succeeded. This changed no experimental result.
- Final verification adds a callback that compares each newly computed reference-frame NPZ before any exact-array storage sharing, rather than accumulating every duplicate draw file first. Default numerical execution is unchanged; the final full rerun must confirm original500CSVschemas/values and every saved raw array. No samples/computations are reduced. Allocated filesystem blocks are also checked with du, in addition to unique-inode payload; the earlier Git packing peak remains unmeasured.


## Post-review additions (recorded 2026-10-27T03:25:44.331315Z)

REVIEW-1 received at2026-10-27T02:50:07Z; review-response deadline2026-10-27T04:50:07Z. Planv15 was fixed and committed before E56/E57. Both added analyses are exploratory: synthetic independent/temporally coupled sampled-label errors, and whole-landscape composition resampling with decision-relevant saved-data summaries. Original outputs, plans and tag submission-1 are unchanged. Preplanned grassland/arable subsets and2022→2025contrasts are newly tabulated, not newly defined. Actual transformed effective-number errors are exploratory. No new AI/API, data subject or paid resource.

Interpretations changed: repeatability of labels conditions both gain and coverage; the original assisted interval rule omitted the projection derivative; additional six-landscape broad/fine ratio ranges include1. Reviewer’s all-budget no-change wording is restricted to direct sampling because original paired forests beat that baseline at512. Four inaccessible classic references remain bibliographic-only, never supporting citations. Completed self-rerun CSVs may share exact byte-identical storage after SHA-256 checks; no path or scientific value was removed. See review/response-1.md and review/exact-csv-storage-sharing.json.
