"""Prospective field-interior and one-pixel auxiliary-prediction stress test."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.ndimage import minimum_filter,maximum_filter
from records import ROOT,now,digest
from inference_core import entropy,estimate_change,influence_diagnostic,NUMERICAL_TOL
from audit_inference import clean_json,sign
from draw_audits import PAIRS

OFFSETS={'center':0,'north':-512,'south':512,'west':-1,'east':1}

def interior_population(record,y):
    indices=np.asarray(record['valid_indices'],int);grid=np.full(512*512,-1,np.int32)
    grid[indices]=np.arange(len(indices));grid=grid.reshape(512,512)
    eligible=minimum_filter((grid>=0).astype(np.int8),size=3,mode='constant',cval=0)==1
    for yy in y:
        labels=np.full(512*512,-1,np.int16);labels[indices]=yy;labels=labels.reshape(512,512)
        eligible &= minimum_filter(labels,size=3,mode='constant',cval=-1)==maximum_filter(labels,size=3,mode='constant',cval=-1)
    centers=np.flatnonzero(eligible.ravel())
    assert len(centers)>=128,'Too few interior pixels: retain failure, do not redefine eligibility'
    positions={name:grid.ravel()[centers+delta] for name,delta in OFFSETS.items()}
    assert all((p>=0).all() for p in positions.values())
    return centers,positions

def run(model_paths,destination):
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve registration-check results')
    out.mkdir(parents=True);(out/'raw').mkdir();(out/'draws').mkdir()
    cohorts={};draws={};rows=[];inputs=[]
    for model_path in model_paths:
        fit=json.loads((ROOT/model_path/'fit.json').read_text())
        assert fit['taxonomy']=='broad' and fit['classifier']=='logistic' and not fit['refreshed']
        manifest=json.loads((ROOT/fit['manifest_path']).read_text());assert manifest['native_census']
        k=len(fit['class_names']);pop={r['landscape_id']:r for r in manifest['landscapes']}
        inputs.append(dict(model_path=model_path,fit_sha256=digest(ROOT/model_path/'fit.json')))
        for entry in fit['prediction_files']:
            lid=entry['landscape_id'];record=pop[lid]
            if record['split']!='test':continue
            assert digest(ROOT/entry['path'])==entry['sha256']
            with np.load(ROOT/entry['path']) as z:full_p=z['probabilities'];full_y=z['labels']
            centers,pos=interior_population(record,full_y);N=len(centers);center_y=full_y[:,pos['center']]
            if lid in cohorts:
                assert cohorts[lid]['centers_sha256']==hashlib.sha256(centers.tobytes()).hexdigest()
            else:
                cohort=dict(landscape_id=lid,stratum=record.get('stratum'),native_population=record['valid_points'],
                            interior_population=N,retained_fraction=N/record['valid_points'],
                            centers_sha256=hashlib.sha256(centers.tobytes()).hexdigest(),
                            positions={name:p.tolist() for name,p in pos.items()})
                cohorts[lid]=cohort
                np.savez_compressed(out/'draws'/f'{lid}-interior.npz',native_flat_indices=centers,
                                    **{name:p for name,p in pos.items()})
            for a,b in PAIRS[:3]:
                ta=a-2021;tb=b-2021;ya=center_y[ta];yb=center_y[tb]
                truth=float(entropy(np.bincount(yb,minlength=k)/N)-entropy(np.bincount(ya,minlength=k)/N))
                key=(lid,a,b)
                if key not in draws:
                    seed=int.from_bytes(hashlib.sha256(f'16016/registration/{lid}/{a}/{b}'.encode()).digest()[:8],'little')
                    rng=np.random.default_rng(seed);dtype=np.uint16 if N<=65535 else np.uint32
                    ia=np.stack([rng.choice(N,128,replace=False).astype(dtype) for _ in range(500)])
                    ib=np.stack([rng.choice(N,128,replace=False).astype(dtype) for _ in range(500)])
                    draws[key]=(ia,ib)
                    np.savez_compressed(out/'draws'/f'{lid}-{a}-{b}.npz',a=ia,b=ib,N=N,seed=seed)
                ia,ib=draws[key]
                for offset,positions in pos.items():
                    pa=full_p[ta,positions];pb=full_p[tb,positions]
                    print('REGISTRATION',fit['representation'],lid,a,b,offset,N,flush=True)
                    soft_change=float(entropy(pb.mean(axis=0,dtype=np.float64))-entropy(pa.mean(axis=0,dtype=np.float64)))
                    raw={}
                    row=dict(landscape_id=lid,stratum=record.get('stratum'),year_a=a,year_b=b,
                             representation=fit['representation'],offset=offset,n=128,N=N,true_change=truth,
                             tiny_change=abs(truth)<.01,zero_change=abs(truth)<=NUMERICAL_TOL,
                             accuracy_a=float((pa.argmax(axis=1)==ya).mean()),accuracy_b=float((pb.argmax(axis=1)==yb).mean()),
                             soft_count_change=soft_change,soft_count_error=soft_change-truth,oracle={},summaries=[])
                    for method in ['direct','model_assisted']:
                        ppa,ppb=(None,None) if method=='direct' else (pa,pb)
                        row['oracle'][method]=influence_diagnostic(ya,yb,ppa,ppb,k,128)
                        for design in ['paired','independent']:
                            sb=ia if design=='paired' else ib
                            result=estimate_change(ya,yb,ppa,ppb,ia.astype(int),sb.astype(int),k,design=='paired')
                            err=result['estimate']-truth
                            covered=(result['low']<=truth+NUMERICAL_TOL)&(result['high']>=truth-NUMERICAL_TOL)
                            reports=result['direction']!=0;wrong=reports&(result['direction']!=sign(truth))
                            prefix=f'{method}_{design}_'
                            for name in ['estimate','se','direction','projected_a','projected_b']:
                                raw[prefix+name]=result[name]
                            raw[prefix+'covered']=covered;raw[prefix+'wrong']=wrong
                            row['summaries'].append(dict(method=method,design=design,mse=float(np.mean(err**2)),
                                     bias=float(err.mean()),coverage=float(covered.mean()),report_rate=float(reports.mean()),
                                     wrong_report_rate=float(wrong.mean()),reports=int(reports.sum()),wrong_reports=int(wrong.sum()),
                                     projection_any_year=float((result['projected_a']|result['projected_b']).mean())))
                    target=out/'raw'/f"{lid}-{a}-{b}-{fit['representation']}-{offset}.npz"
                    np.savez_compressed(target,**raw);row['raw_path']=str(target.relative_to(out));row['raw_sha256']=digest(target)
                    rows.append(clean_json(row))
                    with (out/'units.jsonl').open('a') as f:f.write(json.dumps(clean_json(row),allow_nan=False)+'\n')
            del full_p,full_y
    flat=[]
    for r in rows:
        for s in r['summaries']:
            flat.append({k:r[k] for k in ['landscape_id','stratum','year_a','year_b','representation','offset','N','true_change','accuracy_a','accuracy_b','soft_count_change'] }|s)
    frame=pd.DataFrame(flat);frame.to_csv(out/'unit-performance.csv',index=False)
    summary=[]
    for (rep,offset,method,design),g in frame.groupby(['representation','offset','method','design']):
        summary.append(dict(representation=rep,offset=offset,method=method,design=design,n=128,units=len(g),
                            mse=float(g.mse.mean()),rmse=float(np.sqrt(g.mse.mean())),bias=float(g.bias.mean()),
                            coverage=float(g.coverage.mean()),report_rate=float(g.report_rate.mean()),
                            wrong_report_rate=float(g.wrong_report_rate.mean()),reports=int(g.reports.sum()),wrong_reports=int(g.wrong_reports.sum()),
                            projection_any_year=float(g.projection_any_year.mean())))
    pd.DataFrame(summary).to_csv(out/'summary-performance.csv',index=False)
    # Long position arrays remain in raw NPZ rather than prose/summary output.
    metadata=dict(completed_at_utc=now(),plan_path='protocol/plan-v4-registration-check.md',inputs=inputs,
                  cohorts=[{k:v for k,v in c.items() if k!='positions'} for c in cohorts.values()],
                  offsets=OFFSETS,replications=500,n=128,unit_rows=len(rows),summary=summary,
                  scope='Same fixed interior subset across offsets/representations; 10 m shifts are stress tests, not measured registration errors.')
    (out/'summary.json').write_text(json.dumps(clean_json(metadata),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),cases=len(cohorts),unit_rows=len(rows))),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',action='append',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();run(a.model,a.destination)
