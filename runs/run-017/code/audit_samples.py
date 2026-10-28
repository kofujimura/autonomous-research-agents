"""Verify labelled-position budgets and report allocation coverage, offline."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from records import ROOT,now
from fit_models import Dataset,inverse_object_weights

PIXELS=256*256

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',default='data/derived/dataset-manifest.json')
    p.add_argument('--results',default='data/results');p.add_argument('--out',default='analysis');a=p.parse_args()
    manifest=json.loads((ROOT/a.manifest).read_text());entries=sorted(manifest['cores'],key=lambda x:x['core_id'])
    references=[];metadata=[]
    for e in entries:
        with np.load(ROOT/e['reference_path']) as f:references.append({k:f[k].ravel() for k in f.files})
        metadata.append(json.loads((ROOT/e['metadata_path']).read_text()))
    weight_data=object.__new__(Dataset)
    weight_data.entries=entries;weight_data.metadata=metadata
    weight_data.small={i:value for i,value in enumerate(references)}
    rows=[];seen={};fit_count=0;weight_fits=0
    for path in sorted((ROOT/a.results/'fits').glob('*.json')):
        m=json.loads(path.read_text());fit_count+=1;s=m['sampling'];key=(m['scope'],m['policy'],m['budget'],m['seed'])
        if m.get('sample_weight'):
            w=m['sample_weight'];wp=ROOT/w['path']
            assert hashlib.sha256(wp.read_bytes()).hexdigest()==w['sha256']
            with np.load(ROOT/s['sample_path']) as f:weight_positions=f['positions']
            train=[i for i,e in enumerate(entries) if e['core_id'] in m['train_core_ids']]
            expected,info=inverse_object_weights(weight_data,train,weight_positions,
                cap=10 if m['policy']=='weighted_area_cap10' else None)
            with np.load(wp) as f:
                assert np.array_equal(f['positions'],weight_positions)
                assert np.array_equal(f['weights'],expected)
            for name in ['positive_effective_sample_size','minimum_positive_weight','maximum_positive_weight',
                         'positive_weight_sum','negative_weight_sum']:
                assert np.isclose(info[name],w[name],rtol=0,atol=1e-12)
            assert m['decoder']=='rf_noboot' and m['model_parameters']['bootstrap']=='False'
            weight_fits+=1
        if key in seen:
            assert seen[key]==s['sample_sha256'],'Positions differ across representations or decoders'
            continue
        seen[key]=s['sample_sha256']
        sample=ROOT/s['sample_path'];assert hashlib.sha256(sample.read_bytes()).hexdigest()==s['sample_sha256']
        with np.load(sample) as f:positions=f['positions'];labels=f['labels'];initial=f['initial_positions']
        assert len(positions)==len(np.unique(positions))==m['budget']
        selected_core=positions//PIXELS
        assert set(entries[int(k)]['core_id'] for k in selected_core)<=set(m['train_core_ids'])
        observed=np.array([references[int(k)]['y'][int(v)] for k,v in zip(selected_core,positions%PIXELS)])
        assert np.array_equal(observed,labels)
        assert all(references[int(k)]['valid'][int(v)] for k,v in zip(selected_core,positions%PIXELS))
        if m['policy'] in ['area','interior','object','object_mmu','area_region','object_region','weighted_area','weighted_area_cap10','area_regionmatched','area_corematched']:assert int(labels.sum())==m['budget']//2
        if m['policy'] in ['area_regionmatched','area_corematched']:
            oracle_path=sample.parent/f'object_n{m["budget"]}_s{m["seed"]}.npz'
            assert hashlib.sha256(oracle_path.read_bytes()).hexdigest()==s['quota_source_sample_sha256']
            with np.load(oracle_path) as f:
                assert np.array_equal(positions[labels==0],f['positions'][f['labels']==0])
            codes=np.array([entries[int(k)]['core_id' if s['matched_geographical_level']=='core' else 'region_id'] for k in selected_core])
            for group,quota in s['geographical_positive_quotas'].items():
                assert int(np.sum((codes==group)&(labels==1)))==quota
        if m['policy']=='object_mmu':assert s['sub_mmu_positive_fitting_positions']==0
        if m['policy'].endswith('_classmatched'):assert int(labels.sum())==s['matched_positive_labels']
        if m['policy'] in ['weighted_area','weighted_area_cap10']:
            with np.load(sample.parent/f'area_n{m["budget"]}_s{m["seed"]}.npz') as f:assert np.array_equal(positions,f['positions'])
        if s.get('initialization')=='uniform':
            with np.load(sample.parent/f'natural_area_n{m["budget"]}_s{m["seed"]}.npz') as f:assert np.array_equal(initial,f['positions'][:m['budget']//2])
            assert np.array_equal(positions[:len(initial)],initial)
        row=dict(scope=m['scope'],policy=m['policy'],budget=m['budget'],seed=m['seed'],
            position_array_sha256=hashlib.sha256(positions.astype('<i8').tobytes()).hexdigest(),
            positive_labels=int(labels.sum()),negative_labels=int(len(labels)-labels.sum()),
            initial_labels=len(initial),fallback_labels=s['fallback_labels'],
            shared_with_area=s['positions_shared_with_area'],unique_positions=len(positions),
            sub_mmu_positive_positions=s['sub_mmu_positive_fitting_positions'])
        for region in sorted(set(e['region_id'] for e in entries)):
            keep=np.array([entries[int(k)]['region_id']==region for k in selected_core])
            row[region+'_positive_positions']=int(labels[keep].sum())
            row[region+'_negative_positions']=int(np.sum(labels[keep]==0))
            if m['policy'] in ['area_region','object_region'] and region in s['regional_class_quotas']:
                assert row[region+'_positive_positions']==row[region+'_negative_positions']==s['regional_class_quotas'][region]
        counts={}
        for k,e in enumerate(entries):
            if e['core_id'] not in m['train_core_ids']:continue
            selected=positions[selected_core==k]%PIXELS;start=initial[initial//PIXELS==k]%PIXELS
            local=references[k]['objects'][selected];start_local=references[k]['objects'][start]
            for o in metadata[k]['objects']:
                if not o['main_eligible']:continue
                name=o['size_bin'];stats=counts.setdefault(name,dict(available=0,represented=0,initial_represented=0))
                stats['available']+=1;stats['represented']+=int(np.any(local==o['object_id']))
                stats['initial_represented']+=int(np.any(start_local==o['object_id']))
        for name,stats in counts.items():
            for statistic,value in stats.items():row[name+'_'+statistic]=value
        row['positive_interior_positions']=sum(int(np.sum(references[int(k)]['positive_interior'][positions[selected_core==k]%PIXELS])) for k in np.unique(selected_core))
        rows.append(row)
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).sort_values(['scope','budget','policy','seed']).to_csv(out/'allocation-audit.csv',index=False)
    summary=dict(checked_at_utc=now(),fits_checked=fit_count,sampling_conditions=len(rows),
        distinct_position_sets=len(set(row['position_array_sha256'] for row in rows)),
        unique_budgets_valid=True,training_only=True,labels_match_bundled_reference=True,
        matched_positions_across_representations_and_decoders=True,
        weight_vectors_checked=weight_fits,weight_check='Hash, position identity and exact recomputation from bundled reference groups; implementation consistency, not independent algorithm validation')
    (out/'allocation-audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
