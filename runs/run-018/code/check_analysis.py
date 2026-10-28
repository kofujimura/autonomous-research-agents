"""Hand-computable aggregation check; synthetic verification data, not study evidence."""
from pathlib import Path
import argparse,json,subprocess,sys
import pandas as pd

def main(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);inputs=out/'input';results=out/'summary'
 methods=['hydro_pair','hydro_decoder','pair_aef','pair_tessera','pair_both','aef_cosine','tessera_cosine','label_oracle','geography','hydro_euclidean']
 for rotation in range(4):
  pred=[];pools=[]
  for ri in range(4):
   for hard in [0,1]:
    q=10000*(ri+1)+rotation*10+hard
    meta=dict(region=f'R{ri+1:02}',rotation=rotation,query_id=q,vegetation='PEM1',regime='A' if hard==0 else 'C',image_year=2024,area_m2=5000,margin_m=30,candidate_n=2,candidate_categories=2,has_match=True,nontrivial_matchable=True,uniform_expected_mismatch=.5,training_support_global=True,training_support_local=True)
    pools.append(meta)
    for method in methods:
     score=(.1 if hard==0 else .9) if method=='pair_aef' else (.9 if hard==0 else .1)
     mismatch=hard if method!='label_oracle' else 0
     pred.append(meta|dict(method=method,reference_id=q+1000000+(1 if method=='label_oracle' and hard else 0),confidence=score,mismatch=mismatch,reference_regime=('C' if method=='label_oracle' and hard else 'A'),reference_distance_m=1500))
  folder=inputs/f'r{rotation}';folder.mkdir(parents=True);pd.DataFrame(pred).to_csv(folder/'predictions.csv',index=False);pd.DataFrame(pools).to_csv(folder/'pools.csv',index=False)
 script=Path(__file__).with_name('summarize_matching.py');subprocess.run([sys.executable,str(script),'--inputs',str(inputs),'--out',str(results)],check=True)
 metrics=pd.read_csv(results/'metrics.csv');contrasts=pd.read_csv(results/'contrasts.csv');fixed=pd.read_csv(results/'fixed-screen-risk.csv');overlap=pd.read_csv(results/'choice-overlap.csv')
 def risk(method):return float(metrics.loc[(metrics.coverage==.5)&(metrics.method==method),'macro_risk'].iloc[0])
 d=contrasts[(contrasts.coverage==.5)&(contrasts.method=='pair_aef')&(contrasts.baseline=='hydro_pair')].iloc[0]
 common=fixed[(fixed.selector=='hydro_pair')&(fixed.method=='pair_aef')].iloc[0]
 same=overlap[(overlap.method=='pair_aef')&(overlap.baseline=='hydro_pair')].iloc[0]
 checks=dict(baseline50_risk_zero=risk('hydro_pair')==0,augmented50_risk_one=risk('pair_aef')==1,paired_difference_one=float(d.difference)==1,constant_region_interval_one=float(d.low)==1 and float(d.high)==1,fixed_query_risk_zero=float(common.macro_risk)==0,all_reference_choices_identical=int(same.same_reference)==32,screened_sets_disjoint=int(same.screened_overlap_n)==0)
 record=dict(generation='Deterministic4regions×4rotations×2queries; all deployable methods make the same reference choices and errors; only pair_aef confidence ordering is reversed; the label-aware oracle is a separate bound. Synthetic verification fixture only, not empirical study results.',checks=checks,passed=all(checks.values()))
 (out/'check-result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True);assert record['passed']
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);main(p.parse_args().out)
