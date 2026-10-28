# Exploratory mechanism and practical-frame checks after the primary results

This version adds experiments after the primary results were observed in E38/E41. It does not replace, rerank or redefine any original result. The additions are exploratory. The 64 original cores, reference definitions, common mask, primary split, 2,000-position budget and five original training seeds remain fixed. No new AI API, human participant, paid service or source dataset is used.

## Motivation and alternative explanations

The primary random-forest comparison found an AEF oracle-allocation gain of about 12.8 percentage points, with little gain for optical predictors. The existing optical-only proposal rule did not recover the embedding gain. Equal regional quotas and a linear decoder did not eliminate the interaction. These observations do not establish why oracle allocation helps or that every method without object identities must fail.

First, object sampling changes both which patches are represented and the empirical weighting of their pixels. Test whether weighting the same area-sampled positions can reproduce its benefit. Second, the original proposal forest uses optical predictors even when the final classifier uses embeddings. Test the stronger alternative of constructing the proposal/uncertainty scores from embeddings. Third, the original initialization assumes supplied class-labelled candidate positions; test a less privileged initialization against the already planned natural-prevalence area baseline.

## Inverse component-size loss weights

Fit four policies with AEF and optical predictors, five seeds, 2,000 unique fitting positions: unweighted area, unweighted oracle object allocation, area positions with inverse component-size weights, and the same weights with a fixed truncation. These use a 300-tree random forest with **bootstrap disabled in all four arms**. This separates weighted splitting from weighted bootstrap resampling in the installed scikit-learn implementation. All other RF settings remain the original ones. The resulting `rf_noboot` decoder is distinct from primary `rf`; primary fits are unchanged.

For each selected positive position, let n be the number of common-valid training pixels in its mapped component, grouped across source-polygon-sharing appearances exactly as before. Set its initial weight to 1/n and normalize the observed positive weights to mean one. Negative positions have weight one. The truncated variant caps the initially normalized positive weights at 10, then renormalizes their mean to one. This is a fixed stability check, not a tuned optimum or a strict bound on final renormalized weights. Save all weight vectors and report positive-weight effective sample size, extrema and class totals. Both weighted policies use the exact area-sampled positions and labels, and require the same object frame as the oracle. They do not represent cheaper acquisition of object information.

Compare each weighted area arm with the unweighted area and oracle arms using the existing patch metrics and paired bootstrap. A match with oracle performance is consistent with a loss-weighting explanation under this setup. A failure is not proof that coverage alone causes the oracle benefit: finite-sample weight variance, regularization and the finite-pool sampling rule remain alternatives.

## Embedding-derived proposals and uncertainty

Add `proposal_aef` and `uncertainty_aef`: replace only the 100-tree proposal forest's predictor from optical to AEF, preserving the original class-balanced half-budget initialization, component/entropy rules, separation, fallback, total budget and final AEF/optical comparisons. Save new proposal score maps under distinct paths; never reuse an optical score file for this condition. Add class-count-matched area controls for both new policies, using the same initialization and the exact resulting class counts as before. These require twenty new final fits plus twenty matched-control fits.

## Uniform initialization boundary condition

Add `proposal_uniform_aef` and `uncertainty_uniform_aef`. Their initial half-budget is the first half of the corresponding natural-area policy's seeded, uniformly drawn full-budget sequence. It uses no target-class information to choose those initial positions. Train the proposal forest on their queried NWI labels, then select and label the remaining positions under the same AEF proposal/uncertainty rules. Each new unique queried position counts once. Compare primarily with natural-area fitting at the same total budget and with each other; comparison to the class-balanced teacher initialization is a boundary condition, not equal acquisition information.

The common-valid land-domain mask is still supplied and excludes other inventory aquatic systems. NWI remains the simulated label oracle; no human annotation time, travel, field identification or ecological truth is measured. This is a label-query simulation within a supplied domain, not a measured labour budget. The original dense reference pools make the original sampler restrictions algorithmic restrictions on what a rule uses; they do not prove that object geometry is unavailable or costly to obtain from that same inventory. State this explicitly in the paper.

Both uniform-initialization policies are fit with both final representations and all five seeds, twenty final fits. The full addition has 100 final fits: forty weighting/bagging-control fits, forty embedding-proposal/matched-control fits, and twenty uniform-initialization fits. Keep every negative/failed result. No additional parameter tuning or favorable-arm selection is permitted.

## Analysis, stopping and records

Use original primary test/validation operating points and patch definitions, and the same exploratory secondary bootstrap procedure. Report original and new conditions separately; any claim depending on these additions is exploratory. Preserve dated outputs and distinguish fitting positions, simulated label queries, available reference information and unmeasured labour. Use at most two workers and 1,800-second process limits, the 9 GiB model-start guard within the 10 GiB total limit, and the unchanged extended deadline in manifest.json. Do not start long work in the final 60 minutes. Execute after the committed priority grid and retain omitted cells if resources stop the study.
