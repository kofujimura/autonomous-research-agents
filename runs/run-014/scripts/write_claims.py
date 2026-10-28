"""Evidence mapping assembled from analysis outputs; no manual result transcription."""
import json
from pathlib import Path
import pandas as pd
from record import ROOT,now
from report import clean

COMMAND='python3 -B scripts/reproduce.py --output /absolute/path/to/new-results'

def records(df,columns):return df[columns].to_dict(orient='records')

def write_claims():
    stamp=now();claims=[]
    def add(cid,text,evidence,experiments,scope,verify,expected,exploratory=False,sources=(),implication=None,status='supported'):
        claims.append(dict(claim_id=cid,text=text,status=status,evidence_paths=evidence,source_ids=list(sources),
            experiment_ids=experiments,scope=scope,verify=verify,expected=expected,exploratory=exploratory,
            reader_implication=implication,updated_at_utc=stamp))
    main=pd.read_csv(ROOT/'analysis/main-v1/main-table.csv')
    p=pd.read_csv(ROOT/'analysis/main-v1/paired-comparisons.csv')
    p=p[(p.availability_mode=='paired')&(p.support=='centre')&(p.seed==14014)&(p.reference_mode=='global')]
    primary=p[p.method.isin(['concurrent','control_adjusted'])]
    add('C001','Concurrent-reference and independent tree-control J contrasts have mixed directions across products and tasks at the original calibration rule; the data do not establish a consistent benefit or equivalence.',
        ['analysis/main-v1/main-table.csv','analysis/main-v1/paired-comparisons.csv','analysis/main-v1/predictions.parquet'],['main-analysis-v1'],
        'Original LCMAP dominant-cover endpoint; supplied initial class; AlphaEarth V1 unofficial mosaic/TESSERA v1, centre pixels, global references, seed14014, nominal10% earlier-negative FPR, 2019–2020/2020–2021 test pairs. No population zero-effect or ecological-restoration claim.',
        COMMAND+'; inspect paired/centre/14014/global concurrent and control_adjusted rows.',
        records(primary,['model','task','method','delta_J','delta_J_lo','delta_J_hi','changed_flags','total_pairs']),
        sources=['S007','S008','S009','S011'],implication='Validate the actual endpoint and transferred operating point before assuming contemporary references or control centring improve screening.')
    direct=p[p.method=='direct_gradient_boosting']
    add('C002',f'The prespecified direct transition classifier has higher J point estimates than start-fixed in all {len(direct)} primary product/task conditions, with different earlier-label resources.',
        ['analysis/main-v1/main-table.csv','analysis/main-v1/paired-comparisons.csv','protocol/plan-v1.md'],['main-analysis-v1'],
        'Original target partitions and embeddings, but different use of earlier labels; no equal-annotation-budget, user-benefit, best-model or prospective-deployment claim. The later fitting/calibration perturbations in C018 bound this original four-of-four point pattern; the TESSERA loss contrast is not positive in every split.',
        COMMAND+'; inspect direct_gradient_boosting primary paired contrasts and the full operating-point table.',
        records(direct,['model','task','delta_J','delta_J_lo','delta_J_hi']),
        implication='Information useful for this cover task exists beyond a scalar reference-change readout; extra training labels and costs must be considered separately.')
    mag=pd.read_csv(ROOT/'analysis/main-v1/metrics.csv');mag=mag[(mag.availability_mode=='paired')&(mag.seed==14014)&
        (mag.reference_mode=='global')&(mag.method=='cosine_change')]
    add('C003','Cosine change magnitude flags zero observed gains at the original threshold for both products and both centre/patch supports; loss sensitivity is substantially higher in the same labelled benchmark.',
        ['analysis/main-v1/metrics.csv','analysis/main-v1/thresholds.csv','protocol/plan-v7.md'],['main-analysis-v1'],
        'Original fixed fitting/calibration assignment (seed14014). Observed counts on the supplied conditional Trees-gain/loss labels, not absence of all representation information, all useful vegetation change, or zero population gain sensitivity. Other non-tree changes are gain negatives.',
        COMMAND+'; select cosine_change in paired/14014/global metrics for both supports.',
        records(mag,['model','support','task','n_positive','n_negative','true_positive','false_positive','sensitivity','false_positive_rate']),
        sources=['S002','S007','S008'],implication='A magnitude score validated for loss should not be presumed to identify tree gains at the same calibration rule.')
    counts=main[main.method=='start_fixed']
    add('C004','All evaluated main cases supply the interpreted initial cover class, and neither endpoint directly measures ecological restoration success.',
        ['protocol/plan-v1.md','protocol/plan-v4.md','data/prepared/targets.csv','analysis/main-v1/main-table.csv'],['main-analysis-v1'],
        'Conditional dominant-cover/Forest transitions; no native biodiversity, biomass, function, intervention cause or user decision outcome measured.',
        'Inspect task definitions and label columns; '+COMMAND+' confirms denominators.',
        records(counts,['model','task','n_positive','n_negative']),sources=['S006','S007','S024'],
        implication='Compare subsequent-state classification and keep tree cover separate from ecosystem recovery.')
    ep=ROOT/'analysis/endpoint-v13';es=json.loads((ep/'summary.json').read_text());em=pd.read_csv(ep/'metrics.csv')
    em=em[(em.task=='gain')&(em.method=='cosine_change')]
    add('C005','In the exploratory unchanged-negative counterfactual, the observed magnitude-score gain floor persists after removing Grass/Shrub transitions from calibration and test negatives, with fitted scores unchanged.',
        ['analysis/endpoint-v13/metrics.csv','analysis/endpoint-v13/summary.json','analysis/endpoint-v13/excluded-gain-negative-pairs.csv','analysis/endpoint-v13/scalar-reconstruction-check.csv'],['endpoint-composition-v13'],
        'A changed negative-class definition, not a replacement primary endpoint. Same fitting labels and all original positives subject to fixed availability rules; no biological explanation established.',
        COMMAND+'; inspect endpoint-v13 metrics, exclusions and reconstruction check.',
        dict(summary=es,magnitude_rows=records(em,['model','support','n_positive','n_negative','true_positive','false_positive'])),True,
        implication='The included non-tree transition negatives alone do not account for the observed floor in this sample.')
    cp=ROOT/'analysis/reference-completeness-v14';changes=pd.read_csv(cp/'changes-versus-original.csv');cm=pd.read_csv(cp/'metrics.csv')
    cm=cm[(cm.support=='centre')&(cm.model=='tessera')&(cm.task=='gain')]
    contrast=float(cm[cm.method=='concurrent'].J.iloc[0]-cm[cm.method=='start_fixed'].J.iloc[0])
    original=float(primary[(primary.model=='tessera')&(primary.task=='gain')&(primary.method=='concurrent')].delta_J.iloc[0])
    add('C006','Using the same reference plots before and after changes the exploratory TESSERA gain concurrent-reference contrast through calibration, while the saved test scores remain unchanged.',
        ['analysis/reference-completeness-v14/reference-membership.csv','analysis/reference-completeness-v14/changes-versus-original.csv','analysis/reference-completeness-v14/metrics.csv'],['reference-completeness-v14'],
        'Primary allocation, global references, original target/training sets and nominal10% rule. The original separately-valid reference means remain primary; neither version identifies encoder or ecological causes.',
        COMMAND+'; inspect same-reference sensitivity and changes-versus-original.',
        dict(original_delta_J=original,intersection_delta_J=contrast,changed_test_scores=int(changes.changed_scores.sum()),
            centre_changes=records(changes[(changes.support=='centre')&changes.method.isin(['start_fixed','concurrent','control_adjusted'])],
                ['model','task','method','changed_thresholds','changed_flags','delta_J'])),True,
        implication='Small method contrasts can depend on availability in the calibration reference pool even when target test scores are fixed.')
    audit=pd.read_csv(ROOT/'analysis/robustness-aef-v12/partial-label-audit-summary.csv')
    history_route=json.loads((ROOT/'analysis/cohort-history-feasibility/summary.json').read_text())
    add('C007','The saved auxiliary cover-classification component provides partial later labels for the baseline cohorts; observed binary agreement does not verify their complete annual histories or ecological stability.',
        ['analysis/robustness-aef-v12/partial-label-audit.csv','analysis/robustness-aef-v12/partial-label-audit-summary.csv','sources/future-control-label-access-search.json',
         'analysis/cohort-history-feasibility/summary.json','analysis/cohort-history-feasibility/coordinate-matches.csv'],['robustness-aef-v12','cohort-history-feasibility'],
        'One selected annual label per uniquely matched plot within1m; missing years remain unknown. No plot was removed or reclassified in the primary analyses.',
        COMMAND+'; inspect partial-label audit counts and original classification metadata.',
        dict(cohort=int(audit.cohort.sum()),unique_matches=int(audit.unique_matches.sum()),later_labels=int(audit.later_labels.sum()),
             known_later_binary_disagreements=int(audit.later_binary_disagreement.sum()),unknown_later=int(audit.unknown_later.sum()),saved_forest_history_route=history_route),True,
        sources=['S007','S008'],implication='Stable class labels at isolated dates are insufficient to certify an unchanged reference ecosystem.')
    robustness=pd.read_csv(ROOT/'analysis/robustness-paired-v12/metrics.csv')
    robustness=robustness[robustness.method.isin(['baseline_cohort_logistic','baseline_cohort_random_forest','embedding_matched_controls'])]
    add('C008','Exploratory baseline-cohort state fitting and embedding-matched control readouts have endpoint- and product-dependent operating points; additional calibration levels do not select a uniformly preferable correction.',
        ['analysis/robustness-paired-v12/metrics.csv','analysis/robustness-paired-v12/calibration-metrics.csv','analysis/secondary-v2/paired-comparisons.csv'],
        ['robustness-paired-v12','secondary-analysis-v2'],
        'Post-primary v12 comparisons, original fixed ten-percent calibration primary. Cohort fitting still uses earlier target-negative calibration labels; unequal label resources and exact-class availability preclude annotation-efficiency or pooled-denominator conclusions.',
        COMMAND+'; inspect the three added readouts and all retained calibration levels.',
        records(robustness,['model','task','method','n_positive','n_negative','true_positive','false_positive','J']),True,
        implication='Specify the control pool, label resources and operating point; do not infer a general correction advantage from one condition.')
    initial=pd.read_csv(ROOT/'analysis/initial-vector-v17/metrics.csv')
    initial=initial[initial.method.isin(['initial_state_random_forest','subsequent_state_random_forest',
        'initial_baseline_cohort_random_forest','baseline_cohort_random_forest'])]
    perm=json.loads((ROOT/'analysis/initial-vector-v17/permutation-check.json').read_text())
    initial_ext=pd.read_csv(ROOT/'analysis/nlcd-initial-v17/metrics.csv')
    initial_ext=initial_ext[initial_ext.availability_mode.str.endswith('_primary')&initial_ext.method.isin([
        'initial_state_random_forest','subsequent_state_random_forest','initial_baseline_cohort_random_forest','baseline_cohort_random_forest'])]
    add('C009','Some initial-vector-only state readouts retain observed gain discrimination, while subsequent vectors improve several gain readouts and the full state forest for losses; performance on a later label alone does not quantify dependence on subsequent target-vector values.',
        ['analysis/initial-vector-v17/metrics.csv','analysis/initial-vector-v17/initial-versus-subsequent.csv','analysis/initial-vector-v17/permutation-check.json',
         'analysis/nlcd-initial-v17/metrics.csv','analysis/nlcd-initial-v17/initial-versus-subsequent.csv'],
        ['initial-vector-v17','nlcd-initial-v17'],
        'Exploratory retrospective LCMAP and separately reported NLCD Forest diagnostics using original earlier state training and per-readout calibration; common mask requires both products/dates. Encoders/labels produced later, exact AlphaEarth mosaic support periods unverified. No forecasting, equivalence, leakage, benchmark-defect or static-context mechanism claim.',
        COMMAND+'; inspect initial-versus-subsequent paired contrasts and the input-dependence permutation check.',
        dict(metrics=records(initial,['model','task','method','n_positive','n_negative','true_positive','false_positive','J']),permutation_check=perm,
             separate_forest_metrics=records(initial_ext,['availability_mode','model','task','method','n_positive','n_negative','true_positive','false_positive','J'])),True,
        sources=['S002','S003','S032'],implication='Report a before-only comparator when interpreting how much later-state accuracy depends on subsequent target-vector values.')
    geo=pd.read_csv(ROOT/'analysis/geography-v18/metrics.csv')
    add('C010','The fixed coordinate-only learners show some discrimination in the same conditional LCMAP test population without using embedding values; this does not identify the source of embedding information.',
        ['analysis/geography-v18/metrics.csv','analysis/geography-v18/predictions.parquet','protocol/plan-v18.md'],['geography-v18'],
        'One geographic baseline with four sine/cosine features, original earlier fit/calibration and paired centre mask; initial class defines task. No year/subclass features or embeddings in learners. Retrospective association, not causal explanation, forecasting or two independent product replications.',
        COMMAND+'; inspect geography-v18 and compare fixed counts and calibration.',
        records(geo,['task','method','n_positive','n_negative','true_positive','false_positive','J','J_lo','J_hi','auroc']),True,
        sources=['S002'],implication='Include bounded static-context comparisons without treating their success or failure as proof of an embedding mechanism.')
    cl=pd.read_csv(ROOT/'analysis/initial-class-v19/metrics.csv')
    subgroup=pd.read_csv(ROOT/'analysis/initial-class-v19/subgroup-metrics.csv')
    subgroup=subgroup[(subgroup.task=='gain')&subgroup.method.isin(['initial_state_random_forest','subsequent_state_random_forest'])]
    add('C011','The initial-class rate baseline flags no gains under the transferred threshold; initial-vector full state forests flag gains within both initially Grass/forb/herb and Shrubs groups.',
        ['analysis/initial-class-v19/metrics.csv','analysis/initial-class-v19/subgroup-metrics.csv','analysis/initial-class-v19/subgroup-initial-versus-subsequent.csv'],['initial-class-v19'],
        'Exploratory v19 alternative explanation, unchanged original thresholds within subgroups. Small subgroup positives; this does not rule out interactions of class with other landscape or temporal context. Loss scores are constant within each region-specific fit by construction, so zero loss flags are not a discovery.',
        COMMAND+'; inspect both gain subgroups and the single class-only baseline.',
        dict(class_rate=records(cl,['task','n_positive','n_negative','true_positive','false_positive','threshold_ties','J']),
             state_forest_subgroups=records(subgroup,['availability_mode','model','method','n_positive','n_negative','true_positive','false_positive','J'])),True,
        implication='Report initial-class composition and within-class results before attributing initial-vector association solely to the coarse class distinction.')
    extension=pd.read_csv(ROOT/'analysis/nlcd-v4/metrics.csv')
    extension=extension[(extension.support=='centre')&extension.availability_mode.str.endswith('_primary')]
    extp=pd.read_csv(ROOT/'analysis/nlcd-v4/paired-comparisons.csv')
    extp=extp[(extp.support=='centre')&extp.availability_mode.str.endswith('_primary')]
    ec=extp[extp.method.isin(['concurrent','control_adjusted'])];ed=extp[extp.method=='direct_gradient_boosting']
    comparisons=pd.read_csv(ROOT/'analysis/nlcd-v4/threshold-equality.csv')
    add('C012',f'In the separate Forest endpoint, concurrent J contrasts are nonpositive in all {len(ec[ec.method=="concurrent"])} original centre conditions, tree-control effects vary, and the direct classifier has higher J point estimates in {int((ed.delta_J>0).sum())}/{len(ed)} conditions; the original magnitude zero-gain floor has a later TESSERA exception.',
        ['analysis/nlcd-v4/metrics.csv','analysis/nlcd-v4/paired-comparisons.csv','analysis/nlcd-v4/threshold-equality.csv','analysis/nlcd-v4/availability-targets.csv'],['nlcd-analysis-v4'],
        'Fixed separate public-domain NLCD Forest-class sample, centre/global/14014, original earlier LCMAP fitting/calibration; end2020–2021 and end2022–2023 horizons separate. Initial classes supplied and repeated plot-years retained. Different ontology, sample and horizon; no national prevalence, independence of label imagery, causal temporal-degradation or ecological-success inference.',
        COMMAND+'; inspect original Forest correction/readout rows by horizon and unchanged-calibration checks.',
        dict(correction_contrasts=records(ec,['availability_mode','model','task','method','delta_J','delta_J_lo','delta_J_hi','changed_flags','total_pairs']),
             direct_contrasts=records(ed,['availability_mode','model','task','delta_J']),
             magnitude=records(extension[extension.method=='cosine_change'],['availability_mode','model','task','n_positive','n_negative','true_positive','false_positive','J']),
             unchanged_original_thresholds=len(comparisons)),False,
        sources=['S024','S025'],implication='Do not extend the observed zero-gain floor or one learned-readout advantage across endpoints and years without a separate transfer test.')
    ac=pd.read_csv(ROOT/'analysis/reference-access-v20/paired-comparisons.csv')
    ac=ac[(ac.support=='centre')&ac.method.isin(['concurrent','control_adjusted'])]
    ae=pd.read_csv(ROOT/'analysis/nlcd-reference-access-v20/paired-comparisons.csv')
    ae=ae[(ae.support=='centre')&ae.availability_mode.str.endswith('_primary')&ae.method.isin(['concurrent','control_adjusted'])]
    olddist=pd.read_csv(ROOT/'analysis/main-v1/nearest-reference-distances.csv')
    newdist=pd.read_csv(ROOT/'analysis/reference-access-v20/nearest-reference-distances.csv')
    nearest=lambda d:float(d[(d.model=='aef')&(d.support=='centre')].reference_k8_m.median())
    add('C014','Permitting baseline references/controls inside the target region reduces their geographic distance and changes correction contrasts, while supervised scores remain unchanged; effects remain condition dependent.',
        ['analysis/reference-access-v20/paired-comparisons.csv','analysis/reference-access-v20/nearest-reference-distances.csv','analysis/reference-access-v20/summary.json',
         'analysis/nlcd-reference-access-v20/paired-comparisons.csv','analysis/nlcd-reference-access-v20/threshold-equality.csv'],
        ['reference-access-v20','nlcd-reference-access-v20'],
        'Exploratory different reference-information access: baseline R/C may be inside held-out region, target fitting/calibration still exclude it. Original strict-reference condition remains primary; geography is not ecological matching. Centre global/nearest8 results retained, patch CSVs also supplied. No equal-resource, local reference-ecosystem or causal encoder claim.',
        COMMAND+'; inspect both reference modes, distances, supervised invariance and separate Forest transfer.',
        dict(original_reference_eighth_median_m=nearest(olddist),all_region_reference_eighth_median_m=nearest(newdist),
             lcmap=records(ac,['model','reference_mode','task','method','delta_J','delta_J_lo','delta_J_hi','changed_flags','total_pairs']),
             forest=records(ae,['availability_mode','model','reference_mode','task','method','delta_J','delta_J_lo','delta_J_hi','changed_flags','total_pairs']),
             invariance=json.loads((ROOT/'analysis/reference-access-v20/summary.json').read_text())),True,
        implication='State which baseline reference labels are available in the target region; broad geographic controls do not validate locally verified ecological references.')
    native=pd.read_csv(ROOT/'analysis/native-v5/comparisons.csv');ns=pd.read_csv(ROOT/'analysis/native-v5/summary.csv')
    add('C013','The native-grid co-location diagnostic shows many close vectors but measurable disagreement with the geographic mosaic; pointwise agreement does not establish paired-decision stability.',
        ['analysis/native-v5/comparisons.csv','analysis/native-v5/summary.csv','data/native-check/tasks.csv'],['native-analysis-v5'],
        'Fixed role/year-stratified point-year sample, partially acquired before17:00cutoff; only valid paired input centres/patches summarized. Not a national sample, full native-grid classification evaluation, or attribution of differences solely to encoders.',
        COMMAND+'; inspect native-v5 missing slots, raw equality, cosines, spatial displacements and role/year/latitude strata.',
        dict(planned_point_years=len(native),native_present=int(native.native_present.sum()),valid_centres=int(native.centre_valid.fillna(False).sum()),
             raw_centres_equal=int(native.raw_centre_equal.fillna(False).sum()),overall=records(ns[ns.group=='overall'],['metric','n','minimum','q05','median','maximum'])),
        sources=['S009','S010'],implication='Keep the AlphaEarth results scoped to the mosaic and avoid inferring native-grid operating points from high median vector agreement.')
    unfinished=json.loads((ROOT/'analysis/native-pairs-v21/checks.json').read_text())
    add('C015','Stability of the fixed paired-native target decisions remains untested because no selected pair has both native dates; empty counts are not observed zero errors or sensitivity.',
        ['analysis/native-pairs-v21/checks.json','analysis/native-pairs-v21/availability.csv','analysis/native-pairs-v21/summary.csv','protocol/deviations.md'],
        ['native-pairs-prepare-v21','native-pairs-v21'],
        'The additional acquisition was never launched before the17:00cutoff passed during a confirmed usage stop. One previously saved point-year only; no complete native pair exists anywhere in saved original targets. Retained as unfinished, not a successful robustness experiment.',
        COMMAND+'; inspect the not_tested status and zero common-case denominators; original empty-count table remains in Git and stdout.',
        unfinished,True,implication='Full paired-native operating-point stability is an unresolved limitation.',status='not_tested')
    partial=pd.read_csv(ROOT/'analysis/native-single-date-v22/summary.csv')
    identities=pd.read_csv(ROOT/'analysis/native-single-date-v22/identity/decision-identity.csv')
    identity_summary=json.loads((ROOT/'analysis/native-single-date-v22/identity/summary.json').read_text())
    add('C016','Single-date native input substitution changes some flags in the saved available cases, while many substituted inputs or scores are identical; this does not complete the paired-native test.',
        ['analysis/native-single-date-v22/comparisons.csv','analysis/native-single-date-v22/summary.csv','analysis/native-single-date-v22/checks.json',
         'analysis/native-single-date-v22/identity/input-identity.csv','analysis/native-single-date-v22/identity/decision-identity.csv','data/native-available/targets.csv'],
        ['native-single-date-v22','native-identity-v22'],
        'Post-primary availability-selected20-pair case series: one native date per pair, other date/fitting/R/C/calibration still mosaic. One gain positive/one gain negative, ten loss positives/eight negatives. Both gain centre inputs identical; no gain-robustness or population accuracy claim. Identity reporting added post-result during self-check.',
        COMMAND+'; inspect every readout/support/task count, changed pairs, identical input/score counts and invariant earlier thresholds.',
        dict(summary=identity_summary,readouts=records(partial,['support','task','method','common_cases','positive_cases','negative_cases','changed_flags','maximum_absolute_score_difference']),
             identities=identities.to_dict('records')),True,
        sources=['S009','S010'],implication='Document input reading and verify decisions separately; high median agreement alone does not guarantee identical alerts.')
    direct=pd.read_csv(ROOT/'analysis/direct-inputs-v23/metrics.csv');directp=pd.read_csv(ROOT/'analysis/direct-inputs-v23/contrasts.csv')
    direct_ext=pd.read_csv(ROOT/'analysis/nlcd-direct-inputs-v23/metrics.csv');direct_ext=direct_ext[direct_ext.availability_mode.str.endswith('_primary')]
    direct_ep=pd.read_csv(ROOT/'analysis/nlcd-direct-inputs-v23/contrasts.csv');direct_ep=direct_ep[direct_ep.availability_mode.str.endswith('_primary')]
    dif=pd.concat([directp,direct_ep],ignore_index=True);dif=dif[(dif.method=='direct_difference')&(dif.baseline_method=='direct_gradient_boosting')]
    dg=dif[dif.task=='gain'];dl=dif[dif.task=='loss']
    add('C017',f'With the fixed direct learner/transition target, difference-only J is lower than both-date J in {int((dg.delta_J<0).sum())}/{len(dg)} gain conditions and higher in {int((dl.delta_J>0).sum())}/{len(dl)} loss conditions; initial-only gain association is also retained in observed samples.',
        ['analysis/direct-inputs-v23/metrics.csv','analysis/direct-inputs-v23/contrasts.csv','analysis/direct-inputs-v23/summary.json',
         'analysis/nlcd-direct-inputs-v23/metrics.csv','analysis/nlcd-direct-inputs-v23/contrasts.csv','analysis/nlcd-direct-inputs-v23/threshold-equality.csv'],
        ['direct-inputs-v23','nlcd-direct-inputs-v23'],
        'All additions fixed after both endpoint outcomes were inspected, exploratory with reused Forest data. Centre, original paired mask/fits/calibration, same fixed HGB parameters and transition labels; unequal input dimensions/capacity. Three populations and two products share earlier fitting; not independent replications, forecasting, universal ordering, equivalence or physical observation causality.',
        COMMAND+'; inspect all four inputs, original-both reconstruction and conditional paired intervals, retaining every horizon separately.',
        dict(lcmap_metrics=records(direct,['model','task','method','n_positive','n_negative','true_positive','false_positive','J','auroc']),
             forest_metrics=records(direct_ext,['availability_mode','model','task','method','n_positive','n_negative','true_positive','false_positive','J','auroc']),
             lcmap_contrasts=directp.to_dict('records'),forest_contrasts=direct_ep.to_dict('records')),True,
        sources=['S002','S029','S032'],implication='Compare input choices using matched learning targets before interpreting either scalar change magnitude or later-state accuracy; preserve gain/loss and transfer boundaries.')
    partition_folder=ROOT/'analysis/partition-sensitivity-v24'
    split_summary=json.loads((partition_folder/'summary.json').read_text());split_ranges=pd.read_csv(partition_folder/'primary-ranges.csv')
    correction_ranges=split_ranges[split_ranges.method.isin(['concurrent','control_adjusted'])]
    changing_signs=int(((correction_ranges.delta_J_min<0)&(correction_ranges.delta_J_max>0)).sum())
    direct_loss=split_ranges[(split_ranges.model=='tessera')&(split_ranges.task=='loss')&(split_ranges.method=='direct_gradient_boosting')].iloc[0]
    add('C018',f'All {changing_signs}/{len(correction_ranges)} primary correction contrasts span both signs across the fixed earlier partitions with invariant unsupervised test scores; the direct TESSERA loss contrast is positive in {int(direct_loss.positive_directions)}/{int(direct_loss.available_partitions)} splits.',
        ['analysis/partition-sensitivity-v24/primary-ranges.csv','analysis/partition-sensitivity-v24/paired-comparisons.csv','analysis/partition-sensitivity-v24/condition-availability.csv',
         'analysis/partition-sensitivity-v24/invariance-checks.csv','analysis/partition-sensitivity-v24/fitting-counts.csv','protocol/plan-v24.md'],
        ['partition-sensitivity-v24'],
        'Post-result exploratory ten fixed cell-hash assignments including original, same LCMAP targets/regions/reference cohorts/learner settings and paired availability. Overlapping splits are not independent replications, a population confidence interval or general training variance. No split selected to replace primary; missing conditions retained.',
        COMMAND+'; inspect every primary range and partition-specific counts, original reconstruction, missing conditions and score-invariance checks.',
        dict(summary=split_summary,primary_ranges=split_ranges.to_dict('records'),magnitude_gain_metrics=records(pd.read_csv(partition_folder/'metrics.csv').query("method=='cosine_change' and task=='gain'"),['partition_seed','model','support','n_positive','n_negative','true_positive','false_positive'])),True,
        implication='Assess earlier calibration/fitting choices when transferring an operating point; conditional target bootstrap intervals alone omit this sensitivity.')
    diag=ROOT/'analysis/review-diagnostics-r1'
    sim=pd.read_csv(diag/'score-similarity.csv');sim=sim[sim.period=='all']
    dsummary=json.loads((diag/'summary.json').read_text())
    add('C019','Post-review exact-fold diagnostics show highly correlated corrected/fixed scores and the recorded reference/cohort variation; these are a limited perturbation test, not evidence that correction cannot help under substantial harmful drift.',
        ['analysis/review-diagnostics-r1/score-similarity.csv','analysis/review-diagnostics-r1/reference-drift.csv','analysis/review-diagnostics-r1/reference-year-counts.csv','analysis/review-diagnostics-r1/control-constancy.csv','protocol/review-analysis-v1.md'],
        ['review-diagnostics-r1'],
        'Exploratory after AI-agent review; centre support, original region-excluded/year-valid means and baseline-only R/C allocation14014. Individual cohorts are not verified later stable; reference-only multi-year drift does not test multi-year target screening or identify encoder versus physical drift. Pooled correlations do not imply identical year-specific decisions.',
        COMMAND+'; inspect review-diagnostics-r1 exact-fold drift, all valid-count rows and pooled/per-year score similarities.',
        dict(summary=dsummary,pooled_similarity=sim.to_dict('records'),reference_drift=pd.read_csv(diag/'reference-drift.csv').to_dict('records'),reference_counts=pd.read_csv(diag/'reference-year-counts.csv').to_dict('records'),control_constancy=pd.read_csv(diag/'control-constancy.csv').to_dict('records')),True,
        sources=['S002','S038'],implication='Quantify available reference/cohort variation and score/decision changes before interpreting a correction null as a strong test of drift removal.')
    add('C020','Gain observations are concentrated in the first LCMAP test pair, and post-review unchanged-only comparisons retain the observed magnitude-ranking inversion in both products and both pairs.',
        ['analysis/review-diagnostics-r1/sample-support.csv','analysis/review-diagnostics-r1/magnitude-ranking.csv','analysis/review-diagnostics-r1/magnitude-medians.csv','protocol/review-analysis-v1.md'],
        ['review-diagnostics-r1'],
        'Exploratory post-review reporting from unchanged original scores; CONUS one-year intervals, 21of24gains in2019–2020 and3in2020–2021. AUROC/median differences are descriptive; they do not identify gradual growth, timing errors, smoothing or causal training effects. Every original negative and unchanged-only definition remains separate.',
        COMMAND+'; match all year/region denominators, category medians and original-versus-unchanged-negative AUROCs.',
        dict(sample_support=pd.read_csv(diag/'sample-support.csv').to_dict('records'),magnitude_ranking=pd.read_csv(diag/'magnitude-ranking.csv').to_dict('records'),magnitude_medians=pd.read_csv(diag/'magnitude-medians.csv').to_dict('records')),True,
        sources=['S002','S003','S038'],implication='Annual high-change maps should not be presumed to rank these tree gains above unchanged vegetation, and this small year-concentrated sample cannot establish broad gain transfer.')
    review_scopes={
      'C001':('R1-1/R1-2/R1-8','CONUS one-year pairs only; gain evidence chiefly2019–2020(21positives), with3in2020–2021. Continental baseline pool58assigned reference/58control plots, reduced outside each fold; low reference variation and high score similarity limit this correction test. No multi-year/local-reference generalization.'),
      'C002':('R1-2','Original four-condition point comparison; gain positives concentrated21/3by pair, with sparse regional negatives. No broad multi-year gain-transfer claim.'),
      'C003':('R1-2/R1-3/R1-4','One-year CONUS labelled sample, predominantly first gain pair. Published AlphaEarth training uses NLCD weak supervision, with v2.0/v2.1 differences and unverified mosaic encoder lineage; this and timing/support are possible explanations, not identified mechanisms. Similar TESSERA pattern is a contrast, not matched training replication.'),
      'C005':('R1-3/R1-4','Same one-year/year-concentrated sample. Persistence after changing negatives does not isolate training-target dependence, annual timing or physical growth.'),
      'C009':('R1-2/R1-3','Gain evidence concentrated21/3across original pairs. AlphaEarth dated representations may be affected by land-cover-map weak supervision; exact mosaic encoder lineage is unverified. TESSERA is a contrasting published self-supervised design, not an ablation. No independence from training targets established.'),
      'C012':('R1-3/R1-4','Annual NLCD reference annotations are a different product from the NLCD map targets used for AlphaEarth training, but share a class system and may share imagery; independence from training-target information is not established. The mosaic encoder lineage is not verified beyond product family. One-year intervals, later gain n7.'),
      'C014':('R1-1/R1-8','Same small continental pooled baseline reference construction; changing geographic access is not a local-reference-ecosystem test or proof of drift correction.'),
      'C017':('R1-2/R1-3','Original gains are year-concentrated21/3. AlphaEarth weak land-cover supervision and unverified exact encoder lineage limit dated-vector interpretations and Forest training-target independence; TESSERA supplies a design contrast, not a causal ablation.'),
      'C018':('R1-1','All perturbations retain the same one-year continental reference construction and test cases. High unsupervised score similarity is expected; changed J signs do not prove a general failure of correction under larger drift.')}
    for item in claims:
        if item['claim_id'] in review_scopes:
            point,extra=review_scopes[item['claim_id']];item['scope']+=' '+extra;item['revision_reason']='Scope clarified after '+point+'; observed original counts/status preserved.';item['review_response']='review/response-1.md'
        if item['claim_id']=='C003':
            item['text']+=' Primary magnitude AUROC ranks gains below the original non-tree negatives in both products; unchanged-only post-review comparisons are separately exploratory in C020.'
            item['expected']=records(mag,['model','support','task','n_positive','n_negative','true_positive','false_positive','sensitivity','false_positive_rate','auroc'])
        if item['claim_id'] in ['C009','C012','C017']:item['source_ids']=list(dict.fromkeys(item['source_ids']+['S002','S003','S038']))
    breach=json.loads((ROOT/'manifest.json').read_text())['resource_limit_breaches'][0]
    add('P001',f"The recorded experiment process count exceeded the permitted {breach['permitted']} for a {breach['registered_overlap_seconds']:g}-second interval, reaching {breach['registered_peak']}; a locked launch guard was subsequently added.",
        ['experiments/fetch-nlcd-aef-008-011/run.json','experiments/fetch-nlcd-aef-012-015/run.json','experiments/fetch-tessera-033/run.json','manifest.json','protocol/deviations.md'],
        ['fetch-nlcd-aef-008-011','fetch-nlcd-aef-012-015','fetch-tessera-033'],
        'Registered start/end times are self-reported; actual HTTP concurrency was not instrumented. This is a procedural breach, not a claim of full resource compliance.',
        'Compare the three run intervals and manifest.resource_limit_breaches; scripts/report.py records summarizes registered concurrency.',
        dict(permitted=breach['permitted'],recorded_peak=breach['registered_peak'],registered_overlap_seconds=breach['registered_overlap_seconds']))
    errors=[]
    for line in (ROOT/'data/aef-retrievals.jsonl').read_text().splitlines():
        r=json.loads(line)
        if r.get('status')=='error' and 'is not in the subpath' in (r.get('error') or ''):errors.append(r)
    add('P002','The original additional-control retrieval lost returned arrays during metadata construction; failed records remain and scientific analyses use the later fixed-sample repair.',
        ['experiments/fetch-controls-aef/run.json','data/aef-retrievals.jsonl','experiments/fetch-controls-aef-repair/run.json','manifest.json'],
        ['fetch-controls-aef','fetch-controls-aef-repair'],
        'Recorded completed error attempts; an unrecorded in-flight request at timeout is possible. Lost arrays are not recovered or used as scientific evidence.',
        'Count AEF retrieval error rows containing the recorded relative-path error; inspect repair records and missing_records.',
        dict(recorded_failed_attempts=len(errors),distinct_task_ids=len({r['task_id'] for r in errors})))
    path=ROOT/'claims.jsonl';path.write_text(''.join(json.dumps(clean(r),ensure_ascii=False,allow_nan=False)+'\n' for r in claims))
    print(json.dumps(dict(claims=len(claims),scientific=sum(r['claim_id'].startswith('C') for r in claims),
                         exploratory=sum(r['exploratory'] for r in claims),updated_at_utc=stamp)))

if __name__=='__main__':write_claims()
