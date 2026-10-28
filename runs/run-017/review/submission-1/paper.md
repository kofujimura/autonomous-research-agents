# Training Point Allocation and Recovery of Small Wetland Patches from Satellite Embeddings

*First draft for review by an AI agent.*

## Abstract

Wetland inventories support conservation planning, but accurate representation of wetland area does not ensure recovery of individual small mapped patches. Across 64 geographically separated cores in four US inventory projects, the planned primary test used 227 complete mapped patches of 0.2–1 ha, five training seeds and 2,000 fitting positions. At a test-standardized 5% reference-upland false-positive area rate, oracle object allocation raised annual-embedding patch recovery from 44.8% to 57.6%, compared with 36.4% to 37.6% for seasonal optical predictors. The interaction was 11.6 pp; conditional 95% interval [4.9, 18.5] pp. The planned optical-derived proposal rule did not recover this embedding gain. The interaction remained positive with the tested linear decoder and alternative fitting budgets, but was small and uncertain in all entire-region transfer cases. In the original split, validation-selected thresholds exceeded their nominal test FPR, so these standardized results are not a demonstrated deployment guarantee. 130/227 small test patches had no 20 m interior grid centers, a geometry restriction relevant to homogeneous sampling. Exploratory split rotations over 978 eligible small patches reduced the interaction to 4.5 pp; conditional 95% interval [0.3, 8.3] pp. Exploratory fixed-position loss weighting and embedding-guided uncertainty recovered part of the allocation benefit, leaving its mechanism and the necessity of an oracle frame unestablished. Constant predictions occurred in 0/1200 primary fit–core cases, 19/960 added-rotation cases and 17/1280 transfer cases. We distinguish the number of fitting positions from the cost of obtaining labels and an object sampling frame. The target is agreement with an existing inventory, whose omissions and boundary errors remain unmeasured; the study does not estimate the completeness of ecological wetlands or the labour cost of mapping.

## 1. Introduction

Wetland maps help natural-resource agencies identify restoration opportunities, assess habitat, and consider water storage and land-use impacts. An inventory is a planning resource with a particular definition, source date, minimum mapping unit and positional uncertainty. It is not a substitute for a site assessment or a jurisdictional wetland delineation. These distinctions matter when maps become inputs to conservation decisions rather than illustrations of regional land cover. [Kloiber et al., 2019](https://files.dnr.state.mn.us/eco/wetlands/nwi-user-guide.pdf)

Small wetlands pose a longstanding mapping problem. Their boundaries occupy a large proportion of their area, their spectral signatures can mix with neighboring land, and their seasonal appearance varies. In an aerial-image study, Halabisky and colleagues documented errors concentrated in small wetlands and used additional field observations to investigate errors that image interpretation missed. Object-based wetland mapping has consequently considered patch geometry, landscape context and object-sensitive validation for years. The question here concerns how representation and fitting allocation jointly affect their recovery. [Halabisky et al., 2011](https://doi.org/10.1117/1.3563569), [Dronova, 2015](https://doi.org/10.3390/rs70506380)

Reusable satellite embeddings create a timely practical choice. Instead of processing and learning from a large satellite-image stack for every application, a mapping team can fit a small classifier to annual representations already produced at a global scale. AlphaEarth Foundations (AEF) makes such annual representations available at 10 m resolution. Its published evaluation covers diverse mapping tasks and strong alternatives, but primarily assesses sparse pixel observations rather than recovery of each small wetland patch. [Brown et al., 2025](https://arxiv.org/abs/2507.22291v2)

A recent wetland-vegetation comparison reports similarly high accuracy for conventional predictors and annual embeddings while describing smoother embedding-derived maps as useful. Its samples were selected from homogeneous clusters and screened for outliers. That is a reasonable way to obtain clear examples, but it raises a different question from how well a full landscape's small mapped patches are retained. The original study itself notes limitations of aggregate accuracy measures. [Ryan et al., 2026](https://doi.org/10.3390/rs18020293)

For practitioners who already possess a reference inventory or labelled candidate pool, the actionable choice is how to allocate a limited set of fitting positions. Sampling uniformly from wetland pixels weights a patch according to its number of eligible pixels; sampling patches first changes that allocation. The resulting eligibility probabilities follow from the definitions. Whether that difference improves held-out maps, whether embeddings respond differently from seasonal optical predictors, and whether an image-derived candidate frame can recover an apparent oracle benefit are empirical questions.

Such a model can be intended for extension beyond an existing reference area or for a later mapping cycle. This study tests held-out geographical prediction and transfer using nominally contemporaneous inputs. It does not test temporal updating or discovery of wetlands missing from the reference. Its immediate decision is the allocation of fitting examples when the relevant reference resources already exist.

We therefore ask: **How does training-point allocation interact with annual satellite embeddings versus seasonal optical predictors in recovering small mapped wetland patches at a common reference-upland false-positive area rate, and can image-derived allocation recover an oracle object-frame benefit?** This question concerns an inventory-based mapping workflow. It does not presume that smoother maps lose habitat or that object-aware allocation is beneficial.

## 2. Prior work

Map-validation guidance already explains why a larger minimum mapping unit can improve overall accuracy while reducing representation of small patches. It also requires an explicit sampling design, an appropriate reference interpretation and uncertainty analysis. The distinction between object detection and semantic segmentation, and the sensitivity of aggregate metrics to small structures, are established across image-analysis fields. We use those principles rather than claim a new validation concept. [Olofsson et al., 2014](https://doi.org/10.1016/j.rse.2014.02.015), [Maier-Hein et al., 2024](https://doi.org/10.1038/s41592-023-02151-z)

Geographic object-based image analysis can combine spectral information with shape, texture and spatial context. A wetland-specific review cautions that point observations within a common object need not be independent and describes object detection and extent measures as alternatives for appropriate tasks. That literature also documents the importance of spatial resolution and minimum mapping units. [Dronova, 2015](https://doi.org/10.3390/rs70506380)

AlphaEarth's broad sparse-label evaluations establish that annual embeddings can be useful mapping predictors. Ryan and colleagues directly compare embeddings with a multi-source wetland-vegetation workflow, including spatial-coherence measures. WetSAM, a recent alternative for sparse wetland supervision, combines temporal imagery and segmentation with point labels and examines label-density sensitivity across regions. These studies motivate strong controls; neither generic embedding efficiency nor sparse wetland supervision is the contribution here. [Brown et al., 2025](https://arxiv.org/abs/2507.22291v2), [Ryan et al., 2026](https://doi.org/10.3390/rs18020293), [Yuan et al., 2026](https://arxiv.org/abs/2601.11400)

Within the searches recorded in `protocol/topic-selection.md`, we did not find the exact combination of a frozen-representation comparison, matched fitting positions, object-frame information controls and held-out small-patch recovery. This bounded search result does not establish novelty or absence of related work. A repeated post-result search additionally checked model-guided wetland training and object accuracy guidance. The Wetland Intrinsic Potential tool already samples from preliminary model probability strata, including uncertain areas; object-validation guidance explicitly distinguishes equal-polygon sampling from pixel-induced area probabilities. Our methods implement established sampling principles. [Halabisky et al., 2023](https://doi.org/10.5194/hess-27-3687-2023), [Radoux and Bogaert, 2017](https://doi.org/10.3390/rs9070646)

The search also located *The Effects of Point or Polygon Based Training Data on RandomForest Classification Accuracy of Wetlands* (Corcoran et al., 2015), but only its abstract and bibliographic metadata were checked after the publisher route returned a rate limit. We do not use its reported findings as evidence or claim absence of relevant earlier training-design work. [Abstract-level search hit](https://doi.org/10.3390/rs70404002)

A contemporaneous preprint compares embedding, terrain and optical predictors under boundary-aware inventory labels. It explicitly notes that excluding boundaries changes the evaluation domain, uses spatial separation and examines prevalence and threshold choice. These are existing concerns that our controls address; boundary exclusion itself is not a contribution of this study. [Sharma et al., 2026, preprint](https://www.preprints.org/manuscript/202610.0964)

Size-aware loss weighting has direct precedent in small-water-body mapping: Zhou and colleagues assign larger positive loss weights to smaller mapped components using an exponential area function. Our reciprocal-size weighting is an explicit diagnostic for fixed representations, rather than a proposed new loss principle. The relevant method equations were checked in the publisher-provided full text. [Zhou et al., 2025](https://doi.org/10.3390/rs17111868)

A final search also located *Utility and Explainability of Earth Embeddings in Mapping Small Ponds* (Liu et al., 2026; DOI 10.1109/LGRS.2026.3740204), but only secondary abstract/bibliographic material was readable in the checked range. We cannot assess its exact methodological overlap and do not use its reported findings as supporting evidence. This further limits any claim about the completeness of the prior-work survey.

## 3. Methods

### 3.1. Protocol and provenance

The topic was selected after a recorded candidate comparison and one critique from another model, as required by the research trial. The session itself wrote all code and text and made all scientific decisions. Main protocol v1 preceded main input retrieval; v2 clarified source orientation, radiometric harmonization and sampling-frame assumptions before any mapping model was fit. Subsequent pre-performance amendments added an oracle frame restricted by the evaluation minimum mapping unit, class-count-matched area controls, equal regional training quotas and per-region operating thresholds. These amendments followed input inspection, implementation review and additional literature checks. They are secondary to the original pooled-operating-point interaction, and their exact order is preserved in the protocol versions, events and commits. Exploratory v7–v10 followed the primary outcome: inverse-size loss weights and stronger proposals; fixed split rotations and matched transfer summaries; oracle geographical-quota controls; and deterministic reference-alignment stress. These additions do not redefine the primary estimand. Plans, exact timestamps, input hashes and commits accompany every batch.

### 3.2. Reference and predictor data

The dataset contains 64 non-overlapping 2.56 km square cores on a native 10 m embedding grid, with a 160 m retrieval buffer. Centers come from an outcome-blind, fixed geographic grid inside four US National Wetlands Inventory (NWI) reference projects whose source-feature metadata specifies IMAGE_YR=2020: Prairie Pothole Watersheds 2 NRCS, VT Winooski Otter Creek, GLRI NY Area 1, and WI One Map. Short geographical names are used in tables; the exact source-feature identifiers are retained in the reproduction records. Geometry and source coverage determine eligibility; at least 5 km separates centers. The preassigned roles are eight training, four validation and four test cores per project. Reserve sites are permitted only for technical source-coverage failures, never because a core is empty, difficult or uninteresting. Table 1 describes the realized reference population; a core's available scoring area can be smaller than its imagery footprint because other aquatic inventory classes are excluded.

**Table 1. Fixed split and mapped small-patch reference counts.**

| Project | Train cores | Validation cores | Test cores | Eligible small test patches | Small test patches without 20 m interior |
| --- | --- | --- | --- | --- | --- |
| Prairie Pothole watersheds | 8 | 4 | 4 | 61 | 22 |
| Vermont basins | 8 | 4 | 4 | 67 | 47 |
| Lake Ontario basins | 8 | 4 | 4 | 34 | 21 |
| Wisconsin project | 8 | 4 | 4 | 65 | 40 |

Source-year matching is nominal. The Prairie Pothole report describes 2020 National Agriculture Imagery Program (NAIP) with older ancillary material and no field reconnaissance. The broader Vermont report spans primary imagery from 2016–2020 and secondary 2021 imagery, so its project-level 2020 field does not prove that each interpreted boundary represents only that year. The New York report uses April–May 2020 imagery and purposive later field observations; these are not an independent extent census. The Wisconsin report describes later revisions using 2020 imagery and additional hydrographic information. These source differences accompany the regional comparisons. [Prairie Pothole report](https://documentst.ecosphere.fws.gov/wetlands/data/SupMapInf/R06Y20P14.pdf), [Vermont report](https://documentst.ecosphere.fws.gov/wetlands/data/SupMapInf/R05Y21P01.pdf), [New York report](https://documentst.ecosphere.fws.gov/wetlands/data/SupMapInf/R05Y22P02.pdf), [Wisconsin report](https://documentst.ecosphere.fws.gov/wetlands/data/SupMapInf/R03Y24P03.pdf)

The embedding predictors are the public AlphaEarth Foundations production v2.1 annual outputs for 2020. We decode the 64 signed-byte channels using sign(q)(q/127.5)², exclude the -128 no-data code, and retain exact native cells. Source rows can run south to north, so we flip axes to north-up without interpolation. The source publication's principal evaluations used v2.0; this study evaluates the downloaded production outputs. The data are licensed CC BY 4.0: **The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind.** [Brown et al., 2025](https://arxiv.org/abs/2507.22291v2), [official access documentation](https://developers.google.com/earth-engine/guides/aef_on_gcs_readme)

The optical baseline uses Sentinel-2 Level-2A scenes from April–May, June–July and August–September 2020. In each window, up to two distinct acquisition days must cover the complete buffered core. Selection orders scene cloud percentage, distance from the seasonal midpoint and scene identifier. We retain blue, green, red, near-infrared, two red-edge and two shortwave-infrared bands, plus NDVI and MNDWI. Scene classification categories 2, 4, 5, 6 and 7 are accepted; invalid, cloudy, shadowed and snow-covered values are masked. DN values are bilinearly reprojected and categorical masks use nearest-neighbor resampling. Documented catalog harmonization flags determine whether an additional radiometric offset is needed; both declared and effective offsets are saved. Seasonal clear-pixel medians provide 30 band/index features, with three missing-season indicators. At least two seasons and the embeddings must be valid over 90% of a core before the technical coverage rule passes. A missing third season is imputed from the same pixel's other seasons. Contains modified Copernicus Sentinel data (2020). [Earth Search documentation](https://github.com/Element84/earth-search), [provider harmonization clarification](https://github.com/Element84/earth-search/issues/9)

The conventional context control adds Gaussian means of the 30 optical band/index features at sigma 1 and 2 pixels, computed on buffered inputs, for 93 features including the original 33. A secondary hybrid concatenates the 64 embedding and 33 optical features. The shared output grid does not make effective input resolutions or information sources identical: several Sentinel bands originate at 20 m, and the annual embedding uses broader multisensor information. The NWI polygons, retained source attributes, query completeness checks and source-project reports are bundled. USFWS National Wetlands Inventory is acknowledged as the reference source; its metadata states no access or use constraints.

The reference consists of mapped palustrine wetlands. Other inventory aquatic classes are excluded from the upland-negative pool. Touching palustrine source polygons are grouped before patch definition, so wetland subtype boundaries do not become distinct objects. The primary object target includes complete patches within a core whose vector area meets the recorded minimum mapping unit and that have valid grid-center pixels. These connected mapped patches are not asserted to be hydrologically independent basins. The analysis reports excluded and unscorable objects. A “false positive” means disagreement with reference upland, which may include an inventory omission; it is not proof that an ecological wetland is absent.

The annual embedding fields are production outputs; the representation's publication distinguishes these from its original evaluation version. Seasonal optical predictors use masked clear observations and a common geographic grid. Their temporal summaries and information sources differ from the embeddings. A difference between them cannot identify the causal contribution of an architecture's spatial context. Original metadata, the exact clipped inputs, source dates, processing decisions and hashes are bundled.

### 3.3. Allocation and classifiers

At the primary budget, each model uses 2,000 unique fitting positions from training cores, repeated with five fixed training seeds. The identical positions are supplied to every representation and decoder within an allocation/seed/budget condition. The area baseline draws equal numbers of reference wetland and upland pixels uniformly within class. The homogeneous alternative uses the same class counts but requires centers at least 20 m from mapped boundaries. Oracle allocation selects a training patch uniformly, then a valid pixel uniformly, until the positive half-budget is filled without duplicates; it uses the same negative positions as the area baseline. The original oracle frame includes represented components below the evaluation minimum mapping unit. A secondary frame excludes components smaller than 0.2 ha. Source-polygon identities shared across training appearances are grouped within training geography only. A component leaves the sampling frame when its finite valid-pixel pool is depleted.

Both practical alternatives spend half the budget on a shared class-balanced area initialization. A 100-tree optical forest fitted to those labels supplies scores only in training cores. Proposal allocation thresholds these scores at 0.5, forms eight-connected candidate components with at least four pixels, then samples components and pixels uniformly for the remaining positions. It does not inspect additional reference labels to select these positions. Uncertainty allocation instead selects descending predictive entropy with 30 m separation among added positions. Insufficient proposals are filled from unlabeled area positions and counted. All acquired labels, including false candidate proposals, enter the fitting budget. The realized class counts and missed training-patch coverage are reported.

Additional diagnostic area allocations match each practical method's initial labels, total budget and final class counts. They use the supplied class-labelled pool and no object identities. A natural-prevalence area sample omits class stratification. Equal-region area and oracle controls allocate identical positive and negative quotas across training regions, addressing shifts in geographical training allocation. These are pre-performance amendments and cannot replace the primary area–oracle contrast.

The primary classifier is a random forest (RF) with 300 trees, square-root feature subsampling, minimum leaf size 5 and balanced class weights. A standardized logistic regression (C=1, balanced classes, at most 2,000 iterations) checks decoder dependence. Predictor scaling is estimated from fitting positions only. Additional fitting budgets of 500 and 8,000, hybrid predictors and leave-one-region-out fits are specified as boundary checks; the completion table records which arms actually ran. No test-driven hyperparameter selection is permitted. Classifier probability outputs are scores for thresholding; calibration as ecological probabilities is not asserted.

The balanced policies assume a class-labelled candidate pool. The oracle policy additionally uses mapped object identities. The image-derived proposal policy does not use object identities or second-stage labels to select its additional positions, but its initial labels are supplied and counted. The budget is the number of unique fitting positions, not measured annotation labour, monetary cost or total cost of creating the reference. Full validation reference data are available for threshold assessment and are not silently included in the fitting-position count.

### 3.4. Outcomes and uncertainty

The primary target is a complete mapped palustrine patch with vector area 0.2–1 ha and at least one common-valid grid-center pixel. Touching source polygons, including point contacts, are connected before dissolving. Medium and large bins are 1–10 ha and at least 10 ha. Recovery requires at least half of a patch's common-valid reference centers to receive a score strictly above the operating threshold. Any-overlap and 75% coverage are additional definitions. Zero-center, zero-valid, boundary-crossing and sub-minimum-unit components are counted separately. An isolation stratum requires at least 50 m from another mapped palustrine component, using the surrounding buffer; it does not assert hydrological isolation.

The original primary threshold is the higher empirical 95th percentile of pooled test-reference-upland scores. Strict comparison conservatively handles ties. The resulting FPR is FP/(FP+TN), the fraction of reference-upland area predicted positive; it is different from commission error FP/(TP+FP). We publish achieved rates rather than assume they equal the nominal 5%. Primary patch recovery averages the four regional patch-recovery fractions equally, then averages the five training seeds. The primary interaction is the oracle-minus-area gain for embeddings minus the same gain for optical predictors. Its sign is not specified in advance.

Paired, region-stratified block bootstrap resamples test cores within each of the fixed regions and the five training seeds together across arms, with 2,000 replicates and a fixed seed. Its intervals condition on the fitted models, evaluated operating thresholds and reference maps. Secondary and exploratory intervals are not adjusted for multiple comparisons and are not confirmatory significance tests. They do not include all reference, site-selection or model-training uncertainty. Replicates or strata with no eligible patches are reported as undefined. The region-specific 5% FPR sensitivity addresses redistribution of error among regions, while the primary pooled threshold remains unchanged.

The original validation replay chooses the 95th-percentile upland threshold on validation cores and applies it to test cores unchanged. An additional replay chooses separate thresholds by region when same-region validation data exist. We also report pixel producer's and user's accuracy, intersection over union (IoU), balanced accuracy and average precision, with the positive class defined by the reference. Optical-probability Gaussian smoothing at sigma 1 and 2 is an appearance control, normalized over finite values with nearest padding at core edges. Edge disagreement and predicted component counts describe maps without treating smoothness as accuracy. Raster boundary distances at 0, 10 and 20 m, vector-eroded 20 m pixel interiors, at least 90% patch-valid coverage, habitat codes and isolation provide definition sensitivities.

An object is recovered when the specified fraction of its common-valid reference pixels is predicted as wetland. This is a patch-coverage measure, not merely a one-pixel intersection. We report area-based measures alongside size- and isolation-sensitive outcomes. The standardized operating-point comparison uses held-out reference quantiles; the separate validation-threshold replay measures what happens when a threshold is fixed before application to test geography. The former must not be described as a deployable threshold or a measured inspection budget.

### 3.5. Deviations and scope of inference

See the versioned protocol and deviations record.

The four projects are convenience cases chosen for nominally matching reference-image years and contrasting landscapes. Their mapping procedures, habitat composition and source timing differ. The report covering the Vermont project describes multiple projects with primary images from 2016–2020 and ancillary 2021 imagery, while its selected source feature says 2020. The Wisconsin inventory report includes revisions dated August 2026 based on 2020 imagery. Calendar-year metadata therefore does not guarantee pixel-level temporal alignment or uniform mapping practice. We report projects in a fixed order with these limits and make no regional ranking or national prevalence estimate. No human participants, individual-level social data or security testing are involved. [Prairie mapping report](https://documentst.ecosphere.fws.gov/wetlands/data/SupMapInf/R06Y20P14.pdf), [Vermont mapping report](https://documentst.ecosphere.fws.gov/wetlands/data/SupMapInf/R05Y21P01.pdf), [New York mapping report](https://documentst.ecosphere.fws.gov/wetlands/data/SupMapInf/R05Y22P02.pdf), [Wisconsin mapping report](https://documentst.ecosphere.fws.gov/wetlands/data/SupMapInf/R03Y24P03.pdf)

### 3.5. Exploratory additions after the primary result

The weighting check keeps the exact area-sampled positions but assigns positive losses inverse weights proportional to the number of common-valid pixels in their mapped training component, normalized to a positive mean of one. Negative weights remain one. A second variant truncates the initially normalized positive weights at ten before normalizing again; the final weights therefore need not be bounded by ten. Area and oracle controls are refit with bootstrap disabled in all four weighting arms, separating weighted splitting from weighted bootstrap draws in the installed classifier. Weight vectors, positive effective sample sizes and class totals are saved. A failure to match oracle performance cannot alone distinguish missing patch coverage, weight variance and regularization.

Stronger proposal and uncertainty checks replace the optical proposal forest's predictors with embeddings while retaining the same balanced initialization and selection rules. Class-count-matched controls use the exact resulting counts. A separate simulation starts from the first half of the natural-area seeded sequence, obtains its inventory labels, and selects the remaining positions from embedding-based proposal or entropy scores. Each unique queried position counts once. This uniform initialization uses no target-class information to select its initial positions, but still receives the inventory-derived valid land domain and simulated labels. It is not a measured field-annotation workflow.

Fixed split rotations divide each region into four groups: original test, original validation, first four sorted original training cores, and remaining original training cores. Each rotation tests one group, validates the next cyclically and trains on the other two. The original split is retained; three new rotations test every other core once. No palustrine source polygon ID is shared between groups. The pooled rotation summary sums held-out counts within regions before equal regional weighting. Training sets overlap, so this checks split dependence rather than providing independent replication. Geographic-transfer summaries also isolate the original test-core subgroup while retaining the transfer model's thresholds; a subgroup FPR need not remain five percent.

Geographical-mixture controls retain the original oracle's negative positions and match its positive counts either by region or by core, then draw positive positions uniformly from the corresponding within-class pixel pool. These quotas depend on the oracle sample and retain its privileged information. They test whether between-core or between-region allocation can account for the apparent object benefit; they do not isolate all within-core habitat differences.

Finally, a deterministic alignment check translates the reference one 10 m cell in each cardinal direction, with invalid padding and no wrap, leaving scores fixed. It selects a shared patch cohort from reference masks before reading the translated-condition scores: translation must crop no original valid patch centers and retain at least 90% of them in every common scoring domain. Each directional threshold is recomputed at the same pooled reference-upland FPR. This is a stress test, not an estimated inventory-error distribution. All additions use the original seeds and conditional bootstrap, and all outcomes remain exploratory.

## 4. Results

### 4.1. Reference population and original comparisons

The frozen dataset has 227 eligible small test patches. Of these, 130 have no 20 m interior. This is an eligibility consequence of patch geometry, not a discovery about a model. No selected core was replaced. One training core has an empty reference-scoring domain because other aquatic systems are excluded; it is retained. The original analysis contains 75 fitted models. No primary map is an all-positive or all-negative prediction in the 1200 fit–test-core cases. The primary macro recovery reaches neither zero nor one in any fitted arm. Coincident probability maps and decisions are counted in the comparison audit; none occurred in the evaluated primary pairs.

**Table 2. Original small-patch recovery at a pooled reference-upland FPR of 5%.** Values are means of five seeds after equal weighting of the four regions. Context denotes added optical neighborhood means.

| Allocation | Annual embeddings (%) | Seasonal optical (%) | Optical + context (%) |
| --- | --- | --- | --- |
| Area, balanced | 44.8 | 36.4 | 34.2 |
| 20 m interior | 38.2 | 33.2 | 31.6 |
| Oracle objects | 57.6 | 37.6 | 38.0 |
| Image proposals | 44.6 | 39.4 | 34.2 |
| Uncertainty | 44.9 | 36.9 | 34.8 |

Oracle allocation changed embedding recovery from 44.8% to 57.6%, and optical recovery from 36.4% to 37.6%. The pooled pixel metrics change much less for embeddings: producer's accuracy is 68.52% with area allocation and 68.46% with oracle allocation; IoU is 48.65% and 48.60%, respectively. Optical producer's accuracy is 50.99% and 49.49%, with IoU 36.20% and 35.13%. These are observed means, not tests of equivalence. Pooled pixel metrics weight area, whereas the primary patch measure first weights regions equally. The embedding small-patch change is therefore not apparent from the near-constant pooled area metrics alone. The primary interaction was 11.6 pp; conditional 95% interval [4.9, 18.5] pp. The exact threshold-reselection bootstrap, which includes operating-threshold variability from the resampled cores, is reported separately below. The primary fixed-threshold interval conditions on the original evaluated thresholds.

**Table 3. Planned original contrasts.** Differences are percentage points; intervals are paired conditional block-bootstrap summaries, not population-wide guarantees.

| Comparison | Difference (pp) | Conditional 95% interval (pp) |
| --- | --- | --- |
| Representation × oracle-allocation interaction | 11.6 | [4.9, 18.5] |
| Oracle allocation minus area, embeddings | 12.8 | [8.4, 17.2] |
| Oracle allocation minus area, optical | 1.2 | [-4.5, 6.1] |
| Image proposals minus area, embeddings | -0.2 | [-2.6, 2.3] |
| Image proposals minus area, optical | 2.9 | [-1.6, 8.1] |
| Proposals minus uncertainty, embeddings | -0.3 | [-2.4, 1.6] |
| Proposals minus uncertainty, optical | 2.5 | [0.2, 5.6] |

The original optical-derived proposals gave an embedding change of -0.2 pp; conditional 95% interval [-2.6, 2.3] pp; the optical change was 2.9 pp; conditional 95% interval [-1.6, 8.1] pp. Thus this specific practical rule did not recover the observed embedding oracle gain. This is not an equivalence test, and it does not establish that a method without object identities cannot improve. Uncertainty allocation also remained close to the embedding area baseline. Both methods use the same counted initialization; their final class composition is different from balanced area allocation. Additional class-matched controls appear below.

The oracle and area allocations deliberately share all negative positions. Across seeds they share 1001–1007 of the unique fitting positions. They are neither independent training datasets nor identical inputs. All representation comparisons within an allocation use identical fitting positions. The allocation audit reports positive class counts, sub-minimum-unit positions, spatial allocation, patch representation and fallbacks rather than treating the nominal fitting budget as an annotation-cost measurement.

![Original recovery comparison](figures/primary-recovery.svg)

### 4.2. Regional error distribution and threshold replay

**Table 4. Original regional results, in fixed project order.** The projects differ in habitats, mapping procedures and source timing. These are case descriptions, not a ranking of regional inventory quality.

| Reference project | Small test patches | Embedding area (%) | Embedding oracle (%) | Optical area (%) | Optical oracle (%) | Interaction (pp) |
| --- | --- | --- | --- | --- | --- | --- |
| Prairie Pothole watersheds | 61 | 71.8 | 81.3 | 50.5 | 55.4 | 4.6 |
| Vermont basins | 67 | 14.9 | 24.5 | 4.2 | 5.7 | 8.1 |
| Lake Ontario basins | 34 | 52.4 | 62.4 | 34.1 | 27.6 | 16.5 |
| Wisconsin project | 65 | 40.0 | 62.2 | 56.9 | 61.8 | 17.2 |

A single pooled threshold does not impose equal error rates within regions. The corresponding reference-upland FPRs are:

| Project | Embedding area FPR (%) | Embedding oracle FPR (%) | Optical area FPR (%) | Optical oracle FPR (%) |
| --- | --- | --- | --- | --- |
| Prairie Pothole watersheds | 9.0 | 9.4 | 3.1 | 2.7 |
| Vermont basins | 1.1 | 1.3 | 0.3 | 1.0 |
| Lake Ontario basins | 7.0 | 3.9 | 11.4 | 9.2 |
| Wisconsin project | 4.3 | 7.3 | 4.1 | 6.0 |


When separate test-region thresholds impose the regional operating point, the interaction is 7.6 pp; conditional 95% interval [0.9, 13.7] pp. This reduces the original estimate but does not eliminate its direction in the sampled cases. The original result therefore includes a redistribution-of-error component as well as a remaining within-region ranking component.

**Table 5. Validation-selected threshold replay.** The threshold targets 5% reference-upland FPR in validation geography and is frozen before applying it to the test scores. Actual test FPR is reported alongside recovery.

| Allocation | Embedding recovery (%) | Embedding test FPR (%) | Optical recovery (%) | Optical test FPR (%) |
| --- | --- | --- | --- | --- |
| Area, balanced | 54.5 | 7.3 | 39.9 | 6.6 |
| 20 m interior | 48.3 | 7.1 | 38.8 | 6.9 |
| Oracle objects | 61.2 | 6.8 | 42.1 | 6.6 |
| Image proposals | 53.0 | 7.4 | 42.9 | 6.2 |
| Uncertainty | 51.0 | 7.0 | 43.5 | 6.5 |

For embedding area allocation, replay yields 54.5% recovery at 7.3% test FPR; oracle allocation yields 61.2% at 6.8%. These outcomes do not establish a deployed 5% FPR. The greater replay recovery is partly associated with a less restrictive test operating point. Threshold transport is a separate practical problem from the standardized score comparison.

![Operating threshold transfer](figures/threshold-transfer.svg)

### 4.3. Planned capacity, budget and geographic boundaries

| Budget | Embedding area (%) | Embedding oracle (%) | Optical area (%) | Optical oracle (%) |
| --- | --- | --- | --- | --- |
| 500 | 38.1 | 50.3 | 32.9 | 31.6 |
| 2000 | 44.8 | 57.6 | 36.4 | 37.6 |
| 8000 | 47.6 | 59.2 | 37.5 | 41.9 |

| Decoder | Fitting positions | Representation × allocation interaction |
| --- | --- | --- |
| logit | 2000 | 9.4 pp; conditional 95% interval [1.6, 17.5] pp |
| rf | 500 | 13.4 pp; conditional 95% interval [7.8, 18.7] pp |
| rf | 8000 | 7.2 pp; conditional 95% interval [1.5, 12.6] pp |

The budget and decoder checks retain the sign of the original interaction under their tested settings. The hybrid predictor's observed recovery is 48.3% with area allocation and 56.1% with oracle allocation. A richer predictor does not remove the allocation question, but these comparisons do not identify the causal role of any input sensor or pretraining target.

The geographic-transfer fits omit all training and validation cores in the target reference project, then predict all sixteen cores in that project. Their test cohort is larger than the original four-core cohort. At held-region standardized 5% FPR, their interactions are small and their intervals include zero in every case:

| Held-out reference project | Embedding oracle gain | Optical oracle gain | Interaction |
| --- | --- | --- | --- |
| Prairie Pothole watersheds | 6.0 pp; conditional 95% interval [0.8, 12.3] pp | 7.9 pp; conditional 95% interval [3.6, 12.8] pp | -2.0 pp; conditional 95% interval [-9.5, 5.1] pp |
| Vermont basins | 2.0 pp; conditional 95% interval [-2.9, 6.7] pp | 0.0 pp; conditional 95% interval [-1.6, 1.9] pp | 2.0 pp; conditional 95% interval [-3.5, 6.8] pp |
| Lake Ontario basins | 1.1 pp; conditional 95% interval [-7.3, 7.7] pp | -1.1 pp; conditional 95% interval [-5.3, 2.9] pp | 2.3 pp; conditional 95% interval [-7.8, 10.5] pp |
| Wisconsin project | -0.5 pp; conditional 95% interval [-6.2, 5.8] pp | -1.7 pp; conditional 95% interval [-5.1, 1.4] pp | 1.2 pp; conditional 95% interval [-4.7, 7.7] pp |

This is a material boundary on generalization. The within-region interaction is not established for entire-region transfer. The original transfer validation replay uses only thresholds from the other regions; the standardized transfer thresholds in this table use held-region labels for evaluation, as in the main operating-point comparison. The held-region table is therefore not a deployment estimate. Exploratory matched-cohort and split-rotation checks are distinguished below.

### 4.4. Pre-performance secondary controls

| Additional allocation control | Annual embeddings (%) | Seasonal optical (%) |
| --- | --- | --- |
| Oracle ≥0.2 ha | 55.2 | 35.1 |
| Area, proposal counts | 43.9 | 35.6 |
| Area, uncertainty counts | 44.8 | 36.1 |
| Area, natural prevalence | 42.6 | 33.4 |
| Area, equal regions | 42.8 | 35.9 |
| Objects, equal regions | 55.8 | 37.5 |

The equal-region allocation interaction is 11.5 pp; conditional 95% interval [4.3, 17.7] pp. Restricting the oracle frame to the evaluation minimum mapping unit changes embedding recovery by -2.4 pp; conditional 95% interval [-5.1, -0.3] pp; the optical change is -2.6 pp; conditional 95% interval [-6.4, -0.6] pp. The original oracle's allocation to sub-minimum-unit components therefore is not an innocuous implementation detail. These amendments were fixed before performance, while their extended interval summaries were added after the first primary result.

### 4.5. Exploratory checks added after the primary outcome

**Fixed-position weighting controls.** With bootstrap disabled in every comparator, inverse-size weighting improves embedding recovery by 6.9 pp; conditional 95% interval [2.9, 10.3] pp; the truncated variant changes it by 7.6 pp; conditional 95% interval [3.7, 10.6] pp. The same fitting positions and labels are used, so this improvement does not require newly represented training patches. The weighted models' means remain below the matched oracle mean, with weighted-minus-oracle contrasts -4.3 pp; conditional 95% interval [-8.7, -0.9] pp and -3.6 pp; conditional 95% interval [-8.2, -0.3] pp. This does not decompose the original bootstrapped-forest gain or prove the cause of its remaining gap.

| No-bootstrap fitting condition | Embedding recovery (%) | Optical recovery (%) | Positive-weight effective sample size |
| --- | --- | --- | --- |
| Area (no bootstrap) | 46.7 | 36.7 | unweighted |
| Oracle objects (no bootstrap) | 58.0 | 37.4 | unweighted |
| Same area positions, inverse-size weights | 53.6 | 37.7 | 82.5–140.8 |
| Same area positions, truncated weights | 54.3 | 38.0 | 156.4–207.6 |

Across seeds, minimum positive weights are 0.0046–0.0065 and maximum weights 32.4–57.6 without truncation; corresponding ranges after truncation and normalization are 0.0056–0.0074 and 11.0–12.3. The post-normalization maxima exceed ten, as specified. Full weight vectors, class totals and effective sample sizes remain in the fit records. The control changes the RF bootstrap setting, with matched controls in that setting; its effect cannot simply be assigned to the primary decoder.

**Stronger image-derived allocation.** Replacing only the proposal predictor with embeddings does not give a clear component-proposal gain, but embedding-guided uncertainty improves the final embedding classifier by 5.4 pp; conditional 95% interval [1.2, 9.4] pp. Its comparison with the class-count-matched area control is 6.3 pp; conditional 95% interval [2.1, 10.2] pp. The mean remains below the original oracle mean; equivalence was not tested. The original optical-teacher negative result therefore should not be generalized to every method that does not select by object identity.

| Balanced initialization / final allocation | Embedding recovery (%) | Optical recovery (%) |
| --- | --- | --- |
| Balanced area | 44.8 | 36.4 |
| Original optical proposals | 44.6 | 39.4 |
| Original optical uncertainty | 44.9 | 36.9 |
| Embedding proposals | 45.2 | 36.3 |
| Embedding uncertainty | 50.2 | 37.6 |
| Area matching embedding-proposal counts | 45.0 | 36.6 |
| Area matching embedding-uncertainty counts | 43.8 | 35.7 |

With uniform initialization, embedding proposals change embedding recovery relative to uniform area by 4.8 pp; conditional 95% interval [1.1, 8.4] pp, and embedding uncertainty changes it by 5.3 pp; conditional 95% interval [2.1, 8.1] pp. These simulated-query results still assume the supplied reference-derived land domain. They measure neither human annotation cost nor discovery of omitted ecological wetlands.

| Uniform initialization condition | Embedding recovery (%) | Optical recovery (%) |
| --- | --- | --- |
| Uniform area, all positions | 42.6 | 33.4 |
| Embedding proposals after uniform initialization | 47.4 | 36.0 |
| Embedding uncertainty after uniform initialization | 47.9 | 34.8 |

**Geographical-mixture controls.** Matching the original oracle's positive counts by core improves the embedding area control by 4.4 pp; conditional 95% interval [1.2, 7.8] pp. The oracle-minus-core-matched interaction is 7.8 pp; conditional 95% interval [3.8, 13.2] pp. Between-core allocation can therefore account for part of the observed contrast in this control, while its residual remains. The geographical and weighting controls are not an orthogonal factorial decomposition and their gains must not be added.

| Positive allocation with original oracle negatives | Embedding recovery (%) | Optical recovery (%) |
| --- | --- | --- |
| Original balanced area | 44.8 | 36.4 |
| Area matching oracle regional counts | 45.5 | 37.0 |
| Area matching oracle core counts | 49.2 | 37.0 |
| Original oracle objects | 57.6 | 37.6 |

**Split dependence and transfer cohorts.** The original interaction is larger than each new split's estimate. Two new splits have some undefined core-bootstrap replicates because a resampled region can contain no eligible small patch; the table reports these rather than silently counting all replicates as defined.

| Held-out split | Small patches | Interaction | Undefined bootstrap replicates |
| --- | --- | --- | --- |
| Original split (primary) | 227 | 11.6 pp; conditional 95% interval [4.9, 18.5] pp | 0 |
| rotation1 (exploratory) | 277 | 4.7 pp; conditional 95% interval [-8.1, 11.3] pp | 0 |
| rotation2 (exploratory) | 233 | -0.4 pp; conditional 95% interval [-5.0, 4.8] pp | 5 |
| rotation3 (exploratory) | 241 | 1.2 pp; conditional 95% interval [-6.4, 9.3] pp | 10 |

Pooling all four held-out rotations within each region gives 4.5 pp; conditional 95% interval [0.3, 8.3] pp across all 978 eligible small patches. This attenuated estimate materially changes interpretation of the original split's magnitude. It is a conditional cross-validation summary from overlapping training sets, not independent ecological replication.

The equal-region pooled entire-transfer interaction is 0.9 pp; conditional 95% interval [-2.6, 4.0] pp. Restricting those transfer scores to the original test-core subgroup gives 4.1 pp; conditional 95% interval [-2.9, 13.9] pp, but its achieved FPR differs from the nominal operating point because thresholds were retained from the wider cohort. These subgroup numbers do not establish a matched-FPR improvement. The appendix reports recovery and actual FPR together.

**Reference alignment.** The shared cohort contains 166 of 227 original small patches. The interaction remains positive under every cardinal one-cell shift in this restricted cohort. The excluded 61 patches are outside that robustness claim; this is not an empirical error distribution.

| Synthetic reference offset | Common-cohort patches | Interaction |
| --- | --- | --- |
| unchanged | 166 | 10.0 pp; conditional 95% interval [2.7, 17.1] pp |
| north | 166 | 12.9 pp; conditional 95% interval [5.7, 19.6] pp |
| south | 166 | 10.6 pp; conditional 95% interval [5.2, 16.1] pp |
| west | 166 | 12.4 pp; conditional 95% interval [4.3, 19.6] pp |
| east | 166 | 10.5 pp; conditional 95% interval [4.8, 16.5] pp |

**Constant and empty cases across comparisons.** Counts concern raw maps at the standardized 5% FPR, with zero boundary tolerance. Empty scoring domains are retained separately from constant predictions. Macro floor/ceiling counts concern small-patch recovery.

| Comparison family | Fits | Fit–test-core cases | Empty scoring cases | All-positive cases | All-negative cases | Macro floor fits | Macro ceiling fits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Added split rotations | 60 | 960 | 20 | 3 | 16 | 0 | 0 |
| Embedding-guided allocation | 60 | 960 | 0 | 0 | 0 | 0 | 0 |
| Entire-region transfer | 80 | 1280 | 20 | 7 | 10 | 0 | 0 |
| Oracle-quota controls | 20 | 320 | 0 | 0 | 0 | 0 | 0 |
| Original primary | 75 | 1200 | 0 | 0 | 0 | 0 | 0 |
| Other planned controls | 130 | 2080 | 0 | 0 | 0 | 0 | 0 |
| Weighting and bagging controls | 40 | 640 | 0 | 0 | 0 | 0 | 0 |



## 5. Discussion

For an analyst subsampling an existing wetland reference, allocation can materially change the apparent benefit of a reusable representation. The observed embedding improvement under object allocation is larger than the corresponding optical improvement within the original regions. Choosing a representation using one homogeneous or area-weighted training design can therefore obscure a useful conditional mapping behavior. This evidence supports checking allocation and patch-level outcomes together; it does not justify assuming that embeddings automatically preserve small wetlands.

The oracle comparison is a diagnostic with privileged information. The full inventory already contains class boundaries and connected components, so object geometry is not established to be independently unavailable or costly. The result is about which fitting positions a classifier receives from that resource. It is not a claim that collecting the same number of isolated labels in an unmapped landscape gives the same result. Image-derived sampling is accordingly evaluated as a specific algorithmic alternative, with a separate uniform-initialization simulation, rather than a proof of the necessity of mapped objects.

Geographic transfer and calibration limit the practical inference. An allocation rule helpful for interpolation across separated cores within the same reference projects need not recover the same gain in a completely unrepresented region. Likewise, a standardized reference-upland FPR is an evaluation condition whose threshold uses held-out labels; a practitioner must validate threshold transport using available local reference information. Neither the inventory comparison nor visual map coherence measures ecological wetland completeness.

The intervention an inventory-owning mapping team can consider is modest: include an object-allocation baseline and report recovery of small mapped patches alongside area metrics before settling a fitting design. Whether this improves conservation decisions, annotation effort, ecological discovery or later-year updates requires different evidence. The exploratory controls below are mechanism and scope checks, not confirmations of those unmeasured outcomes.

The exploratory controls change the interpretation in two ways. The original split gives a larger estimate than the pooled rotations, and a benefit can arise from reweighting existing fitting positions or stronger image-guided selection. An explanation based only on exposing additional mapped patches is therefore insufficient for the broader set of tested classifiers and allocations. Neither weighting nor geographical matching identifies a complete causal decomposition of the original effect. Their information requirements also remain explicit: inverse-size weights use the object frame, and matched quotas are derived from the oracle sample.

Equal weighting of mapped patches and a reference-upland false-positive area constraint are evaluation choices. They do not imply that all wetlands have the same ecological value or regulatory priority. The appropriate balance between area and patch objectives depends on the application; that value judgment was not measured here.

## 6. Limitations

The primary benefit is conditional on within-region training and the tested reference agreement task. It is not retained at the same magnitude under entire-region exclusion. Sparse forested/uncertain wetlands omitted from the inventory cannot enter the patch-recovery denominator. Differences between representation inputs, native resolutions and pretraining prevent a causal attribution to spatial context.

An existing inventory provides incomplete and uncertain reference information. The study cannot detect wetlands absent from both its sampling frame and evaluation target, and externally produced interpretation does not guarantee completeness. Source interpretation can use multiple years despite a nominal project-year match; even within one year, seasonal conditions differ. Training labels extracted from an inventory simulate allocation of fitting examples, not a human annotation process.

Only the tested annual representation, optical construction, decoders and reference projects are directly evaluated. The work does not compare every contemporary wetland segmentation model, establish a new learning algorithm, or identify the internal cause of a representation difference. Production embeddings may encode labels or ancillary products related to inventory mapping; public documentation does not prove independence of all pretraining information from the reference.

The original practical sampling comparison evaluates one optical proposal forest and one entropy-based alternative; exploratory additions also use embeddings and a uniform initialization. A failure of these methods to match an oracle gain would not prove that every method without an object frame must fail. Conversely, success under a supplied class-labelled candidate pool would not establish a cheap de novo annotation workflow. The equal-class and oracle comparisons also change within-class habitat and location distributions; even the regional and class-count controls do not isolate every aspect of sample diversity or label quality.

The dense inventory-derived candidate pools make the original sampling restrictions algorithmic restrictions on which information a rule uses. They do not establish that object geometry is unavailable, independently costly, or impossible to reconstruct from the same inventory. The original comparison therefore supports conclusions about subsampling an existing reference resource. Its fitting-position count is not an end-to-end information or annotation budget.

The conditional uncertainty summaries do not turn convenience regions into a representative sample of US wetlands. Training seeds are computational repetitions, not independent ecological replications. No labour cost, field-survey accuracy, change in practitioners' behavior, legal determination, or conservation outcome was measured. Topic selection consulted one critique from `gpt-6-astra` on 2026-10-27; it did not provide experimental annotations, code, interpretation of experimental results or paper text. Its returned model identifier and response are preserved. No research outcome relies on reproducing a fresh API call.

## 7. Reproduction

See `VERIFY.md` for the offline entry point, expected outputs, environment setup, data provenance, timeline checks and deviations. The session's clean-copy offline numerical run passed in 1471.200 seconds, using shared saved-probability inputs; see `review/offline-verification.json` and `review/self-check.md` for the exact committed revision and scope. A rerun by this session is a self-check, not independent reproduction. Git dates and SHA-256 hashes aid inspection but do not establish absence of tampering or independence.

## References

- Brown, C. F., et al. (2025). *AlphaEarth Foundations: An embedding field model for accurate and efficient global mapping from sparse label data*. arXiv:2507.22291v2. https://arxiv.org/abs/2507.22291v2
- Dronova, I. (2015). *Object-Based Image Analysis in Wetland Research: A Review*. Remote Sensing, 7, 6380–6413. https://doi.org/10.3390/rs70506380
- Halabisky, M., Moskal, L. M., & Hall, S. A. (2011). *Object-based classification of semi-arid wetlands*. Journal of Applied Remote Sensing, 5, 053511. https://doi.org/10.1117/1.3563569
- Halabisky, M., et al. (2023). *The Wetland Intrinsic Potential tool: mapping wetland intrinsic potential through machine learning of multi-scale remote sensing proxies of wetland indicators*. Hydrology and Earth System Sciences, 27, 3687–3699. https://doi.org/10.5194/hess-27-3687-2023
- Radoux, J., & Bogaert, P. (2017). *Good Practices for Object-Based Accuracy Assessment*. Remote Sensing, 9, 646. https://doi.org/10.3390/rs9070646
- Kloiber, S. M., Norris, D. J., & Bergman, A. L. (2019). *Minnesota Wetland Inventory: User Guide and Summary Statistics*. Minnesota Department of Natural Resources. https://files.dnr.state.mn.us/eco/wetlands/nwi-user-guide.pdf
- Maier-Hein, L., et al. (2024). *Metrics Reloaded: Recommendations for image analysis validation*. Nature Methods, 21, 195–212. https://doi.org/10.1038/s41592-023-02151-z
- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E., & Wulder, M. A. (2014). *Good practices for estimating area and assessing accuracy of land change*. Remote Sensing of Environment, 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
- Ryan, S., Powell, M., Ling, J., & Wen, L. (2026). *Streamlining Wetland Vegetation Mapping with AlphaEarth Embeddings: Comparable Accuracy to Traditional Methods with Cleaner Maps and Minimal Preprocessing*. Remote Sensing, 18, 293. https://doi.org/10.3390/rs18020293
- Sharma, A., Kharbanda, A., Anand, A., Mishra, R., Zhang, Y., & Biswas, S. (2026). *Wetland Mapping Under Boundary Uncertainty with AlphaEarth Embeddings, LiDAR and Sentinel*. Preprints.org, version 1, posted 10 October 2026; not peer-reviewed. https://www.preprints.org/manuscript/202610.0964
- Zhou, P., et al. (2025). *Using an Area-Weighted Loss Function to Address Class Imbalance in Deep Learning-Based Mapping of Small Water Bodies in a Low-Latitude Region*. Remote Sensing, 17, 1868. https://doi.org/10.3390/rs17111868
- Yuan, S., et al. (2026). *Wetland mapping from sparse annotations with satellite image time series and temporal-aware segment anything model*. arXiv:2601.11400. https://arxiv.org/abs/2601.11400

## Appendix: additional planned and exploratory analyses

### A. Appearance controls and non-identical sensitivity cohorts

| Optical allocation | Map version | Small-patch recovery (%) | Pixel producer accuracy (%) | Adjacent-edge disagreement (%) |
| --- | --- | --- | --- | --- |
| area | raw | 36.4 | 51.0 | 3.2 |
| area | smooth1 | 36.0 | 52.3 | 2.0 |
| area | smooth2 | 28.1 | 51.4 | 1.3 |
| object | raw | 37.6 | 49.5 | 4.1 |
| object | smooth1 | 37.8 | 51.8 | 2.4 |
| object | smooth2 | 29.5 | 51.2 | 1.5 |

Gaussian smoothing changes both edge density and recovery. Its edge-disagreement number describes visual coherence, not correctness. The primary comparison already uses common valid pixels. All original small test patches meet the ≥90% valid-pixel sensitivity, so that filter reproduces the same cohort and is not additional independent robustness evidence. Any-overlap, 75% coverage, boundary tolerance, isolation and habitat-code strata are available in the regenerated `scores.csv`, `regional-scores.csv` and `strata-scores.csv`; empty strata remain undefined.

### B. Threshold uncertainty

The exact threshold-reselection bootstrap retains the fitted models and reference maps while recalculating thresholds from each resampled test-core distribution. It changes the uncertainty calculation, not the original point estimates.

| Comparison | Reselected-threshold 95% interval (pp) | Undefined replicates |
| --- | --- | --- |
| Interaction | [2.1, 19.5] | 0 |
| Embedding oracle gain | [2.7, 19.2] | 0 |
| Optical oracle gain | [-6.3, 7.0] | 0 |

### C. Completion and interpretation

The analysis snapshot includes 465 final fitted models. `completed-cells.csv` lists the exact observed representation, allocation, decoder, budget, geography and seed combinations. The original grid was prioritized to the main area–oracle contrast for decoder, budget, hybrid and transfer checks; it did not execute every possible cross-product of all five policies and all sensitivity settings. Missing cells are not scored as failures or successes. Exploratory v7–v9 additions are separately labelled and retain all outcomes. No human user experiment was performed.

Failed source-orientation and partial-retrieval batches remain in the experiment records. The first full analysis attempt failed at a missing table handoff after preserving its metrics; the corrected snapshot did not substitute different scientific data. `protocol/deviations.jsonl` and `protocol/implementation-clarifications.md` document changes, including scene-selection tile preferences and the E03 code-provenance correction. Hashes and Git records are inspection aids, not an immutable external audit.

### D. Cohort and threshold details

Cells give recovery percent followed by achieved reference-upland FPR in parentheses. The transfer subgroup retains wider-cohort thresholds.

| Cohort | Threshold | Patches | Embedding area | Embedding oracle | Optical area | Optical oracle |
| --- | --- | --- | --- | --- | --- | --- |
| All split rotations | test-standardized | 978 | 41.7 (5.0) | 50.0 (5.0) | 37.9 (5.0) | 41.8 (5.0) |
| All split rotations | validation replay | 978 | 40.5 (5.2) | 47.3 (5.0) | 38.6 (5.3) | 41.2 (5.1) |
| Entire-region transfer, all cores | test-standardized | 978 | 33.5 (5.0) | 35.6 (5.0) | 29.0 (5.0) | 30.2 (5.0) |
| Entire-region transfer, all cores | validation replay | 978 | 28.7 (5.0) | 25.1 (4.0) | 32.5 (6.6) | 31.9 (6.6) |
| Transfer, original test-core subgroup | test-standardized | 227 | 43.9 (7.3) | 48.4 (7.3) | 33.4 (5.3) | 33.9 (5.9) |
| Transfer, original test-core subgroup | validation replay | 227 | 37.2 (7.0) | 35.4 (6.3) | 35.8 (8.4) | 33.5 (8.9) |

For an entire-held-region fit there is only one test region, so its pooled and region-specific test thresholds coincide by construction. These duplicate conditions are not counted as independent robustness evidence.

