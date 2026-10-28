# Design identities, not empirical findings

Let all vectors be unit-normalized. For a target measured in years a and b, let r_a and r_b denote reference centroids. The within-pair start-fixed score is S=(u_b-u_a)·r_a. The concurrent score is C=u_b·r_b-u_a·r_a. Therefore

\[
C-S=u_b\cdot(r_b-r_a).
\]

This identity makes reference-year sensitivity possible. It establishes neither its magnitude nor its practical importance, and does not identify its cause as representational drift. Both actual environmental change and the measurement system can alter reference vectors.

If a control-centred score is A=S-m_{a,b,f}, where m is constant for all targets in a fixed year-pair and held-out region f, then A preserves every exact within-group score ordering. Its within-group AUROC is unchanged. A pooled AUROC across groups can change because the group offsets differ. We do not count ranking invariance as an empirical discovery.

For a transferred threshold tau_A, flagging A>tau_A is equivalent to flagging S>tau_A+m_{a,b,f}. Thus centring can affect screening only through an effective threshold change between groups. If the control offset is the same in all calibration and test groups, quantile thresholds shift by the same constant and every flag is identical. The empirical test is whether actual offsets improve false-positive rate and sensitivity when the earlier threshold is held fixed, not whether subtraction makes the control mean zero.

Different initial cover classes need not share the same environmental response, so centring gains on tree-cover controls has no automatic validity. Conversely, centring on baseline non-tree plots does not guarantee validity: they are not known to remain unchanged and are not necessarily environmentally matched. These limitations motivate the held-out label test and the pre-analysis v2 comparison. No causal claim about restoration interventions follows from these formulas.
