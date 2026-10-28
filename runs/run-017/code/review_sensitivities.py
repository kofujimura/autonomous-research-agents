"""Review-prompted complete reporting of saved, originally planned sensitivities."""
import argparse
import json
import numpy as np
import pandas as pd
from records import ROOT, now
from summarize import primary_bootstrap

ARMS=[('aef','area'),('aef','object'),('optical','area'),('optical','object')]
CONDITIONS=['standardized_0.01','standardized_0.05','standardized_0.1',
            'regional_0.05','validation_0.05','regional_validation_0.05']
NAMES={'standardized_0.01':'Pooled 1% FPR','standardized_0.05':'Pooled 5% FPR',
       'standardized_0.1':'Pooled 10% FPR','regional_0.05':'Regional 5% FPR',
       'validation_0.05':'Pooled validation replay','regional_validation_0.05':'Regional validation replay'}

def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',
        *['| '+' | '.join(map(str,row))+' |' for row in rows]])+'\n'

def fmt(v):return 'undefined' if v is None or not np.isfinite(v) else f'{v*100:.1f}'

def effect(estimate):
    text=fmt(estimate['estimate'])
    ci=estimate.get('conditional_block_bootstrap_95_percent_interval')
    return text+(' ['+', '.join(fmt(v) for v in ci)+']' if ci else ' (point only)')

def select(frame,scopes,condition):
    return frame[frame.scope.isin(scopes)&(frame.decoder=='rf')&(frame.budget==2000)&
        (frame.version=='raw')&(frame.boundary_tolerance_m==0)&(frame.condition==condition)&
        frame.policy.isin(['area','object'])&frame.representation.isin(['aef','optical'])].copy()

def arms(regional,scores,scopes,condition,coverage='50',size='small',exclude_region=None):
    region=select(regional,scopes,condition)
    region=region[(region.coverage_target.astype(str)==coverage)&(region.size_bin==size)]
    if exclude_region:region=region[region.region_id!=exclude_region]
    result={}
    for rep,policy in ARMS:
        group=region[(region.representation==rep)&(region.policy==policy)]
        counts=group.groupby(['seed','region_id'])[['recovered_patches','scored_patch_count']].sum()
        fractions=(counts.recovered_patches/counts.scored_patch_count).unstack('region_id')
        # Require every fixed region and seed to have an estimable fraction.
        recovery=float(fractions.mean(axis=1).mean()) if fractions.notna().all().all() else None
        pix=select(scores,scopes,condition)
        pix=pix[(pix.representation==rep)&(pix.policy==policy)]
        totals=pix.groupby('seed')[['fp','tn']].sum()
        fpr=totals.fp/(totals.fp+totals.tn)
        result[rep+'_'+policy]=dict(recovery=recovery,mean_fpr=float(fpr.mean()),
            minimum_seed_fpr=float(fpr.min()),maximum_seed_fpr=float(fpr.max()),
            patches_per_seed=int(counts.loc[101].scored_patch_count.sum()))
    return result

def point_contrasts(values):
    def diff(rep):
        a=values[rep+'_area']['recovery'];o=values[rep+'_object']['recovery']
        return None if a is None or o is None else o-a
    a=diff('aef');o=diff('optical')
    return {name:dict(estimate=value,conditional_block_bootstrap_95_percent_interval=None,
                     interpretation='Point estimate only; no coverage-specific bootstrap blocks')
        for name,value in [('aef_oracle_gain',a),('optical_oracle_gain',o),
                           ('H1_interaction',None if a is None or o is None else a-o)]}

def boot(blocks,scopes,condition,label):
    part=select(blocks,scopes,condition);part['scope']=label
    assert not part[part.size_bin=='small'].duplicated(['seed','region_id','core_id','representation','policy']).any()
    result=primary_bootstrap(part,scope=label,condition=condition)
    return {k:result[k] for k in ['aef_oracle_gain','optical_oracle_gain','H1_interaction']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--analysis',default='analysis')
    p.add_argument('--evaluation',default='data/evaluation');p.add_argument('--out',default='analysis/review-response');a=p.parse_args()
    analysis=ROOT/a.analysis;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    scores=pd.read_csv(analysis/'scores.csv');regional=pd.read_csv(analysis/'regional-scores.csv')
    blocks=pd.read_csv(analysis/'bootstrap-blocks.csv')
    families={'original':['within'],'four_splits':['within','rotation1','rotation2','rotation3']}
    sensitivity=[];rows=[]
    for family,scopes in families.items():
        for condition,coverage in [(c,'50') for c in CONDITIONS]+[('standardized_0.05','any'),('standardized_0.05','75')]:
            values=arms(regional,scores,scopes,condition,coverage)
            contrasts=boot(blocks,scopes,condition,family) if coverage=='50' else point_contrasts(values)
            for key,point in point_contrasts(values).items():
                assert np.isclose(contrasts[key]['estimate'],point['estimate'],rtol=0,atol=1e-12)
            sensitivity.append(dict(family=family,condition=condition,coverage=coverage,arms=values,contrasts=contrasts))
            row=[family,NAMES[condition]+('; any overlap' if coverage=='any' else '; ≥'+coverage+'% coverage')]
            row += [fmt(values[r+'_area']['recovery'])+'→'+fmt(values[r+'_object']['recovery']) for r in ['aef','optical']]
            row += [effect(contrasts[k]) for k in ['aef_oracle_gain','optical_oracle_gain','H1_interaction']]
            row += [str(contrasts['H1_interaction'].get('undefined_replicates','—'))];rows.append(row)
    (out/'definition-sensitivity.md').write_text(table(['Cohort','Definition','Embedding recovery (%)','Optical recovery (%)',
        'Embedding gain, pp [95%]','Optical gain, pp [95%]','Interaction, pp [95%]','Undefined / 2,000'],rows))
    transfer=[];trows=[];rotation=[];rrows=[]
    for scopes,label,target in [([f'leave_R{i:02d}'],f'R{i:02d}',transfer) for i in range(1,5)]+[
            ([f'leave_R{i:02d}' for i in range(1,5)],'All four projects',transfer)]+[
            ([s],s,rotation) for s in ['within','rotation1','rotation2','rotation3']]:
        condition='validation_0.05';values=arms(regional,scores,scopes,condition)
        contrasts=boot(blocks,scopes,condition,label)
        item=dict(label=label,arms=values,contrasts=contrasts);target.append(item)
        row=[label]+[fmt(values[r+'_'+policy]['recovery'])+' ('+fmt(values[r+'_'+policy]['mean_fpr'])+')' for r,policy in ARMS]
        row += [effect(contrasts[k]) for k in ['aef_oracle_gain','optical_oracle_gain','H1_interaction']]
        (trows if target is transfer else rrows).append(row)
    headers=['Held-out project / split','Embedding area (FPR)','Embedding oracle (FPR)','Optical area (FPR)','Optical oracle (FPR)',
        'Embedding gain, pp [95%]','Optical gain, pp [95%]','Interaction, pp [95%]']
    (out/'transfer-replay.md').write_text(table(headers,trows));(out/'rotation-replay.md').write_text(table(headers,rrows))
    regional_mean_fprs=[arm['mean_fpr'] for row in transfer[:4] for arm in row['arms'].values()]
    seed_fprs=[arm[k] for row in transfer[:4] for arm in row['arms'].values() for k in ['minimum_seed_fpr','maximum_seed_fpr']]
    additional={};srows=[]
    for family,scopes in families.items():
        for size in ['small','medium','large']:
            values=arms(regional,scores,scopes,'standardized_0.05',size=size)
            additional[family+'_'+size]=dict(arms=values,contrasts=point_contrasts(values))
            srows.append([family,size,values['aef_area']['patches_per_seed'],
                *[fmt(values[r+'_area']['recovery'])+'→'+fmt(values[r+'_object']['recovery']) for r in ['aef','optical']]])
    (out/'patch-size.md').write_text(table(['Cohort','Size bin','Patches','Embedding recovery (%)','Optical recovery (%)'],srows))
    without=arms(regional,scores,['within'],'standardized_0.05',exclude_region='R02')
    additional['without_vermont']=dict(arms=without,contrasts=point_contrasts(without))
    new=arms(regional,scores,['rotation1','rotation2','rotation3'],'standardized_0.05')
    additional['three_new_splits']=dict(arms=new,contrasts=point_contrasts(new))
    pixels=[];prows=[]
    for rep,policy in ARMS:
        frame=select(scores,['within'],'standardized_0.05')
        frame=frame[(frame.representation==rep)&(frame.policy==policy)]
        ap=[]
        for fit_id in frame.fit_id:
            evaluation=json.loads((ROOT/a.evaluation/fit_id/'evaluation.json').read_text())
            ap.append(next(r['average_precision'] for r in evaluation['pooled_scores'] if r['version']=='raw'))
        row=dict(representation=rep,policy=policy,balanced_accuracy=float(frame.balanced_accuracy.mean()),average_precision=float(np.mean(ap)))
        pixels.append(row);prows.append([rep,policy,fmt(row['balanced_accuracy']),fmt(row['average_precision'])])
    (out/'pixel-secondary.md').write_text(table(['Predictors','Allocation','Balanced accuracy (%)','Average precision (%)'],prows))
    result=dict(generated_at_utc=now(),plan='protocol/plan-v11.md',review_prompted=True,
        interpretation='Underlying definitions preplanned; expanded tabulation and intervals selected after REVIEW-1. Conditional on fixed models/maps/thresholds; not multiplicity-adjusted.',
        sensitivities=sensitivity,transfer_replay=transfer,rotation_replay=rotation,additional=additional,pixel_secondary=pixels,
        transfer_regional_mean_fpr_range=[min(regional_mean_fprs),max(regional_mean_fprs)],
        transfer_seed_fpr_range=[min(seed_fprs),max(seed_fprs)])
    (out/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(sensitivity_rows=len(sensitivity),transfer_rows=len(transfer),rotation_rows=len(rotation),
                         without_vermont=additional['without_vermont']['contrasts'],transfer_regional_mean_fpr_range=result['transfer_regional_mean_fpr_range'])))

if __name__=='__main__':main()
