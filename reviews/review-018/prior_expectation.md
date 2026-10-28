# Prior expectation (review-018-1)

Read before writing: only the title and the research-question part of paper.md (Introduction, lines 1–4 and 9–18 at tag submission-1; the paper has no separate "research question" heading, the question is the bold sentence at the end of §1). The abstract and the rest of the paper were not read before saving this file.

## Research question as I understood it
Does adding annual satellite-embedding distance (AlphaEarth Foundations / TESSERA annual vectors) improve the screening of wetland reference/analogue sites, measured as agreement of the NWI water-regime class (temporarily / seasonally / semipermanently flooded) between a target wetland and the screened candidates, beyond matching on public terrain and surface-water covariates, at fixed screening coverage and with NWI vegetation subclass and geographic setting held fixed?

## My expected answer and confidence
- Expected answer: a small positive increment. Embedding distance (which encodes a year of optical + SAR + thermal observations) carries some information about wetness and vegetation phenology that is only partly captured by terrain indices and an optical surface-water frequency product (e.g. JRC Global Surface Water). I expect the same-regime rate among screened candidates to rise by a few percentage points (order 1–5 points) over a covariate-only baseline at the same coverage, with wide intervals once spatial blocking is used, and with heterogeneity across regions. I expect the increment to be larger for the semipermanent vs. temporary contrast (open water/saturation visible) than for temporary vs. seasonal.
- I expect raw (unweighted) embedding distance to be a noisier signal than a learned/weighted combination; a learned model using embeddings could show a clearer gain than a plain distance.
- I expect geographic transfer (training in one region, applying elsewhere) to shrink or remove the gain.
- Confidence: about 55% that a small positive, statistically distinguishable increment is found under the paper's design; about 30% that no increment is detectable (interval includes zero); about 15% that adding embedding distance makes screening worse at fixed coverage (e.g. because it dilutes the covariate match).
- Ceiling/floor caveat I anticipate: NWI regime labels are dated and uncertain (mapped from older imagery), so any measure of agreement is capped well below 100%, and an increment will look small in absolute terms.

## How researchers and practitioners would judge this at present (concretely)
- Remote-sensing researchers: since the 2025 releases (Google's AlphaEarth "Satellite Embedding" dataset in Earth Engine, TESSERA), embeddings are widely promoted for similarity search and as general features; most would expect them to add information over a handful of handcrafted covariates for a land-surface classification task, and few would have a quantified estimate for wetland hydroperiod classes specifically. They also know that hydroperiod under vegetation is hard to see in optical data and that NWI regime labels are noisy.
- Wetland scientists / mitigation practitioners (e.g. US compensatory-mitigation staff, restoration planners): reference sites are chosen by HGM class, landscape position, field reconnaissance and hydrologic monitoring; NWI is used as a screening layer, not as proof of hydroperiod. They would treat any map-based similarity score as a pre-screening aid only, would not change field verification requirements on the basis of an embedding, and would likely be uncertain whether embedding "similarity" reflects hydrology rather than vegetation/land cover.
- Therefore the practically relevant uncertainty is the size of the increment (is it large enough to change how candidate lists are drawn up?), not whether embeddings contain any signal.

Saved by the reviewer; save time recorded in events.jsonl. Not to be rewritten (additions will be marked with time).
