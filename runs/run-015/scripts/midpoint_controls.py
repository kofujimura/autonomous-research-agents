"""Exploratory like-for-like interval-midpoint controls from saved bounds."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import TOL
from record import ROOT
from summarize import bootstrap_weights,estimate,clean,markdown_table

def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    frame=pd.read_csv(a.cases,dtype={'date':str});base=frame[frame['matched_date']&(frame['n']==12)]
    design=json.loads((ROOT/'protocol/design-v1.json').read_text());weights=bootstrap_weights(design);rows=[]
    for availability in ['all','historical_matched']:
        selected=base if availability=='all' else base[base['historical_q'].notna()]
        for stratum in ['all','informative']:
            part=selected if stratum=='all' else selected[selected['informative']==1]
            for mode in ['marginal','aggregate','pair']:
                prediction=(part[mode+'_lower']+part[mode+'_upper'])/2
                errors=np.abs(prediction-part['q']);assert np.all(errors<=part[mode+'_width']/2+TOL)
                est=estimate(part,errors,design,weights)
                row={'availability':availability,'stratum':stratum,'mode':mode,'cases':len(part),'dates':est['dates'],
                     'mean_absolute_error':est['mean'],'low':est['low'],'high':est['high'],
                     'mean_compatible_width':float(part[mode+'_width'].mean()) if len(part) else None}
                for c in design['cost_ratios']:
                    mismatch=(prediction>c)!=(part['q']>c)
                    row[f'expected_regret_{c}']=float(np.where(mismatch,np.abs(part['q']-c),0).mean()) if len(part) else None
                rows.append(row)
    pd.DataFrame(rows).to_csv(out/'midpoint-summary.csv',index=False)
    report={'exploratory':True,'rows':clean(rows),'scope':'Additional point conditions, original bounds/outcomes unchanged; expected losses under input ensemble, not realized weather.'}
    (out/'summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    display=[r for r in rows if r['availability']=='historical_matched']
    (out/'table-midpoints.md').write_text(markdown_table(clean(display),[('stratum','Stratum'),('mode','Information'),('cases','N'),('mean_compatible_width','Compatible width'),('mean_absolute_error','Midpoint absolute error'),('low','Resampling low'),('high','Resampling high'),('expected_regret_0.25','Expected regret c=0.25')])+'\n')
    print('Midpoint controls generated')

if __name__=='__main__':main()
