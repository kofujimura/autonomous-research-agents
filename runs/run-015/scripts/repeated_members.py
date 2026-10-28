"""Conditional member-draw sensitivity; no network or model API."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import evaluate,TOL
from record import ROOT,now
from secondary import choose_cases,source_X
from summarize import clean,markdown_table


def selection(draw,date,model,lead):
    digest=hashlib.sha256(f'20261027|{draw}|{date}|{model}|{int(lead)}'.encode()).digest()
    seed=int.from_bytes(digest[:8],'big')
    return np.random.default_rng(seed).permutation(50),digest.hex()


def summarize(out):
    files=sorted(p/'cases.csv' for p in out.glob('chunk-*') if (p/'complete.json').exists());assert files
    frame=pd.concat([pd.read_csv(f,dtype={'date':str}) for f in files],ignore_index=True)
    assert not frame.duplicated(['draw','case_key','member_count']).any()
    draws=sorted(frame['draw'].unique().tolist());assert set(draws)<=set(range(100))
    per_draw=[]
    for draw,part in frame.groupby('draw',sort=True):
        flags=part.pivot(index='case_key',columns='member_count',values='informative')
        assert list(flags)==[10,25,50] and len(flags)==120 and flags.notna().all().all()
        common=set(flags.index[(flags==1).all(axis=1)])
        for stratum in ['fixed_M50_informative','common_informative']:
            selected=part if stratum=='fixed_M50_informative' else part[part['case_key'].isin(common)]
            by_size={M:selected[selected['member_count']==M].set_index('case_key').sort_index() for M in [10,25,50]}
            for M,sub in by_size.items():
                row={'draw':int(draw),'stratum':stratum,'members':int(M),'cases':len(sub),
                     'q_zero':int((sub['q']==0).sum()),'q_one':int((sub['q']==1).sum()),
                     'at_most_two_uncertain':int((sub['uncertain_sites']<=2).sum())}
                for mode in ['marginal','aggregate','pair']:
                    width=np.maximum(0,sub[mode+'_upper']-sub[mode+'_lower'])
                    ref=by_size[50];reference=np.maximum(0,ref[mode+'_upper']-ref[mode+'_lower'])
                    row[mode+'_width']=float(width.mean())
                    row[mode+'_identified_fraction']=float((width<=TOL).mean())
                    row[mode+'_difference_from_M50']=float((width-reference).mean())
                per_draw.append(row)
    results=pd.DataFrame(per_draw);results.to_csv(out/'per-draw-summary.csv',index=False)
    summaries=[]
    for (stratum,M),part in results.groupby(['stratum','members'],sort=True):
        row={'stratum':stratum,'members':int(M),'draws':len(part),'mean_cases':float(part['cases'].mean()),
             'min_cases':int(part['cases'].min()),'max_cases':int(part['cases'].max()),
             'nonempty_draws':int((part['cases']>0).sum()),
             'pair_width_below_M50_draws':int((part['pair_difference_from_M50'] < -TOL).sum())}
        for col in ['pair_width','aggregate_width','marginal_width','pair_identified_fraction','pair_difference_from_M50']:
            row[col+'_mean']=float(part[col].mean())
            row[col+'_draw_q025']=float(part[col].quantile(.025))
            row[col+'_draw_q975']=float(part[col].quantile(.975))
        summaries.append(row)
    pd.DataFrame(summaries).to_csv(out/'width-summary.csv',index=False)
    report={'exploratory':True,'planned_draws':100,'completed_draws':len(draws),'draw_ids':draws,
            'status':'complete' if draws==list(range(100)) else 'incomplete_planned_draws',
            'rows':summaries,'partial_chunk_paths':[str(p.relative_to(out)) for p in out.glob('chunk-*') if not (p/'complete.json').exists()],
            'scope':'Conditional draw variation from a fixed finiteM50dataset, not population confidence or causal size effects.'}
    (out/'summary.json').write_text(json.dumps(clean(report),indent=2)+'\n')
    display=[]
    for r in summaries:
        display.append({**r,'stratum':{'fixed_M50_informative':'M50 informative','common_informative':'Common informative'}[r['stratum']],
            'pair_interval':f"{r['pair_width_draw_q025']:.4f}–{r['pair_width_draw_q975']:.4f}" if np.isfinite(r['pair_width_draw_q025']) else 'undefined'})
    (out/'table-repeated-members.md').write_text(markdown_table(display,[
        ('stratum','Query set'),('members','Members'),('draws','Draws'),('nonempty_draws','Nonempty draws'),('mean_cases','Mean N'),
        ('min_cases','Minimum N'),('max_cases','Maximum N'),('pair_width_mean','Mean pair width'),
        ('pair_interval','Draw quantiles'),('pair_identified_fraction_mean','Mean identified fraction'),
        ('pair_width_below_M50_draws','Width below M50 draws')])+'\n')
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--cases');p.add_argument('--output',required=True)
    p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=20)
    p.add_argument('--summarize',action='store_true');a=p.parse_args();out=Path(a.output)
    if a.summarize:print(json.dumps(clean(summarize(out))));return
    assert a.cases and 0<=a.start<100 and 0<a.count<=20 and a.start+a.count<=100
    folder=out/f'chunk-{a.start:03d}';folder.mkdir(parents=True,exist_ok=False)
    frame=pd.read_csv(a.cases,dtype={'date':str});design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    chosen=choose_cases(frame,design);assert len(chosen)==120
    Xs={row['case_key']:source_X(row,ROOT) for _,row in chosen.iterrows()}
    rows=[];selections=[]
    (folder/'settings.json').write_text(json.dumps({'started_at_utc':now(),'start':a.start,'count':a.count,
        'seed_prefix':20261027,'cases_sha256':hashlib.sha256(Path(a.cases).read_bytes()).hexdigest()},indent=2)+'\n')
    for draw in range(a.start,a.start+a.count):
        groups={}
        for _,row in chosen.iterrows():
            identity=(row['date'],row['model'],int(row['lead']))
            if identity not in groups:
                indices,digest=selection(draw,*identity);groups[identity]=indices
                selections.append({'draw':draw,'date':identity[0],'model':identity[1],'lead':identity[2],
                    'seed_sha256':digest,'members10':(indices[:10]+1).tolist(),'members25':(indices[:25]+1).tolist()})
                with (folder/'selections.jsonl').open('a') as stream:stream.write(json.dumps(selections[-1])+'\n')
            indices=groups[identity];X=Xs[row['case_key']]
            for M in [10,25,50]:
                result=evaluate(X[indices[:M]],[int(row['k'])])[0] if M<50 else {
                    key:row[key] for key in ['q','k','uncertain_sites','marginal_lower','marginal_upper',
                        'aggregate_lower','aggregate_upper','pair_lower','pair_upper']}
                rows.append({'draw':draw,'case_key':row['case_key'],'date':row['date'],'member_count':M,'reused_M50_reference':M==50,
                    **{key:result[key] for key in ['q','uncertain_sites','marginal_lower','marginal_upper',
                        'aggregate_lower','aggregate_upper','pair_lower','pair_upper']},
                    'informative':int(result['uncertain_sites']>=4 and .1<=result['q']<=.9)})
                with (folder/'cases.jsonl').open('a') as stream:stream.write(json.dumps(clean(rows[-1]))+'\n')
        print(json.dumps({'draw':draw,'completed_at_utc':now(),'queries':len(chosen)}),flush=True)
    pd.DataFrame(rows).to_csv(folder/'cases.csv',index=False)
    (folder/'complete.json').write_text(json.dumps({'started_draw':a.start,'draws':a.count,'completed_at_utc':now(),
        'cases_sha256':hashlib.sha256(Path(a.cases).read_bytes()).hexdigest(),'rows':len(rows)},indent=2)+'\n')


if __name__=='__main__':main()
