"""Regenerate coverage tables and paired region-level contrasts from saved predictions."""
from pathlib import Path
import argparse,itertools,json
import numpy as np,pandas as pd

PRIMARY=['pair_aef','pair_tessera','pair_both','pair_noise','pair_constant']
BASES=['hydro_pair','hydro_decoder']
COVERAGES=[.2,.5,.8,1.]

def bootstrap(values):
 values=np.asarray(values,float);values=values[np.isfinite(values)]
 if len(values)<4:return [None,None]
 rng=np.random.default_rng(18018);means=values[rng.integers(0,len(values),(10000,len(values)))].mean(axis=1)
 return np.quantile(means,[.025,.975]).tolist()

def summarize(inputs,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 paths=sorted(Path(inputs).glob('r*/predictions.csv'))
 if len(paths)!=4:raise RuntimeError(f'Expected four rotations, found{len(paths)}')
 pred=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
 pools=pd.concat([pd.read_csv(p.parent/'pools.csv') for p in paths],ignore_index=True)
 yr=pd.to_numeric(pred.image_year,errors='coerce')
 pred['image_group']=np.select([yr.isna(),yr<=2014,yr<=2019],['unknown','<=2014','2015-2019'],default='>=2020')
 pred['size_group']=np.where(pred.area_m2<=10000,'<=1ha','>1ha')
 assert not pools.duplicated(['region','query_id']).any(),'Query appears multiple times'
 assert not pred.duplicated(['region','query_id','method']).any()
 selections={};metric_rows=[];region_rows=[];subgroups=[]
 for coverage in COVERAGES:
  selected=[]
  for (region,r,method),group in pred.groupby(['region','rotation','method'],sort=True):
   group=group.sort_values(['confidence','query_id'],ascending=[False,True],kind='stable');k=int(np.floor(len(group)*coverage));selected.append(group.iloc[:k])
  sel=pd.concat(selected,ignore_index=True);selections[coverage]=sel
  for (method,region),g in sel.groupby(['method','region'],sort=True):region_rows.append(dict(coverage=coverage,method=method,region=region,n=len(g),errors=int(g.mismatch.sum()),risk=float(g.mismatch.mean())))
  for method in sorted(pred.method.unique()):
   g=sel[sel.method==method]
   regional=g.groupby('region').mismatch.mean();ci=bootstrap(regional.to_numpy());all_n=int((pred.method==method).sum());nontrivial=g[g.nontrivial_matchable];nons=pred[(pred.method==method)&pred.nontrivial_matchable]
   metric_rows.append(dict(coverage=coverage,method=method,selected_n=len(g),available_n=all_n,achieved_coverage=len(g)/all_n,region_n=len(regional),macro_risk=float(regional.mean()) if len(regional) else None,macro_low=ci[0],macro_high=ci[1],pooled_risk=float(g.mismatch.mean()) if len(g) else None,errors=int(g.mismatch.sum()),nontrivial_selected_n=len(nontrivial),nontrivial_available_n=len(nons),nontrivial_achieved_coverage=len(nontrivial)/len(nons) if len(nons) else None,nontrivial_pooled_risk=float(nontrivial.mismatch.mean()) if len(nontrivial) else None))
  if coverage==.5:
   sel.to_csv(out/'selected-050.csv',index=False,float_format='%.17g')
   # Descriptive coverage by true query categories and covariates; no re-screening.
   for field in ['regime','vegetation','image_year','image_group','size_group']:
    for (method,value),g in sel.groupby(['method',field],dropna=False):
     base=pred[(pred.method==method)&(pred[field].eq(value) if pd.notna(value) else pred[field].isna())]
     subgroups.append(dict(field=field,value=None if pd.isna(value) else str(value),method=method,available_n=len(base),selected_n=len(g),coverage=len(g)/len(base),risk=float(g.mismatch.mean())))
 metrics=pd.DataFrame(metric_rows);regions=pd.DataFrame(region_rows);metrics.to_csv(out/'metrics.csv',index=False,float_format='%.17g');regions.to_csv(out/'region-metrics.csv',index=False,float_format='%.17g');pd.DataFrame(subgroups).to_csv(out/'subgroups.csv',index=False,float_format='%.17g')
 contrasts=[]
 for cov in COVERAGES:
  frame=regions[regions.coverage==cov].pivot(index='region',columns='method',values='risk').reindex(columns=sorted(pred.method.unique()))
  for method in [m for m in PRIMARY if m in pred.method.unique()]:
   for base in [b for b in BASES if b in pred.method.unique()]:
    pair=frame[[method,base]].dropna();d=pair[method]-pair[base];ci=bootstrap(d.to_numpy())
    contrasts.append(dict(coverage=cov,method=method,baseline=base,region_n=len(d),difference=float(d.mean()) if len(d) else None,low=ci[0],high=ci[1],meaningful_improvement=bool(d.mean()<=-.02) if len(d) else None,regions_improved=int((d<0).sum()),regions_worsened=int((d>0).sum()),regions_equal=int((d==0).sum())))
 pd.DataFrame(contrasts).to_csv(out/'contrasts.csv',index=False,float_format='%.17g')
 pool_counts=[]
 for rid,g in pools.groupby('region'):
  nonempty=g.candidate_n>0;one=g.candidate_categories==1
  pool_counts.append(dict(region=rid,queries=len(g),empty=int((~nonempty).sum()),single_all_correct=int((one&g.has_match).sum()),single_all_wrong=int((one&~g.has_match).sum()),multi_matchable=int(g.nontrivial_matchable.sum()),unmatchable=int((nonempty&~g.has_match).sum()),uniform_expected_risk=float(g.loc[nonempty,'uniform_expected_mismatch'].mean()),median_candidate_n=float(g.loc[nonempty,'candidate_n'].median())))
 pd.DataFrame(pool_counts).to_csv(out/'pool-counts.csv',index=False,float_format='%.17g')
 # Reference-choice and screened-query overlap, independently of observed risk.
 wide=pred.pivot(index=['region','query_id'],columns='method',values='reference_id');overlap=[]
 screen=selections[.5]
 for method in [m for m in PRIMARY if m in pred.method.unique()]:
  for base in [b for b in BASES+['aef_cosine','tessera_cosine'] if b in pred.method.unique()]:
   f=wide[[method,base]].dropna();aa=set(screen.loc[screen.method==method,'query_id']);bb=set(screen.loc[screen.method==base,'query_id'])
   overlap.append(dict(method=method,baseline=base,comparable_queries=len(f),same_reference=int(f[method].eq(f[base]).sum()),different_reference=int(f[method].ne(f[base]).sum()),screened_overlap_n=len(aa&bb),screened_method_n=len(aa),screened_baseline_n=len(bb)))
 pd.DataFrame(overlap).to_csv(out/'choice-overlap.csv',index=False)
 fixed=[]
 for selector in BASES:
  keys=screen.loc[screen.method==selector,['region','query_id']].assign(keep=True)
  common=pred.merge(keys,on=['region','query_id'],how='inner',validate='many_to_one')
  for method,g in common.groupby('method'):
   reg=g.groupby('region').mismatch.mean();fixed.append(dict(selector=selector,method=method,n=len(g),macro_risk=float(reg.mean()),pooled_risk=float(g.mismatch.mean())))
 pd.DataFrame(fixed).to_csv(out/'fixed-screen-risk.csv',index=False,float_format='%.17g')
 totals=dict(source_predictions=str(inputs),queries=len(pools),nonempty_queries=int((pools.candidate_n>0).sum()),empty_queries=int((pools.candidate_n==0).sum()),single_all_correct=int(((pools.candidate_categories==1)&pools.has_match).sum()),single_all_wrong=int(((pools.candidate_categories==1)&~pools.has_match).sum()),unmatchable=int(((pools.candidate_n>0)&~pools.has_match).sum()),nontrivial_matchable=int(pools.nontrivial_matchable.sum()),regions=int(pools.region.nunique()),method_n=int(pred.method.nunique()),uniform_expected_macro_risk=float(pd.DataFrame(pool_counts).uniform_expected_risk.mean()))
 (out/'summary.json').write_text(json.dumps(totals,indent=2)+'\n')
 display=metrics[metrics.coverage==.5].copy();display['macro_risk_percent']=display.macro_risk*100;display['pooled_risk_percent']=display.pooled_risk*100
 # Display only, raw outputs above retain full precision.
 table=display[['method','selected_n','available_n','macro_risk_percent','pooled_risk_percent']].round(2)
 lines=['| '+' | '.join(table.columns)+' |','| '+' | '.join(['---']*len(table.columns))+' |']
 lines.extend('| '+' | '.join(map(str,row))+' |' for row in table.itertuples(index=False,name=None))
 (out/'table-main.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(totals));print(display[['method','macro_risk_percent','pooled_risk_percent']].round(2).to_string(index=False))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--inputs',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();summarize(a.inputs,a.out)
