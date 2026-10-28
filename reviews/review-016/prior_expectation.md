# Prior expectation (review-016-1)

## Deviation to record first
The skill asks me to read only the title and the research-question section before writing this file.
My first command printed the first 40 lines of paper.md, which contained the title, the abstract,
the Introduction (including the research question), section 2 (prior work) and the beginning of 3.1.
I therefore saw the abstract's numbers (e.g. MSE ratio 0.267-0.278, RMSE 0.0559 vs 0.1066 vs no-change
0.0260, coverage 83.4% vs 93.1%, direction reports ~10%) before writing this. The expectation below is
written as I would have stated it from the title and question, but it is contaminated and cannot be
used as a clean blind prediction. I mark below which parts I believe I would have predicted anyway.

## Research question (as stated in paper.md section 1)
"At a fixed annual reference-label budget, how reliably can model-assisted estimates based on frozen
classifiers of annual satellite embeddings identify changes in the diversity of declared crop groups,
and does revisiting reference locations improve inference relative to independent samples?"

## My expected answer and confidence
1. Revisiting vs independent samples: revisiting should reduce the variance of a year-to-year change
   estimate strongly, because declared crop-group labels at a fixed point are highly persistent between
   years (permanent grassland in particular; in Switzerland a large share of agricultural area is
   grassland). With label persistence of perhaps 70-90%, the MSE ratio of revisited/independent direct
   change estimates for a smooth functional like Shannon entropy would be well below 1, roughly 0.2-0.5.
   Confidence: high (~80%) that revisiting is clearly better for direct estimates; this follows from
   classic repeated/rotating-panel survey theory and needs no experiment in direction, only in magnitude.
   Where the landscape is arable-dominated with rotation, persistence is lower and the gain shrinks;
   I would expect the gain to be much smaller or vanish there (confidence moderate, ~60%).
2. "How reliably can changes be identified": year-to-year changes of landscape-level Shannon entropy
   of crop groups are mostly small (order 0.01-0.05 nats) relative to the sampling error at a budget of
   ~100 labels per year. I expect that at practical budgets, change detection will be rare, that a
   "no change" predictor will be hard to beat in RMSE, and that reported direction calls will be few.
   Confidence: moderate-high (~70%).
3. Model-assisted estimation with a frozen classifier on annual embeddings: I expect modest variance
   reduction relative to direct estimates in the source year, eroding under temporal transfer, and that
   the benefit for change estimates is smaller than the benefit of revisiting because residual errors at
   the same point are also persistent. Interval coverage for entropy (nonlinear, near the simplex
   boundary for dominated landscapes) via linearization/bootstrap may be below nominal, especially with
   revisited samples when few points change. Confidence: low-moderate (~50%).

## How researchers and practitioners would judge the matter at present (concretely)
- Survey statisticians (agricultural statistics, forest inventory): it is textbook that a panel /
  rotating sample improves precision of change when the correlation between occasions is positive
  (Cochran; Kish; USDA NASS area frame / June Agricultural Survey uses rotating segments; national
  forest inventories use permanent plots). They would expect revisiting to win for change and would not
  regard the direction as news; magnitude for a Shannon index and coverage problems would be of interest.
- Remote-sensing area-estimation practitioners (Olofsson et al. good practice; Stehman): they would use
  a probability reference sample and a map as auxiliary information (stratified or model-assisted
  estimators). For change, standard practice is to map change directly and sample strata of change;
  they would see a frozen classifier applied to later years as a source of transfer error that the
  reference sample corrects.
- Agri-environmental monitoring staff in countries with complete parcel declarations (e.g. Switzerland,
  EU IACS/LPIS / GSAA): crop diversity indicators are computed from the census of declarations, not from
  samples, so a sampling design is relevant mainly where declarations are unavailable, delayed, or
  differ from realized crops. They would ask whether the declared-crop reference is a stand-in for
  field-visit references and what a reference label costs.
- Users of embedding products (AlphaEarth/Google Satellite Embedding, TESSERA): mostly evaluate
  per-pixel classification accuracy; uncertainty of derived landscape indicators under temporal
  transfer is rarely reported. They would currently judge embeddings + small classifier as "good enough"
  for mapping, without a quantified answer for change in a diversity index.

Saved by the reviewer; save time recorded in events.jsonl.
