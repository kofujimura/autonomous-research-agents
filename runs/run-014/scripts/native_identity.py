"""Post-result descriptive identity counts; original predictions stay unchanged."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from record import ROOT
from features import unit

def native_identity(output,tasks,comparison):
    output.mkdir(parents=True,exist_ok=False);t=pd.read_csv(tasks);rows=[];hashes={}
    def read(p):
        hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        with np.load(p,allow_pickle=False) as f:raw=f['raw']
        x=raw.astype(float);x=np.sign(x)*(x/127.5)**2;x[(raw==-128).any(-1)]=np.nan;u=unit(x)
        return raw,dict(centre=u[1,1],patch=unit(u.mean((0,1))) if np.isfinite(u).all() else np.full(64,np.nan))
    for r in t.itertuples():
        a,av=read(ROOT/'data/embeddings/aef'/f'{r.task_id}.npz')
        b,bv=read(ROOT/'data/native-check'/f'{r.task_id}.npz')
        for support in ['centre','patch']:
            valid=bool(np.isfinite(av[support]).all() and np.isfinite(bv[support]).all())
            rows.append(dict(task_id=r.task_id,point_id=r.point_id,sample_group=r.sample_group,support=support,
                both_valid=valid,vector_identical=bool(np.allclose(av[support],bv[support],rtol=0,atol=1e-12)) if valid else False,
                maximum_absolute_component_difference=float(np.max(np.abs(av[support]-bv[support]))) if valid else None,
                raw_centre_identical=bool(np.array_equal(a[1,1],b[1,1]))))
    identity=pd.DataFrame(rows);identity.to_csv(output/'input-identity.csv',index=False)
    # All dates that were actually replaced must be identical for a pair-level identity.
    pairs=identity.groupby(['support','point_id']).agg(input_identical=('vector_identical','all')).reset_index()
    c=pd.read_csv(comparison).merge(pairs,on=['support','point_id'],validate='many_to_one')
    c['score_identical']=c.both_available&(c.absolute_score_difference<=1e-12)
    tab=c.groupby(['support','task','method']).agg(cases=('point_id','size'),common_cases=('both_available','sum'),
        identical_input_cases=('input_identical','sum'),identical_scores=('score_identical','sum'),changed_flags=('changed_flag','sum')).reset_index()
    tab.to_csv(output/'decision-identity.csv',index=False)
    summary=dict(exploratory=True,added_after_v22_results=True,tolerance_absolute=1e-12,
        pairs=int(c.point_id.nunique()),input_counts=identity.groupby('support').agg(point_years=('task_id','size'),
            identical_vectors=('vector_identical','sum')).reset_index().to_dict('records'),
        changed_pairs=int(c.groupby('point_id').changed_flag.any().sum()),changed_method_case_conditions=int(c.changed_flag.sum()),
        method_case_conditions=len(c),note='Equal inputs and unchanged subsequent inputs can make unchanged scores inevitable; not independent evidence of stability.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'raw-input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    (output/'dependency-sha256.json').write_text(json.dumps(dict(tasks=hashlib.sha256(tasks.read_bytes()).hexdigest(),
        comparison=hashlib.sha256(comparison.read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['output','tasks','comparison']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();native_identity(a.output,a.tasks,a.comparison)
