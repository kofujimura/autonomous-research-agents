"""Revised paper after REVIEW-1, assembled from saved numerical outputs."""
import argparse,json,re
from pathlib import Path
import pandas as pd
from record import ROOT
from write_paper import write_paper,one
from paper_results import additional,initial_context,extension_native,matched_direct,partition_results
from figures import markdown_table,MODEL_LABELS,LABELS

NAMES={**LABELS,'start_fixed':'Fixed start-year reference','concurrent':'Year-matched reference','control_adjusted':'Control-mean adjustment','state_random_forest':'State-probability difference (forest)'}
FMT={name:lambda x:'NA' if pd.isna(x) else f'{x:.3f}' for name in ['J','sensitivity','false_positive_rate','auroc','delta_J','spearman_rho','median_positive','median_negative']}

def table(data,cols):
    q=data.copy()
    if 'model' in q:q['model']=q.model.map(lambda x:MODEL_LABELS.get(x,x))
    if 'method' in q:q['method']=q.method.map(lambda x:NAMES.get(x,x))
    return markdown_table(q,cols,FMT)

def revision(output):
    temp=ROOT/'verification-work/revision-base.md';temp.parent.mkdir(exist_ok=True)
    write_paper(temp,True);base=temp.read_text()
    d=ROOT/'analysis/review-diagnostics-r1';similar=pd.read_csv(d/'score-similarity.csv');pooled=similar[similar.period=='all']
    m=pd.read_csv(ROOT/'analysis/main-v1/main-table.csv');p=pd.read_csv(ROOT/'analysis/main-v1/paired-comparisons.csv');p=p[(p.availability_mode=='paired')&(p.support=='centre')&(p.seed==14014)&(p.reference_mode=='global')]
    primary=p[p.method.isin(['concurrent','control_adjusted'])];ga=one(m,model='aef',task='gain',method='start_fixed');gt=one(m,model='tessera',task='gain',method='start_fixed')
    loss=one(m,model='aef',task='loss',method='start_fixed');mag_a=one(m,model='aef',task='gain',method='cosine_change');mag_t=one(m,model='tessera',task='gain',method='cosine_change')
    sample=pd.read_csv(d/'sample-support.csv');years=sample[sample.dimension=='year'];regions=sample[sample.dimension=='region'];y19=one(years,task='gain',before_year=2019);y20=one(years,task='gain',before_year=2020)
    alert=[]
    for model in ['aef','tessera']:
        for task in ['gain','loss']:
            q=primary[(primary.model==model)&(primary.task==task)];a=one(q,method='concurrent');b=one(q,method='control_adjusted');alert.append(f'{int(a.changed_flags)} and {int(b.changed_flags)}')
    abstract=(f'Tree-cover change maps can guide verification, but their scores need validation for the cover transition of interest. '
      f'We retrospectively compared reference adjustments and classifiers for one-year transitions in the conterminous United States (CONUS) using AlphaEarth V1 mosaic and TESSERA v1, with initial classes supplied. '
      f'The LCMAP tests included {int(ga.n_positive+ga.n_negative)} gain cases and {int(loss.n_positive+loss.n_negative)} loss cases ({int(loss.n_positive)} losses); {int(y19.positive_pairs)} of {int(ga.n_positive)} gains occurred in 2019–2020 and {int(y20.positive_pairs)} in 2020–2021. A separate Annual NLCD Forest test used transferred thresholds. '
      f'At nominal 10% earlier-negative false-positive calibration, reference/control corrections changed Youden’s J by {primary.delta_J.min():+.3f} to {primary.delta_J.max():+.3f}, without consistent improvement. '
      f'For year-matched references and control-mean adjustment, respectively, changed decisions numbered {alert[0]} for AlphaEarth gains, {alert[1]} for losses; TESSERA counts were {alert[2]} and {alert[3]}. '
      f'Only {100*pooled.changed_alert_fraction.min():.1f}–{100*pooled.changed_alert_fraction.max():.1f}% of pooled test decisions changed, and rankings stayed similar (Spearman {pooled.spearman_rho.min():.3f}–{pooled.spearman_rho.max():.3f}; post-review diagnostic). '
      f'The fixed-reference score detected {int(ga.true_positive)} of {int(ga.n_positive)} AlphaEarth gains (AUROC {ga.auroc:.3f}) and {int(gt.true_positive)} TESSERA gains. Cosine magnitude detected no gains in either product and ranked gain plots below non-tree negatives (AUROC {mag_a.auroc:.3f}/{mag_t.auroc:.3f}). '
      f'The direct supervised classifier had higher J in all {len(p[p.method=="direct_gradient_boosting"])} original conditions, with unequal label resources. Exploratory partition changes reversed all {len(primary)} correction contrasts, qualifying that comparison. '
      'An exploratory post-review unchanged-only comparison retained the gain-ranking inversion. Reference-centroid variation was smaller than loss-target changes, and the data do not identify timing, training supervision or physical growth as its cause. '
      'These small-perturbation, one-year tests do not establish performance for multi-year restoration trajectories or ecological recovery.')
    split_ranges=pd.read_csv(ROOT/'analysis/partition-sensitivity-v24/primary-ranges.csv')
    split_corrections=split_ranges[split_ranges.method.isin(['concurrent','control_adjusted'])]
    split_loss=one(split_ranges,model='tessera',task='loss',method='direct_gradient_boosting')
    split_mag=pd.read_csv(ROOT/'analysis/partition-sensitivity-v24/metrics.csv');split_mag=split_mag[(split_mag.model=='aef')&(split_mag.support=='centre')&(split_mag.task=='gain')&(split_mag.method=='cosine_change')&(split_mag.true_positive>0)].iloc[0]
    before=base[:base.index('## Abstract')]
    methods=base[base.index('## 1. Introduction'):base.index('## 4. Results')]
    reference_counts=pd.read_csv(d/'reference-year-counts.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    methods=methods.replace('Half form the reference centroid and half separate tree controls, allocated by a fixed hash.',f'The baseline pool contains {len(refs)} plots: {len(refs)//2} reference plots and {len(refs)-len(refs)//2} separate control plots before region exclusions, allocated by a fixed hash. The annual valid counts outside each region are reported in Appendix E.')
    primary_table=m[m.method.isin(['start_fixed','concurrent','control_adjusted'])].copy()
    for q in [primary_table]:
        q['tp']=[f'{int(a)}/{int(b)}' for a,b in zip(q.true_positive,q.n_positive)];q['fp']=[f'{int(a)}/{int(b)}' for a,b in zip(q.false_positive,q.n_negative)]
    t1=table(primary_table,{'model':'Representation','task':'Task','method':'Change score','tp':'Detected / positive','fp':'False alerts / negative','sensitivity':'Sensitivity','false_positive_rate':'FPR','J':'J','auroc':'AUROC'})
    contrast=primary.merge(pooled[['model','task','method','spearman_rho']],on=['model','task','method'],validate='one_to_one')
    contrast['interval']=[f'{a:.3f} to {b:.3f}' for a,b in zip(contrast.delta_J_lo,contrast.delta_J_hi)];contrast['alerts']=[f'{int(a)}/{int(b)}' for a,b in zip(contrast.changed_flags,contrast.total_pairs)]
    t2=table(contrast,{'model':'Representation','task':'Task','method':'Adjustment versus fixed reference','delta_J':'J difference','interval':'Conditional95% interval','alerts':'Changed alerts / cases','spearman_rho':'Pooled rank correlation'})
    counts=[]
    for label,frame,col in [('Year pair',years,'before_year'),('Held-out region',regions,'region')]:
        for key,g in frame.groupby(col):
            gain=one(g,task='gain');lossr=one(g,task='loss')
            counts.append(dict(group=label,level=f'{int(key)}–{int(key)+1}' if col=='before_year' else str(int(key)),gp=int(gain.positive_pairs),gn=int(gain.negative_pairs),lp=int(lossr.positive_pairs),ln=int(lossr.negative_pairs),gc=int(gain.positive_cells)))
    support_table=markdown_table(pd.DataFrame(counts),{'group':'Grouping','level':'Pair / anonymous region','gp':'Gain positives','gn':'Gain negatives','lp':'Loss positives','ln':'Loss negatives','gc':'Gain-positive cells'})
    drift=pd.read_csv(d/'reference-drift.csv');adjacent=drift[(drift.interval=='one_year')&(drift.start_year<=2020)]
    targets=pd.read_csv(d/'target-magnitudes.csv');drift_rows=[]
    for (model,start),g in adjacent.groupby(['model','start_year']):
        q=targets[(targets.model==model)&(targets.before_year==start)&(targets.truth==1)]
        def magnitude(task):
            v=q[q.task==task].magnitude
            return f'{v.median():.3f} (n={len(v)})' if len(v) else 'unavailable'
        drift_rows.append(dict(model=model,pair=f'{start}–{start+1}',centroid=f'{g.centroid_dissimilarity.min():.4f}–{g.centroid_dissimilarity.max():.4f}',controls=f'{g.control_individual_median.min():.4f}–{g.control_individual_median.max():.4f}',gain=magnitude('gain'),loss=magnitude('loss')))
    drift_table=table(pd.DataFrame(drift_rows),{'model':'Representation','pair':'Year pair','centroid':'Reference-centroid dissimilarity range','controls':'Control-plot median range','gain':'Gain-target median','loss':'Loss-target median'})
    drange=drift[drift.interval=='one_year'].groupby(['model','start_year']).centroid_dissimilarity.agg(['min','max'])
    forest_body,forest_appendix=extension_native();forest_body=forest_body.split('### 4.8')[0]
    forest=pd.read_csv(ROOT/'analysis/nlcd-v4/metrics.csv');forest=forest[(forest.support=='centre')&forest.availability_mode.str.endswith('_primary')]
    fg=forest[(forest.task=='gain')&(forest.method=='start_fixed')]
    gain_ranking=pd.read_csv(d/'magnitude-ranking.csv');stable_ranking=gain_ranking[(gain_ranking.negative_definition=='unchanged_only')&(gain_ranking.period!='all')].copy();stable_ranking['pair']=stable_ranking.period.astype(int).map(lambda y:f'{y}–{y+1}')
    magnitude_table=table(stable_ranking,{'model':'Representation','pair':'Year pair','positive_pairs':'Gains','negative_pairs':'Unchanged negatives','median_positive':'Median gain magnitude','median_negative':'Median unchanged magnitude','auroc':'AUROC versus unchanged'})
    learnt=m[m.method.isin(['direct_gradient_boosting','state_random_forest','subsequent_state_random_forest','subsequent_state_logistic','subsequent_reference_similarity','cosine_change'])].copy()
    learnt['tp']=[f'{int(a)}/{int(b)}' for a,b in zip(learnt.true_positive,learnt.n_positive)];learnt['fp']=[f'{int(a)}/{int(b)}' for a,b in zip(learnt.false_positive,learnt.n_negative)]
    t3=table(learnt,{'model':'Representation','task':'Task','method':'Score / classifier','tp':'Detected / positive','fp':'False alerts / negative','sensitivity':'Sensitivity','false_positive_rate':'FPR','J':'J','auroc':'AUROC'})
    mag_loss=one(m,model='aef',task='loss',method='cosine_change');loss_fixed=one(m,model='aef',task='loss',method='start_fixed')
    adds,appendix_a=additional();context=initial_context();matched,appendix_d=matched_direct();partitions=partition_results()
    full_forest,native_appendix=extension_native();native_body='### Native-grid diagnostics\n'+full_forest.split('### 4.8',1)[1].split('\n',1)[1]
    const=pd.read_csv(d/'control-constancy.csv');same_year=similar[similar.period!='all']
    same_stable=gain_ranking[(gain_ranking.period=='all')&(gain_ranking.negative_definition=='unchanged_only')]
    ref_bounds=reference_counts.groupby('model').agg(rmin=('reference_valid','min'),rmax=('reference_valid','max'),cmin=('control_valid','min'),cmax=('control_valid','max')).reset_index()
    results=f'''## 4. Results

### 4.1 What the test sample supports

The original test has {int(ga.n_positive)} gain positives and {int(loss.n_positive)} loss positives. Gains are concentrated in 2019–2020: {int(y19.positive_pairs)} cases, versus {int(y20.positive_pairs)} in 2020–2021. The table gives every year-pair and region denominator; anonymous region identifiers are split indices, not regional rankings. The small second-pair and regional samples cannot establish broad temporal/geographic gain transfer. The separate later Forest test has few gains too. Initial cover class is supplied in every case.

{support_table}

### 4.2 Reference adjustments mostly preserve the original score

Table1 gives absolute discrimination as well as sensitivity and false-positive rate. AlphaEarth gain AUROC is close to chance under the fixed-reference direction; corrections do not make it a strong gain ranking. Table2 retains every primary correction contrast and decision count. The pooled Spearman range is {pooled.spearman_rho.min():.3f}–{pooled.spearman_rho.max():.3f}, with alert status changed in {100*pooled.changed_alert_fraction.min():.1f}–{100*pooled.changed_alert_fraction.max():.1f}% of cases. These similarity measurements were added after review. For the global control mean, subtraction is constant within region/year by construction (maximum measured SD {const.sd_subtraction.max():.2g}). Near-identical scores and few changed decisions limit the strength of the correction comparison; a lack of consistent benefit is not evidence against correction under substantial harmful drift.

{t1}

Table2. Correction minus fixed-reference J, conditional paired intervals and score similarity. Most decisions are unchanged. These intervals are not equivalence tests and omit fitting/reference uncertainty. Pooled similarity does not mean each year is equally similar: year-specific correlations and alert changes are retained, with changed shares up to {100*same_year.changed_alert_fraction.max():.1f}% in a smaller year-specific condition.

{t2}

### 4.3 How much annual variation was available to correct?

The post-review diagnostic reconstructs the original region-excluded, per-year-valid reference centroids. Values below are cosine dissimilarity (one minus the dot product). Centroid/control ranges span the five held-out regions; target medians pool original eligible paired cases in that year, with counts. Reference/control plots were Trees at baseline, not verified stable ecosystems in later years. Earlier target samples supply context, not extra test evidence.

{drift_table}

AlphaEarth centroid variation is small relative to the loss-target magnitude in these pairs. TESSERA's 2017–2018 centroid variation is larger than its next two adjacent pairs and lies in the earlier fitting/calibration period. Thus the products present different opportunities for an adjustment; neither variation identifies representation drift separately from physical change. Appendix E retains every fold/year count, individual reference/control variation, same-membership centroid check and descriptive2017-to-2023 comparisons. Multi-year target screening was not tested.

### 4.4 Reference direction, magnitude and supervised classification differ

The direct transition classifier has higher J point estimates than the fixed-reference direction in all four original product/task conditions. It uses more earlier labels, so this is not equal-budget superiority. Given initial cover, classifying the subsequent state is also a necessary comparator. For AlphaEarth losses, magnitude is much stronger than the reference direction: AUROC {mag_loss.auroc:.3f} versus {loss_fixed.auroc:.3f}, with sensitivities {mag_loss.sensitivity:.3f} versus {loss_fixed.sensitivity:.3f}. The asymmetry is observed on these labelled pairs, not a new universal property of vegetation change.

{t3}

![Screening sensitivity and false-positive rates](figures/operating-points.png)

For gains, magnitude AUROC is {mag_a.auroc:.3f} for AlphaEarth and {mag_t.auroc:.3f} for TESSERA on the original negatives. The inversion remains when the comparison uses unchanged non-tree plots only: pooled AUROCs are {same_stable.auroc.iloc[0]:.3f} and {same_stable.auroc.iloc[1]:.3f}. The descriptive year-pair table shows smaller median embedding changes for gain plots than unchanged grass/shrub plots in both products and both pairs, with only three gains in the second pair. Unchanged means the same interpreted cover class, not verified absence of within-class structural, seasonal or management change. These unchanged-only ranking diagnostics were added after review; no threshold or prediction was changed. The earlier unchanged-negative calibration sensitivity also retains its zero gain flags (Appendix F).

{magnitude_table}

### 4.5 Separate Forest-class test

{forest_body.split(chr(10),1)[1]}

Fixed-reference J is negative in {int((fg.J<0).sum())} of {len(fg)} gain conditions. The separate reference sample and its unchanged calibration are useful boundary checks, but AlphaEarth's NLCD training targets prevent calling its Forest endpoint independent of training-target information. The map targets and interpreted reference annotations are different products. No ecological restoration outcome is validated.

### 4.6 Exploratory input and calibration boundaries

The matched direct-learner input comparison retains before-only gain discrimination, while difference-only versus concatenated inputs behave differently for gains and losses. This does not establish forecasting or an information source; represented dates, training targets and retrospective encoder production matter. Full conditions, counts and conditional intervals remain in Appendix D.

All {len(split_corrections)} correction contrasts take both signs across the {int(split_loss.available_partitions)} fixed earlier fitting/calibration partitions. The direct TESSERA loss advantage holds in {int(split_loss.positive_directions)} of those partitions. The AlphaEarth centre-magnitude exception detects {int(split_mag.true_positive)} gain with {int(split_mag.false_positive)} false alerts in an alternative split, so the original zero count is not a universal floor. These exploratory conditions share targets and earlier data; they do not estimate independent training variance. Complete tables remain in Appendix F. Coordinate, initial-class, reference-access and native-input diagnostics have also moved there. The fixed paired-native test remains untested, not a completed robustness result.
'''
    discussion='''## 5. Discussion

The absolute scores matter before choosing a correction. In this labelled sample, a reference-forest direction ranks AlphaEarth gains near chance, and annual cosine magnitude ranks gains below the unchanged non-tree negatives. A high-change map therefore does not automatically screen these tree gains. Larger changes within an unchanged cover class may still describe useful phenomena that these labels do not measure. The losses have much larger embedding changes and are better ranked by magnitude. These are endpoint-specific observations on predominantly one gain year pair; they do not show that representations lack gain information, that gains are gradual, or that the labels are wrong.

The correction null is a limited comparison. Small centroid motion, highly correlated scores and mostly unchanged alerts make it unsurprising that changes in J are small. Control subtraction also preserves rankings within a fixed region/year by algebra. The measured transferred decisions can still change, including with earlier calibration choices; their signs are not guaranteed by that algebra. TESSERA's larger2017–2018 variation shows why calibration-period variation should be reported. We have not tested correcting large harmful representation shifts, ecologically matched local controls or multi-year restoration-start trajectories.

Possible explanations for the gain/loss pattern include cover-boundary timing, plot/pixel mismatch, stable landscape associations and training-target dependence. None is isolated here. The known AlphaEarth supervision described in §3.2 could contribute to dated-vector association or temporal smoothing. The similar TESSERA pattern shows that AlphaEarth's particular supervision is not necessary for the qualitative observation, without identifying a causal mechanism. The two products are informative contrasts, not matched independent replications of a training design.

Operational annual-change mapping already faces timing and gain/loss difficulties; the abstract-level Stehman comparison is consistent context, not proof that timing explains these observations. LandTrendr and CCDC use longer temporal information than a single annual pair. Their names identify established alternatives, without a performance comparison in this study. Similarly, the current Google Earth workflow motivates endpoint validation but was not benchmarked: its exact processing and thresholds, unlike our saved mosaic inputs, were not evaluated.

For restoration ecologists and land-cover monitoring teams, the supported decision is to validate the intended cover transition and alert threshold before using embedding change or reference similarity to select locations for imagery or field assessment. Report absolute sensitivity, false-positive rate, score ranking and year-specific counts, alongside any correction difference. Given an initial class, include subsequent-state and initial-date-only comparisons. These suggestions concern evaluation; benefits to users and ecological restoration success were not measured.

## 6. Limitations

Only one-year intervals in CONUS were classified. Twenty-one of24LCMAP gains belong to2019–2020 and only three to2020–2021, with small negative counts in some held-out regions. The gain conclusions chiefly describe the first pair. Later Forest gains are limited too; exact counts appear in §4.5. Descriptive multi-year reference drift is not a multi-year target-classification experiment. Enriched/capped samples do not estimate national prevalence, deployed precision or commission error.

The reference/control construction pools a small baseline-labelled sample across CONUS outside each held-out region. It is a broad reference direction, not a verified local reference ecosystem. Later cohort stability is unknown; isolated auxiliary labels do not establish full histories. Conclusions about corrections apply to that pooled construction, not arbitrary restoration-reference designs.

AlphaEarth uses land-cover weak supervision (§3.2); independence of its Forest endpoint from training-target information is not established. Product-familyV1 does not verify the unofficial mosaic's exact encoder lineage, and public production-model changes further limit an exact training-mechanism assignment. Supporting-observation periods were not independently verified. Encoders/labels were produced retrospectively, and a boundary year overlaps the earlier/later periods. Before-only association is not forecasting or proof of leakage. The native-grid paired check remains unfinished; single-date substitutions cannot validate full native performance.

Bootstrap intervals condition on fitted scores and the observed reference pool, omit training/encoder/future-year variance, and can collapse at error floors. Extra partitions and post-review diagnostics remain exploratory. The process retains a brief concurrency-limit breach, acquisition/reporting failures and lost arrays; those disclosures and local Git/hashes do not establish independent chronology. The planned review was by an AI agent; its reported rerun on the same machine is not an independent reproduction.
'''
    # Replace literal result counts in prose from source tables at rendering time.
    discussion=discussion.replace('Twenty-one of24LCMAP gains belong to2019–2020 and only three to2020–2021',f'{int(y19.positive_pairs)} of {int(ga.n_positive)} LCMAP gains belong to2019–2020 and only {int(y20.positive_pairs)} to2020–2021')
    reproduction=base[base.index('## 7. Reproduction'):base.index('## References')]
    reproduction=reproduction.replace('The sole other-model generation was the permitted topic-candidate critique', 'The authoring session’s sole other-model API generation was the permitted topic-candidate critique')
    reproduction+='The human supplied one planned review by an AI agent (review/review-1.md). Its reported rerun on the same machine and its model/settings are human-provided reports, not directly observed author measurements or independent reproduction. Author revisions and decisions are in review/response-1.md.\n\n'
    references=base[base.index('## References'):base.index('## Appendix A.')]
    # Existing full tables are retained; only their placement and terminology change.
    old_endpoint=base[base.index('### 4.4 Endpoint'):base.index('### 4.5 Alternative')].replace('### 4.4','### Endpoint composition and reference availability:')
    appendix_f='## Appendix F. Retained exploratory and unfinished checks\n\n'+old_endpoint+'\n'+adds.replace('### 4.5','### Additional controls:')+'\n'+context.replace('### 4.6','### Input-period, coordinate and class checks:')+'\n'+native_body+'\n'+partitions.replace('### 4.10','### Partition sensitivity:')
    appendix_d=appendix_d.replace('## Appendix D. Matched direct-learner operating points','## Appendix D. Matched direct-learner input comparisons\n\n'+matched.replace('### 4.9','### Retained paired contrasts:'))
    all_counts=table(reference_counts,{'model':'Representation','fold':'Held-out region','year':'Year','reference_pool_outside_fold':'Assigned references outside region','reference_valid':'Valid references','control_pool_outside_fold':'Assigned controls outside region','control_valid':'Valid controls'})
    mult=drift[drift.interval=='from_2017_multi_year'].copy();mult['pair']=mult.start_year.astype(str)+'–'+mult.end_year.astype(str);mult['centroid']=mult.centroid_dissimilarity.map(lambda x:f'{x:.4f}');mult['control']=mult.control_individual_median.map(lambda x:f'{x:.4f}')
    mult_table=table(mult,{'model':'Representation','fold':'Held-out region','pair':'Reference interval','reference_before':'References before','reference_after':'References after','control_paired':'Paired controls','centroid':'Centroid dissimilarity','control':'Median control dissimilarity'})
    appendix_e='## Appendix E. Reference/control availability and longer reference intervals\n\nPost-review descriptive diagnostics. All counts refer to baseline-selected plots outside the named fold, not verified later stability. Full one-year/individual-plot rows and same-membership means are retained in analysis/review-diagnostics-r1. No multi-year target screening is inferred.\n\n'+all_counts+'\n\nDescriptive2017-to-later reference intervals:\n\n'+mult_table
    # extension_native includes Appendix B and C; preserve both once.
    text=before+'## Abstract\n\n'+abstract+'\n\n'+methods+'\n'+results+'\n'+discussion+'\n'+reproduction+'\n'+references+'\n'+appendix_a+'\n'+native_appendix+'\n'+appendix_d+'\n'+appendix_e+'\n'+appendix_f
    text=text.replace('### Endpoint composition and reference availability: Endpoint composition and reference availability: exploratory checks','### Endpoint composition and reference availability')
    text=text.replace('through2023','through 2023').replace('### 3.4 Score / classifiers and calibration','### 3.4 Change scores, classifiers and calibration')
    text=text.replace('**First draft.**','**Revised after review by an AI agent.**')
    text=re.sub(r'\breadouts\b','scores and classifiers',text);text=re.sub(r'\breadout\b','score or classifier',text);text=text.replace('Readout','Score / classifier').replace('start-fixed','fixed start-year reference').replace('Tree controls','Control-mean adjustment')
    text=text.replace('Table1','Table 1').replace('Table2','Table 2').replace('Conditional95%','Conditional 95%').replace('with17false','with 17 false').replace('larger2017','larger 2017').replace('of24','of 24').replace('to2019','to 2019').replace('to2020','to 2020').replace('Product-familyV1','Product-family V1').replace('Descriptive2017','Descriptive 2017')
    text+='\n\n## Revision history\n\nRevised in response to review-014-1: narrow the title/question to CONUS one-year tests; shorten the abstract; add primary AUROC, exact-fold reference/cohort variation, ranking similarity and year/region denominators; foreground the gain-ranking inversion; qualify AlphaEarth training-target and production-version dependence; move secondary/exploratory checks to appendices. All original scores, thresholds, failures and first-draft snapshots are retained. New saved-data diagnostics are exploratory and fixed after review in protocol/review-analysis-v1.md. Point-by-point decisions, access limits and change records are in review/response-1.md.\n'
    output.write_text(text)
    print(json.dumps(dict(output=str(output),abstract_words=len(abstract.split()),total_words=len(text.split()),readout_occurrences=len(re.findall(r'\breadouts?\b',text,re.I)))))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'paper.md');revision(ap.parse_args().output)
