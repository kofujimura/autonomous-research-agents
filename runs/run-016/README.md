# free-research-016

This study asks whether revisiting reference locations improves estimation and directional reporting of changes in declared crop-group diversity when annual satellite embeddings supply auxiliary predictions. It uses probability samples on public SwissCrop25 declarations; it is not a field experiment or a national estimate.

Current state: reviewed final revision prepared. One AI-agent review was received; all nine points have a recorded disposition in review/response-1.md. Original first draft: tag submission-1. Reviewed version: tag final. The reviewed-final full self-rerun passed in 795.986s: 88 main and 102 supplemental CSV files, 1530 main and 3382 supplemental raw-array files, and exact paper.md/claims.jsonl matches. Source commit fd7bed21eb31d92677fae1e55fd174e4900ca819; original result review/verification-final.json; snapshot review/snapshot-final.json. This is a rerun by this session, not independent reproduction. The first-draft verification remains unchanged in review/verification-submission-1.json.

## Read and reproduce

- [paper.md](paper.md): English manuscript generated from saved outputs and manuscript/template.md.
- [claims.jsonl](claims.jsonl): principal claims, evidence, scope, verification and expected values.
- [VERIFY.md](VERIFY.md): single offline entry point, environment, chronology and optional retrieval/refitting.
- [review/self-check.md](review/self-check.md): this session's completed pre-submission self-assessment.
- [review/verification-preliminary-1.json](review/verification-preliminary-1.json): passed preliminary check of the commit identified in review/snapshot-preliminary-1.json; explicitly not the final submission check.
- [review/verification-submission-1.json](review/verification-submission-1.json): passed final full self-rerun.
- [final_report.md](final_report.md): results, failures, resource/intervention tallies and remaining limitations.
- SHA256SUMS.json: scoped inventory including raw files excluded from Git; exclusions and terminal receipts are explicit.

The full offline command is `python -B scripts/verify.py --all --output /ABSOLUTE/FRESH/OUTPUT`, on a copy outside the original research directory. It needs no AI API key or network after environment setup. Scientific numerical inputs are bundled in Git. Large source catalogues and compressed-label range caches are optional for this command.

## Scientific artifacts

| Location | Content |
| --- | --- |
| data/population-source-v1.json | Frozen 2021 training/calibration frame |
| data/population-main-v1.json | Main test frame shared across representations |
| data/population-census-v1.json | Three prospectively selected native-grid cases |
| data/landscapes/, features/, census/ | Numerical references and embeddings; provenance in manifests and ledgers |
| results/source-models/ | Initial source fits, including convergence warnings |
| results/source-models-v2/ | Revised converged heads fixed before target outcomes |
| results/models/, inference/ | Saved predictions and raw Monte Carlo outputs |
| results/tables/main/, fine/, forest-*/, secondary-*/ | Original and prespecified robustness tables/figures |
| results/census-inference/, census-comparison/, registration/ | Native-grid, first-phase and offset checks |
| results/reference-frames/, stable-arable/, scope-baselines/ | Exploratory complete-reference frames and point baselines |
| results/sparse/, jackknife/, stratified/, power/ | Exploratory uncertainty, sampling and weighting checks |
| results/gradient/, coherent-panel/ | Numerical-floor sensitivity and coherent annual panels |
| data/validation-cohort-v1.json, results/additional-geography*/ | Separate exploratory geography, original points and full/arable references |
| results/additional-arable-high-replication/, covariance-context/ | Higher-precision simulation and known-population influence context |
| results/projection-derivative/, validation-projection-derivative/ | Original and local-derivative intervals, saved controls and local numerical validation |
| results/reference-sensitivity/, description-main/, description-final/ | Hypothetical reference errors and model/cohort context |

Direct outputs shared across representations are counted once. Monte Carlo standard errors describe this fixed benchmark, not representative Swiss population uncertainty. A no-change point baseline is not an interval or evidence of no change. Agricultural and arable supports have different estimands.

## Records and terms

Original instructions are in input_prompt.md; required skill files are copied unchanged in input_skills/. Protocol versions distinguish prospective and exploratory choices. Each bounded experiment has commands, plan/code references, input hashes, times and stdout/stderr under experiments/. events.jsonl and research_log.md index the process; they are not independent immutable audit logs. Local Git history is retained without rewriting.

Sources and the range actually checked are in sources.jsonl. [DATA_LICENSES.md](DATA_LICENSES.md) gives required attribution, including TESSERA's unspecified CC-BY-SA version. SwissCrop25 and the public AlphaEarth mirror state CC BY 4.0. The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. No farm or household identities are linked or analysed, and no organizational ranking is claimed.

One required topic critique used an AI API. Its request, response, usage, price documentation and cost correction are retained; no other AI performed research work. Numerical verification never calls an AI API.

verification-work/ is excluded from Git. Self-rerun copies share immutable inputs only after checking committed blob hashes. Recomputed arrays were compared before any duplicate-container sharing; review/deduplication-preliminary-1.json records the operation. Every scientific array remains accessible. This storage optimization and the rerun are not independent reproduction. Both logical path bytes and unique-inode payload bytes are recorded; all unique payload is inside the research directory and counts toward the storage limit.

The scoped SHA inventory includes all retained scientific raw data, including duplicate self-rerun paths omitted from Git. Only Git internals, dependency environments/caches, bytecode and the current inventory are excluded. Later mirror/check/commit receipts are outside the inventory. events.jsonl uses an explicit byte-prefix hash so terminal commit IDs can be appended without claiming a self-referential whole-file hash.

Post-review additions: results/review-label-error/ (synthetic sampled-label scenarios), results/review-summaries/ (landscape composition ranges, conditional direction errors, effective-number errors and longer contrast), protocol/plan-v15-review-response.md, review/review-1.md, review/response-1.md and review/response-summary.json. All are included in offline verification.

Reviewed-final verification: [review/verification-final.json](review/verification-final.json). The intermediate post-review check remains separate. Exact byte-identical scientific CSV/JSONL/JSON and unchanged files between frozen self-rerun source copies share storage only after full-file hashes match; every path/value remains. See review/exact-csv-storage-sharing.json and review/snapshot-text-storage-final.json.
