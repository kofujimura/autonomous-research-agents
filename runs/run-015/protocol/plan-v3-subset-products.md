# Plan v3: exploratory comparison of reusable products for subset queries

This is a scientific extension of the SAME research question, fixed after the first one-date interim primary summary. It is exploratory, not a replacement for the original primary analysis. Retain v1/v2, their results and their limitations. The methodological idea was logged before the first main width summary, but original per-unit analyses had already run, so that does not make it preregistered. No extension result has been computed at fixation.

## Reason and reader judgment

The critic correctly noted that a count distribution answers every capacity question for a known portfolio. The author then identified two unresolved comparison issues. First, a count distribution for a fixed larger candidate universe is reusable for subset queries, although generally not exact for them. Second, coherent binary member masks are themselves compact and exact for a fixed hazard threshold. Ignoring either comparator would give an incomplete publication-choice analysis.

Evaluate whether a small regional count product or all pairwise counters leave less decision ambiguity for subsequently selected subsets. These information sets are not nested. Do not claim a new probability method, optimal compression scheme, actual bandwidth saving, measured user-query frequency or operational action benefit. If compact exact masks make the remaining product tradeoff unimportant, say so; do not invent a delivery constraint to rescue the claim.

## Data and deterministic query sample

Use only the already scheduled v1 weather fields, same terms and provenance, no new downloads or AI calls. Each original twelve-site portfolio is a fixed candidate universe; each model/lead/date/threshold gives one empirical binary ensemble on that universe. Main matched dates still require all four model/lead units, and all original n=12 results remain primary.

For each candidate universe, evaluate eight four-site and eight eight-site queries. Two per size are structured: n=4 contiguous [0,1,4,5] and dispersed [0,3,8,11]; n=8 contiguous [0,1,2,3,4,5,6,7] and dispersed [0,1,2,3,8,9,10,11]. Draw six further unique subsets per size uniformly without replacement using NumPy default_rng(seed+n), seed=20261026; reject duplicate subsets and the structured ones. Freeze the resulting indices in `subset-design-v3.json` before execution, use the SAME indices across dates, models, geometries and thresholds. These are designed queries, not sampled actual user demand. Capacity k is one quarter, one half and three quarters of query size, as in v1. The parent universe has twelve sites regardless of query size.

## Information conditions and exact references

- **Marginals:** all twelve site probabilities. For the subset event, outside-site marginals alone impose no additional restrictions; compute the sharp subset marginal bounds.
- **All universe pairs:** all twelve marginals and all sixty-six pair co-exceedance probabilities in the parent universe. Apply the queried-subset event objective to the complete parent-universe LP. Thus, unlike v1's smaller-n sensitivity, this uses information involving sites outside the query.
- **Universe count distribution plus marginals:** all twelve marginals plus the complete PMF of total exceedance count over the twelve-site parent universe. Constrain state masses by each total-count bin probability. Apply the SAME queried-subset event objective. Zero-probability bins may be removed exactly, as zero pair cells can in the pair LP.
- **Query-restricted pairs:** marginals/pairs among only the queried sites, as a diagnostic comparison with ignoring the rest of an available universe product. All-universe pair bounds must lie within these bounds; nesting is a code check, not a discovery.
- **Query-specific count distribution:** exact tail probabilities of the queried subset, the compact query-specific reference from v1.
- **Coherent binary ensemble:** pack the fifty-by-twelve binary array into bits, unpack and require exact equality; every subset-tail query must then agree with the input ensemble. Its exactness is mathematical and round-trip correctness is a code check, not an empirical scientific finding.

Keep arbitrary real joint-law masses as in v1; do not silently impose fifty-member integrality. Existing v1 integer sensitivity describes that distinction; a new integer analysis of all subset queries is not required.

## Analytic format counts and limits

For fixed member count M and universe size n, an exact nonnegative counter in 0..M needs ceil(log2(M+1)) bits in a simple fixed-width encoding. Report the bit/byte budgets of n marginal counters, n+n(n-1)/2 site/pair counters, n+n site-plus-count counters (omit one normalization-redundant PMF bin), and M*n coherent binary indicators. Verify counter and mask round trips. Headers, index identities, time/threshold metadata and general-purpose compression are excluded for all conditions. The count mean is also redundant with marginals; this simple encoding does not exploit that relation. These are analytic representation budgets, NOT measured transmission or a proof of optimal coding. Query-specific counts and a single tail counter have different query scope and must be labeled accordingly. All products are tied to a fixed hazard threshold and parent site universe; arbitrary thresholds, new sites, time sequences and weighted demands are untested.

## Exploratory endpoints, exclusions and uncertainty

Per query/capacity, record interval endpoints/widths for every information condition, original q, exact mask/count references, query and complement uncertain-site counts, number of nonzero total-count bins, geometry, system, lead and subset type. Save the difference W_count - W_pair. Report which interval is narrower by more than 1e-7, equal-width counts, interval nesting counts (distinct from global information-set dominance), numerical identification counts and maximum containment violations.

Report all cases and an informative stratum: at least four query sites uncertain, at least two complement sites uncertain, and 0.1<=q<=0.9. In particular, when the complement count is deterministic, the universe total-count PMF exactly determines the query count PMF by a shift; count this analytically explained condition separately rather than presenting it as an empirical advantage. Also report all query sites deterministic, <=2 query sites uncertain, q=0/1, and whether total count is deterministic. Do not discard these from the all-case table. Report counts in the abstract if they materially explain a main comparison.

For c=0.1,0.25,0.5, compare certification of a weakly optimal action using v1's rule/tolerance, overall and within abs(q-c)<=0.1; include informative near-boundary strata and tie/floor counts. Compare systems, leads, geometries and structured/random queries descriptively, without rankings of regions or causal explanations of system differences. Use the same date-level circular moving-block bootstrap, length three scheduled slots, 2000 replications, seed20261026; no site/member/query independence assumption or p-values.

No post-result query selection, statistical stopping or replacing failures. Complete all fixed queries for available matched dates; if compute prevents completion, preserve the uncompleted scope and report it. Execute in bounded per-forecast or date batches under `scripts/run.py`, max two experiment workers, each <=1800 seconds. Reuse parent LP matrices across subset objectives; this is computational reuse, not a change to information. Fix code before execution, validate simple constructions where each product is stronger in turn, and keep numerical primal/dual and original-q containment checks. Stop new long work with <60 minutes left; main reproduction and writing take priority.

The paper must label this comparison exploratory, including in the abstract if it changes interpretation. An exact coherent-mask baseline limits any claim favoring lossy pair summaries. User studies, realized health effects, true weather probabilities, calibrated forecast skill, actual network traffic and provider adoption remain unmeasured.
