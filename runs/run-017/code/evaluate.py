"""Offline, label-explicit evaluation of saved predictions; never fits models."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter, distance_transform_edt, label
from sklearn.metrics import average_precision_score
from records import ROOT, now

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def threshold_for(scores, target):
    if not len(scores):raise ValueError('No reference-upland positions for threshold')
    return float(np.quantile(scores,1-target,method='higher'))

def normalized_smooth(values,sigma):
    valid=np.isfinite(values)
    numerator=gaussian_filter(np.where(valid,values,0),sigma,mode='nearest')
    denominator=gaussian_filter(valid.astype(np.float32),sigma,mode='nearest')
    out=np.divide(numerator,denominator,out=np.zeros_like(numerator),where=denominator>0)
    out[~valid]=np.nan
    return out

def boundary_mask(y,meters):
    if meters==0:return np.ones(y.shape,dtype=bool)
    distances=np.where(y,distance_transform_edt(y),distance_transform_edt(~y))*10-5
    return distances>=meters

def coverage_counts(objects,valid,prediction):
    total=np.bincount(objects[valid],minlength=int(objects.max())+1)
    hit=np.bincount(objects[valid&prediction],minlength=len(total))
    return total,hit

def ratio(a,b):return float(a/b) if b else None

def count_metrics(y,valid,prediction):
    return dict(tp=int(np.sum(valid&y&prediction)),fn=int(np.sum(valid&y&~prediction)),
                fp=int(np.sum(valid&~y&prediction)),tn=int(np.sum(valid&~y&~prediction)))

def edge_counts(prediction,valid):
    disagreements=0;neighbors=0
    for axis in [0,1]:
        a=[slice(None),slice(None)];b=a.copy();a[axis]=slice(1,None);b[axis]=slice(None,-1)
        a=tuple(a);b=tuple(b);keep=valid[a]&valid[b]
        neighbors+=int(keep.sum());disagreements+=int(np.sum((prediction[a]!=prediction[b])&keep))
    return disagreements,neighbors

def evaluate_fit(meta_path,outroot,smoothing=False):
    meta=json.loads(meta_path.read_text());fit_id=meta['fit_id'];out=outroot/fit_id
    source=ROOT/meta['prediction_path']
    if sha(source)!=meta['prediction_sha256']:raise RuntimeError('Prediction hash mismatch: '+fit_id)
    manifest=json.loads((ROOT/meta['manifest_path']).read_text())
    entries={e['core_id']:e for e in manifest['cores']}
    with np.load(source) as f:
        ids=f['core_ids'].tolist();splits=f['splits'].tolist();raw=f['probability']
    references={};objects={}
    for i,cid in enumerate(ids):
        e=entries[cid]
        if sha(ROOT/e['reference_path'])!=e['reference_sha256']:raise RuntimeError('Reference hash mismatch')
        with np.load(ROOT/e['reference_path']) as f:references[cid]={k:f[k] for k in f.files}
        objects[cid]=json.loads((ROOT/e['metadata_path']).read_text())['objects']
        valid=references[cid]['valid'].astype(bool)
        if not np.array_equal(np.isfinite(raw[i]),valid):raise RuntimeError('Prediction/common-valid mask mismatch')
        if np.any((raw[i][valid]<0)|(raw[i][valid]>1)):raise RuntimeError('Probability out of bounds')
    versions=[('raw',raw)]
    if smoothing and meta['representation']=='optical' and meta['decoder']=='rf':
        for sigma in [1,2]:versions.append((f'smooth{sigma}',np.stack([normalized_smooth(x,sigma) for x in raw])))
    core_rows=[];object_rows=[];threshold_rows=[];pooled=[];decision_hashes=[]
    for version,p in versions:
        negative={}
        for split in ['validation','test']:
            negative[split]=np.concatenate([p[i][references[cid]['valid']&~references[cid]['y'].astype(bool)]
                for i,cid in enumerate(ids) if splits[i]==split])
        test_y=np.concatenate([references[cid]['y'][references[cid]['valid']] for i,cid in enumerate(ids) if splits[i]=='test'])
        test_p=np.concatenate([p[i][references[cid]['valid']] for i,cid in enumerate(ids) if splits[i]=='test'])
        pooled.append(dict(version=version,average_precision=float(average_precision_score(test_y,test_p)),
            test_pixels=len(test_y),positive_pixels=int(test_y.sum()),negative_pixels=int(np.sum(test_y==0))))
        conditions=[(f'standardized_{target:g}',threshold_for(negative['test'],target),target,'test') for target in [.01,.05,.1]]
        conditions.append(('validation_0.05',threshold_for(negative['validation'],.05),.05,'validation'))
        regional_negative={}
        for split in ['validation','test']:
            regional_negative[split]={}
            for region in sorted(set(entries[cid]['region_id'] for i,cid in enumerate(ids) if splits[i]==split)):
                regional_negative[split][region]=np.concatenate([p[i][references[cid]['valid']&~references[cid]['y'].astype(bool)]
                    for i,cid in enumerate(ids) if splits[i]==split and entries[cid]['region_id']==region])
        conditions.append(('regional_0.05',{r:threshold_for(v,.05) for r,v in regional_negative['test'].items()},.05,'test'))
        if set(regional_negative['test'])<=set(regional_negative['validation']):
            conditions.append(('regional_validation_0.05',{r:threshold_for(regional_negative['validation'][r],.05)
                for r in regional_negative['test']},.05,'validation'))
        for condition,threshold,target,chosen_split in conditions:
            threshold_at=lambda cid:threshold[entries[cid]['region_id']] if isinstance(threshold,dict) else threshold
            packed=np.packbits(np.stack([(p[i]>threshold_at(cid))&references[cid]['valid']
                for i,cid in enumerate(ids) if splits[i]=='test']))
            decision_hashes.append(dict(version=version,condition=condition,
                decision_sha256=hashlib.sha256(packed.tobytes()).hexdigest()))
            threshold_items=list(threshold.items()) if isinstance(threshold,dict) else [('pooled',threshold)]
            for region,t in threshold_items:
                neg=negative[chosen_split] if region=='pooled' else regional_negative[chosen_split][region]
                threshold_rows.append(dict(version=version,condition=condition,region_id=region,threshold=t,target_fpr=target,
                    chosen_split=chosen_split,threshold_negative_pixels=len(neg),threshold_ties=int(np.sum(neg==t)),
                    threshold_split_achieved_fpr=float(np.mean(neg>t))))
            for i,cid in enumerate(ids):
                if splits[i]!='test':continue
                ref=references[cid];y=ref['y'].astype(bool);valid=ref['valid'].astype(bool)
                t=threshold_at(cid);pred=(p[i]>t)&valid
                erasures=[0,10,20] if condition=='standardized_0.05' and version=='raw' else [0]
                for tolerance in erasures:
                    keep=valid&boundary_mask(y,tolerance)
                    counts=count_metrics(y,keep,pred)
                    totals,hits=coverage_counts(ref['objects'],keep,pred)
                    row=dict(core_id=cid,region_id=entries[cid]['region_id'],version=version,
                        condition=condition,boundary_tolerance_m=tolerance,threshold=t,**counts)
                    row.update(valid_pixels=int(keep.sum()),positive_pixels=int(np.sum(y&keep)),
                        negative_pixels=int(np.sum(~y&keep)),predicted_positive_pixels=int(np.sum(pred&keep)))
                    if tolerance==0:
                        d,n=edge_counts(pred,valid);row.update(edge_disagreements=d,edge_neighbor_pairs=n,
                            predicted_components=int(label(pred,structure=np.ones((3,3)))[1]),
                            reference_scoring_empty=bool(not np.any(valid)),
                            all_positive=bool(np.any(valid) and np.all(pred[valid])),
                            all_negative=bool(np.any(valid) and not np.any(pred)),
                            average_precision=float(average_precision_score(y[valid],p[i][valid])) if np.any(y[valid]) else None)
                    for o in objects[cid]:
                        if not o['main_eligible']:continue
                        oid=o['object_id'];total=int(totals[oid]) if oid<len(totals) else 0
                        hit=int(hits[oid]) if oid<len(hits) else 0
                        object_rows.append(dict(core_id=cid,region_id=entries[cid]['region_id'],
                            object_id=oid,version=version,condition=condition,boundary_tolerance_m=tolerance,
                            size_bin=o['size_bin'],vector_area_m2=o['vector_area_m2'],
                            isolated_50m=o['isolated_50m'],valid_fraction=o['valid_fraction'],
                            interior_pixels=o['interior_pixels'],habitat_codes=';'.join(o['codes']),
                            scored_pixels=total,positive_pixels=hit,coverage=ratio(hit,total),
                            recovered_any=int(hit>0) if total else None,
                            recovered_50=int(2*hit>=total) if total else None,
                            recovered_75=int(4*hit>=3*total) if total else None))
                    core_rows.append(row)
                if condition=='standardized_0.05' and version=='raw':
                    interior=ref['positive_interior'].astype(bool)|ref['negative_interior'].astype(bool)
                    core_rows.append(dict(core_id=cid,region_id=entries[cid]['region_id'],version=version,
                        condition='interior20_0.05',boundary_tolerance_m=20,threshold=t,
                        **count_metrics(y,valid&interior,pred)))
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(core_rows).to_csv(out/'cores.csv',index=False,float_format='%.17g')
    pd.DataFrame(object_rows).to_csv(out/'objects.csv',index=False,float_format='%.17g')
    pd.DataFrame(threshold_rows).to_csv(out/'thresholds.csv',index=False,float_format='%.17g')
    record=dict(fit_id=fit_id,evaluated_at_utc=now(),fit_metadata_path=str(meta_path.relative_to(ROOT)),
        fit_metadata_sha256=sha(meta_path),prediction_sha256=sha(source),
        files={name:sha(out/name) for name in ['cores.csv','objects.csv','thresholds.csv']},
        smoothing=smoothing,object_rows=len(object_rows),core_rows=len(core_rows),pooled_scores=pooled,
        probability_field_sha256=hashlib.sha256(raw.tobytes()).hexdigest(),decision_hashes=decision_hashes)
    (out/'evaluation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(fit_id,'evaluated',len(object_rows),'object rows',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--fits',nargs='*');p.add_argument('--fit-dir',default='data/results/fits')
    p.add_argument('--out',default='data/evaluation');p.add_argument('--smoothing',action='store_true');a=p.parse_args()
    paths=sorted((ROOT/a.fit_dir).glob('*.json'))
    if a.fits:paths=[x for x in paths if x.stem in a.fits]
    for path in paths:
        destination=ROOT/a.out/path.stem/'evaluation.json'
        if destination.exists():
            old=json.loads(destination.read_text())
            if old['fit_metadata_sha256']==sha(path) and (old['smoothing'] or not a.smoothing):continue
        evaluate_fit(path,ROOT/a.out,a.smoothing)

if __name__=='__main__':main()
