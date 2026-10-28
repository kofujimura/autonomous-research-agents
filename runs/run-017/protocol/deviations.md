# Deviations and implementation decisions

- E0031 (observed time in events.jsonl, before main predictor retrieval/model outcomes): region-specific random streams derive from the protocol's base seeds by adding the public project object ID. This makes each region's order independently reproducible; exact derivation is in core-selection.json. This clarifies the stream construction, with no data-dependent choice of seed, metric, hypothesis or exclusion. The original v1 plan is unchanged.

No model-result-dependent scientific deviation has occurred yet. Failed source retrievals and pilots are preserved separately and are not silently substituted as main evidence.

- E0043 (time in events.jsonl): E02/E03 exposed south-up AEF COGs (positive northing step per row). The downloader now reads exact aligned native cells and flips row order to the common north-up grid, with no interpolation. This is a technical coordinate fix before any model comparison; original failure logs are retained.

- Protocol v2 (time/event in events.jsonl): pre-model radiometric interpretation follows the provider harmonization flag instead of blindly applying inconsistent asset offsets; geometry/missingness/frame assumptions are made explicit. All v1 primary tests unchanged. An extra ≥90% patch-validity sensitivity is specified before any performance result; it does not alter primary eligibility.
