# Exploratory interaction between known ensemble size and moment precision

The prespecified integer and moment-perturbation checks were separate. A later
self-check identifies their interaction: for exactly50equallyweighted rows,
each individual and pair probability lies on a0.02lattice. A radius0.005 around
the exact observed moments admits no changed count. Therefore its integer
feasible set equals the original exact-count feasible set. This is a structural
fact for all120frozen cases, not an experimental discovery or an inference about
arbitrarily rounded off-lattice reported values.

Use the unchanged frozen120case cohort. Reuse its saved optimal exact-pair M50
integer endpoints for the radius0.005 condition and verify integer bound
rounding gives exactly the original counts. For radius0.02, actually solve new
M50integer lower/upper tail problems, allowing every individual and pair count
to change by at most one. Restore all binary states. Use the existing five
second limit per endpoint and retain solver statuses, bounds and every feasible
integer witness. No extension of time limits or selection on completion.

Bounds are counts: ceil(M*lower-1e-7) and floor(M*upper+1e-7), normalization fixed
atM. Compare with the saved arbitrary-weight perturbation endpoints on the same
cases. This known feasible-class nesting is a check, not a finding. Report
optimal-case means with denominators, unresolved counts, and an all-case mean
width envelope from incumbent and dual objective bounds (intersecting with the
known arbitrary-weight upper width). Do not substitute unresolved optima.

Every selected empirical event has both kinds of rows. Replacing one event row
by allzeros or one non-event row by allones changes every binary moment count
by at most one, producing two feasible M50laws whose tail probabilities differ
by0.04. Check these witnesses from the actual source X. This gives a structural
width floor at radius0.02 for all120cases, not a new empirical result. The
measured width magnitudes and optimization completion are the outcomes.

Before weather solves, exhaustively enumerate ordered two-member/two-site
ensembles (16possibilities) and compare exact and perturbed integer endpoints
at radii0,0.1,0.5. The new branch must preserve exact-count behavior. Stream each
weather result to disk. At most240five-second new endpoints plus small fixtures
fit one1800second runner; stop at that cap if unexpected overhead intervenes.

This is exploratory after seeing earlier separate sensitivities. It changes no
original results, cohort, release definition, numerical tolerance or primary
law class. It does not model a measured rounding/calibration process. Offline
verification reconstructs integer constraints and checks all saved witnesses,
the lattice equivalence and every aggregate without calling APIs; optional
fresh MILP re-solves are separate because completion may depend on hardware.

Fixed at 2026-10-26T07:38:04Z. No new integer-perturbation weather result has been computed.
