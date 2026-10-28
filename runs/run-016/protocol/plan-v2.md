# Plan v2 — source-only feature requirements and primary-first acquisition

This amendment incorporates plan-v1.md by reference. Its fixing time and commit are recorded before any classifier fitting, diversity-change calculation, or audit resampling. All original plans, failed technical attempts and successful extracts remain. The question, primary outcomes, two representations, taxonomy levels, landscape order/quotas, reference-support definition, sampling budgets, 500 repetitions, frozen classifiers and primary transitions are unchanged.

## Reason and prospective changes

Actual anonymous access showed that a native-resolution AlphaEarth landscape-year read takes about two minutes in the first complete case. Exact native-COG retrieval matched the supplied VRT at every checked value but was no faster, and the published anonymous S3 endpoint was slower. These are input-access/implementation results, not classification or diversity findings. None justifies changing the sampled places or the outcome. Continue the documented VRT route; retain the unsuccessful retrieval optimizations.

The original common-feature requirement unnecessarily conditioned source-only training/calibration points on four future embedding years that the frozen analysis never uses. Correct this before fitting:

- **Training and source calibration:** primary feature eligibility uses both representations in 2021 only. All five years of reference declarations still define the same stable agricultural support. No future reference labels train or calibrate the frozen model. Collect 2021 features first.
- **Test landscapes:** keep the original common valid points across both representations and all five years, including 2021, so all target transitions and the planned 2021→2022 sensitivity share exactly the same evaluation population.
- Source landscapes retain at least 2,048 common valid 2021 points. Test landscapes retain at least 2,048 common valid five-year points. The original 4,096-point reference populations and all raw inputs are retained. Quotas and the 200-candidate stop remain unchanged. Do not replace locations on the basis of outcomes.
- Future features for training landscapes are a second acquisition tier for the preplanned current-year-refreshed classifier diagnostic. Their availability does not retrospectively change the primary 2021 training population. If a future-year training feature is missing, exclude that point only from that year's diagnostic fit, report its count and preserve the frozen analysis. Future calibration features are not needed and will not be downloaded merely to fill a rectangle.
- The first training landscape's already-collected 2022–2025 extracts remain bundled and available for these checks; they are not erased or relabeled as failed data.

Freeze a primary population manifest after the required reads, recording required and available years and exact masks. Later augmented manifests may add optional future training inputs, but must preserve the primary masks exactly. If this requirement cannot be met, record a further prospective change rather than silently refitting.

## Numerical implementation and validation

The 10^-6 entropy-gradient floor remains as fixed in v1. Use a 10^-10 tolerance only for numerical zero/direction comparisons and 10^-12 for cleaning projection roundoff. These tolerances are fixed before inference results; they are not substantive change thresholds. Report the preplanned |ΔH|<0.01 count separately. Classifier accuracy/counts are ancillary descriptive diagnostics, with no classifier/region selection based on them. Keep all optimizer warnings.

Before real audit inference, verify the proportion estimator and finite-population variance formulas by exact enumeration of a saved six-point, three-class synthetic fixture, including census recovery and constant-predictor equivalence. This is a software/mathematical validation, not evidence for the empirical research question. The same-session second Zarr decoding path and raster-reader equality checks likewise do not constitute independent reproduction.

All main inference and model comparison procedures remain those in v1. New outcome-informed analyses later in the study will receive their own versioned plan and exploratory designation. This revision resolves an input-availability design issue before outcomes; it is not a claim that the unexecuted full v1 training condition was tested.
