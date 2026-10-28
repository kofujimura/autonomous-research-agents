# free-research-018

Autonomous research on whether annual satellite embedding distances add to
hydrological matching of wetland references at a fixed screening budget.
The endpoint is exact published NWI water-regime agreement. Field hydroperiod,
functional equivalence, restoration outcomes and user benefit were not tested.

Submission status is given by the local Git tags and conversation record.
`submission-1` identifies the first draft for review; after its announcement,
the directory is frozen until the human supplies REVIEW-1. The broader
geographic-frame replication remains unexecuted, as detailed in the report.

- `paper.md`: generated English paper, when available; `paper-template.md`
  contains the author-written source prose.
- `claims.jsonl`: main claims, evidence, scope and expected verification values.
- `VERIFY.md`: offline regeneration procedure and optional model refits.
- `manifest.json`: resources, environment, provenance, deadlines and canonical
  corrected-analysis paths.
- `protocol/`: original plan, preserved amendments, candidate selection and
  deviations; `input_skills/` is the unchanged topic-selection skill.
- `data/main/`, `data/polygon/`, `data/corrections/`: raw numerical inputs,
  deterministic geometry samples and preserved measurement corrections.
- `analysis/`: saved decisions, metrics, negative controls, source checks and
  generated report data; `figures/` contains exportable PNG/PDF/SVG figures.
- `experiments/`: bounded commands, source hashes, outputs, timing and failures.
- `sources.jsonl`, `references.md`, `DATA_TERMS.md`: passage checks, citations,
  public-data reuse and required attributions.
- `events.jsonl`, `research_log.md`, `interventions.jsonl`, `api_calls.jsonl`:
  chronological records, human interventions and the one authorized critique.
- `review/`: author self-check, frozen submitted snapshots and later review
  response. No review by another AI agent has occurred until explicitly logged.
- `final_report.md`, `checkpoint.md`: completion/usage report and resume state.

Recompute on an immutable copy using the single entry point in `VERIFY.md`.
The pipeline reads archived inputs and makes no network or AI calls. The
dedicated environment and caches are excluded from Git; exact package versions
are recorded. No global installation is required.

The AlphaEarth Foundations Satellite Embedding dataset is produced by Google
and Google DeepMind (CC BY4.0). Surface-water attribution: Source: EC JRC/Google.
FWS/NWI, USGS3DEP, ASF HAND and TESSERA reuse details are in `DATA_TERMS.md`.
TESSERA's public licence statements conflict; attribution and conservative
share-alike treatment are retained. No external publication is authorized or
performed by this study. Census statistical-frame files were acquired for an
exploratory panel; execution status is recorded separately from planned work.


The final review revision is documented in `review/review-1.md`, `review/response-1.md` and `review/response-decisions.json`. The original first draft is preserved at tag `submission-1`; the final version uses tag `final` once present. Review-response results and the fixed additional seed fits are under `analysis/review-reanalysis-v2/` and `analysis/review-seeds/`. The single offline verification entry point regenerates these new tables as well as the manuscript and claims. The review is by an AI agent on the same machine, not independent reproduction. Public literature copies may contain incidental author contact details; these are not research subjects and are not analysed or republished in the paper.

Final state: the revised fixed-panel study and single review response are complete. The post-review fresh-copy author verification passed 108checks, including exact paper/claims regeneration and four matching primary refits. See `analysis/verification-review-primary.json` and `analysis/verification-status.json` for source commits/scopes. All experiment groups have ended. Final frozen content is selected by tag `final`; final commit receipts may append to the local working event log outside the hashed tag snapshot, as declared in `review/final-preparation.json`. Session IDs were not exposed; preserve the conversation and local Git history.
