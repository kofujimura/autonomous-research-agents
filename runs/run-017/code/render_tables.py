"""Generate manuscript tables/numeric substitutions from analysis, without rounding twice."""
import argparse
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd
from records import ROOT
from labels import LABELS,REPS
REGION_LABELS={'R01':'Prairie Pothole watersheds','R02':'Vermont basins','R03':'Lake Ontario basins','R04':'Wisconsin project'}

def number(value,digits=1,scale=1):
    if value is None or not np.isfinite(value):return 'undefined'
    return f'{value*scale:.{digits}f}'

def markdown(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',
        *['| '+' | '.join(map(str,row))+' |' for row in rows]])

def main():
    p=argparse.ArgumentParser();p.add_argument('--analysis',default='analysis');p.add_argument('--out',default='analysis/tables')
    p.add_argument('--template',default='paper-template.md');p.add_argument('--paper-out')
    p.add_argument('--alignment',default='data/alignment-stress')
    p.add_argument('--threshold-bootstrap',default='data/threshold-bootstrap');a=p.parse_args()
    analysis=ROOT/a.analysis;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    scores=pd.read_csv(analysis/'scores.csv');regional=pd.read_csv(analysis/'regional-scores.csv')
    inventory=pd.read_csv(analysis/'inventory-summary.csv');fits=pd.read_csv(analysis/'fits.csv')
    summary=json.loads((analysis/'summary.json').read_text())
    core=scores[(scores.scope=='within')&(scores.decoder=='rf')&(scores.budget==2000)&
        (scores.version=='raw')&(scores.boundary_tolerance_m==0)]
    primary=core[core.condition=='standardized_0.05']
    primary_policies=['area','interior','object','proposal','uncertainty']
    representations=['aef','optical','optical_context']
    def cell(policy,rep,column='small_macro_recovery_50',condition=primary):
        values=condition[(condition.policy==policy)&(condition.representation==rep)][column]
        if len(values)!=5:return f'incomplete ({len(values)}/5)'
        return number(values.mean(),scale=100) if values.notna().all() else 'undefined'
    table=markdown(['Allocation','Annual embeddings (%)','Seasonal optical (%)','Optical + context (%)'],
        [[LABELS[policy],*[cell(policy,rep) for rep in representations]] for policy in primary_policies])
    (out/'primary.md').write_text(table+'\n')
    contrasts=[]
    for key,label in [('H1_interaction','Representation × oracle-allocation interaction'),
        ('aef_oracle_gain','Oracle allocation minus area, embeddings'),('optical_oracle_gain','Oracle allocation minus area, optical'),
        ('aef_proposal_gain','Image proposals minus area, embeddings'),('optical_proposal_gain','Image proposals minus area, optical'),
        ('aef_proposal_vs_uncertainty','Proposals minus uncertainty, embeddings'),('optical_proposal_vs_uncertainty','Proposals minus uncertainty, optical')]:
        row=summary['primary_contrasts'].get(key,{})
        if row.get('status')!='complete':
            state=row.get('status','incomplete');contrasts.append([label,state,state]);continue
        lo,hi=row['conditional_block_bootstrap_95_percent_interval']
        contrasts.append([label,number(row['estimate'],scale=100),
            '['+number(lo,scale=100)+', '+number(hi,scale=100)+']'])
    contrast_table=markdown(['Comparison','Difference (pp)','Conditional 95% interval (pp)'],contrasts)
    (out/'contrasts.md').write_text(contrast_table+'\n')
    inv=inventory[inventory.split=='test']
    regional_primary=regional[(regional.scope=='within')&(regional.decoder=='rf')&(regional.budget==2000)&
        (regional.version=='raw')&(regional.condition=='standardized_0.05')&
        (regional.boundary_tolerance_m==0)&(regional.size_bin=='small')&(regional.coverage_target.astype(str)=='50')]
    reg_rows=[]
    reg_values={}
    for region in sorted(inv.region_id):
        n=int(inv[inv.region_id==region].eligible_small_patches.iloc[0]);row=[REGION_LABELS[region],n]
        for rep in ['aef','optical']:
            values={}
            for policy in ['area','object']:
                part=regional_primary[(regional_primary.region_id==region)&(regional_primary.representation==rep)&(regional_primary.policy==policy)]
                values[policy]=part.recovery.mean() if len(part)==5 else np.nan
                row.append(number(values[policy],scale=100))
            reg_values[region,rep]=values['object']-values['area']
        row.append(number(reg_values[region,'aef']-reg_values[region,'optical'],scale=100));reg_rows.append(row)
    reg_table=markdown(['Reference project','Small test patches','Embedding area (%)','Embedding oracle (%)','Optical area (%)','Optical oracle (%)','Interaction (pp)'],reg_rows)
    (out/'regions.md').write_text(reg_table+'\n')
    fpr_rows=[]
    for region in sorted(inv.region_id):
        row=[REGION_LABELS[region]]
        for rep,policy in [('aef','area'),('aef','object'),('optical','area'),('optical','object')]:
            part=regional_primary[(regional_primary.region_id==region)&(regional_primary.representation==rep)&(regional_primary.policy==policy)]
            row.append(number(part.upland_fpr.mean(),scale=100) if len(part)==5 else 'incomplete')
        fpr_rows.append(row)
    (out/'regional-fpr.md').write_text(markdown(['Project','Embedding area FPR (%)','Embedding oracle FPR (%)',
        'Optical area FPR (%)','Optical oracle FPR (%)'],fpr_rows)+'\n')
    deployment=core[core.condition=='validation_0.05']
    dep_rows=[]
    for policy in primary_policies:
        dep_rows.append([LABELS[policy],cell(policy,'aef',condition=deployment),
            cell(policy,'aef','upland_fpr',deployment),cell(policy,'optical',condition=deployment),
            cell(policy,'optical','upland_fpr',deployment)])
    dep_table=markdown(['Allocation','Embedding recovery (%)','Embedding test FPR (%)','Optical recovery (%)','Optical test FPR (%)'],dep_rows)
    (out/'threshold-replay.md').write_text(dep_table+'\n')
    extra_policies=['object_mmu','proposal_classmatched','uncertainty_classmatched','natural_area','area_region','object_region']
    extra_table=markdown(['Additional allocation control','Annual embeddings (%)','Seasonal optical (%)'],
        [[LABELS[policy],cell(policy,'aef'),cell(policy,'optical')] for policy in extra_policies])
    (out/'additional-controls.md').write_text(extra_table+'\n')
    input_table=markdown(['Project','Train cores','Validation cores','Test cores','Eligible small test patches','Small test patches without 20 m interior'],
        [[REGION_LABELS[region],*[int(inventory[(inventory.region_id==region)&(inventory.split==split)].cores.sum()) for split in ['train','validation','test']],
          int(inv[inv.region_id==region].eligible_small_patches.iloc[0]),int(inv[inv.region_id==region].eligible_small_no_20m_interior.iloc[0])]
          for region in sorted(inv.region_id)])
    (out/'inputs.md').write_text(input_table+'\n')
    values=dict(core_count=int(inventory.cores.sum()),small_test_count=int(inv.eligible_small_patches.sum()),
        test_small_no_interior=int(inv.eligible_small_no_20m_interior.sum()),fit_count=len(fits),
        primary_fit_count=75-summary['missing_primary_arms'],
        macro_interaction_without_R02_pp=number(np.mean([reg_values[r,'aef']-reg_values[r,'optical'] for r in sorted(inv.region_id) if r!='R02']),scale=100))
    for key,value in summary['primary_contrasts'].items():
        if value.get('status')=='complete':
            values[key+'_pp']=number(value['estimate'],scale=100)
            values[key+'_ci_pp']='['+', '.join(number(x,scale=100) for x in value['conditional_block_bootstrap_95_percent_interval'])+']'
    (out/'paper-values.json').write_text(json.dumps(values,indent=2)+'\n')
    from manuscript_sections import sections
    section_fields=sections(ROOT,analysis,scores,summary,values,number,markdown,REGION_LABELS,
        tables_out=out,alignment=ROOT/a.alignment,threshold_directory=ROOT/a.threshold_bootstrap)
    if a.paper_out:
        text=(ROOT/a.template).read_text()
        replacements={**{k:str(v) for k,v in values.items()},'TABLE_INPUTS':input_table,'TABLE_PRIMARY':table,
            'TABLE_CONTRASTS':contrast_table,'TABLE_REGIONS':reg_table,'TABLE_DEPLOYMENT':dep_table,'TABLE_EXTRA':extra_table,
            'TABLE_REGIONAL_FPR':(out/'regional-fpr.md').read_text(),
            **section_fields}
        for _ in range(6):
            previous=text
            for key,value in replacements.items():text=text.replace('{{'+key+'}}',value)
            if text==previous:break
        unresolved=sorted(set(re.findall(r'\{\{([^}]+)\}\}',text)))
        if unresolved:raise RuntimeError('Unresolved manuscript fields: '+', '.join(unresolved))
        (ROOT/a.paper_out).write_text(text)
    print(json.dumps(values,indent=2))

if __name__=='__main__':main()
