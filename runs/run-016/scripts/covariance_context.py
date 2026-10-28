"""Summarize existing known-population influence proxies without new draws."""
import argparse,json
import numpy as np,pandas as pd
from records import ROOT,now,digest

def run(destination):
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve covariance context')
    out.mkdir(parents=True);rows=[];inputs=[]
    for cohort,path in [('original','results/reference-frames'),('original','results/stable-arable'),
                        ('additional','results/additional-geography'),('additional','results/additional-geography-arable')]:
        if not (ROOT/path/'analysis.json').exists():continue
        units=[json.loads(s) for s in (ROOT/path/'units.jsonl').read_text().splitlines()]
        ratios=pd.read_csv(ROOT/path/'pairing-ratios.csv')
        for name in ['units.jsonl','pairing-ratios.csv']:
            inputs.append(dict(path=path+'/'+name,sha256=digest(ROOT/path/name)))
        for frame,tax in sorted(set((u['frame'],u['taxonomy']) for u in units)):
            selected=[u for u in units if u['frame']==frame and u['taxonomy']==tax]
            covariance=np.array([u['oracle']['covariance'] for u in selected])
            paired=np.array([u['oracle']['paired_variance'] for u in selected]);independent=np.array([u['oracle']['independent_variance'] for u in selected])
            r=ratios[(ratios.frame==frame)&(ratios.taxonomy==tax)&(ratios.n==128)];assert len(r)==1
            rows.append(dict(cohort=cohort,frame=frame,taxonomy=tax,landscapes=len(set(u['landscape_id'] for u in selected)),
                units=len(selected),negative_covariance=int((covariance< -1e-12).sum()),zero_covariance=int((np.abs(covariance)<=1e-12).sum()),
                positive_covariance=int((covariance>1e-12).sum()),mean_influence_covariance=float(covariance.mean()),
                mean_paired_influence_variance=float(paired.mean()),mean_independent_influence_variance=float(independent.mean()),
                aggregate_influence_variance_ratio=float(paired.mean()/independent.mean()) if independent.mean()>0 else None,
                empirical_entropy_mse_ratio=float(r.iloc[0].paired_independent_mse_ratio),
                empirical_ratio_mcse=float(r.iloc[0].ratio_mcse),mean_reference_turnover=float(np.mean([u['changed_fraction'] for u in selected]))))
    pd.DataFrame(rows).to_csv(out/'summary.csv',index=False)
    (out/'analysis.json').write_text(json.dumps(dict(completed_at_utc=now(),plan_path='protocol/plan-v13a-covariance-context.md',
        exploratory=True,inputs=inputs,summary=rows,scope='Equal-weight true-population linearized proxies atn128; not exact entropy variance, geographic inference or causal crop-rotation attribution.'),indent=2)+'\n')
    print(pd.DataFrame(rows)[['cohort','frame','taxonomy','units','negative_covariance','aggregate_influence_variance_ratio','empirical_entropy_mse_ratio']].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args();run(a.destination)
