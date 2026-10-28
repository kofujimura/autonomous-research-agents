# Topic-selection pilots only

Written before fetching candidate input data. Maximum 15 minutes per candidate, executed with a timeout. These are feasibility checks, not main hypothesis tests. No candidate is selected. No pilot-derived numerical result will enter the paper unless the eventual main plan explicitly includes it.

1. C01: fetch the public embedding catalogue and a small embedding window if dependencies finish installing; read the official wetland service metadata and obtain a small polygon sample with water-regime labels. Check that enough non-edge wetland samples and usable label classes can in principle be obtained. Stop after 900 seconds.
2. C03: inspect the published forecast-data catalogue and the GenCast data-availability statement; attempt public forecast metadata only. Check for ensembles that support meaningful joint-event evaluation and a licence. Do not train or run a global model. Stop after 900 seconds.
3. C09: inspect the Battle of Water Demand Forecasting data record, licence, temporal resolution and aggregation level. Obtain at most a small public sample or metadata. Check that the model's public small checkpoint and observations are available; no household-level data. Stop after 900 seconds.

At most two pilots/processes simultaneously. No AI APIs in these pilots. If candidate-specific prerequisites fail, record the failure; do not silently replace them. C02 and C12 feasibility will remain estimates if not piloted.
