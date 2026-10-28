# Main protocol v6: regional operating-point sensitivity

This supplements v1–v5 before any mapping model is fit or scored. The original primary pooled-test-upland 5% FPR operating point remains unchanged.

Potential alternative explanation: the primary recovery score averages four regions equally, whereas its single threshold targets pooled upland pixels. A model can change recovery partly by redistributing false-positive area among regions, even without improving within-region rankings. Reporting regional FPRs alone reveals but does not remove this effect.

Add `regional_0.05`: choose a separate strict, higher-quantile 5% reference-upland threshold within each test region and compute the same macro regional small-patch recovery and H1 interaction. This remains an evaluation-only operating point that uses held-out labels, not a deployable threshold. Compare it with the original pooled operating point without replacing either.

Add `regional_validation_0.05`: choose thresholds separately on each region's validation cores, freeze them, and apply to that region's test cores. For leave-one-region-out fits there is no held-region validation data, so this condition is unavailable rather than borrowing test labels or substituting another region. The original pooled validation replay remains available. Regions with no negative pixels cannot define a threshold and must be reported rather than silently dropped.

Apply these evaluation sensitivities to all available saved fits, including smoothing controls where computed. Use the same 2,000 paired core/seed bootstrap draws and mark intervals conditional on the region-specific operating thresholds and reference maps. This is a pre-performance secondary amendment motivated by the aggregation/threshold definitions, not by an observed result. The primary hypothesis and all training procedures remain unchanged.
