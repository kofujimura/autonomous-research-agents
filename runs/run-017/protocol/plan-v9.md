# Exploratory oracle-quota matched geographical controls

Fixed after the primary and geographic-transfer results, before sampling or fitting these controls. Original experiments remain unchanged. This is an exploratory falsification check, not a new primary hypothesis or an unprivileged label-acquisition method.

## Alternative explanation

The original object sampler changes where positive fitting positions occur: cores with many small objects can receive more positions than cores with equal wetland area but fewer objects. Equal-region quotas already test one coarse geographical explanation, but do not match the original oracle's distribution between cores. A remaining apparent object advantage could be explained by this geographical mixture.

## New controls

For each original seed at budget2,000, reuse the original oracle sample's exactly1,000 negative positions. Derive the positive quotas from its1,000 positive positions, either per training region (`area_regionmatched`) or per training core (`area_corematched`). Within each corresponding positive pixel pool, draw the quota uniformly without replacement. Use independent fixed RNG seeds seed+15101 for regional matching and seed+16101 for core matching; process group keys in sorted order. The quota is always feasible because the unique oracle positions came from that same pool. No new labels, object selection, habitat strata or hyperparameter changes. Counts themselves depend on the original oracle's mapped-object frame; explicitly retain that information advantage.

Fit the original300-tree RF, five original seeds, both AEF and optical predictors:20new final fits. Compare each with original area and oracle models at unchanged operating points and patch definitions. Report their exact spatial quotas, negative-position identity, point overlaps, training small-patch coverage, recovery, component gains and representation interaction with the existing paired conditional bootstrap. Do not infer that this isolates every habitat or spectral mixture: sub-core variation and geometry remain.

## Stopping

Same frozen64cores, reference masks and original split. At most two workers, each<=1,800seconds; 9GiB model-start guard and10GiB overall limit; do not start long work during final60minutes. No new data, AI calls or agents. If storage prevents completion, preserve and report missing cells.
