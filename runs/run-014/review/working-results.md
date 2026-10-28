### 4.5 Alternative controls, calendar anchors and readouts

The preplanned non-tree, initial-class and frozen-calendar controls produce different operating points (Appendix A). Exact initial-class matching has fewer available cases, so its contrast must use the common-case denominators in the paired comparison file. A gain in its J cannot be compared by subtracting the full-sample start-fixed J. No control rule gives a consistent advantage across all products, tasks and available cases.

The preplanned reference allocations, centre/patch supports and global/nearest-reference conditions give the ranges below. These settings reuse the same targets and pool; their signs are sensitivity counts, not independent evidence or a vote for a method. All settings remain available in the machine-readable tables.

| Representation | Task | Readout versus start-fixed | Sensitivity settings | Minimum J difference | Maximum J difference | Positive | Negative | Zero |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AlphaEarth V1 mosaic | gain | Concurrent reference | 20 | -0.095 | 0.119 | 9 | 10 | 1 |
| AlphaEarth V1 mosaic | gain | Tree controls | 20 | -0.119 | 0.141 | 13 | 7 | 0 |
| AlphaEarth V1 mosaic | loss | Concurrent reference | 20 | -0.169 | 0.003 | 1 | 19 | 0 |
| AlphaEarth V1 mosaic | loss | Tree controls | 20 | -0.040 | 0.052 | 6 | 14 | 0 |
| TESSERA v1 | gain | Concurrent reference | 20 | -0.284 | 0.059 | 4 | 15 | 1 |
| TESSERA v1 | gain | Tree controls | 20 | -0.167 | 0.148 | 13 | 6 | 1 |
| TESSERA v1 | loss | Concurrent reference | 20 | -0.080 | 0.026 | 6 | 14 | 0 |
| TESSERA v1 | loss | Tree controls | 20 | -0.053 | 0.029 | 9 | 10 | 1 |


Exploratory baseline-cohort state classifiers use only the baseline reference/tree-control/non-tree-control cohorts for state fitting, while their thresholds still require earlier target-negative labels. They therefore reduce one source of state-fitting labels without establishing equal annotation budgets or zero transition-label dependence. Embedding-matched controls use initial-vector similarity rather than geographic distance. Their complete results are in Appendix A. Calibration at the additional five- and twenty-percent nominal levels changes some primary contrast directions; the original ten-percent rule remains primary.

The auxiliary classification release supplies 109 later labels among 166 baseline-cohort plots, with 0 known binary disagreements and 57 unknown later labels. These are isolated annual observations, not complete histories. No primary plot is removed using those later labels.
### 4.6 What requires the subsequent target vector? Exploratory diagnostics

Some gain discrimination remains when a state classifier receives only the initial target vector. The table compares the same fitted state model applied to the before and after vectors, each calibrated using its own earlier-negative scores. Both comparisons retain the same availability mask, which requires both products in both years. The state models were fitted using earlier labelled states, and the encoders and labels were produced retrospectively. These results are therefore associations in a dated representation, not prospective forecasts.

| Representation | Task | State fit | Before vector TP; FP | After vector TP; FP | Before J | After J | Before minus after J | Conditional 95% interval | Changed flags / cases |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AlphaEarth V1 mosaic | gain | Initial-vector state forest | 11/24; 9/85 | 9/24; 9/85 | 0.352 | 0.269 | 0.083 | -0.093 to 0.221 | 8/109 |
| AlphaEarth V1 mosaic | loss | Initial-vector state forest | 47/124; 56/213 | 113/124; 49/213 | 0.116 | 0.681 | -0.565 | -0.693 to -0.386 | 77/337 |
| TESSERA v1 | gain | Initial-vector state forest | 14/24; 10/85 | 14/24; 5/85 | 0.466 | 0.525 | -0.059 | -0.200 to 0.070 | 11/109 |
| TESSERA v1 | loss | Initial-vector state forest | 38/124; 49/213 | 119/124; 45/213 | 0.076 | 0.748 | -0.672 | -0.795 to -0.492 | 93/337 |
| AlphaEarth V1 mosaic | gain | Initial-vector cohort forest | 7/24; 6/85 | 7/24; 8/85 | 0.221 | 0.198 | 0.024 | -0.092 to 0.148 | 4/109 |
| AlphaEarth V1 mosaic | loss | Initial-vector cohort forest | 44/124; 52/213 | 83/124; 38/213 | 0.111 | 0.491 | -0.380 | -0.471 to -0.268 | 63/337 |
| TESSERA v1 | gain | Initial-vector cohort forest | 11/24; 9/85 | 15/24; 4/85 | 0.352 | 0.578 | -0.225 | -0.441 to 0.066 | 15/109 |
| TESSERA v1 | loss | Initial-vector cohort forest | 26/124; 26/213 | 90/124; 34/213 | 0.088 | 0.566 | -0.479 | -0.569 to -0.374 | 78/337 |


Changing the subsequent target-vector values in one fixed within-year permutation leaves all 3568 initial-only scored rows unchanged across 446 target keys. This verifies input dependence in the implementation; it is not another independent empirical replication. Initial reference similarity and baseline-cohort logistic counterparts, including their uncertainty, are retained in analysis/initial-vector-v17/initial-versus-subsequent.csv.

The after vector improves several gain readouts and improves the full state forest substantially for losses. Thus these results do not support the claim that all apparent change accuracy comes from initial information. They do show why subsequent-state classification accuracy alone cannot establish how much information about a transition was newly observed after the initial date.

The separate coordinate-only control uses four sine/cosine latitude/longitude features, with no embedding values, year or initial vegetation subclass as learner inputs. It yields the following associations on the same conditional sample. This is one geographic baseline, not two product replications. It cannot identify the source of information in the embeddings; weaker results would not exclude richer static landscape information.

| Task | Coordinate-only readout | True positives / positives | False positives / negatives | J | AUROC |
| --- | --- | --- | --- | --- | --- |
| gain | Coordinate transition boosting | 7/24 | 5/85 | 0.233 | 0.746 |
| gain | Coordinate state forest | 1/24 | 1/85 | 0.030 | 0.680 |
| gain | Coordinate state logistic | 4/24 | 1/85 | 0.155 | 0.722 |
| loss | Coordinate transition boosting | 91/124 | 88/213 | 0.321 | 0.656 |
| loss | Coordinate state forest | 45/124 | 50/213 | 0.128 | 0.568 |
| loss | Coordinate state logistic | 40/124 | 46/213 | 0.107 | 0.693 |

## Appendix A. Additional controls and exploratory readouts

These tables retain planned additional controls and the exploratory baseline-cohort/matching readouts. The exact class-matched condition has different availability. Full paired comparisons, calibration levels, year/region strata, all supports and all seeds are supplied as CSV files.

Preplanned additional controls and calendar anchors:

| Representation | Task | Readout | True positives / positives | False positives / negatives | J |
| --- | --- | --- | --- | --- | --- |
| AlphaEarth V1 mosaic | gain | Initial-class controls | 5/21 | 12/54 | 0.016 |
| AlphaEarth V1 mosaic | gain | Cosine change magnitude | 0/24 | 7/85 | -0.082 |
| AlphaEarth V1 mosaic | gain | Direct gradient boosting | 12/24 | 6/85 | 0.429 |
| AlphaEarth V1 mosaic | gain | End-year reference | 3/24 | 7/85 | 0.043 |
| AlphaEarth V1 mosaic | gain | Frozen 2017 reference | 3/24 | 11/85 | -0.004 |
| AlphaEarth V1 mosaic | gain | Frozen 2017 + tree controls | 4/24 | 15/85 | -0.010 |
| AlphaEarth V1 mosaic | gain | Nearest non-tree controls | 7/24 | 18/85 | 0.080 |
| AlphaEarth V1 mosaic | gain | Non-tree controls | 6/24 | 14/85 | 0.085 |
| AlphaEarth V1 mosaic | gain | Pooled reference | 3/24 | 8/85 | 0.031 |
| AlphaEarth V1 mosaic | gain | Standardized concurrent | 6/24 | 28/85 | -0.079 |
| AlphaEarth V1 mosaic | gain | State random forest | 5/24 | 5/85 | 0.150 |
| AlphaEarth V1 mosaic | gain | Subsequent-reference similarity | 5/24 | 5/85 | 0.150 |
| AlphaEarth V1 mosaic | gain | Subsequent-state logistic | 12/24 | 20/85 | 0.265 |
| AlphaEarth V1 mosaic | gain | Subsequent-state forest | 9/24 | 9/85 | 0.269 |
| AlphaEarth V1 mosaic | loss | Cosine change magnitude | 112/124 | 27/213 | 0.776 |
| AlphaEarth V1 mosaic | loss | Direct gradient boosting | 111/124 | 33/213 | 0.740 |
| AlphaEarth V1 mosaic | loss | End-year reference | 58/124 | 20/213 | 0.374 |
| AlphaEarth V1 mosaic | loss | Frozen 2017 reference | 57/124 | 15/213 | 0.389 |
| AlphaEarth V1 mosaic | loss | Frozen 2017 + tree controls | 57/124 | 21/213 | 0.361 |
| AlphaEarth V1 mosaic | loss | Pooled reference | 60/124 | 19/213 | 0.395 |
| AlphaEarth V1 mosaic | loss | Standardized concurrent | 63/124 | 21/213 | 0.409 |
| AlphaEarth V1 mosaic | loss | State random forest | 105/124 | 8/213 | 0.809 |
| AlphaEarth V1 mosaic | loss | Subsequent-reference similarity | 54/124 | 51/213 | 0.196 |
| AlphaEarth V1 mosaic | loss | Subsequent-state logistic | 100/124 | 32/213 | 0.656 |
| AlphaEarth V1 mosaic | loss | Subsequent-state forest | 113/124 | 49/213 | 0.681 |
| TESSERA v1 | gain | Initial-class controls | 4/21 | 3/54 | 0.135 |
| TESSERA v1 | gain | Cosine change magnitude | 0/24 | 8/85 | -0.094 |
| TESSERA v1 | gain | Direct gradient boosting | 14/24 | 8/85 | 0.489 |
| TESSERA v1 | gain | End-year reference | 2/24 | 1/85 | 0.072 |
| TESSERA v1 | gain | Frozen 2017 reference | 8/24 | 7/85 | 0.251 |
| TESSERA v1 | gain | Frozen 2017 + tree controls | 6/24 | 3/85 | 0.215 |
| TESSERA v1 | gain | Nearest non-tree controls | 7/24 | 7/85 | 0.209 |
| TESSERA v1 | gain | Non-tree controls | 6/24 | 6/85 | 0.179 |
| TESSERA v1 | gain | Pooled reference | 6/24 | 5/85 | 0.191 |
| TESSERA v1 | gain | Standardized concurrent | 7/24 | 8/85 | 0.198 |
| TESSERA v1 | gain | State random forest | 3/24 | 5/85 | 0.066 |
| TESSERA v1 | gain | Subsequent-reference similarity | 11/24 | 7/85 | 0.376 |
| TESSERA v1 | gain | Subsequent-state logistic | 14/24 | 10/85 | 0.466 |
| TESSERA v1 | gain | Subsequent-state forest | 14/24 | 5/85 | 0.525 |
| TESSERA v1 | loss | Cosine change magnitude | 115/124 | 40/213 | 0.740 |
| TESSERA v1 | loss | Direct gradient boosting | 114/124 | 30/213 | 0.779 |
| TESSERA v1 | loss | End-year reference | 89/124 | 15/213 | 0.647 |
| TESSERA v1 | loss | Frozen 2017 reference | 83/124 | 23/213 | 0.561 |
| TESSERA v1 | loss | Frozen 2017 + tree controls | 75/124 | 16/213 | 0.530 |
| TESSERA v1 | loss | Pooled reference | 92/124 | 16/213 | 0.667 |
| TESSERA v1 | loss | Standardized concurrent | 96/124 | 28/213 | 0.643 |
| TESSERA v1 | loss | State random forest | 102/124 | 21/213 | 0.724 |
| TESSERA v1 | loss | Subsequent-reference similarity | 66/124 | 43/213 | 0.330 |
| TESSERA v1 | loss | Subsequent-state logistic | 109/124 | 51/213 | 0.640 |
| TESSERA v1 | loss | Subsequent-state forest | 119/124 | 45/213 | 0.748 |


Exploratory baseline-cohort and embedding-matched control readouts:

| Representation | Task | Readout | True positives / positives | False positives / negatives | J |
| --- | --- | --- | --- | --- | --- |
| AlphaEarth V1 mosaic | gain | Start-year reference | 3/24 | 9/85 | 0.019 |
| AlphaEarth V1 mosaic | gain | Baseline-cohort logistic | 5/24 | 5/85 | 0.150 |
| AlphaEarth V1 mosaic | gain | Baseline-cohort forest | 7/24 | 8/85 | 0.198 |
| AlphaEarth V1 mosaic | gain | Concurrent reference | 3/24 | 12/85 | -0.016 |
| AlphaEarth V1 mosaic | gain | Tree controls | 5/24 | 16/85 | 0.020 |
| AlphaEarth V1 mosaic | gain | Cosine change magnitude | 0/24 | 7/85 | -0.082 |
| AlphaEarth V1 mosaic | gain | Direct gradient boosting | 12/24 | 6/85 | 0.429 |
| AlphaEarth V1 mosaic | gain | Embedding-matched controls | 10/24 | 17/85 | 0.217 |
| AlphaEarth V1 mosaic | gain | End-year reference | 3/24 | 7/85 | 0.043 |
| AlphaEarth V1 mosaic | gain | Pooled reference | 3/24 | 8/85 | 0.031 |
| AlphaEarth V1 mosaic | gain | Standardized concurrent | 6/24 | 28/85 | -0.079 |
| AlphaEarth V1 mosaic | gain | State random forest | 5/24 | 5/85 | 0.150 |
| AlphaEarth V1 mosaic | gain | Subsequent-reference similarity | 5/24 | 5/85 | 0.150 |
| AlphaEarth V1 mosaic | gain | Subsequent-state logistic | 12/24 | 20/85 | 0.265 |
| AlphaEarth V1 mosaic | gain | Subsequent-state forest | 9/24 | 9/85 | 0.269 |
| AlphaEarth V1 mosaic | loss | Start-year reference | 64/124 | 18/213 | 0.432 |
| AlphaEarth V1 mosaic | loss | Baseline-cohort logistic | 35/124 | 21/213 | 0.184 |
| AlphaEarth V1 mosaic | loss | Baseline-cohort forest | 83/124 | 38/213 | 0.491 |
| AlphaEarth V1 mosaic | loss | Concurrent reference | 60/124 | 19/213 | 0.395 |
| AlphaEarth V1 mosaic | loss | Tree controls | 62/124 | 22/213 | 0.397 |
| AlphaEarth V1 mosaic | loss | Cosine change magnitude | 112/124 | 27/213 | 0.776 |
| AlphaEarth V1 mosaic | loss | Direct gradient boosting | 111/124 | 33/213 | 0.740 |
| AlphaEarth V1 mosaic | loss | Embedding-matched controls | 65/124 | 33/213 | 0.369 |
| AlphaEarth V1 mosaic | loss | End-year reference | 58/124 | 20/213 | 0.374 |
| AlphaEarth V1 mosaic | loss | Pooled reference | 60/124 | 19/213 | 0.395 |
| AlphaEarth V1 mosaic | loss | Standardized concurrent | 63/124 | 21/213 | 0.409 |
| AlphaEarth V1 mosaic | loss | State random forest | 105/124 | 8/213 | 0.809 |
| AlphaEarth V1 mosaic | loss | Subsequent-reference similarity | 54/124 | 51/213 | 0.196 |
| AlphaEarth V1 mosaic | loss | Subsequent-state logistic | 100/124 | 32/213 | 0.656 |
| AlphaEarth V1 mosaic | loss | Subsequent-state forest | 113/124 | 49/213 | 0.681 |
| TESSERA v1 | gain | Start-year reference | 8/24 | 11/85 | 0.204 |
| TESSERA v1 | gain | Baseline-cohort logistic | 18/24 | 16/85 | 0.562 |
| TESSERA v1 | gain | Baseline-cohort forest | 15/24 | 4/85 | 0.578 |
| TESSERA v1 | gain | Concurrent reference | 8/24 | 12/85 | 0.192 |
| TESSERA v1 | gain | Tree controls | 6/24 | 3/85 | 0.215 |
| TESSERA v1 | gain | Cosine change magnitude | 0/24 | 8/85 | -0.094 |
| TESSERA v1 | gain | Direct gradient boosting | 14/24 | 8/85 | 0.489 |
| TESSERA v1 | gain | Embedding-matched controls | 7/24 | 7/85 | 0.209 |
| TESSERA v1 | gain | End-year reference | 2/24 | 1/85 | 0.072 |
| TESSERA v1 | gain | Pooled reference | 6/24 | 5/85 | 0.191 |
| TESSERA v1 | gain | Standardized concurrent | 7/24 | 8/85 | 0.198 |
| TESSERA v1 | gain | State random forest | 3/24 | 5/85 | 0.066 |
| TESSERA v1 | gain | Subsequent-reference similarity | 11/24 | 7/85 | 0.376 |
| TESSERA v1 | gain | Subsequent-state logistic | 14/24 | 10/85 | 0.466 |
| TESSERA v1 | gain | Subsequent-state forest | 14/24 | 5/85 | 0.525 |
| TESSERA v1 | loss | Start-year reference | 93/124 | 19/213 | 0.661 |
| TESSERA v1 | loss | Baseline-cohort logistic | 79/124 | 22/213 | 0.534 |
| TESSERA v1 | loss | Baseline-cohort forest | 90/124 | 34/213 | 0.566 |
| TESSERA v1 | loss | Concurrent reference | 99/124 | 27/213 | 0.672 |
| TESSERA v1 | loss | Tree controls | 92/124 | 15/213 | 0.672 |
| TESSERA v1 | loss | Cosine change magnitude | 115/124 | 40/213 | 0.740 |
| TESSERA v1 | loss | Direct gradient boosting | 114/124 | 30/213 | 0.779 |
| TESSERA v1 | loss | Embedding-matched controls | 101/124 | 34/213 | 0.655 |
| TESSERA v1 | loss | End-year reference | 89/124 | 15/213 | 0.647 |
| TESSERA v1 | loss | Pooled reference | 92/124 | 16/213 | 0.667 |
| TESSERA v1 | loss | Standardized concurrent | 96/124 | 28/213 | 0.643 |
| TESSERA v1 | loss | State random forest | 102/124 | 21/213 | 0.724 |
| TESSERA v1 | loss | Subsequent-reference similarity | 66/124 | 43/213 | 0.330 |
| TESSERA v1 | loss | Subsequent-state logistic | 109/124 | 51/213 | 0.640 |
| TESSERA v1 | loss | Subsequent-state forest | 119/124 | 45/213 | 0.748 |


![Operating points across exploratory calibration levels](figures/diagnostics/calibration-operating-points.png)
