"""Exploratory paired query identities using saved member results only."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import TOL
from summarize import clean, markdown_table


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cases',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    f=pd.read_csv(a.cases,dtype={'date':str})
    f=f[f['n']==12].copy()
    keys=['date','model','lead','portfolio_index','threshold_c','k']
    assert not f.duplicated(keys+['member_count']).any()
    index=f.set_index(keys+['member_count']).sort_index()
    flags=f.pivot(index=keys,columns='member_count',values='informative')
    assert list(flags.columns)==[10,25,50] and flags.notna().all().all()
    selections={'M50_informative':flags.index[flags[50]==1],
                'common_informative':flags.index[(flags==1).all(axis=1)]}
    rows=[]
    for stratum,selected in selections.items():
        by_size={M:index.xs(M,level='member_count').loc[selected] for M in [10,25,50]}
        for M,part in by_size.items():
            row={'stratum':stratum,'members':M,'cases':len(part),
                 'dates':int(part.reset_index()['date'].nunique()),
                 'q_zero':int((part['q']==0).sum()),'q_one':int((part['q']==1).sum()),
                 'at_most_two_uncertain':int((part['uncertain_sites']<=2).sum())}
            for mode in ['marginal','aggregate','pair']:
                widths=np.maximum(0,part[mode+'_upper']-part[mode+'_lower'])
                ref=by_size[50]
                reference=np.maximum(0,ref[mode+'_upper']-ref[mode+'_lower'])
                row[mode+'_width']=float(widths.mean())
                row[mode+'_identified']=int((widths<=TOL).sum())
                row[mode+'_difference_from_M50']=float((widths-reference).mean())
            rows.append(row)
    pd.DataFrame(rows).to_csv(out/'common-member-summary.csv',index=False)
    (out/'summary.json').write_text(json.dumps(clean({'exploratory':True,'rows':rows}),indent=2)+'\n')
    (out/'table-common-members.md').write_text(markdown_table(rows,[
        ('stratum','Fixed query set'),('members','Members'),('cases','N'),
        ('q_zero','q=0'),('q_one','q=1'),('at_most_two_uncertain','≤2 uncertain'),
        ('marginal_width','Marginal width'),('aggregate_width','Aggregate width'),
        ('pair_width','Pair width'),('pair_identified','Pair identified'),
        ('pair_difference_from_M50','Pair width minus M50')])+'\n')
    print(json.dumps(clean(rows)))


if __name__=='__main__':main()
