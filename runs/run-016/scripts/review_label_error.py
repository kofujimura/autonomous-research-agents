"""Post-review synthetic annual misclassification, with fixed declaration truth."""
import argparse,hashlib,json
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from inference_core import simplex,entropy,NUMERICAL_TOL
from summarize_inference import probability_summary
from audit_inference import sign

def sampled_estimate(a,b,N,paired,k):
    R,n=a.shape
    def yearly(y):
        counts=np.zeros((R,k));np.add.at(counts,(np.repeat(np.arange(R),n),y.ravel()),1/n)
        q=simplex(counts);g=-(np.log(np.maximum(q,1e-6))+1)
        return entropy(q),np.take_along_axis(g,y,axis=1)
    ha,va=yearly(a);hb,vb=yearly(b)
    var=np.var(vb-va,axis=1,ddof=1) if paired else np.var(va,axis=1,ddof=1)+np.var(vb,axis=1,ddof=1)
    se=np.sqrt(np.maximum(var*(1-n/N)/n,0));delta=hb-ha;lo=delta-1.96*se;hi=delta+1.96*se
    direction=np.where(lo>NUMERICAL_TOL,1,np.where(hi< -NUMERICAL_TOL,-1,0)).astype(np.int8)
    return dict(estimate=delta,se=se,direction=direction,low=lo,high=hi)

def replacement(y,u,p):
    k=len(p);c=np.zeros((k,k));fallback=0
    for j in range(k):
        q=p.copy();q[j]=0
        if q.sum()==0:q=np.ones(k);q[j]=0;fallback+=int((y==j).sum())
        c[j]=np.cumsum(q/q.sum());c[j,-1]=1
    out=(u[:,:,None]>=c[y]).sum(axis=-1).astype(np.int16)
    assert (out!=y).all()
    return out,fallback

def run(destination):
    base=ROOT/'results/inference/logistic-broad-tessera';meta=json.loads((base/'analysis.json').read_text())
    fit=json.loads((ROOT/meta['model_path']/'fit.json').read_text());k=len(fit['class_names']);files={r['landscape_id']:r for r in fit['prediction_files']}
    draws={(r['landscape_id'],r['year_a'],r['year_b']):r for r in json.loads((ROOT/meta['draw_manifest_path']).read_text())['draws']}
    units=[json.loads(s) for s in (base/'units.jsonl').read_text().splitlines() if json.loads(s)['primary']]
    out=ROOT/destination
    if out.exists():raise FileExistsError('Keep prior error sensitivity')
    out.mkdir(parents=True);(out/'raw').mkdir();rows=[];generation=[];agg=defaultdict(lambda:defaultdict(list));cache={}
    scenarios=[(0.,0.)]+[(e,rho) for e in [.01,.02,.05] for rho in [0.,.5,1.]]
    for u in units:
        lid=u['landscape_id'];a=u['year_a']-2021;b=u['year_b']-2021
        if lid not in cache:
            entry=files[lid];assert digest(ROOT/entry['path'])==entry['sha256']
            with np.load(ROOT/entry['path']) as z:cache[lid]=z['labels']
        y=cache[lid];N=y.shape[1];d=draws[lid,a+2021,b+2021]
        with np.load(ROOT/d['path']) as z:ia=z['a'][:,:128].astype(int);ib=z['b'][:,:128].astype(int)
        R=ia.shape[0];ri=np.arange(R)[:,None];ya=y[a][ia];ybp=y[b][ia];ybi=y[b][ib]
        seed=int.from_bytes(hashlib.sha256(('16016/review-label-error/'+u['unit_id']).encode()).digest()[:8],'little')
        rng=np.random.default_rng(seed);af,ac,bf,bc,share=[rng.random((R,N)) for _ in range(5)]
        fa=af[ri,ia];ca=ac[ri,ia];qa=np.bincount(y[a],minlength=k)/N;qb=np.bincount(y[b],minlength=k)/N
        wronga,fallback=replacement(ya,ca,qa);raw={}
        with np.load(base/u['raw_path']) as z:original={key:z[key] for key in z.files}
        for rho in [0.,.5,1.]:
            use=share<rho;fbp=np.where(use[ri,ia],af[ri,ia],bf[ri,ia]);fbi=np.where(use[ri,ib],af[ri,ib],bf[ri,ib])
            cbp=np.where(use[ri,ia],ac[ri,ia],bc[ri,ia]);cbi=np.where(use[ri,ib],ac[ri,ib],bc[ri,ib])
            wrongbp,f1=replacement(ybp,cbp,qb);wrongbi,f2=replacement(ybi,cbi,qb)
            for rate in [0.,.01,.02,.05]:
                if rate==0 and rho!=0:continue
                aa=np.where(fa<rate,wronga,ya)
                for design,truth_b,wrong_b,flip_b in [('paired',ybp,wrongbp,fbp),('independent',ybi,wrongbi,fbi)]:
                    bb=np.where(flip_b<rate,wrong_b,truth_b);res=sampled_estimate(aa,bb,N,design=='paired',k)
                    prefix=f'e{rate}_rho{rho}_{design}_'
                    if rate==0:
                        for key in ['estimate','se','direction']:assert np.array_equal(res[key],original[f'direct_{design}_128_'+key])
                    covered=(res['low']<=u['true_change']+NUMERICAL_TOL)&(res['high']>=u['true_change']-NUMERICAL_TOL)
                    reported=res['direction']!=0;wrong=reported&(res['direction']!=sign(u['true_change']));err=res['estimate']-u['true_change']
                    zero_changed=(aa==bb).all(axis=1) if design=='paired' else np.zeros(R,bool)
                    for key in ['estimate','se','direction']:raw[prefix+key]=res[key]
                    raw[prefix+'covered']=covered;raw[prefix+'wrong']=wrong;raw[prefix+'zero_observed_changes']=zero_changed
                    row=dict(unit_id=u['unit_id'],landscape_id=lid,rate=rate,coupling=rho,design=design,n=128,replications=R,
                        mse=float(np.mean(err**2)),bias=float(err.mean()),coverage=float(covered.mean()),report_rate=float(reported.mean()),
                        reports=int(reported.sum()),wrong_reports=int(wrong.sum()),wrong_report_rate=float(wrong.mean()),zero_se=float((res['se']==0).mean()),zero_observed_changes=float(zero_changed.mean()))
                    rows.append(row)
                    for name,value in dict(squared_error=err**2,bias=err,coverage=covered,report_rate=reported,wrong_report_rate=wrong,
                                           zero_se=res['se']==0,zero_observed_changes=zero_changed).items():agg[rate,rho,design][name].append(value)
                    generation.append(dict(unit_id=u['unit_id'],rate=rate,coupling=rho,design=design,seed=seed,N=N,R=R,n=128,
                        observed_a_sha256=hashlib.sha256(aa.tobytes()).hexdigest(),observed_b_sha256=hashlib.sha256(bb.tobytes()).hexdigest(),fallback_observations=fallback+f1+f2))
        np.savez_compressed(out/'raw'/f"{u['unit_id']}.npz",**raw)
        print('LABEL ERROR',u['unit_id'],flush=True)
    frame=pd.DataFrame(rows);frame.to_csv(out/'unit-performance.csv',index=False);summary=[]
    for (rate,rho,design),values in agg.items():
        row=dict(rate=rate,coupling=rho,design=design,units=len(units),replications=500,n=128)
        for name,value in values.items():row[name],row[name+'_mcse']=probability_summary(value)
        row['mse']=row.pop('squared_error');row['rmse']=float(np.sqrt(row['mse']))
        g=frame[(frame.rate==rate)&(frame.coupling==rho)&(frame.design==design)]
        row['reports']=int(g.reports.sum());row['wrong_reports']=int(g.wrong_reports.sum());row['wrong_conditional']=row['wrong_reports']/row['reports'] if row['reports'] else None
        summary.append(row)
    sf=pd.DataFrame(summary);sf.to_csv(out/'summary.csv',index=False)
    comparisons=[]
    for rate,rho in scenarios:
        p=sf[(sf.rate==rate)&(sf.coupling==rho)&(sf.design=='paired')].iloc[0];i=sf[(sf.rate==rate)&(sf.coupling==rho)&(sf.design=='independent')].iloc[0]
        comparisons.append(dict(rate=rate,coupling=rho,paired_rmse=p.rmse,independent_rmse=i.rmse,mse_ratio=p.mse/i.mse,paired_coverage=p.coverage,independent_coverage=i.coverage))
    pd.DataFrame(comparisons).to_csv(out/'comparisons.csv',index=False)
    (out/'generation.json').write_text(json.dumps(dict(specification='default_rng(seed), five (R,N) uniforms: A flip/category, B independent flip/category, shared-selector; same location/year across designs; conditional empirical wrong class',records=generation),indent=2)+'\n')
    (out/'analysis.json').write_text(json.dumps(dict(completed_at_utc=now(),plan_path='protocol/plan-v15-review-response.md',exploratory=True,source_analysis=str(base.relative_to(ROOT)),source_sha256=digest(base/'analysis.json'),scenarios=scenarios,truth='Original declaration-population change fixed',interpretation='Synthetic error/coupling assumptions, not estimated error rates or a validity correction'),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args();run(a.destination)
