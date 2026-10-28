# Final research report — free-research-014

Revised package after review by an AI agent; full verification complete.

## Study and supported scope

**Screening one-year tree-cover transitions in CONUS with annual satellite embeddings.** The question is whether year-matched references or separate control-plot mean changes improve classification of these CONUS one-year cover transitions over a fixed start-year reference and supervised classifiers. It is a retrospective public-data measurement study. All initial classes are supplied. The original LCMAP dominant-Trees endpoint and the separate Annual NLCD Forest endpoint remain distinct; neither measures ecological restoration success or benefits to users.

## Results and unresolved tests

- All 8 original primary correction contrasts and their changed-case counts are retained. Directions vary; gain uncertainty does not establish equivalence or a population zero effect. The original direct classifier has higher J point estimates in 4/4 main conditions, with different earlier-label resources.
- Scalar magnitude flags no observed original gains under the original fixed partition. The separate Forest sample has a later TESSERA exception. Original Forest threshold comparisons match in 620 rows; the direct classifier has higher J point estimates in 7/8 original Forest conditions. Complete counts and intervals are in claims.jsonl and the paper tables.
- Exploratory initial-only, matched direct-input, coordinate, initial-class and fitting/calibration-partition comparisons identify different associations and input dependencies. They do not establish forecasting, static-context causation, encoder drift, leakage or annotation efficiency. Matched direct-input Forest results reuse already-inspected outcomes; all four input choices remain reported. All original correction contrasts span both signs across the ten fixed earlier-partition assignments, and the original direct TESSERA loss advantage does not hold in every split. AlphaEarth centre-magnitude gain detections also have an isolated nonzero partition, retained in the paper rather than hidden by the original zero count.
- Native co-location reached 113/120 selected point-years, with 49 raw centre matches among 113 valid centres. The fixed paired-native check remains **not_tested**: 1/32 point-years, 0/16 complete pairs. Its empty counts are not stability evidence.
- The saved-data single-date alternative has 20 availability-selected pairs and 5 pairs with any flag change across methods/supports. It retains the other date, fitting, references and calibration as mosaics. Identity counts and the very small gain sample prevent a general robustness conclusion. A saved-history feasibility check found 0/166 co-located cohort plots under its fixed matching rule; complete cohort histories remain unverified.

There are 20 scientific claim entries plus process entries; current claim statuses are {"not_tested": 1, "supported": 21}. These statuses concern the stated observed scopes. No ecological field outcome, independent future-year variance, current-best-encoder comparison, full native refit or human decision outcome was measured.

## Verification

PASS; 256 checks, 37 measured stages, 896.385 seconds; source working files unchanged=True; current numerical code covered=True. Candidate 40fdcf0d9ce3b467abee309def61fd494869d263. Record: review/self-rerun-4.json.

The entry point is scripts/reproduce.py; VERIFY.md gives setup, the single numerical command, per-claim expected checks, measured stage durations, network/API separation and timeline inspection. The quick scripts/audit_saved.py counter checks saved evidence without fitting and is a different check from raw-data recomputation. All selected raw measurements, invalid values, original failures, plans and API-response records are bundled. The source copy and generated outputs under verification-work are excluded from Git and the SHA-256 list, count toward storage, and are not independent reproduction. A separate sealed-submission integrity check uses scripts/hash_outputs.py --check.

## Failures and procedural departures

The process peak was 3 registered experiments, above the permitted 2; the recorded overlap and later launch guard are in manifest.json/protocol/deviations.md. Earlier library HTTP concurrency was not measured. The old additional-control path error lost returned arrays; error rows and the later fixed-sample repair remain. Gateway reporting failures and offline recovery remain. Native paired acquisition was never launched before the fixed acquisition cutoff passed during a confirmed usage stop. No later acquisition replaced missing slots. These are not represented as full resource compliance or recovered old data.

At the record snapshot, 110 experiment processes have run records, with statuses {"completed": 106, "failed": 2, "timeout": 2}. A completed software process can represent an unfinished scientific test, as in the paired-native availability analysis. The maximum recorded elapsed experiment duration is 1800.055269 seconds, including timeout/termination overhead. Every run records its configured limit and exit code. Main scientific results do not use the lost failed arrays.

## Conditions, timing and storage

Start: 2026-10-25T08:12:56+00:00 (UTC). Current first-draft deadline: 2026-10-25T22:05:39+00:00 (UTC). Confirmed usage-limit exclusions total 6763 seconds. Active research-period elapsed time through 2026-10-25T19:18:05Z is 33146 seconds; other waits remain included. The unspecified resumption adds no exclusion. The embedding/native acquisition cutoff stayed fixed at 17:00 UTC; ordinary scholarly prior-work consultation continued for the required self-check.

Allocated directory size at this snapshot: 4145451008 bytes; logical file size: 3952548257 bytes; storage cap: 10737418240 bytes. Excluded environments/caches/working copies still count. Git contained 134 commits through snapshot 7c3f673ce5b4fb87ce3db08f1bd67ad5aa28ebf6; final documentation/sealing commits follow. This is a dated tally, not a claim to include its own future sealing commit.

Root deployment ID, root reasoning settings, session token use, runtime version, normal-tool billing and persistent-memory existence are not directly observable. The conversation presents the authoring session as Codex based on GPT-6/OpenAI; this is distinguished from a confirmed deployment ID. No profile or past sessions were searched for the topic. Session/continuation IDs remain unexposed; preserve this conversation and this directory.

## AI API usage

| Returned model | Purpose | Generation calls |
| --- | --- | --- |
| gpt-6-astra | candidate critique (explicit sole research-decision exception) | 1 |

Returned input tokens: 115237; cached-input tokens: 0; cache-write tokens: 6120; returned output tokens: 14443, including 9680 reasoning tokens. Search-call items: 13. Generation failures in the latest deduplicated ledger: 0. Polling/accounting rows are not additional generations. No other model was called by the author to write code, summarize literature, draft the paper or review it. The human separately supplied the planned review by an AI agent. No author-invoked subagents were used.

Computed actual cost from returned usage and saved official rates: **USD2.01982**, out of the combined research/review budget USD20.00. This is not invoice-verified. The response's legacy cache-retention field lacks a write-lifetime token breakdown; the documented default30-minute write accounting is used, with the caveat retained in manifest.json and api_calls.jsonl. Reasoning output is included once in output-token cost. Price source: https://developers.openai.com/api/docs/pricing, checked 2026-10-25T08:55:14Z, snapshot sources/openai-pricing.md. The sole critic used the copied skill's explicit no-output-limit/pre-call-maximum exception. No further paid AI calls were made. The saved response is sufficient to recompute accounting without an API call.

## Human interventions

After the initial instructions, the recorded intervention count is 4, by type {"peer_review": 1, "runtime_resume": 3}. Permission requests: 0; scientific feedback: 0; paper-review results received: 1.

| ID | Type | Recorded UTC time | Decision |
| --- | --- | --- | --- |
| I001 | runtime_resume | 2026-10-25T12:11:45Z | Resumed; excluded confirmed stop interval |
| I002 | runtime_resume | 2026-10-25T13:09:04Z | Resume; cause unconfirmed, no excluded interval or deadline extension |
| I003 | runtime_resume | 2026-10-25T17:12:29+00:00 | Resume; exclude confirmed measured stop interval |
| I004 | peer_review | 2026-10-25T19:51:35Z | Received; author decides responses based on evidence |

The one other-model topic critique is an authorized planned instrument of topic selection, not human feedback or the later paper review. No external publication, posting or contact was made.

## End state and main outputs

The reason for ending is completion of the primary/Forest analyses and the relevant alternative-explanation and boundary checks, followed by the required self-check and full verification. Data acquisition is closed; the unsuccessful paired-native check remains referable. Saved measurements were checked for alternative recovery routes and used for the limited single-date analysis, without treating it as completed paired validation. The paired-native test is retained unfinished. The first-draft snapshot and submission-1 tag are preserved. The planned review and response are recorded separately; the final tag identifies the revised package after sealing.

- paper.md, claims.jsonl and figures/: scientific report, evidence mapping and generated visuals.
- VERIFY.md, scripts/reproduce.py, requirements-analysis.txt: offline numerical procedure.
- review/self-check.md and review/self-rerun-*.json: author assessment and actual self-rerun records.
- protocol/, experiments/, data/, sources.jsonl, manifest.json, events.jsonl and interventions.jsonl: fixed plans, provenance, raw/results/failure records and interventions.
- SHA256SUMS.txt with HASH_SCOPE.md: final integrity inventory, generated at sealing. review/submission-1/ contains the required first-draft snapshots after sealing.

## Review response tally

Review period: 2026-10-25T19:51:35Z to this snapshot 2026-10-25T20:43:11Z, 3096 seconds elapsed, deadline 2026-10-25T21:51:35Z. No confirmed usage-limit stop has occurred in this period. First-draft-to-review waiting time is excluded from both periods.

The human provided one review by an AI agent. Reviewer-side rerun and settings are reported, not directly observed; same-machine rerunning is not independent reproduction.

Points: 8; decisions: {"adopted": 5, "partly adopted": 3}. Existing claims modified: 9 (C001, C002, C003, C005, C009, C012, C014, C017, C018); added: 2 (C019, C020); status changes: 0; withdrawn: 0. Scientific saved-data experiments added: 1 (review-diagnostics-r1); full author self-reruns added: 1. New AI API calls:0; combined-period API total remains in the usage section above.

The revised paper foregrounds absolute reference discrimination and magnitude ranking, documents year/region concentration and reference variation, adds training-target/production-version qualifications, and moves secondary checks to appendices. Source-access limits and reasons for partial adoption remain explicit. See review/response-1.md and review/review-response-summary.json. The final tag identifies the sealed revision; no further review round is planned. Session IDs remain unknown; preserve this conversation and the directory/Git history.

Final seal prepared at 2026-10-25T20:48:09Z (UTC). The annotated final tag supplies the actual commit and completion time. Required analysis, revision, response and verification are complete within the stated scope; all incomplete/unverified matters remain listed. No processes are running and no further review round is planned.
