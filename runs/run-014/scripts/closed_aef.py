"""Closed original AlphaEarth cohort; scheduled before the slower paired analysis."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import pandas as pd
from features import load_features,target_coverage
from analyse import make_predictions,summarize,SEED
from record import ROOT

def closed_aef(output):
    output.mkdir(parents=True,exist_ok=False)
    vec,av,hashes,metadata=load_features(models=['aef'])
    # TESSERA arrays may still be arriving. No TESSERA value or availability
    # enters this model-specific analysis or its saved input dependencies.
    av=av[av.model=='aef'].copy()
    assert av.file_present.all(), 'Original AlphaEarth acquisition must be closed first'
    hashes={k:v for k,v in hashes.items() if k.startswith('data/embeddings/aef/')}
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    pred,threshold,counts,ident,near=make_predictions(vec,t,refs,availability_mode='model_specific',models=['aef'])
    assert set(pred.model)=={'aef'}
    av.to_csv(output/'availability.csv',index=False)
    pred.to_parquet(output/'predictions.parquet',index=False)
    for name,df in [('thresholds',threshold),('reference-availability',counts),('identities',ident),('nearest-reference-distances',near)]:
        df.to_csv(output/f'{name}.csv',index=False)
    metrics,pairs,strata=summarize(pred)
    metrics.to_csv(output/'metrics.csv',index=False);pairs.to_csv(output/'paired-comparisons.csv',index=False)
    strata.to_csv(output/'strata.csv',index=False)
    primary=metrics[(metrics.support=='centre')&(metrics.seed==SEED)&(metrics.reference_mode=='global')]
    primary.to_csv(output/'main-table.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    print(primary.to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();closed_aef(a.output)
