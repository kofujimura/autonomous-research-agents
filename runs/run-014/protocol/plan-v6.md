# Version 6 — strengthen the conditional-task comparison before score analysis

This amendment is fixed before any empirical embedding scores or predictive results have been inspected. The v1 primary reference/control comparisons, sample and thresholds remain unchanged. Reason: in the defined gain/loss tasks the initial cover class is supplied. Thus the transition label can be obtained by classifying the subsequent cover alone. Subtracting a predicted initial-state probability, as in v1's state random forest, can introduce unnecessary error. Include that stronger comparator explicitly rather than attributing a difference to change measurement without checking this task property.

## Added readouts

1. **Subsequent-state random forest:** reuse exactly the v1 state forest fitted on both states of the earlier fitting pairs. For gain, score P(Trees | u_b); for loss, score -P(Trees | u_b). Keep the original probability-difference forest as well. No new label, tuning or fitting data are introduced.
2. **Subsequent-state logistic regression:** fit StandardScaler and then LogisticRegression on the earlier fitting states only, with C=1, class_weight='balanced', solver='lbfgs', max_iter=2000, random_state14014. Each state's sample weight is0.5 as for the state forest. Use subsequent-state probability (negative for loss). The scaler never uses calibration or test vectors. This supplies an established linear learned direction as well as the nonlinear forest/boosting comparisons. No automatic parameter search or test-based selection.

Apply the identical separate earlier negative calibration, strict flag rule, nominal10% calibration false-positive operating point, both embedding systems/supports and five held-out regions. Include the added readouts in the original LCMAP report and the unchanged-threshold NLCD extension. A code/plan commit precedes execution. No further external data, AI API calls, compute service or participant study is needed.

## Required interpretation and counts

Every evaluated case in both endpoints supplies an initial reference class. Generate and report that count, along with the total test count, in the results and abstract where material. This is conditional transition screening, not a fully label-free or operationally blind change-detection task. The reference-centroid scores themselves also use baseline reference labels and calibration labels. Do not call them entirely unsupervised or label-free. Check ceiling/floor and identical-flag counts for the added comparisons, keep every comparator, and do not relabel the best one as a method chosen before the test. A strong subsequent-state baseline is appropriate for this task, while its performance does not establish detection of new transitions where the initial class is unavailable or wrong.

This is a pre-analysis correction to comparison strength, motivated by task definitions rather than observed results. Original v1 readouts and definitions are preserved; findings remain limited to the explicit endpoints and retrospective downstream transfer described in interpretation-clarification.md.
