# free-research-017: wetland training allocation

This directory contains one autonomous research study of how training-point allocation interacts with annual satellite embeddings and seasonal optical predictors when recovering small mapped palustrine wetland patches. It measures agreement with existing inventories. It does not estimate ecological wetland completeness, legal wetland extent, human annotation cost or conservation outcomes.

The main original comparison uses 64 separated cores in four US inventory projects, five training seeds and a 2,000-position fitting budget. Additional decoder, budget, geographic-transfer, information-frame, weighting, split-rotation and reference-alignment checks are distinguished in the versioned protocols. The paper retains the original results and the weaker or negative boundary results.

## Main outputs

- `paper.md`: English research manuscript, generated numerical text/tables, limitations and references.
- `claims.jsonl`: main claims, scope, evidence, expected values and verification links.
- `VERIFY.md`: environment setup and one offline entry point for all numerical results; no API or network needed with the bundle.
- `analysis/`: machine-readable results, frozen numerical expectations and generated tables.
- `figures/`: plots generated from the analysis outputs.
- `final_report.md`: scope, results, remaining limitations, intervention and resource tallies, and end state.
- `review/self-check.md`: author self-assessment and clean-copy rerun outcome; this is not independent reproduction or peer review.
- `review/`: first-draft submission snapshot, later review/response if received, numerical consistency and verification reports.
- `checkpoint.md`: exact current deadline and continuation state.

## Evidence and records

`input_prompt.md` preserves the original start instruction; `input_skills/research-question/` is its unchanged topic-selection skill copy. `manifest.json`, `events.jsonl`, `research_log.md`, `sources.jsonl`, `interventions.jsonl`, `api_calls.jsonl`, `protocol/`, `experiments/` and local Git preserve the conditions, decisions, source passages, failed runs and chronology. The one permitted candidate critique is retained under `api/`; it supplied no experimental labels, code, interpretation or manuscript text. No other AI API experiment or agent was used.

The exact 64-core input list is `data/derived/dataset-manifest.json`. Raw clipped arrays, public source responses, scene metadata and original URLs are bundled under `data/main/cores/`; licences and acquisition/hash provenance are recorded. AEF production v2.1 data are CC BY 4.0: **The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind.** Sentinel inputs contain modified Copernicus Sentinel data (2020). USFWS National Wetlands Inventory is acknowledged; its checked metadata states no access/use constraints. Literature has its own source-specific permissions; do not assume one blanket licence for the directory.

Model fit metadata are in `data/results/fits/`; selected positions, proposal scores and weights are in neighboring folders. New large prediction arrays in `data/results/predictions/` are bundled but excluded from Git for storage. Their exact SHA-256 values are in each fit record and the final output hash list. Previously tracked arrays remain in Git. A Git checkout alone therefore needs the supplementary files described in `VERIFY.md`.

Feature-matrix NPZ files are regenerable caches excluded from Git; raw predictor clips and reference arrays remain available. `verification-work/` is excluded from Git and counts toward the storage limit. Its selected input copy and shared probability links are for the author's self-check. Newly generated verification measurements/logs are retained and covered by the output hashes, while duplicated working-copy inputs and caches are excluded from that hash scope.

## Recompute

Follow `VERIFY.md` on an input copy. The short command is:

```sh
PYTHONDONTWRITEBYTECODE=1 /path/to/verification-env/bin/python /path/to/input-copy/code/verify.py --out /path/to/new-output-directory
```

No API key is required. Optional raw-feature rebuilding/refitting is separate from recomputation of the reported saved-score measurements. The expected results and claims document their scope; matching those values is not a validation of inventory truth or an independent reproduction.

This is a local research bundle. Nothing was published or sent externally. After the first-draft submission tag, the directory is frozen while awaiting the human-supplied `REVIEW-1` message. The planned review is a review by an AI agent, distinct from the author's self-check and from the candidate critique.

## Revised version after review

`review/review-1.md` preserves the human-supplied original review by an AI agent. `review/response-1.md` addresses all six findings. Review-prompted complete sensitivities/transfer replay are in `analysis/review-response/`; original numerical fits/predictions remain unchanged. `submission-1` preserves the first draft; `final` denotes the revised submission. The final procedure regenerates25numeric tables and checks11claims without AI or network calls. The reviewer’s reported same-machine saved-prediction re-run is not an independent reproduction, and we did not inspect or alter the reviewer’s directory.
