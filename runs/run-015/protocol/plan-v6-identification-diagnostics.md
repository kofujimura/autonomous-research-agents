# Exploratory v6: sufficient linear-algebra explanations for exact pair tails

Motivation recorded after the initial one-date primary report showed many numerically identified pair intervals, before final aggregation. This is a diagnostic for an alternative explanation, not a new bounding theorem or a replacement for the original endpoints. Run it on every available complete originalM50unit; lead with the same complete-date matched sample and informative stratum.

For each twelve-site portfolio/temperature threshold, construct the existing exact pair constraint matrixA on the states retained after deterministic-site elimination and exact zero-pair-cell pruning. Its columns correspond to possible joint states; its rows are normalization, margins and all pairs. Compute a floating-point singular-value rank with relative threshold1e-10. For each capacity event vectore, solve the least-squares row-space testA^T y=e with the same singular-value threshold and check the maximum residual. Use residual<=1e-8 as numerical row-space evidence; report the tolerance and retain residuals. These are numerical sufficient-condition checks, not formal algebraic proofs.

Assign mutually exclusive descriptive categories in this order:

1. `constant_after_pair_support`: e is exactly constant across retained states. The query value then follows without optimization.
2. `full_column_rank`: rankA equals the number of retained states. The equalities determine all retained state weights if feasible; feasibility is supplied by the original empirical law. This is a sufficient condition for a unique joint distribution within the exact released-information set, up to numerical rank tolerance.
3. `event_in_row_space`: the event is in the numerical row space but the full-column-rank condition is absent. The query value is a linear function of the released moments even if the equalities alone do not determine all state weights.
4. `identified_other`: original pair width<=1e-7 without one of the above sufficient checks. Nonnegative feasible faces or numerical near-identification can matter. Do not assert the joint law is nonunique merely becauseA is rank deficient.
5. `not_identified`: original pair width>1e-7 without those sufficient checks.

For the first three categories, verify the predicted query value against the saved originalq and interval endpoints within1e-7. Keep all counts, including <=2 uncertain sites and floors/ceilings. Summarize matched all/informative cases by category, product and geometry. Also describe retained-state count, observed-pattern count and rank; do not treat correlated capacity queries as independent samples or claim these known sufficient conditions are discoveries.

Check the code on synthetic two-site full support (full column rank), identical columns (two-state full rank after pruning) and three-site parity (rank-deficient with an unidentified majority event). Record those as mathematical/code validation, not weather evidence. All main LP results remain unchanged. No additional model/API/network data or post-result exclusions are needed.
