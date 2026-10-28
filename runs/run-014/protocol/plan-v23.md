# Exploratory amendment v23: matched direct-learner input comparisons

Fixed 2026-10-25T17:55:34Z, after all LCMAP/Forest and native-input results and the first full numerical self-rerun. The initial-vector diagnostic used state classifiers, whereas the strong direct comparator uses a transition target and a different learner. This leaves training target/algorithm as an alternative explanation. Add matched direct-learner input comparisons in the same study; all original results and unsuccessfulv21test stay fixed. The Forest outcomes have already been seen, so these additions are exploratory on both endpoints, not a new untouched external validation or preregistered Forest test. No new data/network/API/participants.

## Fixed learners and inputs

For each product/task/held-out region, fit the original direct HistGradientBoostingClassifier to the same earlier relevant fitting pairs and transition labels. Preserve150iterations,learning_rate0.05,max_leaf_nodes7,min_samples_leaf10,L2=1,early_stoppingFalse,class_weightbalanced,seed14014. Compare four fixed inputs: initial unit vector a only; subsequent unit vector b only; raw difference b-a only (no further normalization); and the original concatenation[a,b,b-a]. No tuning, best-model selection or extra features. Equal hyperparameters do not equate feature dimension or computational capacity. The both-date reconstruction must reproduce original direct scores/flags/thresholds to1e-12 with identical cases.

Use centre support only, the original paired two-product/two-date availability mask, original fitting/calibration cells and initial-class task populations. Each new input condition gets its own original earlier-negative90th/higher/strict threshold, minimum10negativecalibration cases. The before-only target values still come from retrospectively generated encoders with unverified AlphaEarth support periods; this is not forecasting or a physical observation-causality test.

## Evaluation and transfer

Retain all four inputs for gain/loss and both products. Report sensitivity,FPR,J,AUROC,TP/FPcounts,thresholds,fit counts and year/region strata. Compare each reduced input minus both-date J, and after-only minus before-only J, on common cases with the original2,000paired5-degree-block descriptive intervals. No equivalence/significance stopping rule. Equal initial classes, identical scores/flags and small denominators must remain visible; do not call predictable invariance a finding.

Apply the same learned conditions to the existing separate Forest sample with only original earlier LCMAP fit/calibration; assert unchanged own-condition thresholds/counts to1e-12. Preserve overlapping/beyond horizons and primary/alternate-agreeing label subsets. No fit/calibration or selection on Forest labels. Because those outcomes were already inspected, this is an exploratory boundary check using reused data. Do not pool endpoints/horizons or infer ecological recovery, encoder superiority, static-context mechanism or annotation efficiency.

## Records and verification

Save analysis/direct-inputs-v23 and analysis/nlcd-direct-inputs-v23 with raw/report predictions,metrics,contrasts,thresholds,fit counts,original-both reconstruction checks and raw-input hashes. Expected under2minutes/run; hard1800seconds and max2experiment processes. Add both to the single offline entry point, then repeat the end-to-end self-rerun because scientific coverage changed after its first PASS. Keep the first self-rerun and candidate commit as records, not as proof covering this addition.
