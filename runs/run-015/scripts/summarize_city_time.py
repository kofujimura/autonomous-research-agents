"""Offline exploratory city/time boundary summaries; writes only --output."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import TOL
from record import ROOT
from summarize import bootstrap_weights,clean,estimate,markdown_table

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--output',required=True);a=p.parse_args()
    root=Path(a.root);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    design=json.loads((root/'protocol/design-v4.json').read_text())
    boot_design={'dates':design['dates'],'bootstrap_block_length':2,'bootstrap_repetitions':2000,'seed':20261026}
    weights=bootstrap_weights(boot_design);availability=[];frames=[];extraction=[]
    for date in design['dates']:
        for model in design['models']:
            for horizon in [3,7]:
                raw=[root/'data/weather-v4'/date/model/str(24*horizon+t)/'complete.json' for t in [0,6,12,18]]
                endpoint_paths=[root/'results/city-time-units'/endpoint/date/model/str(24*horizon+12)/'bounds.csv'
                                for endpoint in ['snapshot12','maximum4']]
                endpoint_summaries=[p.parent/'summary.json' for p in endpoint_paths]
                complete=all(p.exists() for p in raw+endpoint_paths+endpoint_summaries)
                availability.append({'date':date,'model':model,'horizon':horizon,'complete':complete,
                                     'complete_raw_fields':sum(p.exists() for p in raw)})
                if not complete:continue
                for endpoint,path in zip(['snapshot12','maximum4'],endpoint_paths):
                    result_info=json.loads((path.parent/'summary.json').read_text())
                    assert result_info['output_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
                    part=pd.read_csv(path,dtype={'date':str});assert len(part)==216
                    provenance=root/'data/weather-v4-derived'/endpoint/date/model/str(24*horizon+12)/'provenance.json'
                    info=json.loads(provenance.read_text());comparison=info['original_snapshot_comparison']
                    if endpoint=='snapshot12':extraction.append({'date':date,'model':model,'horizon':horizon,**comparison})
                    part['source_sha256']=info['output_sha256'];frames.append(part)
    matched=[d for d in design['dates'] if all(r['complete'] for r in availability if r['date']==d)]
    (out/'availability.json').write_text(json.dumps(availability,indent=2)+'\n')
    if not frames:
        (out/'summary.json').write_text(json.dumps({'matched_dates':0,'status':'no_complete_horizon','availability':availability},indent=2)+'\n')
        return
    frame=pd.concat(frames,ignore_index=True);frame['matched_date']=frame['date'].isin(matched)
    mask_path=root/'data/cities/land-mask/land-fractions.csv'
    if mask_path.exists():
        mask=pd.read_csv(mask_path)
        land_flags=mask.groupby('portfolio_index')['land_fraction'].min().ge(.5).to_dict()
        frame['all_cells_at_least_half_land']=frame['portfolio_index'].map(land_flags)
        assert frame['all_cells_at_least_half_land'].notna().all()
    else:frame['all_cells_at_least_half_land']=False
    for mode in ['marginal','aggregate','pair']:frame[mode+'_width']=np.maximum(0,frame[mode+'_upper']-frame[mode+'_lower'])
    keys=['date','model','horizon','portfolio_index','threshold_c','k']
    snap=frame[frame['endpoint']=='snapshot12'];maximum=frame[frame['endpoint']=='maximum4']
    joint=snap.merge(maximum,on=keys,suffixes=('_snapshot','_maximum'),validate='one_to_one')
    assert np.all(joint['q_maximum']>=joint['q_snapshot']-TOL)
    joint['common_informative']=(joint['informative_snapshot']==1)&(joint['informative_maximum']==1)
    common=joint[keys+['common_informative']];frame=frame.merge(common,on=keys,validate='many_to_one')
    frame['all_land_informative']=(frame['all_cells_at_least_half_land'])&(frame['informative']==1)
    frame['all_land_common_informative']=(frame['all_cells_at_least_half_land'])&(frame['common_informative'])
    joint['all_land_common_informative']=joint['all_cells_at_least_half_land_snapshot']&joint['common_informative']
    frame.to_csv(out/'cases.csv',index=False);joint.to_csv(out/'paired-cases.csv',index=False)
    base=frame[frame['matched_date']];rows=[];paired=[];decisions=[]
    for kind in ['regular','city']:
        for model in ['all']+design['models']:
            for horizon in ['all',3,7]:
                part=base[base['portfolio_type']==kind]
                if model!='all':part=part[part['model']==model]
                if horizon!='all':part=part[part['horizon']==horizon]
                for endpoint in ['snapshot12','maximum4']:
                    ep=part[part['endpoint']==endpoint]
                    for stratum in ['all','informative','common_informative','all_land_informative','all_land_common_informative']:
                        sub=ep if stratum=='all' else ep[ep[stratum]==1]
                        row={'portfolio_type':kind,'model':model,'horizon':horizon,'endpoint':endpoint,'stratum':stratum,
                             'cases':len(sub),'dates':int(sub['date'].nunique()),'q_zero':int((sub['q']==0).sum()),
                             'q_one':int((sub['q']==1).sum()),'at_most_two_uncertain':int((sub['uncertain_sites']<=2).sum())}
                        for mode in ['marginal','aggregate','pair']:
                            est=estimate(sub,sub[mode+'_width'],boot_design,weights)
                            row[mode+'_width']=est['mean'];row[mode+'_low']=est['low'];row[mode+'_high']=est['high']
                            row[mode+'_identified_count']=int((sub[mode+'_width']<=TOL).sum())
                        rows.append(row)
                        if model=='all' and horizon=='all':
                            for c in [.1,.25,.5]:
                                dec={**{k:row[k] for k in ['portfolio_type','endpoint','stratum','cases','dates']},'cost_ratio':c}
                                for mode in ['marginal','aggregate','pair']:
                                    cert=(sub[mode+'_upper']<=c+TOL)|(sub[mode+'_lower']>=c-TOL)
                                    dec[mode+'_certified']=float(cert.mean()) if len(sub) else None
                                decisions.append(dec)
                # Paired estimates use exactly the same queries/dates for each endpoint.
                subjoint=joint[(joint['matched_date_snapshot'])&(joint['portfolio_type_snapshot']==kind)]
                if model!='all':subjoint=subjoint[subjoint['model']==model]
                if horizon!='all':subjoint=subjoint[subjoint['horizon']==horizon]
                for stratum in ['all','common_informative','all_land_common_informative']:
                    sub=subjoint if stratum=='all' else subjoint[subjoint[stratum]]
                    for mode in ['marginal','aggregate','pair']:
                        delta=sub[mode+'_width_maximum']-sub[mode+'_width_snapshot']
                        est=estimate(sub,delta,boot_design,weights)
                        paired.append({'portfolio_type':kind,'model':model,'horizon':horizon,'stratum':stratum,'mode':mode,
                                       'cases':len(sub),'dates':est['dates'],'maximum_minus_snapshot_width':est['mean'],
                                       'low':est['low'],'high':est['high']})
    pd.DataFrame(rows).to_csv(out/'width-summary.csv',index=False)
    pd.DataFrame(paired).to_csv(out/'paired-width-summary.csv',index=False)
    pd.DataFrame(decisions).to_csv(out/'decision-summary.csv',index=False)
    pd.DataFrame(extraction).to_csv(out/'extraction-checks.csv',index=False)
    summary={'scheduled_dates':len(design['dates']),'matched_dates':len(matched),'matched_date_list':matched,
             'minimum_matched_dates':8,
             'complete_horizons':sum(x['complete'] for x in availability),'complete_raw_forecast_units':sum(x['complete_raw_fields'] for x in availability),
             'matched_cases':len(base),'all_available_cases':len(frame),'exploratory':True,
             'status':'adequate_predeclared_date_count' if len(matched)>=8 else 'undersized_or_incomplete',
             'bootstrap_block_length':2,'bootstrap_repetitions':2000,
             'maximum_below_snapshot_cases':int((joint['q_maximum']<joint['q_snapshot']-TOL).sum()),
             'old_members_compared':sum(x['old_members_compared'] for x in extraction),
             'temperature_value_mismatches':sum(x['temperature_value_mismatches'] for x in extraction),
             'grib_hash_mismatches':sum(x['grib_hash_mismatches'] for x in extraction),
             'max_primal_residual':float(frame['max_primal_residual'].max()),
             'max_dual_violation':float(frame['max_dual_violation'].max()),'max_duality_gap':float(frame['max_duality_gap'].max()),
             'design_sha256':hashlib.sha256((root/'protocol/design-v4.json').read_bytes()).hexdigest()}
    summary['land_fraction_diagnostic_available']=mask_path.exists()
    if mask_path.exists():summary['land_fraction_input_sha256']=hashlib.sha256(mask_path.read_bytes()).hexdigest()
    (out/'summary.json').write_text(json.dumps(clean(summary),indent=2,allow_nan=False)+'\n')
    display=[r for r in rows if r['model']=='all' and r['horizon']=='all']
    (out/'table-city-time.md').write_text(markdown_table(clean(display),[
        ('portfolio_type','Locations'),('endpoint','Time definition'),('stratum','Stratum'),('cases','N'),
        ('q_zero','q=0'),('q_one','q=1'),('at_most_two_uncertain','≤2 uncertain'),
        ('marginal_width','Marginal'),('aggregate_width','Aggregate'),('pair_width','Pairs'),('pair_identified_count','Identified pair')])+'\n')
    print(json.dumps(clean(summary),indent=2))

if __name__=='__main__':main()
