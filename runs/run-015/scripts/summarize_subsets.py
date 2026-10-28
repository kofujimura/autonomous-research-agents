"""Offline exploratory v3 summaries; all numerical text comes from these outputs."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import TOL
from record import ROOT
from summarize import bootstrap_weights,estimate,clean,markdown_table

MODES=['marginal','pair','count','restricted_pair']

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--output',required=True);a=p.parse_args()
    root=Path(a.root).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    design=json.loads((root/'protocol/design-v1.json').read_text());weights=bootstrap_weights(design)
    frames=[];availability=[];encoding=None
    for date in design['dates']:
        for model in design['models']:
            for lead in design['leads']:
                folder=root/'results/subsets-units'/date/model/str(lead)
                ready=(folder/'summary.json').exists() and (root/'data/weather'/date/model/str(lead)/'complete.json').exists()
                availability.append({'date':date,'model':model,'lead':lead,'complete':ready})
                if not ready:continue
                summary=json.loads((folder/'summary.json').read_text());encoding=summary['encoding']
                frame=pd.read_csv(folder/'bounds.csv',dtype={'date':str})
                assert len(frame)==summary['rows']==1728
                frames.append(frame)
    if not frames:raise RuntimeError('No complete exploratory subset files')
    frame=pd.concat(frames,ignore_index=True)
    matched=[date for date in design['dates'] if all(x['complete'] for x in availability if x['date']==date)]
    frame['matched_date']=frame['date'].isin(matched)
    frame['marginal_width']=np.maximum(0,frame['marginal_upper']-frame['marginal_lower'])
    frame.to_csv(out/'cases.csv',index=False)
    (out/'availability.json').write_text(json.dumps(availability,indent=2)+'\n')
    base=frame[frame['matched_date']].copy();rows=[];details={}
    for model in ['all']+design['models']:
        for size in ['all',4,8]:
            part=base if model=='all' else base[base['model']==model]
            if size!='all':part=part[part['query_size']==size]
            for stratum in ['all','informative']:
                sub=part if stratum=='all' else part[part['informative']==1]
                key=f'{model}|{size}|{stratum}'
                row={'model':model,'query_size':size,'stratum':stratum,'cases':len(sub),'dates':int(sub['date'].nunique()),
                     'q_zero':int((sub['q']==0).sum()),'q_one':int((sub['q']==1).sum()),
                     'at_most_two_query_uncertain':int((sub['query_uncertain_sites']<=2).sum()),
                     'all_complement_sites_deterministic':int(sub['complement_sites_deterministic'].sum()),
                     'empirical_complement_count_constant':int(sub['empirical_complement_count_constant'].sum()),
                     'empirical_total_count_constant':int(sub['empirical_total_count_constant'].sum()),
                     'count_narrower_cases':int((sub['count_minus_pair_width'] < -TOL).sum()),
                     'pair_narrower_cases':int((sub['count_minus_pair_width'] > TOL).sum()),
                     'equal_width_cases':int((np.abs(sub['count_minus_pair_width'])<=TOL).sum())}
                intervals={}
                for mode in MODES:
                    est=estimate(sub,sub[mode+'_width'],design,weights);intervals[mode]=est
                    row[mode+'_width']=est['mean'];row[mode+'_low']=est['low'];row[mode+'_high']=est['high']
                    row[mode+'_identified_count']=int((sub[mode+'_width']<=TOL).sum())
                difference=estimate(sub,sub['count_minus_pair_width'],design,weights)
                row['count_minus_pair_mean']=difference['mean'];row['difference_low']=difference['low'];row['difference_high']=difference['high']
                count_in_pair=(sub['count_lower']>=sub['pair_lower']-TOL)&(sub['count_upper']<=sub['pair_upper']+TOL)
                pair_in_count=(sub['pair_lower']>=sub['count_lower']-TOL)&(sub['pair_upper']<=sub['count_upper']+TOL)
                row['count_interval_inside_pair_count']=int(count_in_pair.sum());row['pair_interval_inside_count_count']=int(pair_in_count.sum())
                details[key]={'widths':intervals,'count_minus_pair':difference};rows.append(row)
    pd.DataFrame(rows).to_csv(out/'width-summary.csv',index=False)
    decisions=[]
    for size in [4,8]:
        for c in design['cost_ratios']:
            part=base[base['query_size']==size]
            for stratum in ['all','near_boundary','informative_near_boundary']:
                sub=part
                if stratum!='all':sub=sub[np.abs(sub['q']-c)<=.1+TOL]
                if stratum=='informative_near_boundary':sub=sub[sub['informative']==1]
                row={'query_size':size,'cost_ratio':c,'stratum':stratum,'cases':len(sub),'dates':int(sub['date'].nunique()),
                     'ties':int((np.abs(sub['q']-c)<=TOL).sum()),'q_zero':int((sub['q']==0).sum()),'q_one':int((sub['q']==1).sum()),
                     'all_complement_sites_deterministic':int(sub['complement_sites_deterministic'].sum())}
                for mode in MODES:
                    certified=(sub[mode+'_upper']<=c+TOL)|(sub[mode+'_lower']>=c-TOL)
                    est=estimate(sub,certified.astype(float),design,weights)
                    row[mode+'_certified']=est['mean'];row[mode+'_low']=est['low'];row[mode+'_high']=est['high']
                decisions.append(row)
    pd.DataFrame(decisions).to_csv(out/'decision-summary.csv',index=False)
    by_condition=base.groupby(['model','lead','geometry','query_size','query_type','informative'],observed=True).agg(
        cases=('q','size'),pair_width=('pair_width','mean'),count_width=('count_width','mean'),
        restricted_pair_width=('restricted_pair_width','mean'),difference=('count_minus_pair_width','mean')).reset_index()
    by_condition.to_csv(out/'condition-summary.csv',index=False)
    summary={'exploratory':True,'scheduled_dates':len(design['dates']),'matched_dates':len(matched),'matched_date_list':matched,
             'complete_forecast_units':sum(x['complete'] for x in availability),'available_rows':len(frame),
             'matched_cases':len(base),'informative_cases':int(base['informative'].sum()),'encoding':encoding,
             'oracle_max_absolute_error':float(max(np.max(np.abs(frame['q']-frame['count_oracle_q'])),np.max(np.abs(frame['q']-frame['mask_oracle_q'])))),
             'max_primal_residual':float(frame['max_primal_residual'].max()),'max_dual_violation':float(frame['max_dual_violation'].max()),
             'max_duality_gap':float(frame['max_duality_gap'].max()),'details':details}
    (out/'summary.json').write_text(json.dumps(clean(summary),indent=2,allow_nan=False)+'\n')
    table_rows=[r for r in rows if r['model']=='all' and r['query_size']!='all']
    columns=[('query_size','Query sites'),('stratum','Stratum'),('cases','N'),('dates','Dates'),('q_zero','q=0'),('q_one','q=1'),
             ('all_complement_sites_deterministic','All outside sites fixed'),('pair_width','Universe pairs width'),('count_width','Universe count width'),
             ('count_narrower_cases','Count narrower'),('pair_narrower_cases','Pairs narrower'),('equal_width_cases','Equal width')]
    (out/'table-subsets.md').write_text(markdown_table(clean(table_rows),columns)+'\n')
    print(json.dumps(clean({k:v for k,v in summary.items() if k!='details'}),indent=2))

if __name__=='__main__':main()
