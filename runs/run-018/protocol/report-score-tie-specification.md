# Score ambiguity reporting

The original plan and saved predictions include exact best-score ties and score
ranges. This aggregation is fixed now, after outcome inspection and before
computing its counts, and is treated conservatively as exploratory reporting.

For each corrected primary method count all nonempty queries, multiple-best-
reference ties, constant-score pools with more than one candidate, and the
subset of those constant pools that is nontrivial matchable. Constant means
the saved candidate_score_range is exactly zero; no tolerance is selected.

At original half coverage, sort each window/rotation by saved confidence then
query OID. Count zero-budget groups and groups where accepted and rejected
queries share exactly the cutoff confidence. Count all queries in such a
boundary tie, and the accepted queries resolved by OID within it. These are
CSV-score diagnostics under the published parser and tie policy, not evidence
of field equivalence or an alternative screening rule. Preserve denominators.
Compute with bounded report generation and repeat in offline verification.

Pre-computation scope extension: apply the same definitions to every completed empirical condition during the final pool/influence regeneration. Explicitly flag unavailable legacy fields rather than inventing zero counts. No tie counts have yet been inspected.
