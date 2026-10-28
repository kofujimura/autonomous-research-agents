"""Exploratory equal-label-budget power weighting of frozen predictions."""
import argparse,json
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from power_tuning_core import evaluate
from audit_inference import clean_json,sign
from inference_core import NUMERICAL_TOL
from summarize_inference import probability_summary

def run(analysis_path,destination):
    source=ROOT/analysis_path;meta=json.loads((source/'analysis.json').read_text())
    assert meta['max_units_requested'] is None and meta['taxonomy']=='broad' and not meta['refreshed']
    units=[u for u in map(json.loads,(source/'units.jsonl').read_text().splitlines()) if u['primary']]
    fit=json.loads((ROOT/meta['model_path']/'fit.json').read_text());k=len(fit['class_names'])
    files={r['landscape_id']:r for r in fit['prediction_files']}
    dm=json.loads((ROOT/meta['draw_manifest_path']).read_text());draws={(r['landscape_id'],r['year_a'],r['year_b']):r for r in dm['draws']}
    out=ROOT/destination
    if out.exists():raise FileExistsError('Keep earlier weighting results')
    out.mkdir(parents=True);(out/'raw').mkdir();cache={};rows=[];aggregate=defaultdict(lambda:defaultdict(list));n=128
    for u in units:
        lid=u['landscape_id'];a=u['year_a']-2021;b=u['year_b']-2021;truth=u['true_change']
        print('POWER WEIGHT',meta['representation'],u['unit_id'],flush=True)
        if lid not in cache:
            f=files[lid];assert digest(ROOT/f['path'])==f['sha256']
            with np.load(ROOT/f['path']) as z:cache[lid]=(z['probabilities'],z['labels'])
        p,y=cache[lid];pa=p[a];pb=p[b];ya=y[a];yb=y[b]
        d=draws[lid,a+2021,b+2021];assert digest(ROOT/d['path'])==d['sha256']
        with np.load(ROOT/d['path']) as z:ia=z['a'][:,:n].astype(int);ib=z['b'][:,:n].astype(int)
        raw={}
        for design in ['paired','independent']:
            sb=ia if design=='paired' else ib
            for mode in ['same_sample','crossfit']:
                result=evaluate(ya,yb,pa,pb,ia,sb,k,design=='paired',mode)
                error=result['estimate']-truth;covered=(result['low']<=truth+NUMERICAL_TOL)&(result['high']>=truth-NUMERICAL_TOL)
                reported=result['direction']!=0;wrong=reported&(result['direction']!=sign(truth))
                pre=f'{mode}_{design}_'
                for name,value in result.items():raw[pre+name]=value
                raw[pre+'covered']=covered;raw[pre+'wrong']=wrong
                weights=np.stack([result['lambda_a'],result['lambda_b']]);projection=result['projected_a']|result['projected_b']
                qa=np.bincount(ya,minlength=k)/len(ya);qb=np.bincount(yb,minlength=k)/len(yb)
                row=dict(unit_id=u['unit_id'],landscape_id=lid,representation=meta['representation'],mode=mode,design=design,n=n,
                         N=len(ya),true_change=truth,replications=len(error),mse=float(np.mean(error**2)),bias=float(error.mean()),
                         coverage=float(covered.mean()),report_rate=float(reported.mean()),wrong_report_rate=float(wrong.mean()),
                         reports=int(reported.sum()),wrong_reports=int(wrong.sum()),projection_any_year=float(projection.mean()),
                         mean_lambda=float(weights.mean()),lambda_zero_fraction=float((weights==0).mean()),lambda_one_fraction=float((weights==1).mean()),
                         max_absolute_empirical_raw_proportion_bias_a=float(np.abs(result['raw_a'].mean(axis=0)-qa).max()),
                         max_absolute_empirical_raw_proportion_bias_b=float(np.abs(result['raw_b'].mean(axis=0)-qb).max()))
                rows.append(row);key=(mode,design)
                for name,value in dict(squared_error=error**2,error=error,coverage=covered,report_rate=reported,wrong_report_rate=wrong,
                                       projection_any_year=projection,zero_se=result['se']==0,
                                       mean_lambda=weights.mean(axis=0),lambda_zero_fraction=(weights==0).mean(axis=0),
                                       lambda_one_fraction=(weights==1).mean(axis=0)).items():aggregate[key][name].append(value)
        target=out/'raw'/f"{u['unit_id']}.npz";np.savez_compressed(target,**raw)
        with (out/'units.jsonl').open('a') as f:f.write(json.dumps(clean_json(dict(unit_id=u['unit_id'],raw_path=str(target.relative_to(out)),raw_sha256=digest(target))),allow_nan=False)+'\n')
    frame=pd.DataFrame(rows);frame.to_csv(out/'unit-performance.csv',index=False);summary=[]
    for (mode,design),values in aggregate.items():
        row=dict(representation=meta['representation'],mode=mode,design=design,n=n,units=len(units),replications=500)
        for name,value in values.items():
            mean,se=probability_summary(value);row[name]=mean;row[name+'_mcse']=se
        row['mse']=row.pop('squared_error');row['mse_mcse']=row.pop('squared_error_mcse');row['rmse']=float(np.sqrt(row['mse']))
        row['rmse_mcse']=row['mse_mcse']/(2*row['rmse']) if row['rmse'] else 0.;row['bias']=row.pop('error');row.pop('error_mcse')
        g=frame[(frame['mode']==mode)&(frame.design==design)]
        row['reports']=int(g.reports.sum());row['wrong_reports']=int(g.wrong_reports.sum())
        row['wrong_conditional']=row['wrong_reports']/row['reports'] if row['reports'] else None
        summary.append(row)
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False)
    result=dict(completed_at_utc=now(),plan_path='protocol/plan-v8-power-tuning.md',exploratory=True,
                analysis_path=analysis_path,analysis_sha256=digest(source/'analysis.json'),units_sha256=digest(source/'units.jsonl'),
                units=len(units),representation=meta['representation'],summary=summary,
                interpretation='Bounded scalar control-variate comparison at preselected n128. Crossfit raw means have conditional design-unbiasedness; projected entropy and first-order intervals have no finite-sample guarantee. Not a verbatim implementation of complete published PPI++.')
    (out/'analysis.json').write_text(json.dumps(clean_json(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),units=len(units),destination=destination)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();run(a.analysis,a.destination)
