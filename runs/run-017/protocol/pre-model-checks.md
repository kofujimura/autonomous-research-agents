# Checks before mapping models

E06 constructed predictors and reference targets for the first eight available cores without fitting or scoring a mapping model. All had full optical/embedding core coverage; excluding other aquatic classes from the target's upland pool reduces the evaluation area in some cores. This follows the protocol and will be reported, not hidden as missing imagery.

The source inventory includes many sub-0.2-ha patches, below the primary evaluation MMU. The v1 oracle policy samples all represented training patches, so it may allocate positions to objects too small to enter the main evaluation. This is a potential explanation to check, not a mapping outcome. Any additional oracle-frame minimum-size sensitivity will be planned explicitly before execution and kept separate from the original primary contrast.

The feature-matrix NPZ files are a regenerable cache, excluded from Git. Their SHA-256, construction metadata, raw clipped inputs and small reference arrays remain available. Model probabilities and raw results will be retained separately. No result claim has been made from input counts alone.
