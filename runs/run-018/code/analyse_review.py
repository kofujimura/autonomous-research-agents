"""Post-review saved-output analyses; no network, API or model fitting."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np,pandas as pd
from records import ROOT,now
from analysis_paths import paths

CORE=['hydro_pair','hydro_decoder','pair_aef','pair_tessera']
NEW_SEEDS=[3000,4000,5000,6000,7000]

def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.generic):return clean(x.item())
 if isinstance(x,float) and not np.isfinite(x):return None
 return x

def analyse(root,out,include_new_seeds=False):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False);cp=paths(root);hashes={}
 def read(rel):
  p=root/rel;hashes[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest();return pd.read_csv(p)
 def metrics(key):return read(key+'/metrics.csv').query('coverage == .5').set_index('method')
 primary=cp['primary_summary'];m=metrics(primary);regional=read(primary+'/region-metrics.csv').query('coverage == .5');selected=read(primary+'/selected-050.csv');regions=sorted(regional.region.unique());draw=np.random.default_rng(18018).integers(0,len(regions),(10000,len(regions)))
 contrasts=[]
 for method in ['pair_aef','pair_tessera']:
  for baseline in ['hydro_pair','hydro_decoder']:
   a=regional[regional.method==method].set_index('region').loc[regions];b=regional[regional.method==baseline].set_index('region').loc[regions]
   macro=(a.risk-b.risk).to_numpy();ar=a.errors.to_numpy()[draw].sum(axis=1)/a.n.to_numpy()[draw].sum(axis=1);br=b.errors.to_numpy()[draw].sum(axis=1)/b.n.to_numpy()[draw].sum(axis=1)
   for scale,value,boot in [('window',float(macro.mean()),macro[draw].mean(axis=1)),('pooled',float(m.loc[method,'pooled_risk']-m.loc[baseline,'pooled_risk']),ar-br)]:
    lo,hi=np.quantile(boot,[.025,.975]);contrasts.append(dict(method=method,baseline=baseline,scale=scale,difference=value,low=lo,high=hi,windows=len(regions),selected_n=int(m.loc[method,'selected_n'])))
 influence=[]
 for method in ['pair_aef','pair_tessera']:
  a=regional[regional.method==method].set_index('region').loc[regions];b=regional[regional.method=='hydro_pair'].set_index('region').loc[regions];delta=a.risk-b.risk
  for rid in regions:
   aa=selected[(selected.method==method)&(selected.region==rid)];bb=selected[(selected.method=='hydro_pair')&(selected.region==rid)]
   influence.append(dict(method=method,region=rid,selected_n=int(a.loc[rid,'n']),baseline_selected_n=int(b.loc[rid,'n']),errors=int(a.loc[rid,'errors']),baseline_errors=int(b.loc[rid,'errors']),window_difference=float(delta.loc[rid]),macro_contribution=float(delta.loc[rid]/len(regions)),contribution_fraction=float(delta.loc[rid]/delta.sum()) if delta.sum()!=0 else None,accepted_query_sets_equal=set(aa.query_id)==set(bb.query_id),accepted_overlap_n=len(set(aa.query_id)&set(bb.query_id)),omitting_both_small_windows=float(delta.drop(['R07','R08']).mean()),small_window_contribution=float(delta.loc[['R07','R08']].sum()/len(regions)),small_window_contribution_fraction=float(delta.loc[['R07','R08']].sum()/delta.sum())))
 cases=[('planned-initial',0,'analysis/primary-summary')]+[('planned-initial',s,f'analysis/controls/seed-{s}-summary') for s in [1000,2000]]+[('primary-corrected',0,primary)]
 cases += [('planned-permutation',i,f'analysis/controls/permute-{i}-summary') for i in range(3)]
 cases += [('exploratory-scalar',i,f'analysis/controls/noise-{i}-summary') for i in range(3)]
 cases += [('exploratory-constant',s,f'analysis/controls/constant-seed-{s}-summary') for s in [0,1000,2000]]
 cases += [('exploratory-all-features',0,'analysis/controls/full-features-summary')]
 cases += [('exploratory-all-scalar',i,f'analysis/controls/noise-all-{i}-summary') for i in range(3)]
 cases += [('exploratory-all-constant',0,'analysis/controls/constant-all-summary'),('planned-boosted-corrected',0,cp['hgb_summary']),('exploratory-boosted-constant',0,'analysis/controls/constant-corrected-hgb-summary')]
 cases += [('exploratory-all-corrected',s,f'analysis/controls/all-corrected-seed-{s}-summary') for s in [0,1000,2000]]
 if include_new_seeds:
  cases += [('post-review-corrected',s,f'analysis/review-seeds/seed-{s}-summary') for s in NEW_SEEDS]
 real_null=[];baseline_rows=[]
 for family,seed,key in cases:
  mm=metrics(key)
  baseline_rows.append(dict(family=family,seed=seed,analysis=key,**{f'{method}_{scale}':float(mm.loc[method,scale+'_risk']) for method in ['hydro_pair','hydro_decoder'] for scale in ['macro','pooled']}))
  for method in ['pair_aef','pair_tessera','pair_noise','pair_constant']:
   if method not in mm.index:continue
   for base in ['hydro_pair','hydro_decoder']:
    for scale,column in [('window','macro_risk'),('pooled','pooled_risk')]:real_null.append(dict(family=family,seed=seed,analysis=key,method=method,baseline=base,scale=scale,difference=float(mm.loc[method,column]-mm.loc[base,column]),baseline_risk=float(mm.loc[base,column]),augmented_risk=float(mm.loc[method,column])))
 rn=pd.DataFrame(real_null);seed_means=[]
 groups=[('planned-initial-three',rn.family.eq('planned-initial'))]
 if include_new_seeds:groups.append(('post-review-six-corrected',rn.family.isin(['primary-corrected','post-review-corrected'])))
 for group,mask in groups:
  for (method,base,scale),g in rn[mask].groupby(['method','baseline','scale'],sort=True):seed_means.append(dict(group=group,method=method,baseline=base,scale=scale,seed_n=len(g),mean=float(g.difference.mean()),minimum=float(g.difference.min()),maximum=float(g.difference.max()),baseline_minimum=float(g.baseline_risk.min()),baseline_maximum=float(g.baseline_risk.max())))
 null_ranges=[]
 for family in ['planned-permutation','exploratory-scalar','exploratory-constant']:
  for scale in ['window','pooled']:
   g=rn[(rn.family==family)&(rn.baseline=='hydro_pair')&(rn.scale==scale)]
   null_ranges.append(dict(family=family,scale=scale,n=len(g),minimum=float(g.difference.min()),maximum=float(g.difference.max()),mean=float(g.difference.mean())))
 # Decode saved probabilities without using any new model output.
 rows=pd.DataFrame(json.loads((root/cp['primary_features']/'rows-2024.json').read_text()));region_by_id=rows.set_index('objectid').region.to_dict();probabilities=[]
 for r in range(4):
  p=root/cp['primary_predictions']/f'r{r}/decoder-probabilities.npz';hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest();data=np.load(p);q=data['query_indices']
  for method in ['hydro_decoder','aef_decoder','tessera_decoder','hydro_aef_decoder','hydro_tessera_decoder']:
   for oid,y,pr in zip(data['objectid'][q],data['y'][q],data[method][q]):probabilities.append(dict(region=region_by_id[int(oid)],objectid=int(oid),method=method,y=int(y),prediction=int(pr.argmax()),loss=float(-np.log(np.clip(pr[int(y)],1e-15,1))),p0=float(pr[0]),p1=float(pr[1]),p2=float(pr[2])))
 probabilities=pd.DataFrame(probabilities);decoder_windows=[];confusions={}
 for (method,rid),g in probabilities.groupby(['method','region'],sort=True):
  cm=np.zeros((3,3),int);np.add.at(cm,(g.y.to_numpy(),g.prediction.to_numpy()),1);present=cm.sum(axis=1)>0;ba=float((np.diag(cm)[present]/cm.sum(axis=1)[present]).mean());decoder_windows.append(dict(method=method,region=rid,n=len(g),loss_sum=float(g.loss.sum()),log_loss=float(g.loss.mean()),balanced_accuracy=ba,present_class_n=int(present.sum())));confusions[(method,rid)]=cm
 dw=pd.DataFrame(decoder_windows);decoder=[]
 def ba_matrix(cm):
  denom=cm.sum(axis=-1);return np.divide(np.diagonal(cm,axis1=-2,axis2=-1),denom,out=np.zeros_like(denom,dtype=float),where=denom>0).mean(axis=-1)
 for method in ['aef_decoder','tessera_decoder','hydro_aef_decoder','hydro_tessera_decoder']:
  a=dw[dw.method==method].set_index('region').loc[regions];b=dw[dw.method=='hydro_decoder'].set_index('region').loc[regions];ac=np.stack([confusions[(method,r)] for r in regions]);bc=np.stack([confusions[('hydro_decoder',r)] for r in regions])
  for scale in ['window','pooled']:
   if scale=='window':ld=(a.log_loss-b.log_loss).to_numpy();bd=(a.balanced_accuracy-b.balanced_accuracy).to_numpy();loss=float(ld.mean());bal=float(bd.mean());loss_boot=ld[draw].mean(axis=1);bal_boot=bd[draw].mean(axis=1)
   else:loss=float(a.loss_sum.sum()/a.n.sum()-b.loss_sum.sum()/b.n.sum());bal=float(ba_matrix(ac.sum(axis=0))-ba_matrix(bc.sum(axis=0)));loss_boot=a.loss_sum.to_numpy()[draw].sum(axis=1)/a.n.to_numpy()[draw].sum(axis=1)-b.loss_sum.to_numpy()[draw].sum(axis=1)/b.n.to_numpy()[draw].sum(axis=1);bal_boot=ba_matrix(ac[draw].sum(axis=1))-ba_matrix(bc[draw].sum(axis=1))
   lo,hi=np.quantile(loss_boot,[.025,.975]);bl,bh=np.quantile(bal_boot,[.025,.975]);decoder.append(dict(method=method,scale=scale,log_loss_difference=loss,log_loss_low=float(lo),log_loss_high=float(hi),balanced_accuracy_difference=bal,balanced_accuracy_low=float(bl),balanced_accuracy_high=float(bh),windows=len(regions),queries=int(a.n.sum()),windows_better_log_loss=int((a.log_loss<b.log_loss).sum()),windows_better_balanced_accuracy=int((a.balanced_accuracy>b.balanced_accuracy).sum())))
 sub=read(primary+'/subgroups.csv');sub=sub[sub.field.isin(['size_group','vegetation','image_group'])&sub.method.isin(CORE)].copy();subrows=[]
 for _,row in sub.iterrows():
  g=selected[(selected.method==row.method)&selected[row.field].astype(str).eq(str(row.value))]
  subrows.append(row.to_dict()|dict(selected_windows=int(g.region.nunique())))
 objects={'primary-contrasts':contrasts,'window-influence':influence,'real-null':real_null,'seed-means':seed_means,'null-ranges':null_ranges,'baseline-seeds':baseline_rows,'decoder-contrasts':decoder,'decoder-windows':decoder_windows,'planned-subgroups':subrows}
 for name,values in objects.items():pd.DataFrame(values).to_csv(out/(name+'.csv'),index=False,float_format='%.17g')
 result=dict(analysed_at_utc=now(),post_review=True,include_new_seeds=include_new_seeds,new_seed_offsets=NEW_SEEDS if include_new_seeds else [],bootstrap=dict(unit='paired windows',draws=10000,seed=18018),**{name.replace('-','_'):values for name,values in objects.items()},primary_risks={method:{field:clean(m.loc[method,field]) for field in ['macro_risk','pooled_risk','selected_n','errors']} for method in CORE},input_sha256=hashes,scope='Post-review diagnostics on archived/repeated predictions; no formal null-distribution test, independent sites, field validation or causal age/weighting effect.')
 (out/'result.json').write_text(json.dumps(clean(result),indent=2,allow_nan=False)+'\n');print(json.dumps(dict(contrasts=len(contrasts),decoder_contrasts=len(decoder),real_null_rows=len(real_null),subgroup_rows=len(subrows),new_seed_n=len(NEW_SEEDS) if include_new_seeds else 0)))
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);p.add_argument('--include-new-seeds',action='store_true');a=p.parse_args();analyse(a.root,a.out,a.include_new_seeds)
