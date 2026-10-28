"""Exact score-histogram block bootstrap that reselects test thresholds.

Uses saved probabilities only. It does not refit a classifier and does not model
reference error or the uncertainty of selecting the four convenience regions.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
from records import ROOT,now

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def weighted_thresholds(levels,histogram,weights,q=.95,chunk=16):
    result=np.full(len(weights),np.nan,dtype=np.float64)
    for start in range(0,len(weights),chunk):
        counts=weights[start:start+chunk].astype(np.float64)@histogram
        total=counts.sum(axis=1);index=np.ceil((total-1)*q)
        np.cumsum(counts,axis=1,out=counts)
        chosen=np.argmax(counts>index[:,None],axis=1)
        result[start:start+len(chosen)]=np.where(total>0,levels[chosen],np.nan)
    return result

def core_histograms(negative):
    sizes=[len(x) for x in negative]
    levels,inverse=np.unique(np.concatenate(negative),return_inverse=True)
    histogram=np.empty((len(sizes),len(levels)),dtype=np.float64);offset=0
    for i,n in enumerate(sizes):
        histogram[i]=np.bincount(inverse[offset:offset+n],minlength=len(levels));offset+=n
    return levels,histogram

def fit_bootstrap(meta,entries,core_ids,regions,weights,out):
    source=ROOT/meta['prediction_path']
    if sha(source)!=meta['prediction_sha256']:raise RuntimeError('Prediction hash mismatch')
    destination=out/(meta['fit_id']+'.npz');info_path=destination.with_suffix('.json')
    weights_sha=hashlib.sha256(weights.tobytes()).hexdigest()
    if destination.exists() and info_path.exists():
        old=json.loads(info_path.read_text())
        if old.get('prediction_sha256')==sha(source) and old.get('core_weights_sha256')==weights_sha and old.get('output_sha256')==sha(destination):
            with np.load(destination) as f:return f['regional_recovery']
    with np.load(source) as f:ids=f['core_ids'].tolist();prob=f['probability'];splits=f['splits'].tolist()
    negative=[];object_scores=[]
    for cid in core_ids:
        i=ids.index(cid)
        if splits[i]!='test':raise RuntimeError('Bootstrap core is not in test split')
        e=entries[cid]
        with np.load(ROOT/e['reference_path']) as f:ref={k:f[k] for k in f.files}
        if sha(ROOT/e['reference_path'])!=e['reference_sha256']:raise RuntimeError('Reference hash mismatch')
        valid=ref['valid'].astype(bool);y=ref['y'].astype(bool)
        negative.append(prob[i][valid&~y])
        metadata=json.loads((ROOT/e['metadata_path']).read_text());scores=[]
        for o in metadata['objects']:
            if not (o['main_eligible'] and o['size_bin']=='small'):continue
            values=prob[i][valid&(ref['objects']==o['object_id'])]
            # At least ceil(N/2) strictly positive scores, including even N.
            order=len(values)-(len(values)+1)//2
            scores.append(float(np.partition(values,order)[order]))
        object_scores.append(np.sort(scores))
    levels,histogram=core_histograms(negative)
    thresholds=weighted_thresholds(levels,histogram,weights)
    recovered=np.stack([len(values)-np.searchsorted(values,thresholds,side='right') for values in object_scores],axis=1)
    numbers=np.array([len(x) for x in object_scores])
    regional=[]
    for region in regions:
        mask=np.array([entries[cid]['region_id']==region for cid in core_ids])
        numerator=np.sum(weights[:,mask]*recovered[:,mask],axis=1)
        denominator=weights[:,mask]@numbers[mask]
        with np.errstate(invalid='ignore',divide='ignore'):regional.append(numerator/denominator)
    values=np.stack(regional,axis=1)
    np.savez_compressed(destination,threshold=thresholds,regional_recovery=values,
        core_ids=np.array(core_ids),region_ids=np.array(regions),object_counts=numbers)
    info=dict(fit_id=meta['fit_id'],created_at_utc=now(),prediction_sha256=sha(source),
        core_weights_sha256=weights_sha,
        output_sha256=sha(destination),unique_upland_scores=len(levels),bootstrap_replicates=len(weights),
        threshold_quantiles=np.quantile(thresholds[np.isfinite(thresholds)],[.025,.5,.975]).tolist(),
        undefined_threshold_replicates=int(np.sum(~np.isfinite(thresholds))),
        undefined_recovery_replicates=int(np.sum(~np.all(np.isfinite(values),axis=1))))
    destination.with_suffix('.json').write_text(json.dumps(info,indent=2)+'\n')
    print(meta['fit_id'],'threshold bootstrap complete;',len(levels),'distinct scores',flush=True)
    return values

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',default='data/derived/dataset-manifest.json')
    p.add_argument('--fit-dir',default='data/results/fits');p.add_argument('--out',default='data/threshold-bootstrap')
    p.add_argument('--replicates',type=int,default=2000);a=p.parse_args();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/a.manifest).read_text());entries={e['core_id']:e for e in manifest['cores']}
    regions=sorted(set(e['region_id'] for e in entries.values()))
    ids={r:sorted(e['core_id'] for e in entries.values() if e['region_id']==r and e['split']=='test') for r in regions}
    core_ids=[cid for r in regions for cid in ids[r]]
    seeds=[101,202,303,404,505];rng=np.random.default_rng(20261027)
    seed_draw=rng.integers(0,len(seeds),size=(a.replicates,len(seeds)))
    weights=[]
    for r in regions:
        draw=rng.integers(0,len(ids[r]),size=(a.replicates,len(ids[r])))
        weights.append(np.stack([np.sum(draw==i,axis=1) for i in range(len(ids[r]))],axis=1))
    weights=np.concatenate(weights,axis=1)
    arrays={};tick=time.monotonic()
    with threadpool_limits(limits=2):
        for rep,policy in [('aef','area'),('aef','object'),('optical','area'),('optical','object')]:
            part=[]
            for seed in seeds:
                if time.monotonic()-tick>=1500:
                    (out/'partial.json').write_text(json.dumps(dict(observed_at_utc=now(),status='partial',reason='1500-second internal boundary; completed fit arrays retained for resumption'),indent=2)+'\n')
                    print('PARTIAL: internal time boundary reached; no combined interval asserted',flush=True);return
                fid=f'within_rf_{rep}_{policy}_n2000_s{seed}'
                path=ROOT/a.fit_dir/(fid+'.json')
                if not path.exists():raise RuntimeError('Missing primary fit: '+fid)
                part.append(fit_bootstrap(json.loads(path.read_text()),entries,core_ids,regions,weights,out))
            # [seed, replicate, region] -> paired resampled seed means then region means.
            stack=np.stack(part);replicate=np.arange(a.replicates)[:,None]
            arrays[rep,policy]=np.mean(stack[seed_draw,replicate,:],axis=(1,2))
    contrasts=dict(H1_interaction=arrays['aef','object']-arrays['aef','area']-arrays['optical','object']+arrays['optical','area'],
        aef_oracle_gain=arrays['aef','object']-arrays['aef','area'],
        optical_oracle_gain=arrays['optical','object']-arrays['optical','area'])
    summary={}
    for name,values in contrasts.items():
        finite=np.isfinite(values)
        summary[name]=dict(reselected_threshold_block_bootstrap_95_percent_interval=np.quantile(values[finite],[.025,.975]).tolist() if finite.any() else None,
            undefined_replicates=int(np.sum(~finite)),replicates=a.replicates)
    np.savez_compressed(out/'contrast-replicates.npz',**contrasts)
    report=dict(completed_at_utc=now(),contrasts=summary,
        interpretation='Thresholds reselected from exactly weighted score distributions for resampled test blocks; fitted models and reference maps remain fixed; convenience regions fixed',
        seed=20261027,manifest_sha256=sha(ROOT/a.manifest))
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
