"""Exploratory normal intervals using the local derivative through projection."""
import argparse,json
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from inference_core import proportions,entropy,estimate_change,NUMERICAL_TOL
from audit_inference import sign,clean_json
from summarize_inference import probability_summary

def local_gradient(q):
    active=q>0
    g=np.zeros_like(q);g[active]=-(np.log(q[active])+1)
    average=g.sum(axis=1)/active.sum(axis=1)
    return active*(g-average[:,None])

def values(labels,predictions,indices,gradient):
    result=np.take_along_axis(gradient,labels[indices],axis=1)
    if predictions is not None:
        result-=np.einsum('rk,rnk->rn',gradient,predictions[indices],optimize=True)
    return result

def domain(q,raw):
    active=q>0;m=active.sum(axis=1)
    theta=(np.where(active,raw,0).sum(axis=1)-1)/m
    return dict(singleton=m==1,near_split=(np.abs(raw-theta[:,None])<=1e-10).any(axis=1),
        small_positive=((q>0)&(q<1e-6)).any(axis=1))

def face_estimate(ya,yb,pa,pb,ia,ib,k,paired):
    qa,ra,proja,_=proportions(ya,pa,ia,k);qb,rb,projb,_=proportions(yb,pb,ib,k)
    va=values(ya,pa,ia,local_gradient(qa));vb=values(yb,pb,ib,local_gradient(qb))
    variance=np.var(vb-va,axis=1,ddof=1) if paired else np.var(va,axis=1,ddof=1)+np.var(vb,axis=1,ddof=1)
    n=ia.shape[1];N=len(ya);se=np.sqrt(np.maximum(variance*(1-n/N)/n,0))
    delta=entropy(qb)-entropy(qa);lo=delta-1.96*se;hi=delta+1.96*se
    direction=np.where(lo>NUMERICAL_TOL,1,np.where(hi< -NUMERICAL_TOL,-1,0)).astype(np.int8)
    a=domain(qa,ra);b=domain(qb,rb)
    return dict(estimate=delta,se=se,low=lo,high=hi,direction=direction,
        **{name+'_either_year':a[name]|b[name] for name in a},projected=proja|projb)

def run(analysis_path,destination,plan_path='protocol/plan-v14-projection-derivative.md'):
    source=ROOT/analysis_path;meta=json.loads((source/'analysis.json').read_text())
    assert meta['max_units_requested'] is None
    units=[u for u in map(json.loads,(source/'units.jsonl').read_text().splitlines()) if u['primary']]
    fit=json.loads((ROOT/meta['model_path']/'fit.json').read_text());k=len(fit['class_names'])
    files={r['landscape_id']:r for r in fit['prediction_files']}
    draw_meta=json.loads((ROOT/meta['draw_manifest_path']).read_text())
    draws={(r['landscape_id'],r['year_a'],r['year_b']):r for r in draw_meta['draws']}
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve projection derivative comparisons')
    out.mkdir(parents=True);(out/'raw').mkdir();cache={};rows=[];aggregate=defaultdict(lambda:defaultdict(list))
    for u in units:
        lid=u['landscape_id'];a=u['year_a']-2021;b=u['year_b']-2021;truth=u['true_change']
        print('PROJECTION DERIVATIVE',meta['taxonomy'],meta['representation'],u['unit_id'],flush=True)
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
                sb=ia if design=='paired' else ib
                base=estimate_change(y[a],y[b],pa,pb,ia,sb,k,design=='paired')
                face=face_estimate(y[a],y[b],pa,pb,ia,sb,k,design=='paired')
                prefix=f'{method}_{design}_128_'
                for name in ['estimate','se','direction']:assert np.array_equal(base[name],original[prefix+name])
                assert np.array_equal(face['estimate'],base['estimate'])
                if method=='direct':assert np.allclose(face['se'],base['se'],atol=1e-12,rtol=1e-12)
                error=base['estimate']-truth
                for rule,result in [('original',base),('projection_chain_rule',face)]:
                    covered=(result['low']<=truth+NUMERICAL_TOL)&(result['high']>=truth-NUMERICAL_TOL)
                    reported=result['direction']!=0;wrong=reported&(result['direction']!=sign(truth))
                    name=f'{method}_{design}_{rule}_'
                    for key in ['estimate','se','direction']:raw[name+key]=result[key]
                    raw[name+'covered']=covered;raw[name+'wrong']=wrong
                    indicators={name:face[name] for name in ['singleton_either_year','near_split_either_year','small_positive_either_year','projected']}
                    for key,value in indicators.items():raw[f'{method}_{design}_{key}']=value
                    row=dict(unit_id=u['unit_id'],taxonomy=meta['taxonomy'],representation=meta['representation'],method=method,
                        design=design,rule=rule,n=128,mse=float(np.mean(error**2)),coverage=float(covered.mean()),
                        report_rate=float(reported.mean()),wrong_report_rate=float(wrong.mean()),reports=int(reported.sum()),
                        wrong_reports=int(wrong.sum()),mean_se=float(result['se'].mean()),**{key:float(v.mean()) for key,v in indicators.items()})
                    rows.append(row);group=(method,design,rule)
                    for key,value in dict(squared_error=error**2,coverage=covered,report_rate=reported,wrong_report_rate=wrong,
                                          mean_se=result['se'],**indicators).items():aggregate[group][key].append(value)
        np.savez_compressed(out/'raw'/f"{u['unit_id']}.npz",**raw)
    frame=pd.DataFrame(rows);frame.to_csv(out/'unit-performance.csv',index=False);summary=[]
    for (method,design,rule),values_ in aggregate.items():
        row=dict(taxonomy=meta['taxonomy'],representation=meta['representation'],method=method,design=design,rule=rule,n=128,
            units=len(units),replications=500)
        for name,value in values_.items():
            mean,se=probability_summary(value);row[name]=mean;row[name+'_mcse']=se
        row['mse']=row.pop('squared_error');row.pop('squared_error_mcse');row['rmse']=float(np.sqrt(row['mse']))
        g=frame[(frame.method==method)&(frame.design==design)&(frame.rule==rule)]
        row['reports']=int(g.reports.sum());row['wrong_reports']=int(g.wrong_reports.sum())
        row['wrong_conditional']=row['wrong_reports']/row['reports'] if row['reports'] else None
        summary.append(row)
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False)
    (out/'analysis.json').write_text(json.dumps(clean_json(dict(completed_at_utc=now(),plan_path=plan_path,
        exploratory=True,analysis_path=analysis_path,analysis_sha256=digest(source/'analysis.json'),summary=summary,
        checks='Original-rule point estimates/SE/directions reproduced bitwise; local-chain-rule point estimates identical; direct control SE agrees within1e-12',
        limitation='Locally fixed sampled support. Support changes, cleanup and entropy boundary nonregularity prevent a general coverage guarantee.')),indent=2,allow_nan=False)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',required=True);p.add_argument('--destination',required=True);a=p.parse_args();run(a.analysis,a.destination)
