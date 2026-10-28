"""Exploratory numerical sufficient conditions for exact pair identification."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import matrices,TOL
from record import ROOT,now
from summarize import clean,markdown_table

RCOND=1e-10
ROW_TOL=1e-8

def diagnose(X,ks):
    problem=matrices(X,'pair');A=problem['A'];b=problem['b']
    assert np.isfinite(A).all()
    try:U,s,Vt=np.linalg.svd(A,full_matrices=False)
    except np.linalg.LinAlgError:
        # Deterministic numerical fallback for the same matrix and tolerances.
        from scipy.linalg import svd
        U,s,Vt=svd(A,full_matrices=False,lapack_driver="gesvd",check_finite=True)
    rank=int((s>s[0]*RCOND).sum());rows=[]
    for k in ks:
        e=(problem['state_sums']>=k).astype(float);constant=bool(np.all(e==e[0]))
        coefficients=U[:,:rank]@((Vt[:rank]@e)/s[:rank])
        residual=float(np.max(np.abs(A.T@coefficients-e)))
        implied=float(b@coefficients)
        if constant:category='constant_after_pair_support';implied=float(e[0])
        elif rank==len(e):category='full_column_rank'
        elif residual<=ROW_TOL:category='event_in_row_space'
        else:category=None
        if category is not None:
            q=float(np.mean(X.sum(axis=1)>=k));assert abs(implied-q)<=TOL
        rows.append({'k':k,'possible_states':len(e),'constraint_rows':A.shape[0],'numerical_rank':rank,
                     'row_space_residual':residual,'implied_q':implied,'sufficient_category':category,
                     'uncertain_sites':problem['uncertain_sites']})
    return rows

def fixtures():
    tests=[]
    for name,X,k,expected in [
        ('two-site-full-support',np.array([[0,0],[0,1],[1,0],[1,1]]),1,'full_column_rank'),
        ('identical-columns',np.array([[0,0,0],[1,1,1]]),2,'full_column_rank'),
        ('parity',np.array([[0,0,0],[0,1,1],[1,0,1],[1,1,0]]),2,None)]:
        row=diagnose(X,[k])[0];assert row['sufficient_category']==expected,(name,row)
        tests.append({'fixture':name,**row})
    return tests

def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=20);p.add_argument('--output',required=True);p.add_argument('--summarize',action='store_true');a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    frame=pd.read_csv(a.cases,dtype={'date':str});base=frame[frame['n']==12]
    if not a.summarize:
        tests=fixtures();(out/f'fixtures-{a.start:03d}.json').write_text(json.dumps(clean(tests),indent=2)+'\n')
        units=base[['date','model','lead','source_sha256']].drop_duplicates().sort_values(['date','model','lead'])
        for _,unit in units.iloc[a.start:a.start+a.count].iterrows():
            folder=ROOT/'data/weather'/unit['date']/unit['model']/str(int(unit['lead']))
            source=folder/'temperatures.npz';assert hashlib.sha256(source.read_bytes()).hexdigest()==unit['source_sha256']
            target=out/'units'/unit['date']/unit['model']/str(int(unit['lead']))/'diagnostics.csv'
            if target.exists():raise RuntimeError('Refuse to overwrite completed diagnostics')
            values=np.load(source,allow_pickle=False)['kelvin'];rows=[]
            part=base[(base['date']==unit['date'])&(base['model']==unit['model'])&(base['lead']==unit['lead'])]
            for (pi,t),group in part.groupby(['portfolio_index','threshold_c'],sort=True):
                X=(values[:,int(pi),:]>=t+273.15).astype(np.uint8)
                diagnostics={r['k']:r for r in diagnose(X,group['k'].astype(int).tolist())}
                for _,old in group.iterrows():
                    row=diagnostics[int(old['k'])];category=row.pop('sufficient_category')
                    identified=old['pair_width']<=TOL
                    if category is not None:assert identified and old['pair_lower']-TOL<=row['implied_q']<=old['pair_upper']+TOL
                    else:category='identified_other' if identified else 'not_identified'
                    rows.append({**{key:old[key] for key in ['date','model','lead','center','geometry','portfolio_index','threshold_c','k','case_key','q','informative','matched_date','observed_patterns','pair_width']},
                                 **row,'category':category})
            assert len(rows)==108;target.parent.mkdir(parents=True,exist_ok=True)
            pd.DataFrame(rows).to_csv(target,index=False)
            print(json.dumps({'date':unit['date'],'model':unit['model'],'lead':int(unit['lead']),'completed_at_utc':now(),'rows':len(rows)}),flush=True)
        return
    paths=sorted((out/'units').rglob('diagnostics.csv'));allrows=pd.concat([pd.read_csv(path,dtype={'date':str}) for path in paths],ignore_index=True)
    assert not allrows['case_key'].duplicated().any();allrows.to_csv(out/'cases.csv',index=False)
    summaries=[]
    for product in ['all','aifs-ens','ifs']:
        for stratum in ['all','informative']:
            sub=allrows[allrows['matched_date']]
            if product!='all':sub=sub[sub['model']==product]
            if stratum=='informative':sub=sub[sub['informative']==1]
            for category in ['constant_after_pair_support','full_column_rank','event_in_row_space','identified_other','not_identified']:
                part=sub[sub['category']==category]
                summaries.append({'model':product,'stratum':stratum,'category':category,'cases':len(part),'stratum_cases':len(sub),
                                  'fraction':len(part)/len(sub) if len(sub) else None,'dates':int(part['date'].nunique()),
                                  'at_most_two_uncertain':int((part['uncertain_sites']<=2).sum()),
                                  'q_zero':int((part['q']==0).sum()),'q_one':int((part['q']==1).sum())})
    pd.DataFrame(summaries).to_csv(out/'category-summary.csv',index=False)
    report={'exploratory':True,'unit_count':len(paths),'all_available_cases':len(allrows),
            'numerical_rank_relative_threshold':RCOND,'row_space_max_residual_tolerance':ROW_TOL,'categories':clean(summaries),
            'scope':'Known numerical sufficient conditions, not formal proof or new bounding theory; rank deficiency does not prove joint-law nonuniqueness.'}
    (out/'summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    display=[r for r in summaries if r['model']=='all']
    (out/'table-categories.md').write_text(markdown_table(display,[('stratum','Stratum'),('category','Sufficient explanation or remainder'),('cases','N'),('stratum_cases','Denominator'),('fraction','Fraction'),('at_most_two_uncertain','≤2 uncertain')])+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='categories'},indent=2))

if __name__=='__main__':main()
