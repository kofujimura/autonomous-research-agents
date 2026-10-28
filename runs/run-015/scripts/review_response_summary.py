"""Saved-data reporting additions fixed in plan-v14 after REVIEW-1.

No new LPs, exclusions or primary estimands. State bins and width/window
diagnostics are exploratory; geometry and decision strata were prespecified.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from summarize import clean, markdown_table


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--primary',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();primary=Path(a.primary);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    cases=pd.read_csv(primary/'cases.csv')
    base=cases[(cases['n']==12)&cases['matched_date'].astype(bool)].copy()
    info=base[base['informative']==1].copy()
    bins=[0,10,50,100,500,np.inf];labels=['≤10','11–50','51–100','101–500','>500']
    info['surviving_states']=pd.cut(info['pair_possible_states'],bins=bins,labels=labels)
    rows=[]
    for label in labels:
        part=info[info['surviving_states']==label]
        rows.append({'surviving_states':label,'cases':len(part),'pair_identified':int(part['exact_pair'].sum()),
                     'identified_fraction':part['exact_pair'].mean(),'mean_pair_width':part['pair_width'].mean()})
    pd.DataFrame(rows).to_csv(out/'pruning-summary.csv',index=False)
    diag=[]
    for c in [.1,.25,.5]:
        for name,part in [('all',base),('near_boundary',base[abs(base['q']-c)<=.1+1e-7]),
                          ('informative_near_boundary',info[abs(info['q']-c)<=.1+1e-7])]:
            wide=part['marginal_width']>.2+1e-7
            certified=(part['marginal_lower']>=c-1e-7)|(part['marginal_upper']<=c+1e-7)
            diag.append({'cost_ratio':c,'stratum':name,'cases':len(part),'wide_cases':int(wide.sum()),
                         'certified_cases':int(certified.sum()),'wide_and_certified':int((wide&certified).sum())})
    pd.DataFrame(diag).to_csv(out/'width-window-diagnostic.csv',index=False)
    widths=pd.read_csv(primary/'width-summary.csv')
    strata=widths[(widths['n_sites']==12)&widths['lead'].isin(['84','180'])&widths['geometry'].isin(['compact','dispersed'])]
    # Mixed 'all'/numeric lead columns are strings when read from the CSV.
    assert len(strata)==24,(len(strata),widths['lead'].unique())
    cols=['model','lead','geometry','stratum','cases','marginal_width','aggregate_width','pair_width','aggregate_reduction_share','pair_exact_count']
    strata[cols].to_csv(out/'geometry-lead-summary.csv',index=False)
    compact=info[info['geometry']=='compact'];dispersed=info[info['geometry']=='dispersed']
    summary={'plan':'protocol/plan-v14-review-response.md','primary_cases':len(base),'informative_cases':len(info),
             'median_observed_patterns_informative':float(info['observed_patterns'].median()),
             'pruning':rows,'width_window':diag,
             'informative_pair_width_by_geometry':{name:float(part['pair_width'].mean()) for name,part in [('compact',compact),('dispersed',dispersed)]},
             'exploratory':['pruning-summary.csv','width-window-diagnostic.csv'],
             'prespecified_reporting':['geometry-lead-summary.csv']}
    (out/'summary.json').write_text(json.dumps(clean(summary),indent=2,allow_nan=False)+'\n')
    display=[dict(r,identified_fraction=f"{100*r['identified_fraction']:.1f}%",mean_pair_width=f"{r['mean_pair_width']:.4f}") for r in rows]
    (out/'table-pruning.md').write_text(markdown_table(display,[('surviving_states','States surviving zero-cell pruning'),('cases','N'),('pair_identified','Pair identified'),('identified_fraction','Identified'),('mean_pair_width','Mean pair width')])+'\n')
    display=[]
    for _,r in strata.iterrows():
        row=r.to_dict()
        for key in ['marginal_width','aggregate_width','pair_width']:row[key]=f"{r[key]:.4f}"
        row['aggregate_reduction_share']=f"{100*r['aggregate_reduction_share']:.1f}%"
        row['pair_exact_count']=f"{int(r['pair_exact_count'])}/{int(r['cases'])}"
        display.append(row)
    (out/'table-geometry-lead.md').write_text(markdown_table(display,[('model','Product'),('lead','Lead h'),('geometry','Geometry'),('stratum','Stratum'),('cases','N'),('marginal_width','Marginal'),('aggregate_width','Aggregate'),('pair_width','Pair'),('aggregate_reduction_share','Aggregate narrowing share'),('pair_exact_count','Pair identified / N')])+'\n')
    print(json.dumps({'status':'completed','cases':len(base),'informative':len(info),'geometry_lead_rows':len(strata)}))


if __name__=='__main__':main()
