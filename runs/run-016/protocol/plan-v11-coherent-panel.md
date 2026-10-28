# Exploratory revision v11: one coherent four-year monitoring panel

Fixed after the original pairwise comparisons. Original simulations draw each two-year contrast separately and therefore do not measure simultaneous reliability of a single annual monitoring program. This extension keeps the same30 test landscapes, frozen broad logistic heads, reference populations and illustrative annual budget n128, but uses one four-year sample sequence for2022–2025 (512 reference labels over four years).

Compare independent annual SRS without replacement, a fully revisited panel, and a rotating panel retaining exactly64 of128 locations each following year. For rotation, select the64 retained locations uniformly from the previous sample, then select64 locations uniformly from its complement. Marginal annual samples remain SRS; adjacent-year intersection is exactly64. All designs have500 replications with fixed SHA-derived seeds and saved draws shared across direct and the two original soft-prediction difference estimators. This is an established rotating-sample comparison, not a new survey design.

For independent/full panels use the original variance estimators. For the rotating panel estimate the adjacent-year influence-difference variance as

    (1/n - 1/N)*(s_a^2+s_b^2) - 2*(m/n^2 - 1/N)*s_ab,

where m64 and s_ab is the sample covariance on the overlapping locations. For fixed population influence values this is an unbiased design-variance estimator; with estimated entropy gradients, projection and nonlinear entropy it is only a first-order approximation. Retain negative estimated variances and report their frequency; clip at zero only when forming standard errors, as documented. Validate the finite-population identity and unbiased variance estimate by exhaustive enumeration before the benchmark run. Do not claim nominal entropy coverage from that algebra/software check.

For each adjacent transition retain MSE, coverage, reporting, wrong reporting and projection at the original1.96 multiplier. Also compute intervals with z=normal_quantile(1-0.05/6), a Bonferroni correction for the three adjacent contrasts. Report simultaneous coverage of all three true changes, probability of any reported wrong direction and probability of any reported direction in each four-year landscape/replication. The correction cannot guarantee simultaneous coverage when marginal intervals are invalid. Do not count the three transitions as independent geographic replications. Include all original cases, count true zero changes, and report negative-variance frequencies.

All outcomes are exploratory; the original pairwise results remain primary. No new data, AI calls, participants or fitted models. Run validation and benchmark separately through the two-slot runner, timeout<=1,800seconds, and preserve raw outputs. The rotating design has no measured field-visit cost advantage. If time/storage is insufficient, preserve the plan and unfinished status rather than claim completion.
