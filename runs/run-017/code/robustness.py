"""Exploratory fixed-split rotation and cohort-matched transfer summaries."""
import argparse
import json
import numpy as np
import pandas as pd
from records import ROOT,now
from summarize import primary_bootstrap

SEEDS=[101,202,303,404,505]

def arm_means(blocks,condition,scope):
    part=blocks[(blocks.scope==scope)&(blocks.condition==condition)&
        (blocks.version=='raw')&(blocks.boundary_tolerance_m==0)&(blocks.size_bin=='small')]
    rows=[]
    for (rep,policy),group in part.groupby(['representation','policy'],sort=True):
        regional=group.groupby(['seed','region_id'])[['n','recovered']].sum()
        recovery=(regional.recovered/regional.n).unstack('region_id')
        rows.append(dict(representation=rep,policy=policy,scope=scope,condition=condition,
            estimate=float(recovery.mean(axis=1).mean()) if recovery.notna().all().all() else None,
            patches_per_seed=int(group[group.seed==SEEDS[0]].n.sum()),
            test_cores_per_seed=int(group[group.seed==SEEDS[0]].core_id.nunique())))
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--analysis',default='analysis')
    p.add_argument('--out',default='analysis/robustness');p.add_argument('--evaluation',default='data/evaluation');a=p.parse_args()
    blocks=pd.read_csv(ROOT/a.analysis/'bootstrap-blocks.csv')
    fits=pd.read_csv(ROOT/a.analysis/'fits.csv')
    base=blocks[(blocks.decoder=='rf')&(blocks.budget==2000)&
        blocks.policy.isin(['area','object'])&blocks.representation.isin(['aef','optical'])].copy()
    manifest=json.loads((ROOT/'data/derived/dataset-manifest.json').read_text())
    original_test={e['core_id'] for e in manifest['cores'] if e['split']=='test'}
    families={
        'rotations_all':(['within','rotation1','rotation2','rotation3'],False),
        'geographic_all':(['leave_R01','leave_R02','leave_R03','leave_R04'],False),
        'geographic_original_test':(['leave_R01','leave_R02','leave_R03','leave_R04'],True)}
    result={};tables=[]
    for name,(scopes,restrict) in families.items():
        selected_fits=fits[(fits.decoder=='rf')&(fits.budget==2000)&fits.scope.isin(scopes)&
            fits.policy.isin(['area','object'])&fits.representation.isin(['aef','optical'])]
        expected=20*len(scopes)
        if len(selected_fits)!=expected:
            result[name]=dict(status='incomplete',fits_present=len(selected_fits),fits_required=expected)
            continue
        selected=base[base.scope.isin(scopes)].copy()
        if restrict:selected=selected[selected.core_id.isin(original_test)].copy()
        selected['scope']=name
        check=selected[(selected.version=='raw')&(selected.condition=='standardized_0.05')&
            (selected.boundary_tolerance_m==0)&(selected.size_bin=='small')]
        assert not check.duplicated(['seed','representation','policy','core_id']).any()
        target_cores=16 if restrict else 64
        for _,part in check.groupby(['seed','representation','policy']):
            assert part.core_id.nunique()==target_cores
        conditions={}
        pixel_frames=[]
        for _,fit in selected_fits.iterrows():
            pixel=pd.read_csv(ROOT/a.evaluation/fit.fit_id/'cores.csv')
            pixel=pixel[(pixel.version=='raw')&(pixel.boundary_tolerance_m==0)]
            if restrict:pixel=pixel[pixel.core_id.isin(original_test)]
            for key in ['seed','representation','policy']:pixel[key]=fit[key]
            pixel_frames.append(pixel)
        pixels=pd.concat(pixel_frames,ignore_index=True)
        for condition in ['standardized_0.05','regional_0.05','validation_0.05']:
            conditions[condition]=primary_bootstrap(selected,scope=name,condition=condition)
            rows=arm_means(selected,condition,name)
            for row in rows:
                part=pixels[(pixels.condition==condition)&(pixels.representation==row['representation'])&(pixels.policy==row['policy'])]
                totals=part.groupby('seed')[['fp','tn']].sum()
                fpr=totals.fp/(totals.fp+totals.tn)
                row['mean_achieved_upland_fpr']=float(fpr.mean())
                row['minimum_seed_upland_fpr']=float(fpr.min());row['maximum_seed_upland_fpr']=float(fpr.max())
            tables.extend(rows)
        result[name]=dict(status='complete',test_cores=target_cores,
            original_thresholds_retained=True,conditional_contrasts=conditions,
            interpretation='Exploratory; same fixed inventory and regions; overlapping training sets; thresholds retained from each fitted scope. Matched-subgroup FPR need not equal nominal 5%.')
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(tables).to_csv(out/'arm-means.csv',index=False,float_format='%.17g')
    (out/'summary.json').write_text(json.dumps(dict(generated_at_utc=now(),families=result),indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v['status'] for k,v in result.items()}))

if __name__=='__main__':main()
