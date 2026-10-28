"""Isolate the numerical entropy-gradient floor while holding estimates fixed."""
import argparse,json
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from inference_core import estimate_change,NUMERICAL_TOL
from audit_inference import sign,clean_json
from summarize_inference import probability_summary

def run(analysis_path,destination):
    source=ROOT/analysis_path;meta=json.loads((source/'analysis.json').read_text())
    assert meta['max_units_requested'] is None and not meta['refreshed']
    units=[u for u in map(json.loads,(source/'units.jsonl').read_text().splitlines()) if u['primary']]
    fit=json.loads((ROOT/meta['model_path']/'fit.json').read_text());k=len(fit['class_names'])
    files={r['landscape_id']:r for r in fit['prediction_files']}
    draw_meta=json.loads((ROOT/meta['draw_manifest_path']).read_text());draws={(r['landscape_id'],r['year_a'],r['year_b']):r for r in draw_meta['draws']}
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve previous gradient checks')
    out.mkdir(parents=True);(out/'raw').mkdir();cache={};rows=[];aggregate=defaultdict(lambda:defaultdict(list))
    floors=[1e-2,1e-4,1e-6,1e-8,1e-10]
    for u in units:
        lid=u['landscape_id'];a=u['year_a']-2021;b=u['year_b']-2021;truth=u['true_change']
        print('GRADIENT',meta['taxonomy'],meta['representation'],u['unit_id'],flush=True)
        if lid not in cache:
            entry=files[lid];assert digest(ROOT/entry['path'])==entry['sha256']
            with np.load(ROOT/entry['path']) as z:cache[lid]=(z['probabilities'],z['labels'])
        p,y=cache[lid];draw=draws[lid,a+2021,b+2021];assert digest(ROOT/draw['path'])==draw['sha256']
        with np.load(ROOT/draw['path']) as z:ia=z['a'][:,:128].astype(int);ib=z['b'][:,:128].astype(int)
        with np.load(source/u['raw_path']) as z:original={key:z[key] for key in z.files}
        raw={}
        for method in ['direct','model_assisted']:
            pa,pb=(None,None) if method=='direct' else (p[a],p[b])
            for design in ['paired','independent']:
                original_prefix=f'{method}_{design}_128_';baseline_se=None
                for floor in floors:
                    result=estimate_change(y[a],y[b],pa,pb,ia,ia if design=='paired' else ib,k,design=='paired',floor)
                    assert np.array_equal(result['estimate'],original[original_prefix+'estimate'])
                    if floor==1e-6:
                        assert np.array_equal(result['se'],original[original_prefix+'se'])
                        assert np.array_equal(result['direction'],original[original_prefix+'direction'])
                    if method=='direct' and floor<1/128:
                        if baseline_se is None:baseline_se=result['se']
                        else:assert np.array_equal(baseline_se,result['se'])
                    covered=(result['low']<=truth+NUMERICAL_TOL)&(result['high']>=truth-NUMERICAL_TOL)
                    reported=result['direction']!=0;wrong=reported&(result['direction']!=sign(truth));error=result['estimate']-truth
                    prefix=f'{method}_{design}_{floor}_'
                    for name in ['se','direction']:raw[prefix+name]=result[name]
                    raw[prefix+'covered']=covered;raw[prefix+'wrong']=wrong
                    row=dict(unit_id=u['unit_id'],taxonomy=meta['taxonomy'],representation=meta['representation'],method=method,design=design,
                        gradient_floor=floor,n=128,mse=float(np.mean(error**2)),coverage=float(covered.mean()),report_rate=float(reported.mean()),
                        wrong_report_rate=float(wrong.mean()),reports=int(reported.sum()),wrong_reports=int(wrong.sum()),mean_se=float(result['se'].mean()))
                    rows.append(row);key=(method,design,floor)
                    for name,value in dict(squared_error=error**2,coverage=covered,report_rate=reported,wrong_report_rate=wrong,mean_se=result['se']).items():aggregate[key][name].append(value)
        np.savez_compressed(out/'raw'/f"{u['unit_id']}.npz",**raw)
    frame=pd.DataFrame(rows);frame.to_csv(out/'unit-performance.csv',index=False);summary=[]
    for (method,design,floor),values in aggregate.items():
        row=dict(taxonomy=meta['taxonomy'],representation=meta['representation'],method=method,design=design,gradient_floor=floor,n=128,units=len(units),replications=500)
        for name,value in values.items():
            mean,se=probability_summary(value);row[name]=mean;row[name+'_mcse']=se
        row['mse']=row.pop('squared_error');row.pop('squared_error_mcse');row['rmse']=float(np.sqrt(row['mse']))
        g=frame[(frame.method==method)&(frame.design==design)&(frame.gradient_floor==floor)]
        row['reports']=int(g.reports.sum());row['wrong_reports']=int(g.wrong_reports.sum());row['wrong_conditional']=row['wrong_reports']/row['reports'] if row['reports'] else None
        summary.append(row)
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False)
    (out/'analysis.json').write_text(json.dumps(clean_json(dict(completed_at_utc=now(),plan_path='protocol/plan-v12-gradient-sensitivity.md',
        exploratory=True,analysis_path=analysis_path,analysis_sha256=digest(source/'analysis.json'),floors=floors,summary=summary,
        checks='All point estimates identical; original-floor SE/directions bitwise reproduced; direct below1/128 invariant')),indent=2,allow_nan=False)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',required=True);p.add_argument('--destination',required=True);a=p.parse_args();run(a.analysis,a.destination)
