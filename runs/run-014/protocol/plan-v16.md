# Technical scheduling amendment v16 — 2026-10-25T14:14:27Z

After the v15 documented gateway/raw-equivalence check, completed TESSERA control batches2 and3 took160.702325 and152.445430seconds for64 and58 saved tasks respectively. Preserve these actual measurements; no causal transport-speed inference is made.

Restore the v3 maximum of four consecutive64-task source batches per TESSERA job for the still-fixed NLCD queue. The v9 reduction to one batch was a timing response to the earlier slow route; current measured durations provide ample planning margin under the unchanged1800second process timeout for up to256 serial patch queries. Keep request concurrency2, one TESSERA experiment at once, at most2 experiment processes overall, the same hash task order, source/version, retries and immediate saves. Reuse saved files. If a grouped job times out, preserve it and resume only its remaining fixed tasks; reduce group size if observed timing deteriorates.

Queue source batches0–3,4–7,8–11,12–15,16–19,20–21 at data/nlcd/prepared/tasks.csv. Do not replace points, prioritize by scientific results, extend the17:00UTC cutoff or change a trial resource limit. Near the cutoff decrease group size or formally stop rather than starting a job unlikely to finish. This amendment changes scheduling only and uses no new paid API or AI model.
