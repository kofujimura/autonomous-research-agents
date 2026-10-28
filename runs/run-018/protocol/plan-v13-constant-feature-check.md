# Exploratory constant-column control

Fixed after the original/permutation/forest-seed comparisons, **before inspecting any independent-scalar control risk estimate**. Scalar runs are under way; their loss summaries have not been read. This extends the same alternative-explanation test and retains every previous result. It is exploratory, not part of the original primary hypothesis.

Append one feature equal to0 for **every** training pair and query–candidate pair. It carries no varying individual-site information and cannot support a nonconstant split. Use the same pair features, roles/pairs, transformations, query pools, candidate distances, confidence screening and output metrics as the primary. This tests whether a new column can change the downstream learned pipeline even when the column supplies no variation; it does not identify a unique tree-level mechanism or establish that an embedding contains no useful information.

Run4spatial rotations in each of these fixed conditions:

1. Primary RF parameters/max_features0.7, primary seed offset0. Compare with the archived primary hydrological pair/category baselines.
2. Same RF, seed offsets1000 and2000, separately, each compared with its already archived same-seed hydrological baselines.
3. RF max_features1.0, primary seed offset0, compared with the archived all-features hydrological baselines.
4. The fixed HGB learner, primary seed18018+r, compared with archived HGB hydrological baselines.

For RF record that training and test added values are all0 and count tree splits using the added feature; expect0. Report any change in chosen references, confidence values, screened sets and risk. For HGB report exact/tolerance-based prediction/reference equality rather than assuming invariance from the constant feature. Use tolerance1e-12 for numerical-confidence comparisons. All standard50%/20/80/100% and paired-window summaries remain; no selection among cases, no formal p-values, no inference that these five conditions represent all implementations or seeds.

Implementation must preserve the code used by active bounded batches; do not alter a file that an active batch will load for later tasks. Start these fits only after implementation is committed and a process slot is free. Every batch<=1800s, at most2logical experiments; all original resource/deadline stops apply.
