"""Author-written paper assembly. Every displayed result comes from saved outputs."""
import argparse,json
from pathlib import Path
import pandas as pd
from figures import LABELS,MODEL_LABELS,markdown_table
from record import ROOT
from paper_results import partition_results, additional,initial_context,extension_native,matched_direct
from report import latest_self_rerun,rerun_covers_current

def one(df,**where):
    for key,value in where.items():df=df[df[key]==value]
    assert len(df)==1,where
    return df.iloc[0]

def write_paper(output,first_draft=False):
    main=ROOT/'analysis/main-v1'
    m=pd.read_csv(main/'main-table.csv')
    pc=pd.read_csv(main/'paired-comparisons.csv')
    pc=pc[(pc.availability_mode=='paired')&(pc.support=='centre')&(pc.seed==14014)&(pc.reference_mode=='global')]
    primary=pc[pc.method.isin(['concurrent','control_adjusted'])]
    mg=lambda model,task,method:one(m,model=model,task=task,method=method)
    pp=lambda model,task,method:one(primary,model=model,task=task,method=method)
    gain=mg('aef','gain','start_fixed');loss=mg('aef','loss','start_fixed')
    n=int(gain.n_positive+gain.n_negative+loss.n_positive+loss.n_negative)
    concurrent=primary[primary.method=='concurrent'];control=primary[primary.method=='control_adjusted']
    flags=[]
    for model in ['aef','tessera']:
        parts=[]
        for task in ['gain','loss']:
            a=pp(model,task,'concurrent');b=pp(model,task,'control_adjusted')
            parts.append(f'{int(a.changed_flags)}/{int(b.changed_flags)} of {int(a.total_pairs)} {task} cases')
        flags.append(MODEL_LABELS[model]+': '+', '.join(parts))
    flagtext='; '.join(flags)
    endpoint=json.loads((ROOT/'analysis/endpoint-v13/summary.json').read_text())
    em=pd.read_csv(ROOT/'analysis/endpoint-v13/metrics.csv')
    em=em[em.support=='centre']
    stable=one(em,model='aef',task='gain',method='cosine_change')
    r14=pd.read_csv(ROOT/'analysis/reference-completeness-v14/metrics.csv')
    r14=r14[r14.support=='centre']
    r14changes=pd.read_csv(ROOT/'analysis/reference-completeness-v14/changes-versus-original.csv')
    assert r14changes.changed_scores.sum()==0
    newcontrast=one(r14,model='tessera',task='gain',method='concurrent').J-one(r14,model='tessera',task='gain',method='start_fixed').J
    oldcontrast=pp('tessera','gain','concurrent').delta_J
    direct=pc[pc.method=='direct_gradient_boosting']
    assert (direct.delta_J>0).all()
    forest=pd.read_csv(ROOT/'analysis/nlcd-v4/metrics.csv')
    forest=forest[(forest.support=='centre')&forest.availability_mode.str.endswith('_primary')]
    forestp=pd.read_csv(ROOT/'analysis/nlcd-v4/paired-comparisons.csv')
    forestp=forestp[(forestp.support=='centre')&forestp.availability_mode.str.endswith('_primary')]
    forest_direct=forestp[forestp.method=='direct_gradient_boosting']
    frow=lambda model,task,method,horizon:one(forest,model=model,task=task,method=method,
        availability_mode=f'nlcd_{horizon}_primary')
    forestflags=[]
    for model in ['aef','tessera']:
        parts=[]
        for horizon,label in [('overlapping_2019_2021','2020–2021'),('beyond_2021','2022–2023')]:
            for task in ['gain','loss']:
                q=forestp[(forestp.model==model)&(forestp.task==task)&(forestp.availability_mode==f'nlcd_{horizon}_primary')]
                a=one(q,method='concurrent');b=one(q,method='control_adjusted')
                parts.append(f'{label} {task} {int(a.changed_flags)}/{int(b.changed_flags)} of {int(a.total_pairs)}')
        forestflags.append(MODEL_LABELS[model]+': '+', '.join(parts))
    fg=frow('aef','gain','start_fixed','overlapping_2019_2021')
    late_a=frow('aef','gain','cosine_change','beyond_2021');late_t=frow('tessera','gain','cosine_change','beyond_2021')
    initial_m=pd.read_csv(ROOT/'analysis/initial-vector-v17/metrics.csv')
    initial_a=one(initial_m,model='aef',task='gain',method='initial_state_random_forest')
    initial_t=one(initial_m,model='tessera',task='gain',method='initial_state_random_forest')
    matched_m=pd.read_csv(ROOT/'analysis/direct-inputs-v23/metrics.csv')
    before_a=one(matched_m,model='aef',task='gain',method='direct_before')
    before_t=one(matched_m,model='tessera',task='gain',method='direct_before')
    split_ranges=pd.read_csv(ROOT/'analysis/partition-sensitivity-v24/primary-ranges.csv')
    split_corrections=split_ranges[split_ranges.method.isin(['concurrent','control_adjusted'])]
    split_sign_changes=int(((split_corrections.delta_J_min<0)&(split_corrections.delta_J_max>0)).sum())
    split_direct_loss=one(split_ranges,model='tessera',task='loss',method='direct_gradient_boosting')
    split_metrics=pd.read_csv(ROOT/'analysis/partition-sensitivity-v24/metrics.csv')
    split_aef_magnitude=split_metrics[(split_metrics.model=='aef')&(split_metrics.support=='centre')&(split_metrics.task=='gain')&(split_metrics.method=='cosine_change')]
    native_identity=json.loads((ROOT/'analysis/native-single-date-v22/identity/summary.json').read_text())
    identical_centre=next(r['identical_vectors'] for r in native_identity['input_counts'] if r['support']=='centre')
    abstract=(f'Tree-cover screening can support restoration monitoring, but reference-similarity changes in satellite embeddings need validation against the cover transitions being screened. '
        f'We retrospectively compared fixed and concurrent references, independent tree controls and learned readouts using AlphaEarth V1 mosaic and TESSERA v1. '
        f'All cases supplied the initial class. The US LCMAP test had {n} pairs ending 2020–2021: {int(gain.n_positive)} gain positives/{int(gain.n_negative)} negatives and {int(loss.n_positive)} loss positives/{int(loss.n_negative)} negatives. '
        f'At a nominal 10% earlier-negative calibration false-positive rate, concurrent-reference differences in Youden’s J ranged from {concurrent.delta_J.min():+.3f} to {concurrent.delta_J.max():+.3f}; tree-control differences ranged from {control.delta_J.min():+.3f} to {control.delta_J.max():+.3f}. '
        f'Changed flags for concurrent/controls were {flagtext}. '
        f'The direct classifier had higher J point estimates than start-fixed in all {len(direct)} LCMAP conditions. Cosine magnitude detected {int(stable.true_positive)}/{int(gain.n_positive)} LCMAP gains in either product, including preplanned patch support. '
        f'The separate NLCD Forest test also lacked a consistent correction benefit; the direct classifier had higher J point estimates than start-fixed in {int((forest_direct.delta_J>0).sum())}/{len(forest_direct)} conditions. '
        f'Forest changed flags (concurrent/controls) were {"; ".join(forestflags)}. '
        f'Forest centre magnitude detected no overlapping gains ({int(fg.n_positive)} per product); later scores detected {int(late_a.true_positive)}/{int(late_a.n_positive)} AlphaEarth and {int(late_t.true_positive)}/{int(late_t.n_positive)} TESSERA gains. '
        f'Exploratory matched direct learners had LCMAP gain J point estimates {before_a.J:.3f}/{before_t.J:.3f} using only initial target vectors; later-state accuracy alone does not measure dependence on subsequent target-vector values. '
        f'Exploratory fitting/calibration perturbations make {split_sign_changes}/{len(split_corrections)} correction contrasts span both signs; the direct TESSERA loss advantage holds in {int(split_direct_loss.positive_directions)}/{int(split_direct_loss.available_partitions)} fixed splits, and AlphaEarth centre-magnitude gain detections range from {int(split_aef_magnitude.true_positive.min())}/{int(gain.n_positive)} to {int(split_aef_magnitude.true_positive.max())}/{int(gain.n_positive)}. '
        f'An exploratory single-date native-input check changed flags in {native_identity["changed_pairs"]}/{native_identity["pairs"]} available pairs ({identical_centre}/{native_identity["pairs"]} centre inputs identical); full paired-native validation remained unfinished. '
        'These retrospective results support validation of endpoints, input periods and transferred thresholds; forecasting and ecological restoration success were not measured.')
    title=(ROOT/'paper-methods.md').read_text().splitlines()[0]
    methods='\n'.join((ROOT/'paper-methods.md').read_text().splitlines()[4:])
    retrieval_dates=sorted({json.loads(line)['requested_at_utc'].split('T')[0] for model in ['aef','tessera'] for line in (ROOT/f'data/{model}-retrievals.jsonl').read_text().splitlines() if json.loads(line).get('status')=='saved'})
    methods=methods.replace('Source URLs, version metadata', 'Inputs were retrieved on '+', '.join(retrieval_dates)+' (UTC). Source URLs, version metadata')
    metadata=json.loads((ROOT/'analysis/main-v1/embedding-metadata.json').read_text())
    spacing={m:sorted({abs(row['transform'][0]) for row in metadata if row['model']==m}) for m in ['aef','tessera']}
    assert all(len(v)==1 for v in spacing.values())
    assert all(abs(row['transform'][0])==abs(row['transform'][4]) for row in metadata)
    methods=methods.replace("The geographic mosaic's footprint varies with latitude", f"The mosaic has approximately {spacing['aef'][0]:.8f} degrees per pixel in each axis; the retrieved TESSERA grid has {spacing['tessera'][0]:g}-metre pixels in its projected CRS. The geographic mosaic's footprint varies with latitude")

    methods=methods.replace('The same target partitions are offered to all methods, although their actual use of earlier labels differs.',
        'The 2019 endpoint of the earlier pairs overlaps the first later pair’s starting year in other regions. Later target plots are never used in fitting. The same target partitions are offered to all methods, although their actual use of earlier labels differs.')
    av=pd.read_csv(main/'availability-targets.csv');a=av[(av.model=='aef')&(av.support=='centre')]
    planned=len(a);available=int(a.common_pair_available.sum());missing=a[~a.common_pair_available]
    assert (missing.before_year<=2018).all()
    assert av[av.before_year>=2019].groupby(['model','support']).common_pair_available.sum().eq(n).all()
    early=int(((a.before_year<=2018)&a.common_pair_available).sum())
    pred_main=pd.read_parquet(main/'predictions.parquet')
    pred_main=pred_main[(pred_main.availability_mode=='paired')&(pred_main.model=='aef')&(pred_main.support=='centre')&(pred_main.seed==14014)&(pred_main.reference_mode=='global')&(pred_main.method=='start_fixed')]
    positive_cells={task:int(pred_main[(pred_main.task==task)&(pred_main.truth==1)].block.nunique()) for task in ['gain','loss']}
    fmt={k:lambda v:'NA' if pd.isna(v) else f'{v:.3f}' for k in ['sensitivity','false_positive_rate','J','auroc','delta_J']}
    table=m[m.method.isin(['start_fixed','concurrent','control_adjusted'])].copy()
    table['model']=table.model.map(MODEL_LABELS);table['method']=table.method.map(LABELS)
    table['tp']=[f'{int(a)}/{int(b)}' for a,b in zip(table.true_positive,table.n_positive)]
    table['fp']=[f'{int(a)}/{int(b)}' for a,b in zip(table.false_positive,table.n_negative)]
    operating=markdown_table(table,{'model':'Representation','task':'Task','method':'Readout',
        'tp':'True positives / positives','fp':'False positives / negatives','sensitivity':'Sensitivity',
        'false_positive_rate':'False-positive rate','J':'J'},fmt)
    contrasts=primary.copy();contrasts['model']=contrasts.model.map(MODEL_LABELS);contrasts['method']=contrasts.method.map(LABELS)
    contrasts['interval']=[f'{a:.3f} to {b:.3f}' for a,b in zip(contrasts.delta_J_lo,contrasts.delta_J_hi)]
    contrasts['changed']=[f'{int(a)}/{int(b)}' for a,b in zip(contrasts.changed_flags,contrasts.total_pairs)]
    contrasttable=markdown_table(contrasts,{'model':'Representation','task':'Task','method':'Readout versus start-fixed',
        'delta_J':'J difference','interval':'Conditional 95% interval','changed':'Changed flags / cases'},fmt)
    learned=m[m.method.isin(['direct_gradient_boosting','state_random_forest','subsequent_state_random_forest','subsequent_state_logistic','subsequent_reference_similarity','cosine_change'])].copy()
    learned['model']=learned.model.map(MODEL_LABELS);learned['method']=learned.method.map(LABELS)
    learned['tp']=[f'{int(a)}/{int(b)}' for a,b in zip(learned.true_positive,learned.n_positive)]
    learned['fp']=[f'{int(a)}/{int(b)}' for a,b in zip(learned.false_positive,learned.n_negative)]
    learnedtable=markdown_table(learned,{'model':'Representation','task':'Task','method':'Readout','tp':'True positives / positives',
        'fp':'False positives / negatives','sensitivity':'Sensitivity',
        'false_positive_rate':'False-positive rate','J':'J','auroc':'AUROC'},fmt)
    additions,appendix=additional()
    context=initial_context()
    extension,extension_appendix=extension_native()
    matched,matched_appendix=matched_direct()
    split_results=partition_results()
    status=('**First draft.** The fixed paired-native check remains unfinished; its empty counts are not robustness evidence.' if first_draft else
        '**Working draft.** Main and boundary analyses are complete; the fixed paired-native check is unfinished. Final self-assessment and end-to-end verification remain in progress. This is not the submitted first draft.')
    manifest=json.loads((ROOT/'manifest.json').read_text());critic_model=manifest['api']['critique_model_returned']
    api_records=[json.loads(line) for line in (ROOT/'api_calls.jsonl').read_text().splitlines()]
    critic_date=api_records[-1]['requested_at_utc'].split('T')[0]
    rerun='The end-to-end procedure has not yet been run.'
    rerun_path,result=latest_self_rerun()
    if result:
        coverage='It covers the current numerical code.' if rerun_covers_current(result) else 'Later numerical additions remain outside that candidate and require an expanded rerun.'
        rerun=f'The recorded end-to-end self-rerun returned {result["status"]}. {coverage} This is a rerun by the authoring AI session, not independent reproduction. Details and runtime are in {rerun_path.relative_to(ROOT)}.'
    text=f'''{title}

{status}

## Abstract

{abstract}

{methods}

## 4. Results

### 4.1 Availability and task definition

The fixed main sample contains {planned} target pairs. Both products supply valid paired vectors for {available}; {len(missing)} earlier pairs are unavailable in TESSERA. The resulting paired analysis has {early} earlier fitting/calibration candidates and {n} later test pairs. All later test pairs are available for both centre and patch support. Every test supplies the interpreted initial cover class. Gain and loss are therefore conditional tasks, with the denominators shown below. The positive gain and loss cases occupy {positive_cells["gain"]} and {positive_cells["loss"]} five-degree cells, respectively, counted during self-check to clarify spatial support. No population precision or national transition frequency is estimated.

### 4.2 Primary reference and control contrasts

Table 1 reports the original nominal calibration operating point. A modest change in recall is not automatically an improvement if false positives also increase. Concurrent reference and tree-control effects differ across the four product/task conditions. The point estimates do not support a consistent benefit. The gain intervals remain wide; these observations do not establish equivalence or zero population effects.

{operating}

Table 2 retains every primary contrast and its decision count. The intervals condition on fitted scores and the observed reference pool and are not adjusted for multiple comparisons. Most flags are unchanged, making the small differences in calibration consequential. Neither statistical significance nor an equivalence margin was a stopping or selection rule.

{contrasttable}

### 4.3 Information in the vectors and comparator limits

The prespecified direct transition classifier has higher J point estimates than start-fixed in all {len(direct)} product/task conditions. State probability differences and subsequent-state readouts behave differently. These results show that useful information for the supplied cover labels can coexist with a weak scalar change readout. They do not demonstrate equal annotation cost: learned methods use additional earlier target labels, while reference scores use baseline-selected cohorts and negative calibration labels. Predicting the subsequent state is a necessary comparator because the initial class is supplied by the task definition.

{learnedtable}

![Screening operating points under the earlier-negative calibration rule](figures/operating-points.png)

### 4.4 Endpoint composition and reference availability: exploratory checks

The gain-negative definition includes {int(endpoint['excluded_later_gain_negatives'])} later Grass/Shrub transitions. Removing them from this separate calibration/test condition leaves {int(stable.n_negative)} unchanged-cover negatives and {int(stable.n_positive)} gain positives. Cosine change magnitude still detects {int(stable.true_positive)} gains for AlphaEarth; the full two-product table is analysis/endpoint-v13/stable-negative-gain-table.md. Fitted scores are unchanged on all common cases. Within this sample, the floor persists after removing those transitions. Its biological, temporal or spatial-support cause remains unresolved.

Before/after similarity components reconstructed from saved scores agree with direct raw-vector calculations to a maximum absolute error of {endpoint['maximum_scalar_reconstruction_error']:.3g}. The scalar plot shows where the change readout differs from an absolute subsequent-state score. It does not measure ecological condition or establish that either the labels or representations are wrong.

![Before and after cosine similarity to the start-year reference](analysis/endpoint-v13/reference-similarity.png)

The same-reference-plots check changes the TESSERA gain concurrent-reference J contrast from {oldcontrast:+.3f} to {newcontrast:+.3f}. Target test scores remain fixed; earlier calibration inputs and thresholds change. Original separately-valid reference means remain primary. This sensitivity limits claims about a general advantage or disadvantage of concurrent references.

{additions}

{context}

{extension}

{matched}

{split_results}

## 5. Discussion

The measurement decision matters more than whether a reference trajectory looks smooth. A constant control subtraction preserves within-year/region rankings by construction; transferred thresholds can nevertheless change alerts. Here the primary point estimates are small and mixed, and an availability sensitivity changes one contrast’s sign. Applying a concurrent centroid or removing a control mean is therefore insufficient evidence that a tree-cover screen has improved.

The loss/gain asymmetry requires endpoint-specific interpretation. A magnitude score can respond to many changes, while a tree-gain label describes a particular transition. Even the unchanged-negative counterfactual leaves the observed gain floor, and supplied initial states make subsequent-state classification informative. The data do not establish a mechanism for the asymmetry. Gradual changes crossing a dominant-cover boundary, differences between plot and pixel support, annual timing, and stable contextual information in representations remain possible explanations. None is confirmed by this experiment.

Initial-vector state readouts make a further distinction necessary. Performance on a subsequent label need not all depend on the subsequent target-vector values. Initial vectors can already associate with later transitions in this retrospective, enriched sample. Coordinate-only results show one measured geographic association, without explaining the embedding results. Conversely, the subsequent vector improves several gain readouts and the loss state forest. The evidence supports reporting both input periods and readouts, without calling initial-only discrimination forecasting, leakage or a benchmark defect.

Holding the direct learner and transition target fixed retains the distinction between gain and loss input requirements in the observed samples. Difference-only inputs have different point behaviour for gains and losses, and both-date inputs are not uniformly the strongest operating point. This is additional exploratory evidence for checking the input construction and endpoint together, rather than treating the scalar magnitude floor as absence of all predictive information in vector differences. Shared fitting, unequal feature dimensions, data reuse and conditional uncertainty prevent a general causal or optimality conclusion.

The fitting/calibration partition check shows that earlier data assignment can change the sign of every primary correction contrast while leaving its unsupervised test scores fixed. The original direct-learner advantage also has a TESSERA loss boundary across these splits. Reporting conditional test-case intervals alone therefore misses a measured source of operating-point sensitivity. These overlapping perturbations do not quantify independent training-sample uncertainty or identify whether fitting versus calibration drives changes in learned readouts.

A negative result for this cover-transition endpoint does not reject sensitivity to useful within-class ecological changes that the labels do not measure. Conversely, successful cover classification cannot validate restoration recovery. Practitioners should evaluate the intended endpoint, false-positive budget and temporal/geographic transfer rather than treating a change in reference similarity as self-validating progress.

## 6. Limitations

The samples are enriched benchmarks and the gain denominators are small. All initial classes are given without mapping error. The products and labels were made after some represented years; temporal holdout concerns downstream readouts, with an overlapping boundary year, not historical deployment or encoder pretraining isolation. Input representations and human interpretation may share satellite information. Ecological field outcomes, causal interventions, practitioners’ decisions and benefits to users are not measured.

Baseline Trees plots are not verified reference ecosystems and can change after selection. Partial additional cover labels cannot verify full annual histories or within-class stability. Geographic nearest controls can remain distant after region holdout. The primary AlphaEarth input is an unofficial geographic mosaic; a co-location diagnostic cannot substitute for a full native-grid classification evaluation. Reference, supervised and baseline-cohort methods use different labelled cohorts and calendar coverage, so their differences do not isolate annotation efficiency.

Bootstrap intervals condition on the observed fitted scores and reference pool and omit training, encoder and independent future-year uncertainty. An observed zero sensitivity can yield a degenerate interval; it is not evidence of zero population sensitivity. Products, versions, sample definitions, support, threshold rules and retrieval dates delimit every empirical claim. The NLCD endpoint differs in definition, sample and horizon and remains separate.

The process record discloses a brief breach of the concurrent-experiment limit and a later launch guard, retained acquisition/reporting failures and incomplete raw records from one failed retrieval. These records permit inspection; local Git, timestamps and hashes do not demonstrate independent chronology or reproduction.

Topic selection consulted one required critique from another model, OpenAI {critic_model}, on {critic_date}. That model did not write or review the paper. The paired-native test was not completed by the acquisition cutoff; the saved single-date alternative does not resolve full native-grid transfer.

## 7. Reproduction and data attribution

VERIFY.md describes the offline entry point. {rerun} Selected raw measurements, public labels, fixed plans, code, predictions and failure records are bundled. No live data download or AI call is required to recompute the scientific estimates. The sole other-model generation was the permitted topic-candidate critique; it was not a paper review, research assistant or experimental model measurement.

The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. AlphaEarth data are CC BY 4.0; TESSERA v1 data are CC0; analysed LCMAP and Annual NLCD reference data are public domain. The full input archive contains unused components with separate terms. Source records distinguish relevant full-text checks from abstract-only search records.

## References

'''
    for r in json.loads((ROOT/'references.json').read_text()):
        text+=f"{r['authors']} ({r['year']}). [{r['title']}]({r['url']}). {r['venue']}.\n\n"
    text+='\n'+appendix+'\n'+extension_appendix+'\n'+matched_appendix
    output.write_text(text)
    print(json.dumps(dict(output=str(output),working_draft=not first_draft,words=len(text.split()),primary_cases=n)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'paper.md');p.add_argument('--first-draft',action='store_true')
    a=p.parse_args();write_paper(a.output,a.first_draft)
