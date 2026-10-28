# Value to readers (review-016-1)

Written after reading paper.md, claims.jsonl, VERIFY.md, README.md, protocol/ and research_log.md, after
re-running the primary direct-sampling results with my own code and while/after the research side's
full verification entry point ran (see review-1.md section 4 for its final status).
This is the reviewer's self-report, not a measurement of any change in readers' behaviour.

## 1. Comparison with the prior expectation (prior_expectation.md)

Caveat: prior_expectation.md was written after I had inadvertently seen the abstract (recorded there),
so "as expected" below is weaker evidence of predictability than a clean blind prediction would be.

As expected:
- Revisiting strongly reduces the MSE of a direct change estimate (expected 0.2-0.5; observed 0.267-0.278
  across budgets). The direction follows from repeated-occasion sampling theory (Jessen 1942; Patterson
  1950; Cochran) once label persistence is high; my recomputation gives a median of 18.5% of reference
  points changing broad group between adjacent years, i.e. ~81% persistence.
- The gain is smaller on arable-dominated land (prespecified subset: ratio 0.597 vs 0.198 for
  grassland-dominated; this number is in results/tables/main/pairing-mse-ratios.csv but not in the paper text).
- Year-to-year changes are small relative to sampling error; a no-change point prediction beats all
  sampled estimators in squared error at n=128 (RMS true change 0.026 nats, median |dH| 0.014).
- Frozen-classifier model assistance adds little: frozen logistic assisted RMSE with revisiting
  (0.0605 / 0.0565) is not better than direct revisited sampling (0.0559); forests help modestly (0.047-0.049).
- Normal/delta intervals for entropy change under-cover in some situations.

Different from / beyond expectation:
- The size of the no-change advantage: even at 512 labels/year, revisited direct RMSE (0.0268) does not
  beat the no-change baseline (0.0260); the no-change squared error is smaller than the revisited MSE in
  84/90 units at n=128 and 62/90 at n=512 (my recomputation). I expected budgets of a few hundred labels
  to start resolving changes.
- The specific mechanism of the revisited coverage deficit (12.9% of revisited n=128 samples contain no
  changed label and give a zero-width interval) and its concentration in grassland-dominated landscapes
  (per-unit coverage as low as 8%; 32/90 units below 90%). I had expected under-coverage but not this
  degenerate form. My own sensitivity check suggests it depends on error-free repeated administrative
  labels: with 1% independent annual labelling error the revisited coverage rises from 83.4% to 91.8%.
- The original model-assisted interval's over-coverage (98.8-99.1%) is a numerical artefact of the
  clipped gradient and of ignoring the simplex projection; with the projection derivative the assisted
  intervals behave like the direct ones. I did not anticipate that the preplanned interval rule itself
  would be the main driver of the model-assisted interval result.
- High conditional wrong-direction rates: among reported directions at n=128, 20% (revisited) and 32%
  (independent) point the wrong way (42%/50% for units with |dH|<0.01). The abstract reports only the
  unconditional per-trial rates (1.9% / 2.5%).
- Possible reversal of the revisiting gain on stable arable land in an additional 6-landscape cohort
  (MSE ratio 1.07): not expected, but small and from few landscapes.

## 2. Which understanding or judgement could change, supporting claims, and trust

- Agricultural monitoring staff planning a reference panel for crop-group diversity change: "revisit the
  same locations" gives a large precision gain where land use is persistent (grassland), a smaller one on
  arable land, and possibly none on strictly rotating arable land. Claims C01, C05, C10.
  Trust: C01 numerically reproduced by the research side's entry point and by my own code; magnitude is
  specific to error-free declared labels at fixed pixel locations in 30 Swiss landscapes (landscape
  bootstrap interval for the n=128 ratio 0.21-0.36), and sensitive to labelling error (0.31 at 1%,
  0.43 at 5% in my check). C10 is exploratory, 6 landscapes.
- Analysts reporting year-to-year diversity change: at a few hundred labels per year per 26 km^2
  landscape, sampled annual changes in broad crop-group Shannon diversity are mostly below the
  resolution of the sample; reporting a direction is rare and, when reported, wrong in a substantial
  fraction of cases. Claims C02, C03 (+ conditional rates in Table 1). Trust: high for this benchmark
  (reproduced exactly); this is the most decision-relevant result, but it is underweighted in the abstract.
- Users of satellite-embedding classifiers: model assistance with a frozen source-year classifier did not
  improve revisited estimates, and reported interval behaviour depended on numerical details of the
  delta method (gradient floor, projection derivative). Claims C04, C07, C11. Trust: reproduced by the
  entry point; C07/C11 exploratory and show that C04 is an artefact of the interval rule rather than of
  model assistance.
- Methodologists: the study is an application of established tools; no new estimator or theory.

## 3. Accuracy of the abstract

- The numbers in the abstract that I checked match the output files and my recomputation.
- The abstract does not overstate in the sense of claiming universality; it ends with an explicit scope
  sentence. However it (a) omits that frozen-logistic assistance gives no precision gain with
  revisiting, (b) gives only unconditional wrong-direction rates, (c) does not give the prespecified
  arable-dominated ratio, so the 0.27 figure is read as general, (d) is overloaded with exploratory
  details and case counts that a practitioner cannot interpret, and (e) the title implies results about
  satellite embeddings and crop diversity in general, while the main gain comes from direct
  sampling of Swiss declared crop groups and does not use the embeddings.

## 4. Limitation of this self-report

This is my judgement of possible changes in understanding; no reader was asked and no behaviour change
was measured.
