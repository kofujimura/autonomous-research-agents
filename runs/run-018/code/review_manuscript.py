"""Author-written review revision, with every displayed value from saved analyses."""
import json
import pandas as pd
from build_report_data import LABELS,markdown
from analysis_paths import paths
from describe_analysis import describe

def revise(values,report,root):
 cp=paths(root);key=cp.get('review_reanalysis')
 if not key:return
 rr=json.loads((root/key/'result.json').read_text());a=report['analyses'];p=a[cp['primary_summary']];rn=pd.DataFrame(rr['real_null']);sm=pd.DataFrame(rr['seed_means']);dc=pd.DataFrame(rr['decoder_contrasts']);wi=pd.DataFrame(rr['window_influence'])
 def pp(x):return f'{100*x:+.2f}'
 def pct(x):return f'{100*x:.2f}'
 def risk(k,m,s='macro'):return a[k]['methods'][m][s+'_risk']
 def change(m,s='window',base='hydro_pair'):
  return next(r for r in rr['primary_contrasts'] if r['method']==m and r['scale']==s and r['baseline']==base)
 def ci(v,lo,hi,scale=100):
  precision=3 if scale==1 else 2
  return f'{scale*v:+.{precision}f} [{scale*lo:+.{precision}f}, {scale*hi:+.{precision}f}]'
 def table(rows):return markdown(pd.DataFrame(rows))
 primary=cp['primary_summary'];core=['hydro_pair','hydro_decoder','pair_aef','pair_tessera'];perm=next(r for r in rr['null_ranges'] if r['family']=='planned-permutation' and r['scale']=='window');permp=next(r for r in rr['null_ranges'] if r['family']=='planned-permutation' and r['scale']=='pooled')
 values['primary_abstract_results']=f"At half coverage, an increment attributable to the embeddings was not established under the planned qualification rule: planned permutation controls gave changes comparable to the real distances. Against a model scoring wetland pairs from these covariates, AlphaEarth/TESSERA changed mismatch by {pp(change('pair_aef')['difference'])}/{pp(change('pair_tessera')['difference'])} percentage points with equal window weights, but {pp(change('pair_aef','pooled')['difference'])}/{pp(change('pair_tessera','pooled')['difference'])} when queries were pooled."
 r7=wi[(wi.method=='pair_aef')&(wi.region=='R07')].iloc[0];r8=wi[(wi.method=='pair_aef')&(wi.region=='R08')].iloc[0]
 values['pool_abstract_counts']=f"One fewer mismatch among {int(r7.selected_n)} accepted queries in one window supplied {100*r7.contribution_fraction:.0f}% of the AlphaEarth equal-window change."
 values['exploratory_abstract_results']=f"Planned permutation changes ranged from {pp(perm['minimum'])} to {pp(perm['maximum'])} percentage points equal-window ({pp(permp['minimum'])} to {pp(permp['maximum'])} pooled); planned seed and alternative-learner checks also qualified the gain. Exploratory paired decoder diagnostics indicated label-prediction value, while reference-screening improvements remained sensitive to model settings and aggregation."
 head='### 4.1 Prespecified primary comparison\n\nThe increment attributable to annual embedding distance is **not established on the prespecified metric under the planned qualification rule**. Plan v6 required qualification when the gain disappeared with the second learner or was comparable to null-feature perturbations. The planned permutations and seed checks meet that qualification (section 4.5). This is a descriptive diagnostic conclusion, not a formal test of equality or a permutation p-value.\n\n'
 old=values['primary_results'].split('\n\n',1)[1];values['primary_results']=head+old
 rows=[]
 for m in ['pair_aef','pair_tessera']:
  for base in ['hydro_pair','hydro_decoder']:
   x=change(m,'window',base);y=change(m,'pooled',base)
   rows.append({'Augmentation':LABELS[m],'Comparator':LABELS[base],'Window Δ pp [95% interval]':ci(x['difference'],x['low'],x['high']),'Pooled Δ pp [95% interval]':ci(y['difference'],y['low'],y['high'])})
 values['primary_results']+='\n\n'+table(rows)+f"\nBoth scales use {int(p['methods']['hydro_pair']['selected_n']):,} accepted queries across {p['counts']['regions']} windows, with method-specific accepted sets. The pooled point metric was planned; its paired-window uncertainty was added after review. Negative differences favour the augmentation. Equal-window means give each window the same weight; pooled mismatch gives each accepted query the same weight. The intervals resample windows and do not incorporate random-forest seed variation.\n\nThe hydrological pair model does not beat geographic nearest reference on the primary equal-window scale: {pct(risk(primary,'hydro_pair'))}% versus {pct(risk(primary,'geography'))}%. The order reverses when queries are pooled: {pct(risk(primary,'hydro_pair','pooled'))}% versus {pct(risk(primary,'geography','pooled'))}%."
 rows=[]
 for _,r in wi[wi.region.isin(['R07','R08'])].iterrows():
  rows.append({'Augmentation':LABELS[r.method],'Window':r.region,'Accepted':str(int(r.selected_n)),'Errors, augmented / pair':f'{int(r.errors)} / {int(r.baseline_errors)}','Window Δ pp':pp(r.window_difference),'Contribution to mean, pp':pp(r.macro_contribution),'Accepted-set overlap':str(int(r.accepted_overlap_n))})
 values['pool_results']+='\n\n'+table(rows)+f"\nThe two windows contain {int(r7.selected_n+r8.selected_n)} of {int(p['methods']['hydro_pair']['selected_n']):,} accepted queries. Together they supply {100*r7.small_window_contribution_fraction:.1f}% of the AlphaEarth equal-window change; omitting both gives {pp(r7.omitting_both_small_windows)} pp. Neither window is removed from the primary result. R07 has one fewer error, rather than necessarily one corrected prediction on the same query: accepted sets overlap only partly, as the table shows. These contribution calculations were added after review.\n"
 rows=[]
 for _,r in dc.iterrows():
  rows.append({'Decoder':LABELS[r.method],'Weighting':r.scale,'Δ log loss, nats [95% interval]':ci(r.log_loss_difference,r.log_loss_low,r.log_loss_high,1),'Δ balanced accuracy, pp [95% interval]':ci(r.balanced_accuracy_difference,r.balanced_accuracy_low,r.balanced_accuracy_high),'Windows with lower log loss':f'{int(r.windows_better_log_loss)}/{int(r.windows)}'})
 values['ranking_and_decoder_results']+='\n\n'+table(rows)+'\nThese post-review exploratory paired-window intervals compare each label predictor with the hydrological category model on all query wetlands. Log loss measures the probability assigned to the observed class (natural logarithm, lower is better); balanced accuracy averages class-specific recall (higher is better). Window balanced accuracy averages recalls for true classes present in that window; pooled accuracy uses the summed three-class confusion matrix. The results indicate useful predictive information for these classifiers, without establishing conditional information absent from every possible physical model, better reference screening, or field hydrological validity.\n'
 # One compact table reports all diagnostic families, both scales, by fixed seed.
 rows=[]
 for (family,seed),g in rn[rn.baseline.eq('hydro_pair')].groupby(['family','seed'],sort=False):
  names={'planned-initial':'Planned forest; initial inputs','primary-corrected':'Primary forest; corrected inputs','planned-permutation':'Planned embedding shuffle','exploratory-scalar':'Later independent scalar; forest0.7','exploratory-constant':'Later zero column; forest0.7','exploratory-all-features':'Later all-feature forest; initial inputs','exploratory-all-scalar':'Later scalar; all-feature forest','exploratory-all-constant':'Later zero column; all-feature forest','planned-boosted-corrected':'Planned boosted trees; corrected inputs','exploratory-boosted-constant':'Later zero column; boosted trees','exploratory-all-corrected':'Later all-feature forest; corrected inputs','post-review-corrected':'Post-review forest; corrected inputs'}
  row={'Condition':names[family],'Seed / repeat':str(seed)}
  for method,label in [('pair_aef','AlphaEarth'),('pair_tessera','TESSERA'),('pair_noise','Scalar'),('pair_constant','Zero')]:
   for scale,short in [('window','W'),('pooled','P')]:
    q=g[(g.method==method)&(g.scale==scale)];row[label+' '+short]=pp(q.difference.iloc[0]) if len(q) else '—'
  rows.append(row)
 controls='### 4.5 Planned secondary controls and later randomness diagnostics\n\nThe seed, embedding-permutation and boosted-tree checks were fixed in plan v6 before the first explicitly logged aggregate inspection. They are **planned secondary analyses**, not externally preregistered tests. Independent scalars, constant columns and all-feature forests were added later and remain exploratory.\n\n'+table(rows)+'\nChanges from the matched physical pair model, in percentage points: W = equal-window mean, P = query-pooled. “Planned-initial” and the original permutations/scalars/constant seeds share the initial extraction. The corrected primary and post-review seeds are separate homogeneous inputs. Appending a constant or scalar can change random feature draws; these diagnostics are not a formal null distribution. The permutation audit also records a small number of unchanged candidate pools. Real-distance columns copied into null-control outputs are reused archived comparisons, not new fits. Full changes against the category model are in `'+key+'/real-null.csv`.\n\n'
 meanrows=[]
 for _,r in sm.iterrows():
  meanrows.append({'Seed group':{'planned-initial-three':'Three planned seeds; initial inputs','post-review-six-corrected':'Six seeds; corrected inputs, five after review'}[r.group],'Method':LABELS[r.method],'Comparator':LABELS[r.baseline],'Weighting':r.scale,'Seeds':str(int(r.seed_n)),'Mean Δ pp':pp(r['mean']),'Range Δ pp':f'{pp(r.minimum)} to {pp(r.maximum)}','Physical baseline range, %':f'{pct(r.baseline_minimum)} to {pct(r.baseline_maximum)}'})
 controls+=table(meanrows)+'\nThe three-seed mean uses the internally paired initial-extraction fits; it does not silently replace initial seed zero with the corrected fit. The six corrected-seed mean includes the original corrected seed and five fixed offsets added after review. A mean over seeds averages fitting randomness on the same sites; it is not six independent geographic replications.\n\n'
 old=values['robustness_results'];old=old.split('### 4.5 Learner and input controls\n\n',1)[1]
 old=old.replace('The constant feature has no variation; the independent scalar is generated without outcomes.', 'The first three seed rows and the three permutation rows are planned secondary controls; constant/scalar and all-feature checks are later exploratory additions. The zero column contains no varying site information. The independent scalar is generated without outcomes.')
 old=old.replace('This establishes sensitivity of this fitted pipeline to a noninformative input; it does not uniquely identify a tree-level cause.','This is consistent with ordinary feature-sampling and tree randomization: a fixed random-state integer does not hold the fitted trees fixed when the input dimension changes. It is not a newly discovered failure mechanism. The seed baseline ranges above quantify the relevant Monte Carlo variability; no unique tree-level cause was tested.')
 old=old.replace('In these original settings neither beat both corresponding physical comparators.','On the equal-window scale in these original settings neither beat both corresponding physical comparators. On the pooled scale, TESSERA does beat both; the paired scales below make that qualification explicit.')
 values['robustness_results']=controls+old
 # Put paired-scale values next to every scale-dependent polygon/transfer conclusion.
 for anchor,keys in [('### 4.7', ['analysis/polygon/C-rf-summary','analysis/polygon/C-hgb-summary']),('### 4.10',['analysis/transfer-corrected-summary','analysis/transfer-strong/hgb-raw-summary'])]:
  rows=[]
  for k in keys:
   if k not in a:continue
   row={'Condition':describe(k)}
   for m in core:row[LABELS[m]+' W / P']=f'{pct(risk(k,m))} / {pct(risk(k,m,"pooled"))}'
   rows.append(row)
  extra=table(rows)+'\nMismatch (%) as equal-window / pooled. These weightings answer different questions. The other-window boosted-tree TESSERA gain against its category comparator reverses on the pooled scale; the polygon-C pooled advantage does not establish the prespecified equal-window benchmark.\n\n'
  position=values['robustness_results'].find(anchor)
  if position>=0:values['robustness_results']=values['robustness_results'][:position]+extra+values['robustness_results'][position:]
  else:values['robustness_results']+='\n\n'+extra
 recent=cp['recent_summary'];values['recent_results']+=f" On the pooled scale, the physical pair and AlphaEarth augmentation each have {pct(risk(recent,'hydro_pair','pooled'))}% mismatch, while TESSERA has {pct(risk(recent,'pair_tessera','pooled'))}%."
 # Report the planned subgroup analyses without inferring an age or vegetation effect.
 rows=[]
 for r in rr['planned_subgroups']:
  rows.append({'Group':{'size_group':'Polygon area','vegetation':'Vegetation subclass','image_group':'Source-image year'}[r['field']]+': '+str(r['value']),'Method':LABELS[r['method']],'Available':str(int(r['available_n'])),'Accepted':str(int(r['selected_n'])),'Windows':str(int(r['selected_windows'])),'Pooled mismatch, %':pct(r['risk'])})
 sub='#### Planned descriptive subgroups\n\n'+table(rows)+'\nOwn-screen risks at half coverage; no group-specific rescreening. The source-image groups, size groups and vegetation subclasses were planned. Accepted denominators differ by method. Image dates and other subgroup composition are confounded with window; these figures cannot identify an inventory-age, size or vegetation effect. Full available/retained coverage is in `'+key+'/planned-subgroups.csv`.\n\n'
 values['robustness_results']=values['robustness_results'].replace('### 4.9 Training',sub+'### 4.9 Training')
 values['discussion']='''The embeddings show label-prediction value for the specified classifiers. The exploratory paired decoder analysis improves probability-based predictions in several comparisons, with different patterns for equal-window and pooled balanced accuracy. This is evidence about predicting the published inventory regimes from these representations. It does not establish that the physical covariates contain no comparable information under a stronger model, nor that the predictions represent current field hydrology.

Improved reference screening is a separate claim. The prespecified equal-window contrast does not establish an increment attributable to the embeddings under the study's own planned qualification rule: planned permutation changes are comparable, seed variability is substantial, and the second learner changes the comparison. The primary intervals resample windows rather than model seeds. A zero column changing a forest is consistent with its ordinary randomization, so the relevant lesson is the size of fitting variability relative to the proposed increment. Small retained windows and method-specific acceptance further amplify instability. Pooled results and fixed-query comparisons must accompany the equal-window endpoint.

Exploratory transformations, all-feature forests, embedding years and training geographies contain favourable cases, retained in Results. These are configuration-specific observations without a validated selection rule or independent confirmation. They prevent a general claim that satellite representations are uninformative, but cannot rescue the primary attribution claim.

For method developers, an added-feature comparison should include fixed seeds, multiple seed fits, permuted representations, alternative physical learners and reference quality on identical accepted queries. The tests here concern a particular optical surface-water/terrain/HAND baseline; they omit an explicit SAR-derived inundation predictor.

For wetland practitioners: use these results to judge evidence for a proposed map-based candidate screen, not to choose a field reference site. Neither a low embedding distance nor an inventory-category match establishes hydrological comparability, ecological condition or a restoration target. The potential settings are outdated inventory audits or locations without current regime labels. Those deployments, independently delineated wetlands and user benefit were not tested; other-window training is a limited retrospective check with no stable conclusion across weightings and model settings.'''
 values['remaining_limitations']=values['remaining_limitations'].replace('The additional controls were selected after inspecting some results and are explicitly exploratory.','The seed, permutation and fixed boosted-tree checks were planned before aggregate inspection; later controls and all review-response additions are exploratory. Both timings are distinguished in section 4.5.')
 if rr['include_new_seeds']:
  group=sm[(sm.group=='post-review-six-corrected')&(sm.baseline=='hydro_pair')]
  def seedrow(method,scale):return group[(group.method==method)&(group.scale==scale)].iloc[0]
  aw=seedrow('pair_aef','window');tw=seedrow('pair_tessera','window');ap=seedrow('pair_aef','pooled');tp=seedrow('pair_tessera','pooled')
  values['discussion']+=f"\n\nThe post-review corrected six-seed mean changes against the physical pair model are AlphaEarth {pp(aw['mean'])} pp equal-window / {pp(ap['mean'])} pp pooled and TESSERA {pp(tw['mean'])} / {pp(tp['mean'])} pp. Their equal-window seed ranges are {pp(aw.minimum)} to {pp(aw.maximum)} and {pp(tw.minimum)} to {pp(tw.maximum)} pp, respectively. These additional fixed runs supply favourable point evidence where the means are negative; they do not erase the original planned seed reversal or the comparable permutation controls. The five added seeds have no corresponding repeated-permutation fits, so their averages do not isolate an information effect from all fitting perturbations. All seed results are retained."
  values['exploratory_abstract_results']=f"Planned permutation changes ranged from {pp(perm['minimum'])} to {pp(perm['maximum'])} percentage points equal-window ({pp(permp['minimum'])} to {pp(permp['maximum'])} pooled); planned seed and alternative-learner checks also qualified the gain. Exploratory six-seed corrected-input mean changes against the same model were {pp(aw['mean'])}/{pp(tw['mean'])} equal-window and {pp(ap['mean'])}/{pp(tp['mean'])} pooled. Exploratory category-prediction diagnostics also indicated value for predicting inventory labels."
 values['robustness_methods_and_timing']+='\n\nAfter review by an AI agent, plan v23 fixed paired-window uncertainty for pooled screening and decoder metrics, small-window contribution/overlap calculations, real/null seed summaries, planned subgroup reporting and five additional corrected-input forest seed offsets. These analyses reuse the same sites and labels and are not independent confirmation. Decoder intervals resample paired windows 10,000 times at seed 18018; log loss uses natural logarithms and balanced accuracy averages recall over present classes per window or all three pooled classes. The original primary metric, population and acceptance rule are unchanged.'

 # Prefer ordinary wording for sampling rules throughout the generated prose.
 for name in values:
  if isinstance(values[name],str):values[name]=values[name].replace('measurement operators','rules for sampling maps').replace('measurement operator','rule for sampling maps').replace('sampling operators','sampling rules').replace('optical embeddings and physical covariates equivalent sensors','embedding products and explicit physical maps equivalent measurements')
