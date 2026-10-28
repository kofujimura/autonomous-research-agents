"""Fit pre-specified classifiers and save full validation/test probabilities.

No performance metric or test label enters fitting or sample selection.
"""
import argparse
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import time
import warnings
import numpy as np
from scipy.ndimage import label
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from records import ROOT, now

PIXELS=256*256
POLICIES=['area','interior','object','proposal','uncertainty']
PROPOSAL_CONFIG={
    'proposal':('proposal','optical','balanced'),
    'uncertainty':('uncertainty','optical','balanced'),
    'proposal_aef':('proposal','aef','balanced'),
    'uncertainty_aef':('uncertainty','aef','balanced'),
    'proposal_uniform_aef':('proposal','aef','uniform'),
    'uncertainty_uniform_aef':('uncertainty','aef','uniform')}

def atomic_npz(path,**arrays):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.stem+'.partial.npz')
    np.savez_compressed(temporary,**arrays);temporary.replace(path)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class Dataset:
    def __init__(self,manifest):
        self.manifest=json.loads(manifest.read_text())
        self.entries=sorted(self.manifest['cores'],key=lambda x:x['core_id'])
        self.ids=[x['core_id'] for x in self.entries]
        self.metadata=[json.loads((ROOT/x['metadata_path']).read_text()) for x in self.entries]
        self.small={}
        for k,e in enumerate(self.entries):
            if sha(ROOT/e['metadata_path'])!=e['metadata_sha256']:
                raise RuntimeError('Feature metadata hash mismatch: '+e['core_id'])
            if sha(ROOT/e['feature_path'])!=e['feature_sha256']:
                raise RuntimeError('Feature hash mismatch: '+e['core_id'])
            if sha(ROOT/e['reference_path'])!=e['reference_sha256']:
                raise RuntimeError('Reference hash mismatch: '+e['core_id'])
            with np.load(ROOT/e['reference_path']) as data:
                self.small[k]={v:data[v].reshape(-1) for v in
                    ['y','valid','objects','positive_interior','negative_interior']}

    @lru_cache(maxsize=4)
    def values(self,k,representation):
        with np.load(ROOT/self.entries[k]['feature_path']) as data:
            if representation=='hybrid':return np.concatenate([data['aef'],data['optical']],axis=-1).reshape(PIXELS,-1)
            return data[representation].reshape(PIXELS,-1)

    def sample_values(self,positions,representation):
        order=np.argsort(positions//PIXELS,kind='stable')
        chosen=positions[order]
        chunks=[]
        for k in np.unique(chosen//PIXELS):
            subset=chosen[chosen//PIXELS==k]%PIXELS
            chunks.append(self.values(int(k),representation)[subset])
        x=np.concatenate(chunks,axis=0)
        inverse=np.argsort(order)
        return x[inverse]

    def labels(self,positions):
        return np.array([self.small[int(k)]['y'][int(p)] for k,p in zip(positions//PIXELS,positions%PIXELS)],dtype=np.uint8)

    def pools(self,train):
        pools={name:[] for name in ['positive','negative','positive_interior','negative_interior','all']}
        for k in train:
            data=self.small[k];valid=data['valid'].astype(bool);y=data['y'].astype(bool)
            masks=dict(positive=valid&y,negative=valid&~y,all=valid,
                       positive_interior=data['positive_interior'].astype(bool),
                       negative_interior=data['negative_interior'].astype(bool))
            for name,mask in masks.items():pools[name].append(k*PIXELS+np.flatnonzero(mask))
        return {name:np.concatenate(arrays) for name,arrays in pools.items()}

    def object_groups(self,train,minimum_area=0):
        # Merge appearances sharing a source polygon within training geography.
        nodes=[];source_seen={};parent=[];areas=[]
        def find(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        for k in train:
            for o in self.metadata[k]['objects']:
                oid=o['object_id'];mask=(self.small[k]['objects']==oid)&self.small[k]['valid'].astype(bool)
                if not np.any(mask):continue
                n=len(nodes);parent.append(n);nodes.append((k,oid));areas.append(o['vector_area_m2'])
                for sid in o['source_ids']:
                    if sid in source_seen:
                        a,b=find(n),find(source_seen[sid])
                        if a!=b:parent[max(a,b)]=min(a,b)
                    else:source_seen[sid]=n
        groups={};group_areas={}
        for n,(k,oid) in enumerate(nodes):
            positions=k*PIXELS+np.flatnonzero((self.small[k]['objects']==oid)&self.small[k]['valid'].astype(bool))
            groups.setdefault(find(n),[]).append(positions)
            group_areas[find(n)]=max(group_areas.get(find(n),0),areas[n])
        return [np.concatenate(v) for g,v in sorted(groups.items()) if group_areas[g]>=minimum_area]

def draw_groups(groups,n,rng):
    arrays=[a.copy() for a in groups if len(a)]
    remaining=[len(a) for a in arrays];active=list(range(len(arrays)));result=[]
    while len(result)<n and active:
        slot=int(rng.integers(len(active)));g=active[slot];j=int(rng.integers(remaining[g]))
        result.append(int(arrays[g][j]));remaining[g]-=1
        arrays[g][j]=arrays[g][remaining[g]]
        if remaining[g]==0:active[slot]=active[-1];active.pop()
    return np.array(result,dtype=np.int64)

def quota_matched_positions(pool,oracle_positive,negative,group_codes,seed):
    """Match oracle positive counts by supplied geographical group, retaining negatives."""
    rng=np.random.default_rng(seed);chosen=[];quotas={}
    oracle_codes=np.array([group_codes[int(k)] for k in oracle_positive//PIXELS])
    pool_codes=np.array([group_codes[int(k)] for k in pool//PIXELS])
    for group in sorted(set(oracle_codes)):
        n=int(np.sum(oracle_codes==group));quotas[str(group)]=n
        chosen.append(rng.choice(pool[pool_codes==group],n,replace=False))
    return np.concatenate([*chosen,negative]),quotas

def predict_core(model,data,k,representation):
    x=data.values(k,representation);valid=data.small[k]['valid'].astype(bool)
    result=np.full(PIXELS,np.nan,dtype=np.float32)
    ids=np.flatnonzero(valid)
    for j in range(0,len(ids),16384):
        selected=ids[j:j+16384]
        probabilities=model.predict_proba(x[selected]);positive=np.flatnonzero(model.classes_==1)
        result[selected]=probabilities[:,int(positive[0])] if len(positive) else 0
    return result.reshape(256,256)

def proposal_scores(data,train,initial,seed,path,representation='optical'):
    if path.exists():
        with np.load(path) as f:
            if not np.array_equal(f['initial_positions'],initial):raise RuntimeError('Proposal initialization cache mismatch')
            return {int(k):p for k,p in zip(f['core_indices'],f['probability'])}
    model=RandomForestClassifier(n_estimators=100,min_samples_leaf=5,max_features='sqrt',
        class_weight='balanced',random_state=seed,n_jobs=2)
    model.fit(data.sample_values(initial,representation),data.labels(initial))
    scores={k:predict_core(model,data,k,representation) for k in train}
    atomic_npz(path,core_indices=np.array(train),probability=np.stack([scores[k] for k in train]),initial_positions=initial)
    return scores

def choose_sample(data,train,budget,seed,policy,sample_dir):
    path=sample_dir/f'{policy}_n{budget}_s{seed}.npz'
    meta_path=path.with_suffix('.json')
    if path.exists():
        with np.load(path) as f:positions=f['positions']
        return positions,json.loads(meta_path.read_text())
    if budget%4:raise ValueError('Budget must be divisible by four')
    pools=data.pools(train);rng=np.random.default_rng(seed)
    half=budget//2
    uniform_policy=policy=='natural_area' or (policy in PROPOSAL_CONFIG and PROPOSAL_CONFIG[policy][2]=='uniform')
    class_pool_can_fill=min(len(pools['positive']),len(pools['negative']))>=half
    if not class_pool_can_fill and not uniform_policy:raise RuntimeError('Balanced class pool too small')
    positive=rng.choice(pools['positive'],half,replace=False) if class_pool_can_fill else np.array([],dtype=np.int64)
    negative=rng.choice(pools['negative'],half,replace=False) if class_pool_can_fill else np.array([],dtype=np.int64)
    area=np.concatenate([positive,negative])
    initial=np.concatenate([positive[:half//2],negative[:half//2]])
    details=dict(policy=policy,budget=budget,seed=seed,initial_labels=0,fallback_labels=0,
                 train_core_ids=[data.ids[k] for k in train])
    if policy in ['area','weighted_area','weighted_area_cap10']:positions=area
    elif policy in ['area_regionmatched','area_corematched']:
        oracle,oracle_details=choose_sample(data,train,budget,seed,'object',sample_dir)
        positive_oracle=oracle[data.labels(oracle)==1];negative_oracle=oracle[data.labels(oracle)==0]
        by_core=policy=='area_corematched'
        groups={k:data.ids[k] if by_core else data.entries[k]['region_id'] for k in train}
        positions,quotas=quota_matched_positions(pools['positive'],positive_oracle,negative_oracle,
            groups,seed+(16101 if by_core else 15101))
        details.update(oracle_frame_derived_quotas_used=True,matched_geographical_level='core' if by_core else 'region',
            geographical_positive_quotas=quotas,quota_source_sample_sha256=oracle_details['sample_sha256'],
            negative_positions_identical_to_oracle=True)
    elif policy in ['area_region','object_region']:
        regions=sorted(set(data.entries[k]['region_id'] for k in train))
        quota={r:half//len(regions) for r in regions}
        for r in np.random.default_rng(seed+13001).permutation(regions)[:half%len(regions)]:quota[r]+=1
        positives=[];negatives=[];all_groups=data.object_groups(train) if policy=='object_region' else []
        for ri,r in enumerate(regions):
            keys=[k for k in train if data.entries[k]['region_id']==r]
            pos=pools['positive'][np.isin(pools['positive']//PIXELS,keys)]
            neg=pools['negative'][np.isin(pools['negative']//PIXELS,keys)]
            negatives.append(np.random.default_rng(seed+13101+ri).choice(neg,quota[r],replace=False))
            if policy=='area_region':
                positives.append(np.random.default_rng(seed+14101+ri).choice(pos,quota[r],replace=False))
            else:
                groups=[]
                for group in all_groups:
                    belongs=np.isin(group//PIXELS,keys)
                    if np.any(belongs):
                        if not np.all(belongs):raise RuntimeError('A training object unexpectedly spans multiple reference regions')
                        groups.append(group)
                chosen=draw_groups(groups,quota[r],np.random.default_rng(seed+8101+ri))
                if len(chosen)!=quota[r]:raise RuntimeError('Region object pool cannot fill quota')
                positives.append(chosen)
        positions=np.concatenate(positives+negatives);details['regional_class_quotas']=quota
    elif policy=='natural_area':positions=np.random.default_rng(seed+11101).choice(pools['all'],budget,replace=False)
    elif policy.endswith('_classmatched'):
        base=policy.replace('_classmatched','')
        base_positions,base_details=choose_sample(data,train,budget,seed,base,sample_dir)
        with np.load(ROOT/base_details['sample_path']) as f:initial=f['initial_positions']
        base_labels=data.labels(base_positions);initial_labels=data.labels(initial)
        n_positive=int(base_labels.sum()-initial_labels.sum())
        n_negative=budget-len(initial)-n_positive
        rng=np.random.default_rng(seed+12101)
        positive_pool=np.setdiff1d(pools['positive'],initial)
        negative_pool=np.setdiff1d(pools['negative'],initial)
        positions=np.concatenate([initial,rng.choice(positive_pool,n_positive,replace=False),
            rng.choice(negative_pool,n_negative,replace=False)])
        details.update(initial_labels=len(initial),matched_policy=base,
            matched_positive_labels=int(base_labels.sum()),class_count_matching_uses_reference_pool=True)
    elif policy=='interior':
        if min(len(pools['positive_interior']),len(pools['negative_interior']))<half:
            raise RuntimeError('Unique interior class pool cannot fill this arm')
        positions=np.concatenate([rng.choice(pools['positive_interior'],half,replace=False),
                                  rng.choice(pools['negative_interior'],half,replace=False)])
    elif policy in ['object','object_mmu']:
        groups=data.object_groups(train,minimum_area=2000 if policy=='object_mmu' else 0)
        chosen=draw_groups(groups,half,np.random.default_rng(seed+8101))
        if len(chosen)!=half:raise RuntimeError('Oracle object pool cannot fill arm')
        positions=np.concatenate([chosen,negative]);details['oracle_training_objects']=len(groups)
    elif policy in PROPOSAL_CONFIG:
        kind,proposal_representation,initialization=PROPOSAL_CONFIG[policy]
        if initialization=='uniform':
            natural=np.random.default_rng(seed+11101).choice(pools['all'],budget,replace=False)
            initial=natural[:half]
        filename='proposal_model' if proposal_representation=='optical' and initialization=='balanced' else f'proposal_{proposal_representation}_{initialization}_model'
        scorepath=sample_dir/f'{filename}_n{budget}_s{seed}.npz'
        scores=proposal_scores(data,train,initial,seed,scorepath,representation=proposal_representation)
        details['initial_labels']=len(initial);details['proposal_score_path']=str(scorepath.relative_to(ROOT))
        details.update(proposal_predictors=proposal_representation,initialization=initialization,
            target_labels_used_to_choose_initial_positions=initialization=='balanced',additional_target_labels_used_for_selection=False)
        blocked=set(map(int,initial));need=budget-len(initial)
        rng=np.random.default_rng(seed+9101)
        if kind=='proposal':
            groups=[];frame_patch_count=0;frame_patch_misses=0
            for k in train:
                components,n=label((scores[k]>=.5)&data.small[k]['valid'].reshape(256,256),structure=np.ones((3,3)))
                counts=np.bincount(components.ravel())
                candidate_mask=(components>0)&(counts[components]>=4)
                for o in data.metadata[k]['objects']:
                    if not o['main_eligible']:continue
                    frame_patch_count+=1
                    frame_patch_misses+=not np.any(candidate_mask.ravel()&(data.small[k]['objects']==o['object_id']))
                for oid in np.flatnonzero(counts>=4):
                    if oid==0:continue
                    positions=k*PIXELS+np.flatnonzero(components.ravel()==oid)
                    positions=np.array([int(x) for x in positions if int(x) not in blocked],dtype=np.int64)
                    if len(positions):groups.append(positions)
            chosen=draw_groups(groups,need,rng);details['proposal_components']=len(groups)
            details.update(proposal_frame_eligible_training_patches=frame_patch_count,
                proposal_frame_missed_training_patches=int(frame_patch_misses))
        else:
            candidates=np.concatenate([k*PIXELS+np.flatnonzero(data.small[k]['valid']) for k in train])
            prob=np.concatenate([scores[k].ravel()[data.small[k]['valid']] for k in train])
            prob=np.clip(prob.astype(np.float64),1e-8,1-1e-8)
            entropy=-(prob*np.log(prob)+(1-prob)*np.log(1-prob))
            order=np.lexsort((candidates,-entropy))
            occupied={k:np.zeros((256,256),dtype=bool) for k in train};chosen_list=[]
            for j in order:
                pos=int(candidates[j]);k,p=divmod(pos,PIXELS);row,col=divmod(p,256)
                if pos in blocked or occupied[k][row,col]:continue
                chosen_list.append(pos)
                for dy in range(-2,3):
                    for dx in range(-2,3):
                        if dx*dx+dy*dy<9 and 0<=row+dy<256 and 0<=col+dx<256:
                            occupied[k][row+dy,col+dx]=True
                if len(chosen_list)==need:break
            chosen=np.array(chosen_list,dtype=np.int64)
        if len(chosen)<need:
            available=np.setdiff1d(pools['all'],np.concatenate([initial,chosen]),assume_unique=False)
            missing=need-len(chosen)
            chosen=np.concatenate([chosen,rng.choice(available,missing,replace=False)])
            details['fallback_labels']=missing
        positions=np.concatenate([initial,chosen])
    else:raise ValueError(policy)
    if len(positions)!=budget or len(np.unique(positions))!=budget:raise RuntimeError('Sample budget/uniqueness mismatch')
    labels=data.labels(positions)
    details.update(unique_fitting_positions=len(positions),positive_labels=int(labels.sum()),
        negative_labels=int(len(labels)-labels.sum()),positions_shared_with_area=int(len(np.intersect1d(positions,area))),
        oracle_object_frame_used=policy in ['object','object_mmu','object_region','weighted_area','weighted_area_cap10','area_regionmatched','area_corematched'],
        supplied_class_candidate_pool=True,created_at_utc=now())
    sub_mmu=0;represented=set()
    for k in train:
        ids=positions[positions//PIXELS==k]%PIXELS
        local=data.small[k]['objects'][ids]
        for o in data.metadata[k]['objects']:
            count=int(np.sum(local==o['object_id']))
            if count:represented.add((k,o['object_id']))
            if o['vector_area_m2']<2000:sub_mmu+=count
    details.update(sub_mmu_positive_fitting_positions=sub_mmu,represented_local_components=len(represented))
    atomic_npz(path,positions=positions,labels=labels,initial_positions=initial if policy.startswith(('proposal','uncertainty')) else np.array([],dtype=np.int64))
    details['sample_path']=str(path.relative_to(ROOT));details['sample_sha256']=sha(path)
    meta_path.write_text(json.dumps(details,indent=2)+'\n')
    return positions,details

def inverse_object_weights(data,train,positions,cap=None):
    groups=data.object_groups(train);keys=np.concatenate(groups)
    sizes=np.concatenate([np.full(len(g),len(g),dtype=np.int64) for g in groups])
    order=np.argsort(keys);keys=keys[order];sizes=sizes[order]
    positive=data.labels(positions)==1;selected=positions[positive];index=np.searchsorted(keys,selected)
    if np.any(index>=len(keys)) or not np.array_equal(keys[index],selected):raise RuntimeError('Positive position missing from training object frame')
    values=1/sizes[index].astype(np.float64);values/=values.mean()
    if cap is not None:values=np.minimum(values,cap);values/=values.mean()
    weights=np.ones(len(positions),dtype=np.float64);weights[positive]=values
    info=dict(rule='inverse number of common-valid training component pixels; positive mean normalized to one',
        truncation_before_final_renormalization=cap,positive_effective_sample_size=float(values.sum()**2/np.sum(values**2)),
        minimum_positive_weight=float(values.min()),maximum_positive_weight=float(values.max()),
        positive_weight_sum=float(values.sum()),negative_weight_sum=float(weights[~positive].sum()))
    return weights,info

def fit_one(data,manifest,train,validation,test,scope,budget,seed,policy,representation,decoder,outdir):
    key=f'{scope}_{decoder}_{representation}_{policy}_n{budget}_s{seed}'
    meta_path=outdir/'fits'/(key+'.json');pred_path=outdir/'predictions'/(key+'.npz')
    if meta_path.exists() and pred_path.exists():
        previous=json.loads(meta_path.read_text())
        if previous['manifest_sha256']!=sha(manifest) or previous['prediction_sha256']!=sha(pred_path):
            raise RuntimeError('Existing fit inputs/output hashes differ; preserve and investigate: '+key)
        print(key,'already completed',flush=True);return False
    started=now();tick=time.monotonic()
    positions,sampling=choose_sample(data,train,budget,seed,policy,outdir/'samples'/scope)
    x=data.sample_values(positions,representation);y=data.labels(positions)
    weighted=policy in ['weighted_area','weighted_area_cap10']
    if weighted and decoder!='rf_noboot':raise ValueError('Weighted exploratory policies require the declared no-bootstrap decoder')
    weights=None;weight_info=None
    if weighted:
        weights,weight_info=inverse_object_weights(data,train,positions,cap=10 if policy=='weighted_area_cap10' else None)
        weight_path=outdir/'weights'/(key+'.npz');atomic_npz(weight_path,positions=positions,weights=weights)
        weight_info.update(path=str(weight_path.relative_to(ROOT)),sha256=sha(weight_path))
    if decoder in ['rf','rf_noboot']:
        model=RandomForestClassifier(n_estimators=300,max_features='sqrt',min_samples_leaf=5,
                                    class_weight='balanced',random_state=seed,n_jobs=2,bootstrap=decoder=='rf')
    elif decoder=='logit':
        model=make_pipeline(StandardScaler(),LogisticRegression(C=1,class_weight='balanced',max_iter=2000,random_state=seed))
    else:raise ValueError('Unknown declared decoder: '+decoder)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        if weights is None:model.fit(x,y)
        else:model.fit(x,y,sample_weight=weights)
        evaluation=validation+test
        probabilities=[predict_core(model,data,k,representation) for k in evaluation]
    atomic_npz(pred_path,core_ids=np.array([data.ids[k] for k in evaluation]),
        splits=np.array(['validation']*len(validation)+['test']*len(test)),probability=np.stack(probabilities))
    metadata=dict(fit_id=key,scope=scope,decoder=decoder,representation=representation,policy=policy,
        budget=budget,seed=seed,started_at_utc=started,ended_at_utc=now(),elapsed_seconds=time.monotonic()-tick,
        experiment_id=os.environ.get('RESEARCH_EXPERIMENT_ID'),train_core_ids=[data.ids[k] for k in train],
        validation_core_ids=[data.ids[k] for k in validation],test_core_ids=[data.ids[k] for k in test],
        manifest_path=str(manifest.relative_to(ROOT)),manifest_sha256=sha(manifest),sampling=sampling,
        model_parameters={k:str(v) for k,v in model.get_params().items()},feature_count=x.shape[1],
        classifier_class=type(model).__name__,sample_weight=weight_info,
        prediction_path=str(pred_path.relative_to(ROOT)),prediction_sha256=sha(pred_path),
        warnings=[dict(type=type(w.message).__name__,message=str(w.message)) for w in caught],
        status='complete',test_labels_used_for_fitting=False)
    meta_path.parent.mkdir(parents=True,exist_ok=True)
    if scope.startswith('rotation'):
        split_file=ROOT/'protocol/rotation-splits.json'
        metadata['split_specification']=dict(path=str(split_file.relative_to(ROOT)),sha256=sha(split_file),split_name=scope)
    meta_path.write_text(json.dumps(metadata,indent=2)+'\n')
    print(key,'COMPLETE',round(metadata['elapsed_seconds'],2),'seconds',flush=True)
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',default='data/derived/dataset-manifest.json')
    p.add_argument('--budget',type=int,default=2000);p.add_argument('--seeds',type=int,nargs='+',default=[101])
    p.add_argument('--policies',nargs='+',default=POLICIES);p.add_argument('--representations',nargs='+',default=['aef','optical','optical_context'])
    p.add_argument('--decoders',nargs='+',default=['rf']);p.add_argument('--holdout-region')
    p.add_argument('--split-file');p.add_argument('--split-name')
    p.add_argument('--max-new-fits',type=int);p.add_argument('--time-budget',type=int,default=1500)
    p.add_argument('--storage-stop-gib',type=float,default=9)
    p.add_argument('--out',default='data/results');a=p.parse_args()
    manifest=ROOT/a.manifest;data=Dataset(manifest);outdir=ROOT/a.out
    if bool(a.split_file)!=bool(a.split_name):raise ValueError('Supply both split file and split name')
    if a.split_file:
        if a.holdout_region:raise ValueError('Custom split and geographic holdout are distinct conditions')
        split_path=ROOT/a.split_file;spec=json.loads(split_path.read_text())
        roles=spec['splits'][a.split_name]
        if set(roles)!=set(data.ids) or set(roles.values())!={'train','validation','test'}:
            raise ValueError('Custom split must assign every frozen core exactly once')
        for region in sorted(set(e['region_id'] for e in data.entries)):
            for role,n in [('train',8),('validation',4),('test',4)]:
                assert sum(e['region_id']==region and roles[e['core_id']]==role for e in data.entries)==n
        scope=a.split_name
        train=[k for k,e in enumerate(data.entries) if roles[e['core_id']]=='train']
        validation=[k for k,e in enumerate(data.entries) if roles[e['core_id']]=='validation']
        test=[k for k,e in enumerate(data.entries) if roles[e['core_id']]=='test']
    elif a.holdout_region:
        scope='leave_'+a.holdout_region
        train=[k for k,e in enumerate(data.entries) if e['region_id']!=a.holdout_region and e['split']=='train']
        validation=[k for k,e in enumerate(data.entries) if e['region_id']!=a.holdout_region and e['split']=='validation']
        test=[k for k,e in enumerate(data.entries) if e['region_id']==a.holdout_region]
    else:
        scope='within'
        train=[k for k,e in enumerate(data.entries) if e['split']=='train']
        validation=[k for k,e in enumerate(data.entries) if e['split']=='validation']
        test=[k for k,e in enumerate(data.entries) if e['split']=='test']
    tick=time.monotonic();new_fits=0
    with threadpool_limits(limits=2):
        for seed in a.seeds:
            for policy in a.policies:
                for representation in a.representations:
                    for decoder in a.decoders:
                        if time.monotonic()-tick>=a.time_budget or (a.max_new_fits is not None and new_fits>=a.max_new_fits):
                            print('BATCH STOP at complete-fit boundary;',new_fits,'new fits; unfinished requested arms may remain',flush=True)
                            return
                        size=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink())
                        if size>=a.storage_stop_gib*1024**3:
                            print('STORAGE STOP at complete-fit boundary;',size,'bytes; unfinished arms remain',flush=True)
                            return
                        new_fits+=int(fit_one(data,manifest,train,validation,test,scope,a.budget,seed,policy,representation,decoder,outdir))

if __name__=='__main__':main()
