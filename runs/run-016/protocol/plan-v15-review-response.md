# Post-review plan v15: measurement sensitivity and reader-facing summaries

Fixed 2026-10-27T02:57:41.417949Z after REVIEW-1, before the added analyses. All original data, plans/results and review/submission-1 remain immutable. Review-response deadline2026-10-27T04:50:07Z. No new long experiment after04:20:07Z; reserve a full offline rerun and final sealing. No AI API, subagents, participants or new paid resources.

## A. Annual label-error scenarios (R1-1)

Use the original broad-group frozen-TESSERA reference labels and saved500draws for all90primary contrasts, n128, both direct designs. Keep declaration-population truth fixed. Replace an observed label with probability0,0.01,0.02,0.05by a draw from that landscape-year's empirical class distribution excluding its true class. For a single-class population use uniform alternatives and count this fallback (none expected from original case counts). This is a synthetic misclassification scenario, not an estimated error rate or a model of realised harvest.

Generate seeded location/trial uniform matrices. Reuse the same location/year error across designs when their samples overlap. For annual coupling rho=0,0.5,1, set year-B flip and category uniforms equal to year-A uniforms at a location/trial with probability rho, otherwise use independent uniforms. This preserves each year's marginal corruption rule; it specifies coupling, not a claim that all positively correlated real-world errors lie between scenarios. Share uniforms across error rates; deduplicate the zero-rate condition.

Apply the original direct proportions, simplex cleanup, clipped entropy gradient, FPC and normal multiplier/reporting tolerances unchanged to the noisy sampled labels. The FPC is not re-derived for measurement error; this tests robustness of the original operational rule rather than constructing a new valid interval. Assert zero-noise point estimates/SE/directions match originals. Report RMSE,bias,coverage,reporting,wrong conditional/unconditional shares,zero-SE and paired zero-observed-change rates; keep each scenario's raw estimates/SE/directions/coverage/wrong and noisy-label array hashes with seeds/generation code. Do not store large duplicate synthetic label/index matrices; regenerate them offline.

## B. Within-cohort landscape resampling (R1-3)

Using saved per-unit metrics, average the three primary contrasts within each landscape; resample30original landscapes with replacement5000times, preserving all contrasts and weighting landscape draws equally. At n128 summarize paired/independent MSE ratio and each coverage's2.5/97.5percentiles. Repeat for all six additional stable-arable landscapes using their5000-replication broad/fine per-unit metrics. Save bootstrap indices and metric distributions. These ranges describe within-cohort composition sensitivity and include Monte Carlo noise; they are not national confidence intervals or proof of a representative superpopulation. No data exclusions based on ratios.

## C. Existing-data decision summaries (R1-2,3,4,7)

Export preplanned arable/grassland MSE ratios at every budget. Summarize conditional wrong directions with actual denominators, overall and |deltaH|<0.01versus>=0.01; per-unit coverage min,p10,median,p90,countbelow0.90; per-unit no-change advantage at all budgets. Check the reviewer statement that no tested method beats no-change at512against all original frozen broad logistic/forest outputs; restrict any statement to the conditions actually supported. Summarize the prespecified2022to2025contrast against its own baseline for direct sampling, all five budgets.

Translate errors by computing RMS of100*(exp(estimated_delta-true_delta)-1) from saved trial outputs, not by relabelling exp(log-scaleRMSE)-1as percentage RMSE. Report original entropy-scale results too. Include direct and both original frozen logistic/forest heads, both designs and all original budgets; baseline zerochange is evaluated on each true contrast. No new estimator/fitting/data or outcome-based selection.

Each analysis goes through the two-slot timeout runner<=1800seconds, preserving failures and linking this committed plan/code. Save all outputs under new results/review-*destinations and index them for offline verification. Added metrics/scenarios are exploratory; preplanned subset metrics remain identified as preplanned.
