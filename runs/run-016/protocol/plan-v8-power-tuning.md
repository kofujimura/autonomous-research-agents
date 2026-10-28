# Exploratory extension v8 — adaptive prediction weights

Fixed after two implementation-check target units and the reference-only full-grid results, before complete-cohort model-assisted results. This extends the comparison, keeping all original results and every included case. All v8 outcomes are exploratory. No additional labels, downloads or AI API calls are required.

## Motivation and relation to prior work

The original difference estimator fixes the prediction correction weight at one. Generalized-difference/control-variate weighting and PPI++ power tuning are established ways to reduce reliance on poor predictions. Relevant PPI++ full-text sections 2.2, 4 and 6.1–6.2 were checked. Its smooth i.i.d. asymptotic guarantees are not a finite-sample guarantee for this projected entropy-change estimator or for a fixed finite population. Do not claim to implement the complete published PPI++ procedure verbatim.

Compare two bounded scalar-weight implementations, using the original n=128 audit samples, 500 replications, both frozen broad logistic representations, all three primary transitions and all main included test landscapes. This is the illustrative budget selected before outcomes, not a choice based on optimal observed error. Keep C=1 classifiers and all coefficients fixed.

## Weight estimation

For any training sample, use direct class proportions to form year-specific entropy gradients with the same 10^-6 floor as v1. Let W_t be the gradient indexed by the reference label and V_t the gradient dotted with predicted probabilities. In a revisited sample, estimate lambda by Cov(W_b-W_a,V_b-V_a)/Var(V_b-V_a). In independent samples use [Cov(W_a,V_a)+Cov(W_b,V_b)]/[Var(V_a)+Var(V_b)]. Clip to [0,1]; if the denominator is <=10^-14 set lambda=0. This is a scalar control-variate rule for the linearized change. It is neither a claim of optimal finite-sample entropy MSE nor a selection using the benchmark truth. Retain lambda values and endpoint frequencies.

First, fit the scalar on all 128 sampled labels per year and use p_hat_t=mean(Y_t)+lambda*(population_mean(P_t)-sample_mean(P_t)). This same-sample estimator can have finite-sample proportion bias; measure it only as a stronger standard-style comparison, without claiming exact unbiasedness.

Second, split the ordered uniform sample into halves A and B (m=64), using the same panel split in both years for revisited sampling, and separate ordered annual samples for independent sampling. Learn lambda_A from A's labels in both years, and lambda_B from B. For each year define

    p_hat_t^(A) = (m/N)*mean_A(Y_t)
                  +(1-m/N)*[mean_B(Y_t)
                    +lambda_A*(mean_(U\A)(P_t)-mean_B(P_t))].

Average this with the expression swapping A and B. The population-excluding-A prediction mean is computed from the saved population mean and sampled A predictions. Conditional on A, B is a uniform sample from its complement, so the unprojected class-proportion estimate is design-unbiased; the swapped average preserves that property. This proof does not establish unbiased entropy after projection. Check the claim by exact enumeration before execution.

For estimated standard errors, apply the same entropy gradient to per-location residuals using the effective coefficients lambda_eff,A=(m/N)*lambda_A+(1-m/N)*lambda_B and the swapped coefficient on B. Add independent annual sample variances or use the paired residual-difference variance, then the v1 finite-population correction. This treats estimated weights as fixed at first order and does not supply a new finite-sample coverage guarantee. Measure actual coverage and preserve failures. Same-sample weights use the original whole-sample residual variance with the fitted scalar. Use the original simplex projection, interval, tolerance and direction rules.

## Validation and reporting

Validate constant-weight zero/one equivalence to direct/original difference estimation, constant-predictor equivalence, census recovery, and exact unprojected class-proportion unbiasedness under the crossfitted rule for all ordered two-fold samples on a saved six-point population. Include independent-year enumeration as well as paired enumeration. The same-sample variant need not pass the unbiasedness property. Save synthetic inputs and all validation outputs.

For the actual benchmark retain raw estimates, standard errors, weights, projection flags, coverage, reporting and wrong-direction indicators. Report MSE/RMSE, simulation error, coverage, reporting/abstention and both unconditional and conditional wrong-direction rates with denominators. Compare with the original direct/fixed-weight estimators from exactly the same draws. Do not describe an improvement at one selected budget as uniform across budgets, or generalize a failure of lambda=1 to all model-assisted estimators. If inference depends on projection or rare changes, retain that limitation.

Every process uses scripts/run.py, a free slot and a timeout <=1,800 seconds. Commit code before validation and execution. Observe the original storage/deadline limits, and do not begin long work with 60 minutes left. If unfinished, report which comparisons did not run.
