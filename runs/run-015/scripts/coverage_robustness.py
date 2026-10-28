"""Exploratory diagnostics from saved cases; no imputation or data retrieval."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from record import ROOT
from summarize import bootstrap_weights,estimate,clean,markdown_table

def main():
    p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--subsets');p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    frame=pd.read_csv(Path(a.primary)/'cases.csv',dtype={'date':str});base=frame[frame['n']==12]
    expected=len(design['dates'])*len(design['models'])*len(design['leads'])*12*3*3
    assert len(base)<=expected;missing=expected-len(base)
    rows=[]
    for stratum in ['all','informative']:
        part=base if stratum=='all' else base[base['informative']==1]
        matched=part[part['matched_date']]
        for mode in ['marginal','aggregate','pair']:
            values=np.maximum(0,part[mode+'_upper']-part[mode+'_lower']);total=float(values.sum())
            denominator=len(part)+missing
            rows.append({'stratum':stratum,'mode':mode,'available_cases':len(part),'matched_cases':len(matched),
                         'unavailable_cases_or_unknown_eligibility':missing,
                         'complete_date_mean':float(matched[mode+'_width'].mean()) if len(matched) else None,
                         'available_case_mean':float(values.mean()) if len(part) else None,
                         'full_schedule_mean_lower':total/denominator if denominator else None,
                         'full_schedule_mean_upper':(total+missing)/denominator if denominator else None})
    pd.DataFrame(rows).to_csv(out/'missingness-widths.csv',index=False)
    center_rows=[];weight_rows=[];matched=base[base['matched_date']]
    for stratum in ['all','informative']:
        part=matched if stratum=='all' else matched[matched['informative']==1]
        for center,_,_ in design['centers']:
            sub=part[part['center']==center]
            row={'center':center,'stratum':stratum,'cases':len(sub),'dates':int(sub['date'].nunique()),
                 'q_zero':int((sub['q']==0).sum()),'q_one':int((sub['q']==1).sum())}
            for mode in ['marginal','aggregate','pair']:row[mode+'_width']=float(sub[mode+'_width'].mean()) if len(sub) else None
            center_rows.append(row)
        for mode in ['marginal','aggregate','pair']:
            center_means=part.groupby('center')[mode+'_width'].mean()
            leave=[float(part[part['center']!=center][mode+'_width'].mean()) for center,_,_ in design['centers']
                   if len(part[part['center']!=center])]
            weight_rows.append({'stratum':stratum,'mode':mode,'query_weighted_mean':float(part[mode+'_width'].mean()) if len(part) else None,
                               'equal_eligible_center_mean':float(center_means.mean()) if len(center_means) else None,
                               'eligible_centers':len(center_means),'scheduled_centers':len(design['centers']),
                               'leave_one_center_out_min':min(leave) if leave else None,'leave_one_center_out_max':max(leave) if leave else None})
    pd.DataFrame(center_rows).to_csv(out/'center-descriptives.csv',index=False)
    pd.DataFrame(weight_rows).to_csv(out/'weighting-summary.csv',index=False)
    blocks=[]
    for block in [1,3,5]:
        boot_design={**design,'bootstrap_block_length':block};weights=bootstrap_weights(boot_design)
        for stratum in ['all','informative']:
            part=matched if stratum=='all' else matched[matched['informative']==1]
            for mode in ['marginal','aggregate','pair']:
                est=estimate(part,part[mode+'_width'],boot_design,weights)
                blocks.append({'block_length':block,'stratum':stratum,'mode':mode,**est})
    pd.DataFrame(blocks).to_csv(out/'block-sensitivity.csv',index=False)
    subsets=[]
    if a.subsets and (Path(a.subsets)/'cases.csv').exists():
        sub=pd.read_csv(Path(a.subsets)/'cases.csv',dtype={'date':str});target=len(design['dates'])*4*1728
        assert len(sub)<=target;unknown=target-len(sub)
        for stratum in ['all','informative']:
            part=sub if stratum=='all' else sub[sub['informative']==1]
            denominator=len(part)+unknown;total=float(part['count_minus_pair_width'].sum())
            subsets.append({'stratum':stratum,'available_cases':len(part),'unavailable_cases_or_unknown_eligibility':unknown,
                            'available_case_mean':float(part['count_minus_pair_width'].mean()) if len(part) else None,
                            'full_schedule_difference_lower':(total-unknown)/denominator if denominator else None,
                            'full_schedule_difference_upper':(total+unknown)/denominator if denominator else None})
        pd.DataFrame(subsets).to_csv(out/'missingness-subsets.csv',index=False)
    report={'exploratory':True,'scheduled_primary_cases':expected,'available_primary_cases':len(base),'missing_primary_cases':missing,
            'width_envelopes':rows,'weighting':weight_rows,'subset_envelopes':subsets,
            'scope':'Conservative missing-data envelopes, not sharp law bounds or confidence intervals; no missing-at-random assumption. Descriptive convenience-calendar resampling and geography weighting.'}
    (out/'summary.json').write_text(json.dumps(clean(report),indent=2,allow_nan=False)+'\n')
    (out/'table-missingness.md').write_text(markdown_table(clean(rows),[
        ('stratum','Stratum'),('mode','Information'),('available_cases','Available'),('unavailable_cases_or_unknown_eligibility','Unknown'),
        ('complete_date_mean','Matched-date mean'),('full_schedule_mean_lower','Scheduled lower'),('full_schedule_mean_upper','Scheduled upper')])+'\n')
    print(json.dumps(clean({k:v for k,v in report.items() if k not in ['width_envelopes','weighting']}),indent=2))

if __name__=='__main__':main()
