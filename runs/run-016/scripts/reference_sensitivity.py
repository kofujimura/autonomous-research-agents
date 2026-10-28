"""Preplanned reference-error sensitivity; no assumed measured error rate."""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from records import ROOT,now,digest
from inference_core import entropy
from draw_audits import PAIRS

RATES=[.01,.02,.05]

def continuity_bound(eps,k):
    # Audenaert/Fannes classical entropy bound for total variation <= eps.
    # For eps beyond 1-1/k the universal bound is ln(k).
    if eps>=1-1/k:return float(np.log(k))
    return float(eps*np.log(k-1)-eps*np.log(eps)-(1-eps)*np.log1p(-eps))

def pair_bounds(p,i,j,eps):
    """Exact entropy extrema moving <=eps mass within the specified pair."""
    if i==j:
        h=float(entropy(p));return h,h
    lo=-min(eps,p[i]);hi=min(eps,p[j])
    candidates=[lo,hi,float(np.clip((p[j]-p[i])/2,lo,hi))]
    h=[]
    for move in candidates:
        q=p.copy();q[i]+=move;q[j]-=move
        assert q.min()>=-1e-14 and np.isclose(q.sum(),1)
        h.append(float(entropy(np.maximum(q,0))))
    return min(h),max(h)

def run(manifest_path,destination):
    m=json.loads((ROOT/manifest_path).read_text());tax=json.loads((ROOT/'data/taxonomy.json').read_text())
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve prior sensitivity outputs')
    out.mkdir(parents=True);rows=[]
    fine_pair=[tax['fine'].index(s) for s in ['Grain Maize','Silage Maize']]
    for r in m['landscapes']:
        if r['status']!='included' or r['split']!='test':continue
        ix=np.array(r['valid_indices'],int)
        with np.load(ROOT/r['path']) as z:labels={t:z[t][:,ix] for t in ['broad','fine']}
        for t in ['broad','fine']:
            ids=m[t+'_ids'];k=len(ids);lookup={v:i for i,v in enumerate(ids)}
            raw_pair=fine_pair if t=='fine' else [tax['fine_to_broad'][i] for i in fine_pair]
            pair=[lookup[i] for i in raw_pair]
            pp=[np.array([(y==c).mean() for c in ids]) for y in labels[t]]
            for a,b in PAIRS:
                pa=pp[a-2021];pb=pp[b-2021];delta=float(entropy(pb)-entropy(pa))
                for eps in RATES:
                    bound=2*continuity_bound(eps,k)
                    amin,amax=pair_bounds(pa,*pair,eps);bmin,bmax=pair_bounds(pb,*pair,eps)
                    low=bmin-amax;high=bmax-amin
                    rows.append(dict(landscape_id=r['landscape_id'],year_a=a,year_b=b,primary=(a,b) in PAIRS[:3],
                                     taxonomy=t,k=k,N=len(ix),true_change=delta,total_variation_per_year=eps,
                                     general_change_error_bound=bound,general_sign_robust=abs(delta)>bound+1e-10,
                                     maize_ambiguity_change_low=low,maize_ambiguity_change_high=high,
                                     maize_ambiguity_sign_robust=low>1e-10 or high< -1e-10,
                                     maize_same_broad_group=pair[0]==pair[1]))
    frame=pd.DataFrame(rows);frame.to_csv(out/'reference-sensitivity.csv',index=False)
    summary=[]
    for (t,eps),g in frame[frame.primary].groupby(['taxonomy','total_variation_per_year']):
        summary.append(dict(taxonomy=t,rate=float(eps),units=len(g),general_sign_robust=int(g.general_sign_robust.sum()),
                            general_change_error_bound=float(g.general_change_error_bound.iloc[0]),
                            maize_ambiguity_sign_robust=int(g.maize_ambiguity_sign_robust.sum()),
                            maize_same_broad_group=bool(g.maize_same_broad_group.all())))
    result=dict(generated_at_utc=now(),manifest_path=manifest_path,manifest_sha256=digest(ROOT/manifest_path),
                measured_error_rates=False,summary=summary,
                interpretation='Sensitivity scenarios, not observed reference errors or probability intervals. Two years may have different error directions. Grain/silage ambiguity is confined to that pair.')
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();run(a.manifest,a.destination)
