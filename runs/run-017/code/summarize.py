"""Regenerate descriptive tables and paired block-bootstrap contrasts offline."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from records import ROOT, now

KEYS=['fit_id','scope','decoder','representation','policy','budget','seed']

def divide(a,b):return float(a/b) if b else None

def load_evaluations(evaluation_root):
    cores=[];objects=[];fits=[];thresholds=[]
    for path in sorted(evaluation_root.glob('*/evaluation.json')):
        e=json.loads(path.read_text());m=json.loads((ROOT/e['fit_metadata_path']).read_text())
        tags={k:m[k] for k in KEYS}
        fits.append(dict(**tags,**{k:m['sampling'].get(k) for k in [
            'positive_labels','negative_labels','initial_labels','fallback_labels','oracle_training_objects',
            'sub_mmu_positive_fitting_positions','represented_local_components',
            'proposal_frame_eligible_training_patches','proposal_frame_missed_training_patches']},
            fitting_elapsed_seconds=m['elapsed_seconds'],feature_count=m['feature_count'],
            warnings=len(m['warnings']),prediction_sha256=m['prediction_sha256'],
            sample_sha256=m['sampling']['sample_sha256']))
        if m.get('sample_weight'):
            for key,value in m['sample_weight'].items():fits[-1]['weight_'+key]=value
        for collection,name in [(cores,'cores.csv'),(objects,'objects.csv'),(thresholds,'thresholds.csv')]:
            frame=pd.read_csv(path.parent/name)
            for k,v in tags.items():frame[k]=v
            collection.append(frame)
    if not fits:raise RuntimeError('No completed evaluations')
    return pd.concat(cores,ignore_index=True),pd.concat(objects,ignore_index=True),pd.DataFrame(fits),pd.concat(thresholds,ignore_index=True)

def describe(cores,objects):
    levels=KEYS+['version','condition','boundary_tolerance_m']
    rows=[];regions=[];blocks=[]
    object_indices=objects.groupby(levels,dropna=False,sort=False).indices
    for key,group in cores.groupby(levels,dropna=False,sort=True):
        tags=dict(zip(levels,key));selected=objects.iloc[object_indices.get(key,[])]
        sums=group[['tp','fp','fn','tn']].sum()
        row=dict(**tags,**{k:int(v) for k,v in sums.items()},
            upland_fpr=divide(sums.fp,sums.fp+sums.tn),producer_accuracy=divide(sums.tp,sums.tp+sums.fn),
            user_accuracy=divide(sums.tp,sums.tp+sums.fp),iou=divide(sums.tp,sums.tp+sums.fp+sums.fn),
            balanced_accuracy=.5*(divide(sums.tp,sums.tp+sums.fn)+divide(sums.tn,sums.tn+sums.fp))
                if sums.tp+sums.fn and sums.tn+sums.fp else None,
            all_positive_cores=int(group.get('all_positive',pd.Series(dtype=float)).fillna(False).sum()),
            all_negative_cores=int(group.get('all_negative',pd.Series(dtype=float)).fillna(False).sum()),
            empty_scoring_cores=int(group.get('reference_scoring_empty',pd.Series(dtype=float)).fillna(False).sum()),
            core_count=len(group))
        # These arrays replace repeated small DataFrame filters and repeated
        # regional confusion sums. Definitions, counts and averaging order stay fixed.
        size_array=selected.size_bin.to_numpy();region_array=selected.region_id.to_numpy()
        core_array=selected.core_id.to_numpy();scored=selected.scored_pixels.to_numpy()
        recovered={suffix:selected['recovered_'+suffix].to_numpy(dtype=float) for suffix in ['any','50','75']}
        region_ids=sorted(group.region_id.unique())
        group_regions=group.region_id.to_numpy();pixel_counts=group[['tp','fp','fn','tn']].to_numpy()
        regional_pixels={r:pixel_counts[group_regions==r].sum(axis=0) for r in region_ids}
        size_masks={size:size_array==size for size in ['small','medium','large']}
        region_masks={r:region_array==r for r in region_ids}
        for size,mask in size_masks.items():
            row[size+'_patch_count']=int(mask.sum())
            row[size+'_zero_scored_pixels']=int(np.sum(mask&(scored==0)))
            for suffix in ['any','50','75']:
                values=[]
                for region in region_ids:
                    keep=mask&region_masks[region];outcomes=recovered[suffix][keep]
                    finite=np.isfinite(outcomes)
                    value=float(np.mean(outcomes[finite])) if finite.any() else np.nan
                    values.append(value);tp,fp,fn,tn=regional_pixels[region]
                    regions.append(dict(**tags,region_id=region,size_bin=size,coverage_target=suffix,
                        patch_count=int(keep.sum()),scored_patch_count=int(finite.sum()),
                        recovered_patches=int(np.nansum(outcomes)),recovery=value,
                        reference_upland_pixels=int(fp+tn),false_positive_pixels=int(fp),
                        upland_fpr=divide(fp,fp+tn)))
                row[f'{size}_macro_recovery_{suffix}']=float(np.mean(values)) if np.all(np.isfinite(values)) else None
                row[f'{size}_undefined_regions_{suffix}']=int(np.sum(~np.isfinite(values)))
        selected_core_ids=sorted(set(core_array))
        for cid in selected_core_ids:
            core_mask=core_array==cid;region=region_array[np.flatnonzero(core_mask)[0]]
            for size,mask in size_masks.items():
                outcomes=recovered['50'][core_mask&mask]
                blocks.append(dict(**tags,core_id=cid,region_id=region,size_bin=size,
                    n=int(np.isfinite(outcomes).sum()),recovered=int(np.nansum(outcomes))))
        for cid in sorted(set(group.core_id)-set(selected_core_ids)):
            region=group[group.core_id==cid].region_id.iloc[0]
            for size in ['small','medium','large']:
                blocks.append(dict(**tags,core_id=cid,region_id=region,size_bin=size,n=0,recovered=0))
        if 'edge_disagreements' in group and group.edge_neighbor_pairs.sum()>0:
            row['edge_disagreement_fraction']=float(group.edge_disagreements.sum()/group.edge_neighbor_pairs.sum())
        rows.append(row)
    return pd.DataFrame(rows),pd.DataFrame(regions),pd.DataFrame(blocks)

def strata_scores(objects):
    selected=objects[(objects.version=='raw')&(objects.condition=='standardized_0.05')&
        (objects.boundary_tolerance_m==0)&(objects.size_bin=='small')].copy()
    rows=[]
    definitions={
        'all_small':lambda d:np.ones(len(d),dtype=bool),
        'valid_fraction_ge_90_percent':lambda d:d.valid_fraction>=.9,
        'isolated_ge_50m':lambda d:d.isolated_50m.astype(bool),
        'nonisolated_lt_50m':lambda d:~d.isolated_50m.astype(bool),
        'has_20m_interior':lambda d:d.interior_pixels>0,
        'no_20m_interior':lambda d:d.interior_pixels==0,
        'contains_forested_code':lambda d:d.habitat_codes.str.contains('PFO',regex=False),
        'contains_emergent_code':lambda d:d.habitat_codes.str.contains('PEM',regex=False),
        'contains_scrub_shrub_code':lambda d:d.habitat_codes.str.contains('PSS',regex=False)}
    for key,group in selected.groupby(KEYS,sort=True):
        tags=dict(zip(KEYS,key))
        for name,select in definitions.items():
            subset=group[select(group)]
            for region in sorted(group.region_id.unique()):
                part=subset[subset.region_id==region]
                rows.append(dict(**tags,stratum=name,region_id=region,patch_count=len(part),
                    recovered_patches=int(part.recovered_50.sum()),recovery=part.recovered_50.mean()))
    return pd.DataFrame(rows)

def primary_bootstrap(blocks,replicates=2000,seed=20261027,condition='standardized_0.05',scope='within',decoder='rf',budget=2000):
    b=blocks[(blocks.scope==scope)&(blocks.decoder==decoder)&(blocks.budget==budget)&
        (blocks.version=='raw')&(blocks.condition==condition)&
        (blocks.boundary_tolerance_m==0)&(blocks.size_bin=='small')]
    seeds=[101,202,303,404,505];regions=sorted(b.region_id.unique())
    contrasts={
        'H1_interaction':[('aef','object',1),('aef','area',-1),('optical','object',-1),('optical','area',1)],
        'regional_allocation_interaction':[('aef','object_region',1),('aef','area_region',-1),('optical','object_region',-1),('optical','area_region',1)],
        'aef_oracle_gain':[('aef','object',1),('aef','area',-1)],
        'optical_oracle_gain':[('optical','object',1),('optical','area',-1)],
        'aef_proposal_gain':[('aef','proposal',1),('aef','area',-1)],
        'optical_proposal_gain':[('optical','proposal',1),('optical','area',-1)],
        'aef_proposal_vs_uncertainty':[('aef','proposal',1),('aef','uncertainty',-1)],
        'optical_proposal_vs_uncertainty':[('optical','proposal',1),('optical','uncertainty',-1)],
        'aef_mmu_frame_change':[('aef','object_mmu',1),('aef','object',-1)],
        'optical_mmu_frame_change':[('optical','object_mmu',1),('optical','object',-1)]}
    for representation in ['aef','optical']:
        for policy in ['proposal','uncertainty']:
            contrasts[representation+'_'+policy+'_vs_classmatched']=[(representation,policy,1),
                (representation,policy+'_classmatched',-1)]
        contrasts[representation+'_natural_vs_balanced']=[(representation,'natural_area',1),(representation,'area',-1)]
        for policy in ['weighted_area','weighted_area_cap10','proposal_aef','uncertainty_aef']:
            contrasts[representation+'_'+policy+'_gain']=[(representation,policy,1),(representation,'area',-1)]
        for policy in ['area_regionmatched','area_corematched']:
            contrasts[representation+'_'+policy+'_gain']=[(representation,policy,1),(representation,'area',-1)]
            contrasts[representation+'_'+policy+'_vs_oracle']=[(representation,policy,1),(representation,'object',-1)]
        for policy in ['weighted_area','weighted_area_cap10']:
            contrasts[representation+'_'+policy+'_vs_oracle']=[(representation,policy,1),(representation,'object',-1)]
        for policy in ['proposal_aef','uncertainty_aef']:
            contrasts[representation+'_'+policy+'_vs_classmatched']=[(representation,policy,1),(representation,policy+'_classmatched',-1)]
        for policy in ['proposal_uniform_aef','uncertainty_uniform_aef']:
            contrasts[representation+'_'+policy+'_vs_natural']=[(representation,policy,1),(representation,'natural_area',-1)]
    for policy in ['area_regionmatched','area_corematched']:
        contrasts['oracle_vs_'+policy+'_interaction']=[('aef','object',1),('aef',policy,-1),
            ('optical','object',-1),('optical',policy,1)]
    result={};rng=np.random.default_rng(seed)
    # Shared draws ensure pairing across policies/representations, including zero-object cores.
    seed_draw=rng.integers(0,len(seeds),size=(replicates,len(seeds)))
    core_ids={r:sorted(b[b.region_id==r].core_id.unique()) for r in regions}
    core_draw={r:rng.integers(0,len(ids),size=(replicates,len(ids))) for r,ids in core_ids.items()}
    arm_values={};arm_points={}
    for rep,policy in sorted(set((x[0],x[1]) for terms in contrasts.values() for x in terms)):
        part=b[(b.representation==rep)&(b.policy==policy)]
        if set(part.seed)!=set(seeds):continue
        regional=[];points=[]
        for r,ids in core_ids.items():
            numerator=np.zeros((len(seeds),len(ids)));denominator=numerator.copy()
            for si,s in enumerate(seeds):
                for ci,cid in enumerate(ids):
                    cell=part[(part.seed==s)&(part.core_id==cid)]
                    if len(cell)!=1:raise RuntimeError('Missing/duplicate paired block')
                    numerator[si,ci]=cell.recovered.iloc[0];denominator[si,ci]=cell.n.iloc[0]
            with np.errstate(invalid='ignore',divide='ignore'):
                points.append(np.mean(np.sum(numerator,axis=1)/np.sum(denominator,axis=1)))
            draws=core_draw[r]
            num=numerator[seed_draw[:,:,None],draws[:,None,:]].sum(axis=2)
            den=denominator[seed_draw[:,:,None],draws[:,None,:]].sum(axis=2)
            with np.errstate(invalid='ignore',divide='ignore'):regional.append(np.mean(num/den,axis=1))
        arm_values[rep,policy]=np.mean(regional,axis=0);arm_points[rep,policy]=float(np.mean(points))
    for name,terms in contrasts.items():
        if not all((r,p) in arm_values for r,p,w in terms):
            result[name]=dict(status='incomplete',reason='All five seeds not yet evaluated for every arm');continue
        values=sum(w*arm_values[r,p] for r,p,w in terms)
        point=sum(w*arm_points[r,p] for r,p,w in terms)
        finite=np.isfinite(values)
        result[name]=dict(status='complete' if np.isfinite(point) else 'undefined',estimate=point if np.isfinite(point) else None,
            conditional_block_bootstrap_95_percent_interval=np.quantile(values[finite],[.025,.975]).tolist() if finite.any() else None,
            undefined_replicates=int(np.sum(~finite)),replicates=replicates,
            interpretation=f'Conditional on evaluated thresholds and reference maps; {len(regions)} convenience regions fixed; paired cores within region and shared training-seed resampling')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--evaluation',default='data/evaluation');p.add_argument('--out',default='analysis')
    p.add_argument('--bootstrap',type=int,default=2000);a=p.parse_args();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    tick=time.monotonic();cores,objects,fits,thresholds=load_evaluations(ROOT/a.evaluation)
    print('Loaded',len(fits),'fits;',len(objects),'object-condition rows;',round(time.monotonic()-tick,3),'seconds',flush=True)
    scores,regions,blocks=describe(cores,objects)
    print('Described all conditions;',round(time.monotonic()-tick,3),'seconds',flush=True)
    strata=strata_scores(objects)
    print('Strata complete;',round(time.monotonic()-tick,3),'seconds',flush=True)
    for name,frame in [('scores',scores),('regional-scores',regions),('bootstrap-blocks',blocks),('fits',fits),('thresholds',thresholds),('strata-scores',strata)]:
        frame.to_csv(out/(name+'.csv'),index=False,float_format='%.17g')
    contrasts=primary_bootstrap(blocks,a.bootstrap)
    secondary=[]
    for (scope,decoder,budget),part in fits.groupby(['scope','decoder','budget'],sort=True):
        if scope=='within' and decoder=='rf' and budget==2000:continue
        secondary.append(dict(scope=scope,decoder=decoder,budget=int(budget),
            contrasts=primary_bootstrap(blocks,a.bootstrap,scope=scope,decoder=decoder,budget=int(budget))))
    summary=dict(generated_at_utc=now(),fit_count=len(fits),primary_contrasts=contrasts,
        region_standardized_contrasts=primary_bootstrap(blocks,a.bootstrap,condition='regional_0.05'),
        secondary_condition_contrasts=secondary,
        missing_primary_arms=75-int(np.sum((fits.scope=='within')&(fits.budget==2000)&(fits.decoder=='rf')&
            fits.policy.isin(['area','interior','object','proposal','uncertainty'])&fits.representation.isin(['aef','optical','optical_context']))),
        bootstrap_replicates=a.bootstrap)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
