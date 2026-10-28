# Feasibility pilots (not the main experimental plan)

Weather access pilot P01 ended before this file, with its actual metadata requests and failure retained in experiments/pilot-weather/result.json. No physical effect was estimated; the access restrictions are decisive for the candidate as formulated.

P02 (Q04): at most 15 minutes, one small anonymous annual embedding sample from a US agricultural region, and official public crop-raster availability/terms. No farmer/household identities; no ownership linkage. Check vector dimensions, finite coverage, and whether a matched crop-label raster can be obtained. Do not use pilot features as main-study test evidence; either exclude their locations/years or label their reuse explicitly in plan-v1. Geographic point: a generic cropland location near -93.5 longitude, 42 latitude; not chosen for an outcome.

P03 (Q05): at most 15 minutes, obtain one public intermittent-demand dataset from its repository (licence checked first) and load the smallest open Chronos model on CPU. Generate 20 trajectories over a short lead time for a few series to test shape, finite values, and total-demand variation. Seed 16003. Treat any distributional effect as feasibility only; main hypotheses/metrics will be fixed later. No API inference is used; locally running public weights is permitted by the trial.

Run each through scripts/run.py with --timeout 900. At most two child experiments concurrently. All caches point inside the research directory. There is no human experiment and no external posting or contact. Record original model files, dataset URLs, input hashes, and any failures.
