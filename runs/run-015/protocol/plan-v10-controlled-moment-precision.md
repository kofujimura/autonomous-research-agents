# Exploratory controlled moment-precision comparisons

The prespecified perturbation result relaxes individual and pairwise moments
together, including deterministic margins and exact zero pair cells. After
seeing that result, isolate two stronger delivered-information conditions on
the unchanged frozen 120-query sensitivity cohort:

1. Keep every individual probability exact and allow each pair moment an
   absolute error at most 0.005 or 0.02.
2. Keep those individual probabilities and the aggregate second factorial
   moment exact, while allowing the same pair-moment errors.

Restore all binary states for each positive tolerance. Exact constraints on
deterministic margins then enforce their required states without relying on
pruning. Use the same empirical reference, arbitrary real probability weights,
capacity query, LP numerical settings and identification tolerance. The exact
aggregate row is the sum of the pair-feature rows, with its original target.
Zero-tolerance constraints are implemented as equal lower/upper inequalities.

Report per-case endpoints, mean widths and identification counts, alongside
the existing all-moments-relaxed and exact-moment conditions. Check that the
original empirical law is feasible and that intervals nest in the expected
order within numerical tolerance. This known nesting is not a finding. The
size of each difference diagnoses sensitivity to which moments are exact;
it does not attribute all residual change to zero cells or identify a real
publication error process. Do not call any neighborhood a confidence set.

Before weather execution, validate heterogeneous tolerances on a small seeded
binary fixture: uniform allowances reproduce the original solver; zero
allowances reproduce exact pair bounds; both controlled conditions contain
the empirical event probability. Re-run all weather endpoints offline during
final verification. Preserve the original prespecified analysis unchanged.

Fixed at 2026-10-26T05:53:26Z.
