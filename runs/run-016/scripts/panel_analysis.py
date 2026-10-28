"""Exploratory coherent four-year annual samples and simultaneous reporting."""
import argparse,hashlib,json
from collections import defaultdict
import numpy as np,pandas as pd
from scipy.stats import norm
from records import ROOT,now,digest
from inference_core import entropy,estimate_change,NUMERICAL_TOL
from rotating_core import change as rotating_change
from audit_inference import clean_json,sign
from summarize_inference import probability_summary

def make_draws(N,seed,n=128,repetitions=500):
    rng=np.random.default_rng(seed);draws={};overlaps={}
    for design in ['independent','half_retained','fully_revisited']:
        x=np.empty((4,repetitions,n),np.uint16 if N<=65535 else np.uint32)
        x[0]=np.stack([rng.choice(N,n,replace=False) for _ in range(repetitions)])
        positions=np.empty((3,repetitions,n//2),int)
        for t in range(1,4):
            if design=='independent':x[t]=np.stack([rng.choice(N,n,replace=False) for _ in range(repetitions)])
            elif design=='fully_revisited':x[t]=x[0]
            else:
                for r in range(repetitions):
                    keep=rng.choice(n,n//2,replace=False);available=np.ones(N,bool);available[x[t-1,r]]=False
                    fresh=rng.choice(np.flatnonzero(available),n//2,replace=False)
                    x[t,r]=np.r_[x[t-1,r,keep],fresh];positions[t-1,r]=keep
                    assert len(np.intersect1d(x[t-1,r],x[t,r]))==n//2
        draws[design]=x
        if design=='half_retained':overlaps[design]=positions
    return draws,overlaps

def run(destination):
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve prior panel results')
    out.mkdir(parents=True);(out/'draws').mkdir();(out/'raw').mkdir()
    fits={rep:json.loads((ROOT/f'results/models/logistic-broad-{rep}/fit.json').read_text()) for rep in ['tessera','alphaearth']}
    manifest=json.loads((ROOT/fits['tessera']['manifest_path']).read_text());k=len(fits['tessera']['class_names'])
    files={rep:{r['landscape_id']:r for r in f['prediction_files']} for rep,f in fits.items()}
    rows=[];joint_rows=[];aggregates=defaultdict(lambda:defaultdict(list));marginals=defaultdict(lambda:defaultdict(list));inputs=[]
    z_values={'pointwise':1.96,'bonferroni':float(norm.ppf(1-.05/6))}
    for record in manifest['landscapes']:
        if record['status']!='included' or record['split']!='test':continue
        lid=record['landscape_id'];N=record['valid_points'];seed=int.from_bytes(hashlib.sha256(f'16016/coherent-panel/{lid}'.encode()).digest()[:8],'little')
        draws,overlap=make_draws(N,seed)
        dp=out/'draws'/f'{lid}.npz';np.savez_compressed(dp,**draws,half_retained_previous_positions=overlap['half_retained'],N=N,seed=seed)
        inputs.append(dict(landscape_id=lid,draw_path=str(dp.relative_to(out)),draw_sha256=digest(dp)))
        data={}
        for rep in fits:
            f=files[rep][lid];assert digest(ROOT/f['path'])==f['sha256']
            with np.load(ROOT/f['path']) as source:data[rep]=(source['probabilities'],source['labels'])
        assert np.array_equal(data['tessera'][1],data['alphaearth'][1])
        for label in ['direct','tessera','alphaearth']:
            p,y=data['tessera' if label=='direct' else label]
            for design,indices in draws.items():
                print('PANEL',lid,label,design,flush=True);raw={};coverage={name:[] for name in z_values};wrong={name:[] for name in z_values};reports={name:[] for name in z_values}
                for transition in range(3):
                    a=transition+1;b=a+1;ia=indices[transition].astype(int);ib=indices[transition+1].astype(int)
                    pa,pb=(None,None) if label=='direct' else (p[a],p[b])
                    truth=float(entropy(np.bincount(y[b],minlength=k)/N)-entropy(np.bincount(y[a],minlength=k)/N))
                    if design=='half_retained':
                        posa=overlap[design][transition];posb=np.broadcast_to(np.arange(64),posa.shape)
                        result=rotating_change(y[a],y[b],pa,pb,ia,ib,k,posa,posb)
                    else:
                        result=estimate_change(y[a],y[b],pa,pb,ia,ib,k,design=='fully_revisited')
                        result['negative_variance']=np.zeros(500,bool)
                    error=result['estimate']-truth;pre=f'{a+2021}-{b+2021}_'
                    for key in ['estimate','se','negative_variance','projected_a','projected_b']:raw[pre+key]=result[key]
                    for interval,z in z_values.items():
                        low=result['estimate']-z*result['se'];high=result['estimate']+z*result['se']
                        covered=(low<=truth+NUMERICAL_TOL)&(high>=truth-NUMERICAL_TOL)
                        direction=np.where(low>NUMERICAL_TOL,1,np.where(high< -NUMERICAL_TOL,-1,0))
                        reported=direction!=0;bad=reported&(direction!=sign(truth))
                        coverage[interval].append(covered);wrong[interval].append(bad);reports[interval].append(reported)
                        raw[pre+interval+'_covered']=covered;raw[pre+interval+'_direction']=direction;raw[pre+interval+'_wrong']=bad
                        row=dict(landscape_id=lid,label=label,design=design,interval=interval,year_a=a+2021,year_b=b+2021,N=N,n=128,
                            true_change=truth,mse=float(np.mean(error**2)),coverage=float(covered.mean()),report_rate=float(reported.mean()),wrong_report_rate=float(bad.mean()),
                            reports=int(reported.sum()),wrong_reports=int(bad.sum()),negative_variance=float(result['negative_variance'].mean()))
                        rows.append(row);key=(label,design,interval)
                        for name,value in dict(squared_error=error**2,coverage=covered,report_rate=reported,wrong_report_rate=bad,negative_variance=result['negative_variance']).items():marginals[key][name].append(value)
                for interval in z_values:
                    joint=np.all(coverage[interval],axis=0);any_bad=np.any(wrong[interval],axis=0);any_report=np.any(reports[interval],axis=0)
                    raw[interval+'_joint_coverage']=joint;raw[interval+'_any_wrong']=any_bad;raw[interval+'_any_report']=any_report
                    joint_rows.append(dict(landscape_id=lid,label=label,design=design,interval=interval,joint_coverage=float(joint.mean()),any_wrong_report=float(any_bad.mean()),any_report=float(any_report.mean())))
                    for name,value in dict(joint_coverage=joint,any_wrong_report=any_bad,any_report=any_report).items():aggregates[label,design,interval][name].append(value)
                np.savez_compressed(out/'raw'/f'{lid}-{label}-{design}.npz',**raw)
    pd.DataFrame(rows).to_csv(out/'unit-performance.csv',index=False);pd.DataFrame(joint_rows).to_csv(out/'landscape-performance.csv',index=False)
    summary=[]
    for (label,design,interval),values in aggregates.items():
        row=dict(label=label,design=design,interval=interval,landscapes=30,primary_transitions=90,n=128,replications=500)
        for name,value in (values|marginals[label,design,interval]).items():
            mean,se=probability_summary(value);row[name]=mean;row[name+'_mcse']=se
        row['rmse']=float(np.sqrt(row.pop('squared_error')));row.pop('squared_error_mcse')
        summary.append(row)
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False)
    result=dict(completed_at_utc=now(),plan_path='protocol/plan-v11-coherent-panel.md',exploratory=True,inputs=inputs,z_values=z_values,
                model_inputs={rep:dict(path=f'results/models/logistic-broad-{rep}/fit.json',sha256=digest(ROOT/f'results/models/logistic-broad-{rep}/fit.json')) for rep in fits},
                summary=summary,scope='Single coherent2022–2025 sample sequence,128labels/year, three adjacent pointwise/simultaneous contrasts; no field cost measured; nonlinear intervals approximate')
    (out/'analysis.json').write_text(json.dumps(clean_json(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),status='completed',destination=destination)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args();run(a.destination)
