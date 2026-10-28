"""Count coincident/trivial comparisons rather than interpret them as evidence."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from records import ROOT,now

def main():
    p=argparse.ArgumentParser();p.add_argument('--evaluation',default='data/evaluation')
    p.add_argument('--analysis',default='analysis');p.add_argument('--out',default='analysis');a=p.parse_args()
    index={};trivial=[];pair_rows=[]
    for path in sorted((ROOT/a.evaluation).glob('*/evaluation.json')):
        e=json.loads(path.read_text());m=json.loads((ROOT/e['fit_metadata_path']).read_text())
        key=(m['scope'],m['decoder'],m['budget'],m['seed'],m['representation'],m['policy'])
        index[key]=(e,m)
    for key,(e,m) in sorted(index.items()):
        scope,decoder,budget,seed,rep,policy=key
        pairs=[]
        if policy!='area':pairs.append((scope,decoder,budget,seed,rep,'area'))
        if rep=='aef':pairs.append((scope,decoder,budget,seed,'optical',policy))
        for other in pairs:
            if other not in index:continue
            e2,m2=index[other]
            d1=next(x['decision_sha256'] for x in e['decision_hashes'] if x['version']=='raw' and x['condition']=='standardized_0.05')
            d2=next(x['decision_sha256'] for x in e2['decision_hashes'] if x['version']=='raw' and x['condition']=='standardized_0.05')
            pair_rows.append(dict(fit_a=m['fit_id'],fit_b=m2['fit_id'],scope=scope,decoder=decoder,budget=budget,seed=seed,
                representation_a=rep,policy_a=policy,representation_b=other[-2],policy_b=other[-1],
                primary_pair=scope=='within' and decoder=='rf' and budget==2000 and
                    policy in ['area','interior','object','proposal','uncertainty'] and
                    other[-1] in ['area','interior','object','proposal','uncertainty'] and
                    rep in ['aef','optical','optical_context'] and other[-2] in ['aef','optical','optical_context'],
                identical_probabilities=e['probability_field_sha256']==e2['probability_field_sha256'],
                identical_test_decisions=d1==d2,same_sample_positions=m['sampling']['sample_sha256']==m2['sampling']['sample_sha256']))
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(pair_rows).to_csv(out/'comparison-audit.csv',index=False)
    scores=pd.read_csv(ROOT/a.analysis/'scores.csv')
    primary=scores[(scores.scope=='within')&(scores.decoder=='rf')&(scores.budget==2000)&
        (scores.version=='raw')&(scores.condition=='standardized_0.05')&(scores.boundary_tolerance_m==0)&
        scores.policy.isin(['area','interior','object','proposal','uncertainty'])&
        scores.representation.isin(['aef','optical','optical_context'])]
    primary_pairs=[x for x in pair_rows if x['primary_pair']]
    summary=dict(checked_at_utc=now(),fitted_models_evaluated=len(index),paired_comparisons_checked=len(pair_rows),
        primary_paired_comparisons_checked=len(primary_pairs),
        primary_identical_probability_comparisons=sum(x['identical_probabilities'] for x in primary_pairs),
        primary_identical_test_decision_comparisons=sum(x['identical_test_decisions'] for x in primary_pairs),
        identical_probability_comparisons=sum(x['identical_probabilities'] for x in pair_rows),
        identical_test_decision_comparisons=sum(x['identical_test_decisions'] for x in pair_rows),
        primary_fit_count=len(primary),primary_all_positive_fit_core_cases=int(primary.all_positive_cores.sum()),
        primary_all_negative_fit_core_cases=int(primary.all_negative_cores.sum()),
        primary_empty_scoring_fit_core_cases=int(primary.empty_scoring_cores.sum()),
        primary_fit_core_cases=int(primary.core_count.sum()),
        primary_minimum_achieved_fpr=float(primary.upland_fpr.min()),primary_maximum_achieved_fpr=float(primary.upland_fpr.max()),
        primary_recovery_at_floor_fits=int(np.sum(primary.small_macro_recovery_50==0)),
        primary_recovery_at_ceiling_fits=int(np.sum(primary.small_macro_recovery_50==1)))
    (out/'comparison-audit.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
