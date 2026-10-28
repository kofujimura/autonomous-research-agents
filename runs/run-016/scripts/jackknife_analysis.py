"""Exploratory n=128 jackknife comparison from the unchanged main audit draws."""
import argparse,json
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from jackknife_core import jackknife_change
from audit_inference import clean_json,sign
from inference_core import NUMERICAL_TOL
from summarize_inference import probability_summary

def run(analysis_path,destination):
    d=ROOT/analysis_path;meta=json.loads((d/'analysis.json').read_text())
    assert meta['max_units_requested'] is None and meta['taxonomy']=='broad'
    units=[r for r in map(json.loads,(d/'units.jsonl').read_text().splitlines()) if r['primary']]
    fit=json.loads((ROOT/meta['model_path']/'fit.json').read_text());k=len(fit['class_names'])
    files={r['landscape_id']:r for r in fit['prediction_files']}
    draw_meta=json.loads((ROOT/meta['draw_manifest_path']).read_text())
    draws={(r['landscape_id'],r['year_a'],r['year_b']):r for r in draw_meta['draws']}
    out=ROOT/destination
    if out.exists():raise FileExistsError('Keep original exploratory outputs')
    out.mkdir(parents=True);(out/'raw').mkdir();rows=[];cache={};aggregate=defaultdict(lambda:defaultdict(list));n=128
    for u in units:
        lid=u['landscape_id'];a=u['year_a']-2021;b=u['year_b']-2021;truth=u['true_change']
        print('JACKKNIFE',meta['representation'],u['unit_id'],flush=True)
        if lid not in cache:
            entry=files[lid];assert digest(ROOT/entry['path'])==entry['sha256']
            with np.load(ROOT/entry['path']) as z:cache[lid]=(z['probabilities'],z['labels'])
        p,y=cache[lid];pa=p[a];pb=p[b];ya=y[a];yb=y[b]
        draw=draws[lid,a+2021,b+2021];assert digest(ROOT/draw['path'])==draw['sha256']
        with np.load(ROOT/draw['path']) as z:ia=z['a'][:,:n].astype(int);ib=z['b'][:,:n].astype(int)
        raw={}
        for method in ['direct','model_assisted']:
            ppa,ppb=(None,None) if method=='direct' else (pa,pb)
            for design in ['paired','independent']:
                sb=ia if design=='paired' else ib
                result=jackknife_change(ya,yb,ppa,ppb,ia,sb,k,design=='paired')
                prefix=f'{method}_{design}_'
                for name,value in result.items():raw[prefix+name]=value
                for variant in ['ordinary','fpc']:
                    estimate=result[variant+'_estimate'];error=estimate-truth;se=result['se']
                    covered=(result[variant+'_low']<=truth+NUMERICAL_TOL)&(result[variant+'_high']>=truth-NUMERICAL_TOL)
                    direction=result[variant+'_direction'];reported=direction!=0;wrong=reported&(direction!=sign(truth))
                    raw[prefix+variant+'_covered']=covered;raw[prefix+variant+'_wrong']=wrong
                    row=dict(unit_id=u['unit_id'],landscape_id=lid,representation=meta['representation'],method=method,design=design,
                             variant=variant,n=n,N=len(ya),true_change=truth,replications=len(estimate),
                             mse=float(np.mean(error**2)),bias=float(error.mean()),coverage=float(covered.mean()),
                             report_rate=float(reported.mean()),wrong_report_rate=float(wrong.mean()),
                             reports=int(reported.sum()),wrong_reports=int(wrong.sum()),zero_se=float((se==0).mean()))
                    rows.append(row);key=(method,design,variant)
                    for name,value in dict(squared_error=error**2,error=error,coverage=covered,report_rate=reported,
                                           wrong_report_rate=wrong,zero_se=se==0).items():aggregate[key][name].append(value)
        target=out/'raw'/f"{u['unit_id']}.npz";np.savez_compressed(target,**raw)
    frame=pd.DataFrame(rows);frame.to_csv(out/'unit-performance.csv',index=False);summary=[]
    for (method,design,variant),values in aggregate.items():
        row=dict(representation=meta['representation'],method=method,design=design,variant=variant,n=n,units=len(units),replications=500)
        for name,value in values.items():
            mean,se=probability_summary(value);row[name]=mean;row[name+'_mcse']=se
        row['mse']=row.pop('squared_error');row['mse_mcse']=row.pop('squared_error_mcse')
        row['rmse']=float(np.sqrt(row['mse']));row['rmse_mcse']=row['mse_mcse']/(2*row['rmse']) if row['rmse']>0 else 0.
        row['bias']=row.pop('error');row.pop('error_mcse')
        selected=frame[(frame.method==method)&(frame.design==design)&(frame.variant==variant)]
        row['reports']=int(selected.reports.sum());row['wrong_reports']=int(selected.wrong_reports.sum())
        row['wrong_conditional']=row['wrong_reports']/row['reports'] if row['reports'] else None
        summary.append(row)
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False)
    result=dict(completed_at_utc=now(),plan_path='protocol/plan-v6a-jackknife-fpc.md',exploratory=True,analysis_path=analysis_path,
                analysis_sha256=digest(d/'analysis.json'),units_sha256=digest(d/'units.jsonl'),units=len(units),summary=summary,
                interpretation='Both ordinary and FPC-scaled bias corrections retained. Approximate intervals; no guarantee at entropy boundaries or for unobserved changes.')
    (out/'analysis.json').write_text(json.dumps(clean_json(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),units=len(units),destination=destination)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();run(a.analysis,a.destination)
