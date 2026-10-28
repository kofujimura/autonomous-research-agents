"""Publish exactly which classifier combinations and repetitions were run."""
import argparse
import json
from pathlib import Path
import pandas as pd
from records import ROOT,now

def main():
    p=argparse.ArgumentParser();p.add_argument('--results',default='data/results');p.add_argument('--out',default='analysis');a=p.parse_args()
    rows=[]
    for path in sorted((ROOT/a.results/'fits').glob('*.json')):
        m=json.loads(path.read_text());rows.append({k:m[k] for k in ['fit_id','scope','decoder','budget','seed','policy','representation']})
    if not rows:raise RuntimeError('No completed fits')
    fits=pd.DataFrame(rows);cells=[]
    for key,part in fits.groupby(['scope','decoder','budget','policy','representation'],sort=True):
        cells.append(dict(zip(['scope','decoder','budget','policy','representation'],key),
            completed_seeds=';'.join(str(x) for x in sorted(part.seed)),fit_count=len(part),
            all_five_original_seeds=set(part.seed)=={101,202,303,404,505}))
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(cells).to_csv(out/'completed-cells.csv',index=False)
    stage=[]
    for (scope,decoder,budget),part in fits.groupby(['scope','decoder','budget'],sort=True):
        count=part.groupby(['policy','representation']).seed.nunique()
        stage.append(dict(scope=scope,decoder=decoder,budget=budget,completed_fits=len(part),
            observed_allocations=';'.join(sorted(part.policy.unique())),
            observed_representations=';'.join(sorted(part.representation.unique())),
            distinct_cells=len(count),minimum_seeds_per_observed_cell=int(count.min()),maximum_seeds_per_observed_cell=int(count.max())))
    pd.DataFrame(stage).to_csv(out/'completed-stages.csv',index=False)
    primary=fits[(fits.scope=='within')&(fits.decoder=='rf')&(fits.budget==2000)&
        fits.policy.isin(['area','interior','object','proposal','uncertainty'])&
        fits.representation.isin(['aef','optical','optical_context'])]
    result=dict(checked_at_utc=now(),completed_fits=len(fits),original_primary_completed=len(primary),
        original_primary_required=75,original_primary_complete=len(primary)==75,
        interpretation='Observed cells are not a claim that every planned extension was completed; inspect the protocol and omitted-arm account.')
    (out/'completion.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
