# Exploratory repeated nested member selections

The original member sensitivity used one seeded nested subset per forecast.
The later common-query control preserved its direction, but cannot show how
dependent that result is on one member selection. This additional check uses
only saved original M50 arrays and the unchanged frozen120query sensitivity
cohort. It is planned after those earlier member results were seen.

Use100 draws. Within each draw and each date/product/lead, obtain one permutation
of the50 original member indices from NumPy default_rng, seeded by the first
eight bytes of SHA256 of `20261027|draw|date|model|lead` interpreted big-endian.
Take its first10 and first25 indices, preserving nesting and sharing the same
selected members across every query for that forecast. Every draw is sampled
without replacement from the original finite ensemble. Save the seed digest
and selected member identifiers. Keep all draws, including zero/one tails.

Recompute the unchanged marginal/aggregate/pair intervals and q for each selected
query, including its original capacity trigger. Reuse the saved M50 endpoints
as the fixed reference. Report per-draw means and identified fractions on
(a) all120fixed query identities and (b) the queries informative at both M10
and M25, retaining the original M50 informative criterion. Include denominators,
floor/ceiling counts, ≤2-uncertain counts and the common-set size. Summarize
per-draw results with mean and2.5/97.5percentiles and count how often mean pair
width is below the M50 reference on the same identities.

These percentiles describe conditional member-draw variation in this fixed
finite dataset. They are not confidence intervals for weather probabilities,
population forecast laws or the geographic sample. Member size changes the
empirical law; this is not a causal size effect at a fixed law. Shared forecasts
and overlapping queries are not independent observations. This is an exploratory
check of selection sensitivity, not independent confirmation or calibration.

Run in five disjoint20draw chunks, each with the existing1800second timeout and
two-worker limit. Stop after100draws, with no adaptive sample-size change. If
time prevents completion, report the actual draws and mark the plan incomplete.
Retain raw case outputs and selections. Offline verification re-solves one fixed
draw (draw0), checks all saved selections against the stated generator, and
recomputes every reported aggregate from all saved draws; full re-solves remain
available in bounded chunks and are separate from the reduced verification.

Fixed at 2026-10-26T06:16:43Z. Execution remains pending; prioritize completion of fixed city/time sample and existing full replay.
