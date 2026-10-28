# Review-response plan v14

Fixed at 2026-10-26T12:58:32Z. Added after REVIEW-1; all additions below are labelled as such. Preserve submission-1 and its source/results unchanged. No new weather acquisition, model/API call, human experiment, changed primary exclusion, cohort, bound, bootstrap or law class.

Report existing prespecified results more fully: all-query, near-boundary and informative-near-boundary certification from decision-summary.csv; geometry×lead×product widths, narrowing share and identified counts from width-summary.csv; member-size widths and their own denominators from sensitivity/member-summary.csv. Generate every manuscript number from those outputs.

Add a small exploratory saved-data diagnostic requested in R1-1: in matched n12 informative primary rows, bin pair_possible_states as ≤10,11–50,51–100,101–500,>500. Report N, identified count/fraction and mean pair width; report median observed_patterns. These bins are fixed now, after review and before aggregation, not prespecified primary metrics. They describe association, not a causal decomposition of finite support versus spatial dependence, and do not test M>50 or a population/smoothed law.

For R1-2, check the interpretation of near-threshold non-certification using the existing n12 matched cases: at c0.1/0.25/0.5, for all/near-boundary/informative-near-boundary rows, count marginal width>0.2, marginal certification and their intersection. Width alone does not logically determine whether c lies inside the interval. Record this as an exploratory interpretation check; no new decision rule or selection.

One local report script writes review-response aggregates/tables/summary from these saved files. Use the standard runner, timeout≤1800seconds and two-worker limit. Stop after all fixed rows/bins are processed; no adaptive resampling, new optimization or API repetitions. Independent re-solving of the original LPs is not required for these reporting additions. Integrate the report script into offline verification so all new summaries/tables are regenerated from saved values.

Read relevant full passages of suggested primary literature where publicly accessible; label abstract/bibliographic-only items explicitly. Cite full scientific support only where relevant full text has been checked. Do not infer novelty/absence from unsuccessful searches or read reviewer files outside the research directory. Clarify how first/two-binomial-moment bounds differ from retaining every marginal plus the aggregate.

Revise abstract/discussion/glossary and generated typography; state finite-M50/exact-moment scope and two-spacing heterogeneity. Do not claim the member-size association identifies a causal mechanism or guarantees monotonicity for larger M. Add an append-only D002 disambiguation note, leaving original failed records intact.

Before final submission, rerun the updated offline entry point in a fresh copied commit with a separate output,1800second cap; compare source hashes before/after. Preserve the initial submission's verification report separately. Update claims/response point decisions and tool-counted tallies, revision history, checksums and local final tag. Reserve the last30minutes for verification/documentation/sealing; response deadline14:54:07UTC unless a confirmed usage-limit stop extends it.
