"""Compare direct-sampling error to the preplanned no-change point baseline."""
import argparse,json
import numpy as np,pandas as pd
from records import ROOT,now,digest

def run(destination):
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve earlier scope comparisons')
    out.mkdir(parents=True);rows=[];inputs=[]
    for path in ['results/reference-frames','results/stable-arable']:
        base=ROOT/path
        if not (base/'analysis.json').exists():continue
        inputs.append(dict(path=path,analysis_sha256=digest(base/'analysis.json')))
        units=pd.DataFrame([json.loads(s) for s in (base/'units.jsonl').read_text().splitlines()])
        summary=pd.read_csv(base/'summary.csv')
        for (frame,taxonomy),g in units.groupby(['frame','taxonomy'],sort=False):
            for subset,mask in [('all',np.ones(len(g),bool)),('absolute_change_at_least_0.01',g.true_change.abs().to_numpy()>=.01)]:
                selected=g[mask]
                if selected.empty:continue
                baseline=float(np.mean(selected.true_change.to_numpy()**2))
                for design in ['paired','independent']:
                    for n in [32,64,128,256,512]:
                        metrics=[next(s for s in u['summaries'] if s['design']==design and s['n']==n) for u in selected.to_dict('records')]
                        mse=float(np.mean([s['mse'] for s in metrics]))
                        rows.append(dict(frame=frame,taxonomy=taxonomy,subset=subset,units=len(selected),design=design,n=n,
                            no_change_mse=baseline,no_change_rmse=float(np.sqrt(baseline)),direct_mse=mse,direct_rmse=float(np.sqrt(mse)),
                            direct_no_change_mse_ratio=mse/baseline if baseline>0 else None,
                            zero_change=int((selected.true_change.abs()<=1e-10).sum()),tiny_change=int((selected.true_change.abs()<.01).sum()),
                            median_absolute_true_change=float(selected.true_change.abs().median()),maximum_absolute_true_change=float(selected.true_change.abs().max())))
    pd.DataFrame(rows).to_csv(out/'scope-baselines.csv',index=False)
    (out/'analysis.json').write_text(json.dumps(dict(completed_at_utc=now(),inputs=inputs,
        scope='No-change point comparison was prespecified; reference-frame and stable-arable scopes are exploratory. A point baseline does not supply a confidence interval or establish no change.'),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args();run(a.destination)
