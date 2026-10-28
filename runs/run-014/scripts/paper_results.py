"""Author-written result sections, with all displayed quantities read from outputs."""
import json
import pandas as pd
from record import ROOT
from figures import LABELS,MODEL_LABELS,markdown_table

F={k:lambda x:'NA' if pd.isna(x) else f'{x:.3f}' for k in ['J','auroc','sensitivity','false_positive_rate','delta_J','minimum','maximum','before_J','after_J']}
NAMES={**LABELS,'coordinate_direct_boosting':'Coordinate transition boosting',
       'coordinate_state_forest':'Coordinate state forest','coordinate_state_logistic':'Coordinate state logistic',
       'coordinates_only':'Coordinates only'}

def table(q,cols):
    q=q.copy()
    if 'model' in q:q['model']=q.model.map(lambda x:MODEL_LABELS.get(x,NAMES.get(x,x)))
    if 'method' in q:q['method']=q.method.map(lambda x:NAMES.get(x,x))
    if 'true_positive' in q:
        q['tp']=[f'{int(a)}/{int(b)}' for a,b in zip(q.true_positive,q.n_positive)]
        q['fp']=[f'{int(a)}/{int(b)}' for a,b in zip(q.false_positive,q.n_negative)]
    return markdown_table(q,cols,F)

def additional():
    sec=pd.read_csv(ROOT/'analysis/secondary-v2/metrics.csv')
    rob=pd.read_csv(ROOT/'analysis/robustness-paired-v12/metrics.csv')
    audit=pd.read_csv(ROOT/'analysis/robustness-paired-v12/partial-label-audit-summary.csv')
    p=pd.read_csv(ROOT/'analysis/main-v1/paired-comparisons.csv')
    p=p[(p.availability_mode=='paired')&p.method.isin(['concurrent','control_adjusted'])]
    ranges=p.groupby(['model','task','method']).agg(conditions=('delta_J','size'),minimum=('delta_J','min'),maximum=('delta_J','max'),
        positive=('delta_J',lambda x:int((x>0).sum())),negative=('delta_J',lambda x:int((x<0).sum())),zero=('delta_J',lambda x:int((x==0).sum()))).reset_index()
    q=sec[(sec.support=='centre')&sec.method.isin(['non_tree_control_adjusted','nearest8_non_tree_control_adjusted',
        'class_matched_control_adjusted','frozen_2017','frozen_2017_control_adjusted'])]
    sec_table=table(q,{'model':'Representation','task':'Task','method':'Readout','tp':'True positives / positives',
        'fp':'False positives / negatives','J':'J'})
    r=rob[(rob.support=='centre')&rob.method.isin(['baseline_cohort_logistic','baseline_cohort_random_forest','embedding_matched_controls'])]
    rob_table=table(r,{'model':'Representation','task':'Task','method':'Readout','tp':'True positives / positives',
        'fp':'False positives / negatives','J':'J'})
    range_table=table(ranges,{'model':'Representation','task':'Task','method':'Readout versus start-fixed',
        'conditions':'Sensitivity settings','minimum':'Minimum J difference','maximum':'Maximum J difference',
        'positive':'Positive','negative':'Negative','zero':'Zero'})
    access=pd.read_csv(ROOT/'analysis/reference-access-v20/paired-comparisons.csv')
    access=access[(access.support=='centre')&access.method.isin(['concurrent','control_adjusted'])].copy()
    access['interval']=[f'{a:.3f} to {b:.3f}' for a,b in zip(access.delta_J_lo,access.delta_J_hi)]
    access['changed']=[f'{int(a)}/{int(b)}' for a,b in zip(access.changed_flags,access.total_pairs)]
    access_table=table(access,{'model':'Representation','reference_mode':'Reference selection','task':'Task','method':'Readout versus start-fixed',
        'delta_J':'J difference','interval':'Conditional 95% interval','changed':'Changed flags / cases'})
    olddist=pd.read_csv(ROOT/'analysis/main-v1/nearest-reference-distances.csv')
    newdist=pd.read_csv(ROOT/'analysis/reference-access-v20/nearest-reference-distances.csv')
    select=lambda q:q[(q.model=='aef')&(q.support=='centre')].reference_k8_m
    oldmedian=select(olddist).median()/1000;newmedian=select(newdist).median()/1000
    neg=int((access[access.method=='concurrent'].delta_J<0).sum())
    body=f'''### 4.5 Alternative controls, calendar anchors and readouts

The preplanned non-tree, initial-class and frozen-calendar controls produce different operating points (Appendix A). Exact initial-class matching has fewer available cases, so its contrast must use the common-case denominators in the paired comparison file. A gain in its J cannot be compared by subtracting the full-sample start-fixed J. No control rule gives a consistent advantage across all products, tasks and available cases.

The preplanned reference allocations, centre/patch supports and global/nearest-reference conditions give the ranges below. These settings reuse the same targets and pool; their signs are sensitivity counts, not independent evidence or a vote for a method. All settings remain available in the machine-readable tables.

{range_table}

The original strict reference-region exclusion places the eighth-nearest reference a median {oldmedian:,.0f} km away in the centre-pixel sample. An exploratory condition allowing baseline reference/control plots from all regions reduces that median to {newmedian:,.0f} km. Target fitting and calibration remain region-held-out; the reference-label information access changes. The concurrent-reference J contrast is negative in {neg}/{len(access[access.method=='concurrent'])} centre conditions across global/nearest selection, while control effects vary (Appendix A). Supervised scores and flags are unchanged by construction and verified. References remain geographically broad and are not locally verified reference ecosystems, even under the relaxed access condition.

Exploratory baseline-cohort state classifiers use only the baseline reference/tree-control/non-tree-control cohorts for state fitting, while their thresholds still require earlier target-negative labels. They therefore reduce one source of state-fitting labels without establishing equal annotation budgets or zero transition-label dependence. Embedding-matched controls use initial-vector similarity rather than geographic distance. Their complete results are in Appendix A. Calibration at the additional five- and twenty-percent nominal levels changes some primary contrast directions; the original ten-percent rule remains primary.

The auxiliary classification release supplies {int(audit.later_labels.sum())} later labels among {int(audit.cohort.sum())} baseline-cohort plots, with {int(audit.later_binary_disagreement.sum())} known binary disagreements and {int(audit.unknown_later.sum())} unknown later labels. These are isolated annual observations, not complete histories. No primary plot is removed using those later labels.
'''
    appendix=f'''## Appendix A. Additional controls and exploratory readouts

These tables retain planned additional controls and the exploratory baseline-cohort/matching readouts. The exact class-matched condition has different availability. Full paired comparisons, calibration levels, year/region strata, all supports and all seeds are supplied as CSV files.

Preplanned additional controls and calendar anchors:

{sec_table}

Exploratory baseline-cohort and embedding-matched control readouts:

{rob_table}

Exploratory baseline-reference access including the target region, with target labels still held out:

{access_table}

![Operating points across exploratory calibration levels](figures/diagnostics/calibration-sensitivity.png)
'''
    return body,appendix

def initial_context():
    d=ROOT/'analysis/initial-vector-v17'
    m=pd.read_csv(d/'metrics.csv');p=pd.read_csv(d/'initial-versus-subsequent.csv')
    pairs={'initial_state_random_forest':'subsequent_state_random_forest',
           'initial_baseline_cohort_random_forest':'baseline_cohort_random_forest'}
    rows=[]
    for r in p[p.method.isin(pairs)].itertuples():
        a=m[(m.model==r.model)&(m.task==r.task)&(m.method==r.method)].iloc[0]
        b=m[(m.model==r.model)&(m.task==r.task)&(m.method==pairs[r.method])].iloc[0]
        rows.append(dict(model=r.model,task=r.task,method=r.method,
            before=f'{int(a.true_positive)}/{int(a.n_positive)}; {int(a.false_positive)}/{int(a.n_negative)}',
            after=f'{int(b.true_positive)}/{int(b.n_positive)}; {int(b.false_positive)}/{int(b.n_negative)}',
            before_J=a.J,after_J=b.J,delta_J=r.delta_J,
            interval=f'{r.delta_J_lo:.3f} to {r.delta_J_hi:.3f}',changed=f'{int(r.changed_flags)}/{int(r.total_pairs)}'))
    t=table(pd.DataFrame(rows),{'model':'Representation','task':'Task','method':'State fit',
        'before':'Before vector TP; FP','after':'After vector TP; FP','before_J':'Before J','after_J':'After J',
        'delta_J':'Before minus after J','interval':'Conditional 95% interval','changed':'Changed flags / cases'})
    perm=json.loads((d/'permutation-check.json').read_text())
    geo=pd.read_csv(ROOT/'analysis/geography-v18/metrics.csv')
    gt=table(geo,{'task':'Task','method':'Coordinate-only readout','tp':'True positives / positives',
        'fp':'False positives / negatives','J':'J','auroc':'AUROC'})
    body=f'''### 4.6 What requires the subsequent target vector? Exploratory diagnostics

Some gain discrimination remains when a state classifier receives only the initial target vector. The table compares the same fitted state model applied to the before and after vectors, each calibrated using its own earlier-negative scores. Both comparisons retain the same availability mask, which requires both products in both years. The state models were fitted using earlier labelled states, and the encoders and labels were produced retrospectively. These results are therefore associations in a dated representation, not prospective forecasts.

{t}

Changing the subsequent target-vector values in one fixed within-year permutation leaves all {int(perm['scored_rows'])} initial-only scored rows unchanged across {int(perm['mapped_target_keys'])} target keys. This verifies input dependence in the implementation; it is not another independent empirical replication. Initial reference similarity and baseline-cohort logistic counterparts, including their uncertainty, are retained in analysis/initial-vector-v17/initial-versus-subsequent.csv.

The after vector improves several gain readouts and improves the full state forest substantially for losses. Thus these results do not support the claim that all apparent change accuracy comes from initial information. They do show why subsequent-state classification accuracy alone cannot establish how much information about a transition was newly observed after the initial date.

The separate coordinate-only control uses four sine/cosine latitude/longitude features, with no embedding values, year or initial vegetation subclass as learner inputs. It yields the following associations on the same conditional sample. This is one geographic baseline, not two product replications. It cannot identify the source of information in the embeddings; weaker results would not exclude richer static landscape information.

{gt}
'''
    cl=pd.read_csv(ROOT/'analysis/initial-class-v19/metrics.csv')
    cr=cl[cl.task=='gain'].iloc[0];lr=cl[cl.task=='loss'].iloc[0]
    sub=pd.read_csv(ROOT/'analysis/initial-class-v19/subgroup-metrics.csv')
    sub=sub[(sub.task=='gain')&sub.method.isin(['initial_state_random_forest','subsequent_state_random_forest'])].copy()
    sub['initial_class']=sub.availability_mode.str.split('_initial_').str[-1].replace({'Grass_forb_herb':'Grass/forb/herb'})
    st=table(sub,{'model':'Representation','initial_class':'Initial vegetation class','method':'State readout',
        'tp':'True positives / positives','fp':'False positives / negatives','J':'J','auroc':'AUROC'})
    body+=f'''
The exploratory initial-class-rate baseline flags {int(cr.true_positive)}/{int(cr.n_positive)} gains and {int(cr.false_positive)}/{int(cr.n_negative)} negatives; {int(cr.threshold_ties)} gain-task cases tie their regional threshold. This simple baseline does not explain the initial-vector forest results: gains are flagged within both initial vegetation classes, as shown below. The original mixed-class thresholds are retained within each subgroup. Small subgroup denominators and richer interactions with landscape context remain limitations.

{st}

All {int(lr.n_positive+lr.n_negative)} loss-task cases begin as Trees. The class-rate score is constant within each regional fit, making zero loss flags a consequence of the task and threshold definition. This is not counted as a discovery. Region-specific estimates can differ, so the pooled score is not globally constant.
'''
    return body

def extension_native():
    folder=ROOT/'analysis/nlcd-v4'
    m=pd.read_csv(folder/'metrics.csv');p=pd.read_csv(folder/'paired-comparisons.csv')
    a=pd.read_csv(folder/'availability-targets.csv')
    primary=m[(m.support=='centre')&m.availability_mode.str.endswith('_primary')]
    primary_p=p[(p.support=='centre')&p.availability_mode.str.endswith('_primary')]
    rows=[]
    for r in primary[primary.method=='start_fixed'].itertuples():
        g=primary_p[(primary_p.model==r.model)&(primary_p.task==r.task)&(primary_p.availability_mode==r.availability_mode)]
        c=g[g.method=='concurrent'].iloc[0];t=g[g.method=='control_adjusted'].iloc[0]
        rows.append(dict(model=r.model,task=r.task,horizon='2020–2021' if 'overlapping' in r.availability_mode else '2022–2023',
            n=f'{int(r.n_positive)}/{int(r.n_negative)}',J=r.J,
            concurrent=f'{c.delta_J:+.3f} [{c.delta_J_lo:.3f}, {c.delta_J_hi:.3f}]',
            controls=f'{t.delta_J:+.3f} [{t.delta_J_lo:.3f}, {t.delta_J_hi:.3f}]',
            changed=f'{int(c.changed_flags)}/{int(t.changed_flags)} of {int(c.total_pairs)}'))
    ct=table(pd.DataFrame(rows),{'model':'Representation','horizon':'Pair end years','task':'Task','n':'Positive / negative',
        'J':'Start-fixed J','concurrent':'Concurrent J difference [interval]','controls':'Tree-control J difference [interval]',
        'changed':'Changed flags concurrent/control'})
    count=primary[primary.method=='start_fixed'].drop_duplicates(['availability_mode','task'])
    counttext='; '.join(f"{('2020–2021' if 'overlapping' in r.availability_mode else '2022–2023')} {r.task}: {int(r.n_positive)} positives/{int(r.n_negative)} negatives" for r in count.itertuples())
    summary=json.loads((folder/'summary.json').read_text())
    eq=pd.read_csv(folder/'threshold-equality.csv')
    source_pred=pd.read_parquet(folder/'predictions.parquet')
    late_gain=source_pred[(source_pred.availability_mode=='nlcd_beyond_2021_primary')&(source_pred.model=='aef')&(source_pred.support=='centre')&(source_pred.method=='start_fixed')&(source_pred.task=='gain')&(source_pred.truth==1)]
    late_gain_cells=int(late_gain.block.nunique())
    valid_boot=primary_p[(primary_p.task=='gain')&primary_p.availability_mode.str.contains('beyond')&primary_p.method.isin(['concurrent','control_adjusted'])].paired_bootstrap_valid
    assert valid_boot.nunique()==1
    ava=a[(a.model=='aef')&(a.support=='centre')]
    body=f'''### 4.7 Separate Forest-class endpoint and later years

The NLCD extension contains {int(summary['new_pairs'])} selected pairs from {int(summary['new_plots'])} plots. Paired centre availability is {int(ava.common_pair_available.sum())}/{len(ava)}. Its primary denominators are {counttext}. Pairs ending in 2020–2021 pairs overlap the original calendar range; 2022–2023 pairs extend it. Neither endpoint differences nor horizon differences can be attributed solely to time.

All {len(eq)} original-method threshold comparisons match the LCMAP calibration, with the added initial/cohort/coordinate/class-rate thresholds checked separately. No NLCD outcome enters fitting or calibration. The primary correction contrasts and counts are below. Intervals remain conditional descriptive block intervals; the small positive counts limit their interpretation. The later gain positives occupy {late_gain_cells} five-degree cells; the corresponding correction intervals retain {int(valid_boot.min())} valid draws after omitting resamples without both classes. These support counts were added during self-check; the original bootstrap draws and intervals are unchanged.

{ct}

The complete readouts, magnitude-score counts, initial-versus-subsequent comparisons and primary/alternate-agreeing subset are retained in Appendix B and the CSV outputs. Agreement means identical primary and alternate interpreted cover classes at both dates. It is not a verified confidence level, absence of within-class change or ecological recovery.
'''
    q=primary[primary.method.isin(['cosine_change','direct_gradient_boosting','subsequent_state_random_forest'])].copy()
    q['horizon']=q.availability_mode.map(lambda x:'2020–2021' if 'overlapping' in x else '2022–2023')
    mt=table(q,{'model':'Representation','horizon':'Pair end years','task':'Task','method':'Readout',
        'tp':'True positives / positives','fp':'False positives / negatives','J':'J'})
    initial=pd.read_csv(ROOT/'analysis/nlcd-initial-v17/metrics.csv')
    q=initial[initial.availability_mode.str.endswith('_primary')&initial.method.isin(['initial_state_random_forest','subsequent_state_random_forest',
        'initial_baseline_cohort_random_forest','baseline_cohort_random_forest'])].copy()
    q['horizon']=q.availability_mode.map(lambda x:'2020–2021' if 'overlapping' in x else '2022–2023')
    it=table(q,{'model':'Representation','horizon':'Pair end years','task':'Task','method':'State readout',
        'tp':'True positives / positives','fp':'False positives / negatives','J':'J','auroc':'AUROC'})
    agree=m[(m.support=='centre')&m.availability_mode.str.endswith('_unambiguous')&
        m.method.isin(['start_fixed','concurrent','control_adjusted','cosine_change'])].copy()
    agree['horizon']=agree.availability_mode.map(lambda x:'2020–2021' if 'overlapping' in x else '2022–2023')
    at=table(agree,{'model':'Representation','horizon':'Pair end years','task':'Task','method':'Readout',
        'tp':'True positives / positives','fp':'False positives / negatives','J':'J'})
    appendix=f'''## Appendix B. The separate NLCD Forest endpoint

All readouts retain LCMAP fitting/calibration. The complete method set, strata, paired contrasts and conditional intervals are in analysis/nlcd-v4, analysis/nlcd-initial-v17, analysis/nlcd-geography-v18 and analysis/nlcd-class-v19. The rows below are fixed primary methods, the standard magnitude/direct/state comparators, and the added input-period diagnostic. No winning condition is selected. Initially supplied classes and repeated plot-years remain part of the design.

Magnitude, direct and subsequent-state comparisons under primary labels:

{mt}

Initial versus subsequent state forest readouts under primary labels:

{it}

Primary/alternate-agreeing cover subset, reported separately:

{at}
'''
    if not (ROOT/'analysis/native-v5/comparisons.csv').exists():
        return body+'\n### 4.8 Native-grid checks pending\n\nNative acquisition and analysis are still in progress. No agreement or paired-input result is inferred.\n',appendix
    native=pd.read_csv(ROOT/'analysis/native-v5/comparisons.csv')
    ns=pd.read_csv(ROOT/'analysis/native-v5/summary.csv')
    ns=ns[ns.group=='overall'].copy()
    ns['metric']=ns.metric.map({'centre_cosine':'Centre cosine','patch_cosine':'Patch cosine','pixel_centres_distance_m':'Pixel-centre distance (m)'})
    nf={k:lambda v:'NA' if pd.isna(v) else f'{v:.6f}' for k in ['minimum','q05','median','maximum']}
    nt=markdown_table(ns,{'metric':'Native/mosaic co-location metric','n':'Valid pairs','minimum':'Minimum','q05':'Fifth percentile',
        'median':'Median','maximum':'Maximum'},nf)
    valid=int(native.centre_valid.fillna(False).sum()) if 'centre_valid' in native else 0
    equal=int(native.raw_centre_equal.fillna(False).sum()) if 'raw_centre_equal' in native else 0
    body+=f'''### 4.8 Native-grid input co-location

Of {len(native)} fixed sampled point-years, {int(native.native_present.sum())} native patches were obtained, {valid} centres are valid in both inputs and {equal} raw centre vectors are exactly equal. Overall summaries are below; role/year/latitude strata and every selected slot remain in analysis/native-v5. Pixel-centre distances are in metres. Centre/patch cosine values compare representations at the same requested coordinates but potentially different footprints.

{nt}

This diagnostic neither re-fits the full study on native inputs nor tests stability of every small threshold contrast. Any disagreement confines the AlphaEarth estimates to the geographic mosaic actually evaluated. Cross-product differences cannot be attributed solely to encoders with their different input-processing paths.
'''
    incomplete=json.loads((ROOT/'analysis/native-pairs-v21/checks.json').read_text())
    partial=json.loads((ROOT/'data/native-available/summary.json').read_text())
    identity=json.loads((ROOT/'analysis/native-single-date-v22/identity/summary.json').read_text())
    inp=pd.read_csv(ROOT/'analysis/native-single-date-v22/identity/input-identity.csv')
    decisions=pd.read_csv(ROOT/'analysis/native-single-date-v22/identity/decision-identity.csv')
    sub=pd.read_csv(ROOT/'analysis/native-single-date-v22/summary.csv')
    centre_equal=int(inp[(inp.support=='centre')].vector_identical.sum())
    patch_equal=int(inp[(inp.support=='patch')].vector_identical.sum())
    body+=f'''
The separately fixed paired-native case check is unfinished: only {int(incomplete['present_point_years'])}/{int(incomplete['planned_point_years'])} point-years are available, leaving {int(incomplete['complete_native_file_pairs'])}/{int(incomplete['planned_pairs'])} complete pairs. Its empty counts are not evidence of unchanged decisions. Checking all saved original targets found no complete native pair, so the full paired comparison cannot be recovered from these measurements without additional acquisition.

An exploratory saved-data alternative replaces one available target date in each of {int(partial['selected_pairs'])} pairs, leaving its other date as a mosaic input. It contains {int(partial['groups'].get('gain_positive',0))} gain positive/{int(partial['groups'].get('gain_negative',0))} gain negative and {int(partial['groups'].get('loss_positive',0))} loss positive/{int(partial['groups'].get('loss_negative',0))} loss negatives; {int(partial['before_only'])} substitutions affect the before date and {int(partial['after_only'])} the after date. All fitting, references, controls and calibration remain mosaics. At least one flag changes in {int(identity['changed_pairs'])}/{int(identity['pairs'])} pairs across the retained readouts and supports. This is an availability-selected, mixed-footprint case test, not an estimate of full native-grid performance or which footprint is correct.

Identity counts added during self-check show {centre_equal}/{int(partial['native_point_years'])} identical centre vectors and {patch_equal}/{int(partial['native_point_years'])} identical patch vectors. Both gain-case centre inputs are identical, so their unchanged centre decisions are predictable, not robustness evidence. Subsequent-state scores can also stay fixed when only the initial date changes. Appendix C gives these counts for every readout and separates score identity from changed flags. The observed changes reinforce the geographic-mosaic scope of small AlphaEarth contrasts; paired-native transfer remains untested.
'''
    dt=table(decisions,{'support':'Support','task':'Task','method':'Readout','cases':'Cases','identical_input_cases':'Identical substituted inputs',
        'identical_scores':'Identical scores','changed_flags':'Changed flags'})
    appendix+=f'''\n## Appendix C. Saved single-date native input sensitivity

Only one date per pair is substituted; the other remains a mosaic vector. The fixed-pair native experiment remains incomplete. Identical-score tolerance is an absolute tolerance of 1e-12. Counts below refer to the same small set of pairs across multiple methods and are not independent observations. Full scores, common-case TP/FP counts and input identities are supplied in analysis/native-single-date-v22.

{dt}
'''
    return body,appendix

def matched_direct():
    a=pd.read_csv(ROOT/'analysis/direct-inputs-v23/metrics.csv')
    b=pd.read_csv(ROOT/'analysis/nlcd-direct-inputs-v23/metrics.csv')
    b=b[b.availability_mode.str.endswith('_primary')].copy()
    a['dataset']='LCMAP, end 2020–2021'
    b['dataset']=b.availability_mode.map(lambda x:'NLCD Forest, end 2020–2021' if 'overlapping' in x else 'NLCD Forest, end 2022–2023')
    metrics=pd.concat([a,b],ignore_index=True)
    p=pd.read_csv(ROOT/'analysis/direct-inputs-v23/contrasts.csv')
    e=pd.read_csv(ROOT/'analysis/nlcd-direct-inputs-v23/contrasts.csv')
    e=e[e.availability_mode.str.endswith('_primary')]
    allp=pd.concat([p,e],ignore_index=True)
    dif=allp[(allp.method=='direct_difference')&(allp.baseline_method=='direct_gradient_boosting')]
    gain=dif[dif.task=='gain'];loss=dif[dif.task=='loss']
    comp=p[p.baseline_method=='direct_gradient_boosting'].copy()
    comp['interval']=[f'{a:.3f} to {b:.3f}' for a,b in zip(comp.delta_J_lo,comp.delta_J_hi)]
    comp['changed']=[f'{int(a)}/{int(b)}' for a,b in zip(comp.changed_flags,comp.total_pairs)]
    ct=table(comp,{'model':'Representation','task':'Task','method':'Input versus both-date direct learner',
        'delta_J':'J difference','interval':'Conditional 95% interval','changed':'Changed flags / cases'})
    mt=table(metrics,{'dataset':'Test population','model':'Representation','task':'Task','method':'Direct input condition',
        'tp':'True positives / positives','fp':'False positives / negatives','J':'J','auroc':'AUROC'})
    text=f'''### 4.9 Matched direct-learner input comparison: exploratory

The initial-vector state diagnostic does not hold the training target and algorithm constant against the direct transition comparator. The later exploratory matched-learner analysis addresses that comparison: before-only, after-only, difference-only and original both-date inputs use the same earlier transition labels, learner hyperparameters, partitions and calibration rule. Input dimensions differ, so equal settings do not imply equal capacity. Original both-date scores/flags/thresholds are reconstructed exactly. Both endpoints had already been inspected before this amendment; the Forest results here are reused exploratory data, not a fresh validation.

The before-only input retains gain discrimination in the observed sample. Difference-only J is lower than both-date J in {int((gain.delta_J<0).sum())}/{len(gain)} gain conditions and higher in {int((loss.delta_J>0).sum())}/{len(loss)} loss conditions across the three separately reported populations and two products. These are descriptive point directions on shared fitted samples; conditional intervals often include zero, and no universal ordering or equivalence is established. A learned difference-vector readout can flag some LCMAP gains even when scalar magnitude flags none. Conversely, differencing alone does not give uniformly strong gain transfer. These results qualify interpretations based solely on either a magnitude score or a subsequent-state classifier.

![Matched direct-learner input comparisons](figures/direct-inputs.png)

Appendix D retains every input condition's operating point. The original LCMAP reduced-input contrasts below show uncertainty and changed decisions explicitly; the separate Forest contrasts and label-agreement subsets are in the supplied CSV files. Before-only results remain retrospective associations with dated vector values, not prospective forecasts or identification of the source of the information.

{ct}
'''
    appendix=f'''## Appendix D. Matched direct-learner operating points

All four fixed inputs are shown. Both-date input means the original concatenation of before, after and difference vectors. This amendment was fixed after inspecting both endpoints; all rows are exploratory and share earlier LCMAP fitting/calibration. Full conditional paired intervals, year/region strata, feature dimensions and threshold/reconstruction checks are in analysis/direct-inputs-v23 and analysis/nlcd-direct-inputs-v23. No winning input condition is selected.

{mt}
'''
    return text,appendix


def partition_results():
    folder=ROOT/'analysis/partition-sensitivity-v24'
    summary=json.loads((folder/'summary.json').read_text());ranges=pd.read_csv(folder/'primary-ranges.csv')
    magnitude=pd.read_csv(folder/'metrics.csv');magnitude=magnitude[(magnitude.method=='cosine_change')&(magnitude.task=='gain')]
    magnitude_ranges=magnitude.groupby(['model','support']).agg(minimum=('true_positive','min'),maximum=('true_positive','max')).reset_index()
    magnitude_text='; '.join(f"{MODEL_LABELS[r.model]} {r.support}: {int(r.minimum)}–{int(r.maximum)}" for r in magnitude_ranges.itertuples())
    nonzero=magnitude[(magnitude.model=='aef')&(magnitude.support=='centre')&(magnitude.true_positive>0)]
    nonzero_text='; '.join(f"seed {int(r.partition_seed)}: {int(r.true_positive)}/{int(r.n_positive)} true positives and {int(r.false_positive)}/{int(r.n_negative)} false positives" for r in nonzero.itertuples())
    q=ranges.copy();q['contrast_range']=[f'{a:+.3f} to {b:+.3f}' for a,b in zip(q.delta_J_min,q.delta_J_max)]
    q['directions']=[f'{int(a)}/{int(b)}/{int(c)}' for a,b,c in zip(q.positive_directions,q.zero_directions,q.negative_directions)]
    q['case_range']=[f'{int(a)}–{int(b)} / {int(c)}–{int(d)}' for a,b,c,d in zip(q.positive_cases_min,q.positive_cases_max,q.negative_cases_min,q.negative_cases_max)]
    q['changed_range']=[f'{int(a)}–{int(b)}' for a,b in zip(q.changed_flags_min,q.changed_flags_max)]
    rendered=table(q,{'model':'Representation','task':'Task','method':'Readout versus start-fixed','available_partitions':'Available partitions',
        'contrast_range':'J difference range','directions':'Positive/zero/negative directions','case_range':'Positive / negative case ranges','changed_range':'Changed flags range'})
    return f'''### 4.10 Earlier fitting/calibration partition sensitivity: exploratory

The final exploratory check completed all {summary['completed_partitions']} fixed earlier geographic-cell assignments: the original partition and its {summary['completed_partitions']-1} perturbations. Reference cohorts, model settings, later tests and the calibration rule remain fixed. The original condition reconstructs {summary['original_reconstructed_prediction_rows']} prediction rows and {summary['original_reconstructed_threshold_rows']} thresholds. Unsupervised score values on common keys are unchanged; their transferred decisions can vary through calibration. Learned scores can also vary through fitting.

The table retains every centre primary correction and direct-learner contrast. Its range is over these overlapping conditions, not an uncertainty interval or a selection of a best split. Positive/negative direction counts are not independent replications. Case ranges show whether differing availability could explain contrasts. There are {summary['available_method_fold_conditions']}/{summary['expected_method_fold_conditions']} available method/fold conditions across all readouts/supports; {summary['missing_threshold_record_conditions']} lack a threshold record and {summary['invalid_threshold_conditions']} have invalid calibration. Unavailable conditions are retained in the output rather than replaced.

{rendered}

Magnitude-score gain true-positive ranges across these same partitions are {magnitude_text}. The nonzero AlphaEarth centre condition is {nonzero_text}. This bounds the original zero-count observation; the original partition is not replaced.

All partition-specific counts, operating points, conditional intervals, cell memberships, fitting counts and patch-support counterparts remain in analysis/partition-sensitivity-v24. This check examines one fitting/calibration choice; it does not estimate independent training-data, encoder or future-year variance. The original results remain primary.
'''
