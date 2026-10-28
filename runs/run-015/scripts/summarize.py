"""Offline primary summaries from saved selected temperatures and bound CSVs.

Writes only to --output. Historical rank reconstruction uses earlier forecast
dates only. All numerical manuscript fragments are generated here or in the
secondary-analysis report; no values need manual transcription.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from record import ROOT
from bounds import TOL

MODES=['marginal','aggregate','pair']

def clean(value):
    if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean(v) for v in value]
    if isinstance(value,np.generic):value=value.item()
    if isinstance(value,float) and not np.isfinite(value):return None
    return value

def markdown_table(rows,columns):
    lines=['| '+' | '.join(title for key,title in columns)+' |','| '+' | '.join('---' for _ in columns)+' |']
    for row in rows:
        cells=[]
        for key,title in columns:
            v=row.get(key)
            cells.append('—' if v is None else (f'{v:.4f}' if isinstance(v,float) else str(v)))
        lines.append('| '+' | '.join(cells)+' |')
    return '\n'.join(lines)

def bootstrap_weights(design):
    D=len(design['dates']);block=design['bootstrap_block_length'];R=design['bootstrap_repetitions']
    rng=np.random.default_rng(design['seed'])
    starts=rng.integers(0,D,(R,int(np.ceil(D/block))))
    ids=((starts[:,:,None]+np.arange(block))%D).reshape(R,-1)[:,:D]
    return np.eye(D,dtype=np.int32)[ids].sum(axis=1)

def estimate(frame,values,design,weights):
    totals=np.zeros(len(design['dates']));counts=np.zeros_like(totals)
    index={date:i for i,date in enumerate(design['dates'])}
    for date,value in zip(frame['date'],values):
        i=index[str(date)];totals[i]+=value;counts[i]+=1
    if counts.sum()==0:return {'mean':None,'low':None,'high':None,'n':0,'dates':0}
    numerator=weights@totals;denominator=weights@counts
    boot=np.divide(numerator,denominator,out=np.full(len(numerator),np.nan),where=denominator>0)
    finite=boot[np.isfinite(boot)]
    return {'mean':float(totals.sum()/counts.sum()),'low':float(np.quantile(finite,.025)),
            'high':float(np.quantile(finite,.975)),'n':int(counts.sum()),'dates':int((counts>0).sum())}

def ratio_estimate(frame,numerator,denominator,design,weights):
    sums=np.zeros((len(design['dates']),2));index={date:i for i,date in enumerate(design['dates'])}
    for date,a,b in zip(frame['date'],numerator,denominator):sums[index[str(date)]]+=[a,b]
    total=sums.sum(axis=0)
    if total[1]<=TOL:return {'ratio':None,'low':None,'high':None}
    boot=weights@sums;valid=boot[:,1]>TOL;ratios=boot[valid,0]/boot[valid,1]
    return {'ratio':float(total[0]/total[1]),'low':float(np.quantile(ratios,.025)),
            'high':float(np.quantile(ratios,.975))}

def assemble(design,root):
    frames=[];availability=[];pmfs=[]
    for model in design['models']:
        for lead in design['leads']:
            previous=[]
            for date in design['dates']:
                folder=root/'data/weather'/date/model/str(lead)
                result=root/'results/units'/date/model/str(lead)/'bounds-50.csv'
                complete=(folder/'complete.json').exists() and result.exists()
                availability.append({'date':date,'model':model,'lead':lead,'complete':bool(complete)})
                if not complete:continue
                source=folder/'temperatures.npz';saved=np.load(source,allow_pickle=False);temps=saved['kelvin']
                portfolios=json.loads(str(saved['portfolios_json']))
                frame=pd.read_csv(result,dtype={'date':str});assert len(frame)==324
                frame['historical_q']=np.nan
                bank=previous[-6:]
                for pi,portfolio in enumerate(portfolios):
                    for size,indices in design['sizes'].items():
                        size=int(size);now_values=temps[:,pi,:][:,indices]
                        for threshold in design['thresholds_c']:
                            X=now_values>=threshold+273.15;sums=X.sum(axis=1)
                            pmf=np.bincount(sums,minlength=size+1)/50
                            pmfs.append({'date':date,'model':model,'lead':lead,**portfolio,'n':size,
                                         'threshold_c':threshold,'pmf':pmf.tolist()})
                            selector=(frame['portfolio_index']==pi)&(frame['n']==size)&(frame['threshold_c']==threshold)
                            selected=frame.loc[selector]
                            for idx,row in selected.iterrows():
                                q=float(pmf[int(row['k']):].sum());assert abs(q-row['q'])<TOL
                            if len(bank)>=3:
                                cut=50-X.sum(axis=0)
                                reconstructed=np.concatenate([r[:,pi,:][:,indices]>cut for r in bank])
                                assert np.allclose(reconstructed.mean(axis=0),X.mean(axis=0),rtol=0,atol=1e-12)
                                for idx,row in selected.iterrows():
                                    frame.loc[idx,'historical_q']=np.mean(reconstructed.sum(axis=1)>=row['k'])
                frame['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
                frames.append(frame)
                # Stable sorts break ties by original row/member number 1..50.
                ranks=np.argsort(np.argsort(temps,axis=0,kind='stable'),axis=0,kind='stable')+1
                previous.append(ranks)
    if not frames:raise RuntimeError('No completed unit analyses')
    frame=pd.concat(frames,ignore_index=True)
    matched=[date for date in design['dates'] if all(x['complete'] for x in availability if x['date']==date)]
    frame['matched_date']=frame['date'].isin(matched)
    for mode in MODES:frame[mode+'_width']=np.maximum(0,frame[mode+'_upper']-frame[mode+'_lower'])
    frame['midpoint_q']=(frame['pair_lower']+frame['pair_upper'])/2
    frame['exact_pair']=(frame['pair_width']<=TOL).astype(int)
    frame['marginal_exact']=(frame['marginal_width']<=TOL).astype(int)
    return frame,availability,pmfs,matched

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--root',default=str(ROOT));a=p.parse_args()
    root=Path(a.root).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    if out==root or root in out.parents:
        # In normal execution results live in the research directory. VERIFY
        # passes a separate output directory; this script never rewrites inputs.
        pass
    design=json.loads((root/'protocol/design-v1.json').read_text());weights=bootstrap_weights(design)
    frame,availability,pmfs,matched=assemble(design,root)
    frame.to_csv(out/'cases.csv',index=False)
    with (out/'count-distributions.jsonl').open('w') as f:
        for row in pmfs:f.write(json.dumps(row,sort_keys=True)+'\n')
    (out/'availability.json').write_text(json.dumps(availability,indent=2)+'\n')
    rows=[];details={}
    primary=frame[frame['matched_date']&(frame['n']==12)].copy()
    for size in [12,8,4]:
        for model in ['all']+design['models']:
            for lead in ['all']+design['leads']:
                for geometry in ['all']+list(design['geometries']):
                    base=frame[frame['matched_date']&(frame['n']==size)]
                    if model!='all':base=base[base['model']==model]
                    if lead!='all':base=base[base['lead']==lead]
                    if geometry!='all':base=base[base['geometry']==geometry]
                    for stratum in ['all','informative']:
                        sub=base if stratum=='all' else base[base['informative']==1]
                        label=f'{size}|{model}|{lead}|{geometry}|{stratum}'
                        row={'n_sites':size,'model':model,'lead':lead,'geometry':geometry,'stratum':stratum,
                             'cases':int(len(sub)),'dates':int(sub['date'].nunique()),
                             'q_zero':int((sub['q']==0).sum()),'q_one':int((sub['q']==1).sum()),
                             'all_sites_deterministic':int((sub['uncertain_sites']==0).sum()),
                             'at_most_two_uncertain':int((sub['uncertain_sites']<=2).sum()),
                             'marginal_exact_count':int(sub['marginal_exact'].sum()),
                             'pair_exact_count':int(sub['exact_pair'].sum())}
                        detailed={}
                        for mode in MODES:
                            est=estimate(sub,sub[mode+'_width'],design,weights);detailed[mode]=est
                            row[mode+'_width']=est['mean'];row[mode+'_low']=est['low'];row[mode+'_high']=est['high']
                        share=ratio_estimate(sub,sub['marginal_width']-sub['aggregate_width'],sub['marginal_width']-sub['pair_width'],design,weights)
                        detailed['aggregate_reduction_share']=share
                        row['aggregate_reduction_share']=share['ratio'];rows.append(row);details[label]=detailed
    pd.DataFrame(rows).to_csv(out/'width-summary.csv',index=False)
    decisions=[]
    for model in ['all']+design['models']:
        for c in design['cost_ratios']:
            base=primary if model=='all' else primary[primary['model']==model]
            for stratum in ['all','near_boundary','informative_near_boundary']:
                sub=base
                if stratum!='all':sub=sub[np.abs(sub['q']-c)<=.1+TOL]
                if stratum=='informative_near_boundary':sub=sub[sub['informative']==1]
                row={'model':model,'cost_ratio':c,'stratum':stratum,'cases':len(sub),
                     'dates':int(sub['date'].nunique()),'ties':int((np.abs(sub['q']-c)<=TOL).sum()),
                     'oracle_act_strict':int((sub['q']>c+TOL).sum()),
                     'oracle_skip_strict':int((sub['q']<c-TOL).sum()),
                     'q_zero':int((sub['q']==0).sum()),'q_one':int((sub['q']==1).sum()),
                     'deterministic':int((sub['uncertain_sites']==0).sum())}
                for mode in MODES:
                    certified=(sub[mode+'_upper']<=c+TOL)|(sub[mode+'_lower']>=c-TOL)
                    est=estimate(sub,certified.astype(float),design,weights)
                    row[mode+'_certified']=est['mean'];row[mode+'_low']=est['low'];row[mode+'_high']=est['high']
                decisions.append(row)
    pd.DataFrame(decisions).to_csv(out/'decision-summary.csv',index=False)
    reconstruction=[]
    for availability_label in ['all','historical_matched']:
        base=primary if availability_label=='all' else primary[primary['historical_q'].notna()]
        for stratum in ['all','informative']:
            sub=base if stratum=='all' else base[base['informative']==1]
            for method,column in [('independent','independent_q'),('historical_copula','historical_q'),('pair_midpoint','midpoint_q')]:
                part=sub[sub[column].notna()]
                errors=np.abs(part[column]-part['q'])
                est=estimate(part,errors,design,weights)
                row={'availability':availability_label,'stratum':stratum,'method':method,'cases':len(part),
                     'dates':int(part['date'].nunique()),'mean_absolute_error':est['mean'],'mae_low':est['low'],'mae_high':est['high']}
                for c in design['cost_ratios']:
                    difference=(part[column]>c)!=(part['q']>c)
                    regret=np.where(difference,np.abs(part['q']-c),0.0)
                    row[f'regret_{c}']=float(regret.mean()) if len(part) else None
                    row[f'zero_regret_disagreements_{c}']=int((difference&(np.abs(part['q']-c)<=TOL)).sum())
                    row[f'positive_regret_disagreements_{c}']=int((difference&(np.abs(part['q']-c)>TOL)).sum())
                reconstruction.append(row)
    pd.DataFrame(reconstruction).to_csv(out/'reconstruction-summary.csv',index=False)
    strata=primary.groupby(['model','lead','geometry','uncertain_sites'],observed=True).agg(
        cases=('q','size'),marginal_width=('marginal_width','mean'),aggregate_width=('aggregate_width','mean'),
        pair_width=('pair_width','mean'),pair_exact=('exact_pair','mean'),pair_possible_states=('pair_possible_states','mean'),
        observed_patterns=('observed_patterns','mean')).reset_index()
    strata.to_csv(out/'uncertainty-strata.csv',index=False)
    summary={'scheduled_dates':len(design['dates']),'matched_dates':len(matched),'matched_date_list':matched,
             'scheduled_forecast_units':len(availability),'complete_forecast_units':sum(x['complete'] for x in availability),
             'all_available_rows':len(frame),'primary_cases':len(primary),'primary_informative_cases':int(primary['informative'].sum()),
             'primary_historical_missing':int(primary['historical_q'].isna().sum()),
             'max_primal_residual':float(frame['max_primal_residual'].max()),
             'max_dual_violation':float(frame['max_dual_violation'].max()),'max_duality_gap':float(frame['max_duality_gap'].max()),
             'status':'adequate_predeclared_date_count' if len(matched)>=12 else 'undersized_or_incomplete',
             'bootstrap_repetitions':design['bootstrap_repetitions'],'bootstrap_block_length':design['bootstrap_block_length'],
             'widths':details,'design_sha256':hashlib.sha256((root/'protocol/design-v1.json').read_bytes()).hexdigest()}
    (out/'summary.json').write_text(json.dumps(clean(summary),indent=2,allow_nan=False)+'\n')
    main_rows=[r for r in rows if r['n_sites']==12 and r['geometry']=='all' and r['lead']=='all']
    table=markdown_table(clean(main_rows),[('model','System'),('stratum','Cases'),('cases','N'),('dates','Dates'),
        ('q_zero','q=0'),('q_one','q=1'),('at_most_two_uncertain','≤2 uncertain sites'),
        ('marginal_width','Marginal width'),('aggregate_width','Aggregate width'),('pair_width','Pair width'),
        ('pair_exact_count','Exact pair count'),('aggregate_reduction_share','Aggregate share')])
    (out/'table-primary.md').write_text(table+'\n')
    print(json.dumps(clean({k:v for k,v in summary.items() if k!='widths'}),indent=2))

if __name__=='__main__':main()
