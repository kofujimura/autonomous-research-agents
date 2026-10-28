# Exploratory screening-budget allocation sensitivity

Fixed after inspecting primary own-screen, fixed-query and window-influence
results, before computing these allocation policies. The primary rounding rule
and all original outcomes remain unchanged. This deepens the same screening
question; no new model fitting, endpoint, site selection or field claim.

Use eight fixed corrected conditions when complete: original forest and boosted
trees, original whitened-distance boosted trees/all-feature forest, and the
polygon averaged-physical condition under original forest/boosted trees and
whitened-distance boosted trees/all-feature forest. Use all methods archived
within each condition. Do not select conditions based on these new outcomes.

At the same20/50/80/100% nominal coverages, compute two acceptance policies:

1. Window budget: set K=floor(coverage*N) for all nonempty queries in a window.
   Allocate K across its four rotations proportionally to nonempty query counts
   using the largest-remainder method. Rank confidence only within each rotation,
   avoiding comparisons between separately fitted models' score scales.
2. Vegetation allocation: preserve the original K=floor(coverage*N) in each
   window/rotation, then allocate K proportionally across known vegetation
   subclasses using the same largest-remainder method. Rank confidence within
   each resulting vegetation stratum. This is a coverage policy, not a normative
   claim of fairness or an acceptance rule using withheld regime labels.

For integer K and stratum counts n_i, use floors of K*n_i/sum(n_i); allocate
the remaining slots in decreasing integer remainder order. Break exact
remainder ties by SHA256(trial,policy,window,rotation if applicable,coverage,
stratum). Reference selection and confidence ties retain original OID rules.
Check that method query sets and stratum counts agree before assigning budgets.

Report each policy's realized coverage, window/pooled mismatch, per-window
counts and paired augmentation-versus-physical differences using the existing
10000-window bootstrap/seed18018. Save all half-coverage accepted query IDs and
vegetation-specific coverage. No resampling p-value, revised primary estimate
or prospective ecological benefit is inferred. Include every completed fixed
condition and preserve any uncompleted one explicitly. Run locally in a free
bounded slot; no network or AI calls. Recompute in offline verification.
