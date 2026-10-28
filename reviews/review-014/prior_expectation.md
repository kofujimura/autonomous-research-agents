# Prior expectation (review-014-1)

## Disclosure on blindness

The skill asks for this file to be written after reading only the title and the research-question section. In my first look at paper.md I printed its first 80 lines, which included the abstract and Sections 1–3.5 (methods), before writing this file. So this expectation is **not blind** to the abstract's numbers. I tried to write what I would have expected from the title and the research question alone, but the comparison with the results in section 5 (reader_value.md) has to allow for this contamination.

## Research question (as stated in paper.md §1)

"Do concurrent reference vectors or independent-control adjustment improve tree-cover transition screening in later years and held-out regions, relative to fixed-reference scores and learned readouts?"

## Expected answer and confidence

- Concurrent (year-matched) reference vectors and independent-control adjustment: I expect **no consistent improvement** over a fixed reference score. Any differences in sensitivity/specificity would be small (a few points of Youden's J) and would vary in sign across products, tasks and regions. Confidence about 70%. Reason: in a calibrated retrieval-style embedding, year-to-year changes in a forest-reference centroid are small compared with the change in a target plot that changes cover, and subtracting the control mean mainly shifts the score by a near-constant, which a threshold recalibrated on earlier negatives largely absorbs.
- Learned readouts that use the supplied initial class and classify the subsequent cover state (or classify the transition directly): I expect them to **beat the reference-similarity scores** on most conditions, with confidence about 75%. Supervised probes on these embeddings are known to classify land cover well.
- An unsigned cosine-change magnitude: I expect it to be **weak for gains** (non-tree to tree takes years and changes one-year embeddings only a little; grass/shrub variation creates false positives), and better for losses (abrupt clearing). Confidence about 65%.
- Thresholds calibrated on earlier years and other regions: I expect realized false-positive rates to drift away from the nominal 10%, with at least some conditions well off. Confidence about 60%.
- Sample size: with tens of gain positives per product, I expect wide intervals, so many contrasts would be inconclusive.

## How researchers and practitioners would judge this at present

- Remote-sensing land-cover change researchers (e.g., those working with LCMAP, Annual NLCD, Global Forest Watch-style alerts) would already expect a supervised classifier trained on labels to outperform an unsupervised similarity-to-reference score for detecting a defined cover transition, and would treat "validate the indicator against the endpoint" as standard practice (accuracy assessment of change maps, Olofsson-type good practice). They would see the comparison of reference-update strategies as a reasonable but narrow methodological check.
- Users of the new embedding products (AlphaEarth Foundations satellite embeddings, TESSERA) in applied conservation/restoration work have started to use cosine similarity to forest references as a quick restoration/forest-likeness indicator (as in recent case studies). Many would currently assume that a year-matched reference or a control subtraction "fixes" year-to-year drift of the embeddings. They would likely not have tested how transferred thresholds behave on independent change labels.
- Restoration ecologists would already hold that tree cover is not restoration success (SER standards), so a study limited to cover transitions would be judged relevant only as a screening-indicator check.
- Practitioners (government monitoring teams, NGOs, carbon/restoration project verifiers) would be interested mainly in a simple message: whether a reference-similarity score can be used with a threshold to flag gains/losses, and how bad the errors are.

Saved: see events.jsonl for the save time.
