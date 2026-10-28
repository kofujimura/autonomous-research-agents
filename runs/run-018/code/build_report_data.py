"""Generate every empirical manuscript number/table input from saved analyses."""
from pathlib import Path
import argparse,json,math
import numpy as np,pandas as pd
from sklearn.metrics import balanced_accuracy_score,log_loss
from records import ROOT,now
from analysis_paths import paths

LABELS={'hydro_pair':'Hydrological pair model','hydro_decoder':'Hydrological category model','pair_aef':'Hydrology + AlphaEarth distance','pair_tessera':'Hydrology + TESSERA distance','pair_both':'Hydrology + both distances','pair_noise':'Hydrology + independent scalar','geography':'Geographic nearest reference','hydro_euclidean':'Hydrological Euclidean distance','aef_cosine':'AlphaEarth cosine','tessera_cosine':'TESSERA cosine','aef_centred':'AlphaEarth centred cosine','aef_whitened':'AlphaEarth whitened cosine','tessera_centred':'TESSERA centred cosine','tessera_whitened':'TESSERA whitened cosine','aef_decoder':'AlphaEarth category model','tessera_decoder':'TESSERA category model','hydro_aef_decoder':'Hydrology + AlphaEarth category model','hydro_tessera_decoder':'Hydrology + TESSERA category model','label_oracle':'Label-aware oracle'}

def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,np.generic):return clean(x.item())
 if isinstance(x,float) and not math.isfinite(x):return None
 return str(x) if isinstance(x,Path) else x

def markdown(frame,formats=None):
 formats=formats or {};lines=['| '+' | '.join(frame.columns)+' |','| '+' | '.join(['---']*len(frame.columns))+' |']
 for _,row in frame.iterrows():
  vals=[]
  for k,v in row.items():
   if pd.isna(v):s='—'
   elif k in formats:s=formats[k](v)
   else:s=str(v)
   vals.append(s)
  lines.append('| '+' | '.join(vals)+' |')
 return '\n'.join(lines)+'\n'

def build(root,out):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True);roots=sorted({p.parent for p in (root/'analysis').rglob('metrics.csv') if p.parent.name.endswith('-summary')});all_metrics=[];all_contrasts=[];all_pools=[];summaries={}
 for folder in roots:
  key=str(folder.relative_to(root));m=pd.read_csv(folder/'metrics.csv');m.insert(0,'analysis',key);all_metrics.append(m)
  c=pd.read_csv(folder/'contrasts.csv');c.insert(0,'analysis',key);all_contrasts.append(c)
  pc=pd.read_csv(folder/'pool-counts.csv');pc.insert(0,'analysis',key);all_pools.append(pc);summaries[key]=json.loads((folder/'summary.json').read_text())
 metrics=pd.concat(all_metrics,ignore_index=True);contrasts=pd.concat(all_contrasts,ignore_index=True);pools=pd.concat(all_pools,ignore_index=True);metrics.to_csv(out/'metrics-all.csv',index=False,float_format='%.17g');contrasts.to_csv(out/'contrasts-all.csv',index=False,float_format='%.17g');pools.to_csv(out/'pools-all.csv',index=False,float_format='%.17g')
 canonical=paths(root);primary=canonical['primary_summary'];main=metrics[(metrics.analysis==primary)&(metrics.coverage==.5)].copy();hgb=canonical['hgb_summary'];recent=canonical['recent_summary'];stats={}
 for key in summaries:
  mm=metrics[(metrics.analysis==key)&(metrics.coverage==.5)];cc=contrasts[(contrasts.analysis==key)&(contrasts.coverage==.5)];stats[key]=dict(counts=summaries[key],methods={v['method']:v for v in mm.drop(columns='analysis').to_dict('records')},contrasts={v['method']+'|'+v['baseline']:v for v in cc.drop(columns='analysis').to_dict('records')})
  spec=summaries[key].get('source_predictions')
  if spec:
   inp=Path(spec)
   if inp.is_absolute():inp=inp.relative_to(Path(json.loads((root/'manifest.json').read_text())['research_directory']))
   training=[]
   for r in range(4):
    path=root/inp/f'r{r}/analysis-record.json'
    if path.exists():
     detail=json.loads(path.read_text())
     if 'training_retained_n' in detail:training.append({k:detail[k] for k in ['rotation','training_nominal_n','training_retained_n','training_pairs']})
   stats[key]['training_per_rotation']=training
 rows=pd.DataFrame(json.loads((root/canonical['primary_features']/'rows-2024.json').read_text()));year=pd.to_numeric(rows.image_year,errors='coerce');cohort=dict(wetlands=len(rows),windows=int(rows.region.nunique()),image_year_groups={'<=2014':int((year<=2014).sum()),'2015-2019':int(((year>=2015)&(year<=2019)).sum()),'>=2020':int((year>=2020).sum()),'unknown':int(year.isna().sum())},vegetation_counts=rows.vegetation.value_counts().to_dict(),regime_counts=rows.regime.value_counts().to_dict(),hydro_feature_n=len(np.load(root/canonical['primary_features']/'features-2024.npz')['hydro_names']))
 selected=pd.read_csv(root/primary/'subgroups.csv');selected=selected[(selected.field=='regime')&selected.method.isin(['hydro_pair','hydro_decoder','pair_aef','pair_tessera'])];selected.to_csv(out/'regime-coverage.csv',index=False,float_format='%.17g')
 overlap=pd.read_csv(root/primary/'choice-overlap.csv');overlap=overlap[overlap.method.isin(['pair_aef','pair_tessera'])&overlap.baseline.isin(['hydro_pair','hydro_decoder'])];overlap.to_csv(out/'reference-choice-overlap.csv',index=False)
 fixed=pd.read_csv(root/primary/'fixed-screen-risk.csv');decomp=[]
 for selector in ['hydro_pair','hydro_decoder']:
  base=float(fixed[(fixed.selector==selector)&(fixed.method==selector)].macro_risk.iloc[0])
  for method in ['pair_aef','pair_tessera','pair_both']:
   on_base=float(fixed[(fixed.selector==selector)&(fixed.method==method)].macro_risk.iloc[0]);own=float(main[main.method==method].macro_risk.iloc[0]);own_base=float(main[main.method==selector].macro_risk.iloc[0]);assert abs(base-own_base)<1e-12;decomp.append(dict(selector=selector,method=method,total_difference=own-base,ranking_on_fixed_screen=on_base-base,selection_remainder=own-on_base))
 pd.DataFrame(decomp).to_csv(out/'screen-decomposition.csv',index=False,float_format='%.17g')
 probabilities=[]
 for r in range(4):
  x=np.load(root/canonical['primary_predictions']/f'r{r}/decoder-probabilities.npz');q=x['query_indices'];ids=x['objectid'][q];truth=x['y'][q]
  for method in ['hydro_decoder','aef_decoder','tessera_decoder','hydro_aef_decoder','hydro_tessera_decoder']:
   pr=x[method][q]
   probabilities.extend(dict(rotation=r,objectid=int(oid),method=method,y=int(y),pA=float(pp[0]),pC=float(pp[1]),pF=float(pp[2])) for oid,y,pp in zip(ids,truth,pr))
 pp=pd.DataFrame(probabilities);assert not pp.duplicated(['objectid','method']).any();pp.to_csv(out/'decoder-query-probabilities.csv',index=False,float_format='%.17g');diagnostics=[]
 for method,g in pp.groupby('method',sort=True):
  pr=g[['pA','pC','pF']].to_numpy();diagnostics.append(dict(method=method,n=len(g),balanced_accuracy=float(balanced_accuracy_score(g.y,pr.argmax(axis=1))),log_loss=float(log_loss(g.y,np.clip(pr,1e-15,1),labels=np.arange(3)))))
 pd.DataFrame(diagnostics).to_csv(out/'decoder-information.csv',index=False,float_format='%.17g')
 primary_table=main[['method','selected_n','available_n','macro_risk','pooled_risk']].copy();primary_table['Method']=primary_table.method.map(LABELS);primary_table=primary_table[['Method','selected_n','available_n','macro_risk','pooled_risk']].rename(columns={'selected_n':'Retained','available_n':'Nonempty queries','macro_risk':'Window mean (%)','pooled_risk':'Pooled (%)'})
 (out/'table-primary.md').write_text(markdown(primary_table,{'Retained':lambda v:f'{int(v):,}','Nonempty queries':lambda v:f'{int(v):,}','Window mean (%)':lambda v:f'{100*v:.2f}','Pooled (%)':lambda v:f'{100*v:.2f}'}))
 null_rows=[]
 for tag,real in [('constant-seed-0','primary'),('constant-seed-1000','controls/seed-1000'),('constant-seed-2000','controls/seed-2000'),('constant-all','controls/full-features'),('constant-hgb','controls/hgb')]:
  null_path=root/f'analysis/controls/{tag}-summary/region-metrics.csv';real_path=root/f'analysis/{real}-summary/region-metrics.csv'
  if not null_path.exists() or not real_path.exists():continue
  nn=pd.read_csv(null_path);rr=pd.read_csv(real_path);nn=nn[(nn.coverage==.5)&(nn.method=='pair_constant')].set_index('region')
  for method in ['pair_aef','pair_tessera']:
   mm=rr[(rr.coverage==.5)&(rr.method==method)].set_index('region');assert set(mm.index)==set(nn.index)
   for rid in nn.index:null_rows.append(dict(condition=tag,method=method,region=rid,real_risk=float(mm.loc[rid,'risk']),constant_risk=float(nn.loc[rid,'risk']),difference=float(mm.loc[rid,'risk']-nn.loc[rid,'risk'])))
 null_frame=pd.DataFrame(null_rows);null_frame.to_csv(out/'null-feature-comparisons.csv',index=False,float_format='%.17g');null_aggregate=[]
 if len(null_frame):null_aggregate=null_frame.groupby(['condition','method'],sort=True).agg(region_n=('region','size'),difference=('difference','mean')).reset_index().to_dict('records')
 pool_diagnostic={};pool_path=root/canonical.get('pool_influence','analysis/pool-influence-v2')
 if (pool_path/'result.json').exists():
  conditional=pd.read_csv(pool_path/'fixed-nontrivial.csv');leave=pd.read_csv(pool_path/'leave-window-out.csv');influence=[]
  for (analysis,method,baseline),g in leave.groupby(['analysis','method','baseline'],sort=True):
   influence.append(dict(analysis=analysis,method=method,baseline=baseline,omission_n=len(g),minimum=float(g.omission_difference.min()),maximum=float(g.omission_difference.max()),sign_changed_n=int(g.sign_changed.sum()),benchmark_changed_n=int(g.benchmark_changed.sum())))
  pd.DataFrame(influence).to_csv(out/'window-influence-overview.csv',index=False,float_format='%.17g');conditional.to_csv(out/'fixed-nontrivial.csv',index=False,float_format='%.17g');pool_diagnostic=dict(path=str(pool_path.relative_to(root)),conditional=conditional.to_dict('records'),influence=influence)
 from score_ambiguity import diagnose
 tie_predictions=pd.concat([pd.read_csv(root/canonical['primary_predictions']/f'r{r}/predictions.csv') for r in range(4)],ignore_index=True);tie_rows=diagnose(tie_predictions);pd.DataFrame(tie_rows).to_csv(out/'score-ambiguity.csv',index=False)
 budget_diagnostic={};budget_path=root/canonical.get('budget_allocation','analysis/budget-allocation-v1')
 if (budget_path/'result.json').exists():budget_diagnostic=dict(path=str(budget_path.relative_to(root)),metrics=pd.read_csv(budget_path/'metrics.csv').to_dict('records'),contrasts=pd.read_csv(budget_path/'contrasts.csv').to_dict('records'),conditions=json.loads((budget_path/'result.json').read_text()))
 repair=json.loads((root/'data/corrections/edge-correction-manifest.json').read_text());changes=json.loads((root/'analysis/tile-edge-audit/feature-correction-check.json').read_text());correction=dict(pixels=sum(r['corrected_pixels'] for r in repair),polygons=sum(r['affected_polygons'] for r in repair),primary_changed_rows=next(len(r['changed_rows']['aef']) for r in changes if r['source']=='features'),recent_changed_rows=next(len(r['changed_rows']['aef']) for r in changes if r['source']=='recent-features'))
 record=dict(generated_at_utc=now(),canonical_paths=canonical,cohort=cohort,measurement_correction=correction,primary_pool_counts=pd.read_csv(root/primary/'pool-counts.csv').to_dict('records'),analyses=stats,screen_decomposition=decomp,decoder_diagnostics=diagnostics,reference_choice_overlap=overlap.to_dict('records'),null_feature_comparisons=null_aggregate,score_ambiguity=tie_rows,pool_diagnostic=pool_diagnostic,budget_diagnostic=budget_diagnostic,input_change_audit=json.loads((root/'analysis/input-change-audit/result.json').read_text()) if (root/'analysis/input-change-audit/result.json').exists() else None,source_analysis_roots=[str(p.relative_to(root)) for p in roots]);(out/'report.json').write_text(json.dumps(clean(record),indent=2,allow_nan=False)+'\n');print(json.dumps(dict(analyses=len(roots),primary_wetlands=len(rows),primary_windows=int(rows.region.nunique()))))
 return record
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.root,a.out)
