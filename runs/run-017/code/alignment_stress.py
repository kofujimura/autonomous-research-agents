"""Deterministic translated-reference check on unchanged saved model scores."""
import argparse
import hashlib
import json
import numpy as np
import pandas as pd
from records import ROOT,now
from evaluate import threshold_for,count_metrics
from summarize import primary_bootstrap

OFFSETS={'unchanged':(0,0),'north':(-1,0),'south':(1,0),'west':(0,-1),'east':(0,1)}

def translate(array,dy,dx,fill=0):
    result=np.full_like(array,fill)
    h,w=array.shape
    sy=slice(max(0,-dy),min(h,h-dy));sx=slice(max(0,-dx),min(w,w-dx))
    ty=slice(max(0,dy),min(h,h+dy));tx=slice(max(0,dx),min(w,w+dx))
    result[ty,tx]=array[sy,sx]
    return result

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='data/alignment-stress');a=p.parse_args()
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'data/derived/dataset-manifest.json').read_text())
    entries=sorted([x for x in manifest['cores'] if x['split']=='test'],key=lambda x:x['core_id'])
    refs={};transformed={};cohort=[];rows=[]
    for e in entries:
        assert sha(ROOT/e['reference_path'])==e['reference_sha256']
        with np.load(ROOT/e['reference_path']) as f:r={k:f[k] for k in ['valid','y','objects']}
        r['valid']=r['valid'].astype(bool);r['y']=r['y'].astype(bool)
        cid=e['core_id'];refs[cid]=r;transformed[cid]={}
        for direction,(dy,dx) in OFFSETS.items():
            transformed[cid][direction]=dict(y=translate(r['y'],dy,dx),
                objects=translate(r['objects'],dy,dx),domain=r['valid']&translate(r['valid'],dy,dx))
        meta=json.loads((ROOT/e['metadata_path']).read_text())
        for o in meta['objects']:
            if not o['main_eligible'] or o['size_bin']!='small':continue
            source=(r['objects']==o['object_id'])&r['valid'];n=int(source.sum());details={};retained=True
            for direction,(dy,dx) in OFFSETS.items():
                shifted=translate(source,dy,dx);domain=transformed[cid][direction]['domain']
                cropped=int(shifted.sum())!=n;valid=int(np.sum(shifted&domain))
                details[direction]=dict(cropped=cropped,remaining_scored_pixels=valid,original_valid_pixels=n)
                retained &= not cropped and valid>=.9*n
            row=dict(core_id=cid,region_id=e['region_id'],object_id=o['object_id'],retained=bool(retained),
                original_valid_pixels=n,directions=details)
            rows.append(row)
            if retained:cohort.append(row)
    cohort_info=dict(fixed_at_utc=now(),original_patches=len(rows),retained_patches=len(cohort),
        by_region={r:dict(original=sum(x['region_id']==r for x in rows),retained=sum(x['region_id']==r for x in cohort))
            for r in sorted(set(e['region_id'] for e in entries))},rows=rows,
        score_independent=True,offsets=OFFSETS,interpretation='Synthetic integer translations; not an estimated inventory error distribution')
    (out/'cohort.json').write_text(json.dumps(cohort_info,indent=2)+'\n')
    # The common cohort is saved before opening any probability field.
    objects=[];cores=[];blocks=[];thresholds=[]
    for seed in [101,202,303,404,505]:
        for representation in ['aef','optical']:
            for policy in ['area','object']:
                key=f'within_rf_{representation}_{policy}_n2000_s{seed}'
                meta_path=ROOT/'data/results/fits'/(key+'.json');m=json.loads(meta_path.read_text())
                source=ROOT/m['prediction_path'];assert sha(source)==m['prediction_sha256']
                with np.load(source) as f:prob={cid:p for cid,p,split in zip(f['core_ids'],f['probability'],f['splits']) if split=='test'}
                assert set(prob)==set(refs)
                for cid,pred in prob.items():assert np.array_equal(np.isfinite(pred),refs[cid]['valid'])
                for direction in OFFSETS:
                    tag=dict(fit_id=key,scope='alignment_'+direction,decoder='rf',budget=2000,seed=seed,
                        representation=representation,policy=policy,version='raw',condition='standardized_0.05',
                        boundary_tolerance_m=0,size_bin='small')
                    negative=np.concatenate([prob[e['core_id']][transformed[e['core_id']][direction]['domain']&
                        ~transformed[e['core_id']][direction]['y'].astype(bool)] for e in entries])
                    threshold=threshold_for(negative,.05)
                    thresholds.append(dict(**tag,threshold=threshold,achieved_fpr=float(np.mean(negative>threshold)),
                        reference_upland_pixels=len(negative),source_prediction_sha256=m['prediction_sha256']))
                    for e in entries:
                        cid=e['core_id'];target=transformed[cid][direction];prediction=prob[cid]>threshold
                        counts=count_metrics(target['y'].astype(bool),target['domain'],prediction)
                        cores.append(dict(**tag,core_id=cid,region_id=e['region_id'],**counts))
                        eligible=[x for x in cohort if x['core_id']==cid];recovered=0
                        for o in eligible:
                            mask=(target['objects']==o['object_id'])&target['domain'];n=int(mask.sum());hit=int(np.sum(mask&prediction))
                            success=2*hit>=n;assert n>0;recovered+=success
                            objects.append(dict(**tag,core_id=cid,region_id=e['region_id'],object_id=o['object_id'],
                                scored_pixels=n,positive_pixels=hit,coverage=hit/n,recovered_50=success))
                        blocks.append(dict(**tag,core_id=cid,region_id=e['region_id'],n=len(eligible),recovered=recovered))
                print(key,'translated references evaluated',flush=True)
    block_frame=pd.DataFrame(blocks)
    for name,collection in [('objects',objects),('cores',cores),('thresholds',thresholds),('bootstrap-blocks',blocks)]:
        pd.DataFrame(collection).to_csv(out/(name+'.csv'),index=False,float_format='%.17g')
    contrasts={direction:primary_bootstrap(block_frame,scope='alignment_'+direction) for direction in OFFSETS}
    result=dict(completed_at_utc=now(),original_patches=len(rows),common_cohort_patches=len(cohort),
        by_region=cohort_info['by_region'],contrasts=contrasts,
        interpretation='Exploratory deterministic spatial stress test; fixed model predictions, shared reference cohort, directional thresholds; not reference truth or an empirical error model')
    (out/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({d:v['H1_interaction'] for d,v in contrasts.items()},indent=2))

if __name__=='__main__':main()
