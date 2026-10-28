"""Synthetic software fixture, NOT a wetland/model experiment.

No model is fit. Artificial score maps have hand-computed recovery rates. The
RF/budget/scope tags exercise the actual analysis filters and do not describe a
trained classifier. All fixture inputs/outputs are isolated under --out.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluate import evaluate_fit
from summarize import load_evaluations,describe,primary_bootstrap
from records import ROOT,now
from check_metrics import main as check_metrics

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    check_metrics()
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();out=ROOT/a.out
    out.mkdir(parents=True,exist_ok=True);entries=[];ids=[];splits=[];probabilities={}
    manifest_path=out/'manifest.json'
    for region in ['R01','R02','R03','R04']:
        for split in (['validation','test','empty_test'] if region=='R01' else ['validation','test']):
            empty=split=='empty_test';actual_split='test' if empty else split
            cid=region+'_'+split;ids.append(cid);splits.append(actual_split)
            obj=np.zeros((256,256),dtype=np.int32)
            if not empty:obj[10:12,10:20]=1;obj[30:32,30:40]=2
            y=obj>0;valid=np.zeros_like(y) if empty else np.ones_like(y);refpath=out/(cid+'-reference.npz')
            np.savez_compressed(refpath,y=y,valid=valid,objects=obj,positive_interior=np.zeros_like(y),negative_interior=~y)
            objects=[dict(object_id=i,core_id=cid,region_id=region,main_eligible=True,size_bin='small',
                vector_area_m2=2000.,valid_fraction=1.,isolated_50m=True,interior_pixels=0,codes=['PEM1C']) for i in ([] if empty else [1,2])]
            metadata_path=out/(cid+'-metadata.json');metadata_path.write_text(json.dumps(dict(objects=objects)))
            entries.append(dict(core_id=cid,region_id=region,split=actual_split,reference_path=str(refpath.relative_to(ROOT)),
                reference_sha256=sha(refpath),metadata_path=str(metadata_path.relative_to(ROOT))))
            for rep,policy in [('aef','area'),('aef','object'),('optical','area'),('optical','object')]:
                scores=np.linspace(0,.1,256*256,dtype=np.float32).reshape(256,256)
                scores[obj==1]=.9;scores[obj==2]=.8 if rep=='aef' and policy=='object' else 0
                scores[~valid]=np.nan
                probabilities.setdefault((rep,policy),[]).append(scores)
    manifest_path.write_text(json.dumps(dict(cores=entries,synthetic_software_fixture=True)))
    fitdir=out/'fits';fitdir.mkdir(exist_ok=True)
    for (rep,policy),values in probabilities.items():
        for seed in [101,202,303,404,505]:
            fid=f'fixture_{rep}_{policy}_{seed}';path=out/(fid+'.npz')
            np.savez_compressed(path,core_ids=np.array(ids),splits=np.array(splits),probability=np.stack(values))
            metadata=dict(fit_id=fid,scope='within',decoder='rf',budget=2000,seed=seed,policy=policy,
                representation=rep,prediction_path=str(path.relative_to(ROOT)),prediction_sha256=sha(path),
                manifest_path=str(manifest_path.relative_to(ROOT)),sampling=dict(sample_sha256=None),
                elapsed_seconds=None,feature_count=0,warnings=[],synthetic_software_fixture=True,
                interpretation='No model fit; scope/decoder/budget are artificial schema tags only')
            mpath=fitdir/(fid+'.json');mpath.write_text(json.dumps(metadata))
            evaluate_fit(mpath,out/'evaluation')
    cores,objects,fits,thresholds=load_evaluations(out/'evaluation')
    scores,regions,blocks=describe(cores,objects)
    for condition in ['standardized_0.05','regional_0.05']:
        result=primary_bootstrap(blocks,replicates=30,condition=condition)
        h1=result['H1_interaction']
        assert h1['estimate']==.5 and h1['conditional_block_bootstrap_95_percent_interval']==[.5,.5]
        assert result['aef_oracle_gain']['estimate']==.5
        assert result['optical_oracle_gain']['estimate']==0
    primary=scores[(scores.condition=='standardized_0.05')&(scores.boundary_tolerance_m==0)]
    assert np.all(primary[(primary.representation=='aef')&(primary.policy=='object')].small_macro_recovery_50==1)
    assert np.all(primary[~((primary.representation=='aef')&(primary.policy=='object'))].small_macro_recovery_50==.5)
    assert np.all(primary.upland_fpr<=.05)
    assert np.all(primary.empty_scoring_cores==1)
    assert np.all(primary.all_positive_cores==0)
    report=dict(checked_at_utc=now(),status='PASS',synthetic_software_fixture=True,no_model_fitted=True,
        evaluated_artificial_maps=len(fits),expected_h1_interaction=.5,expected_conditional_interval=[.5,.5],
        expected_aef_oracle_gain=.5,expected_optical_oracle_gain=0,
        generator='code/check_pipeline.py; deterministic two 20-pixel objects per core, common negative-score ramp, explicit class-score assignments',
        meaning='Checks probability files → thresholds → object coverage → CSV → paired summary; not scientific evidence about real wetlands or classifiers')
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
