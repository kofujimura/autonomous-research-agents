"""Compare optimized aggregation with a frozen earlier implementation's output.

This is a self-check of numerical consistency, not independent reproduction.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
from records import ROOT,now
from summarize import load_evaluations,describe,strata_scores,primary_bootstrap

def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',default='experiments/E51/outputs/analysis')
    p.add_argument('--out',required=True);a=p.parse_args();reference=ROOT/a.reference;out=ROOT/a.out
    out.mkdir(parents=True,exist_ok=False);links=out/'evaluation-links';links.mkdir()
    fits=pd.read_csv(reference/'fits.csv')
    primary=((fits.scope=='within')&(fits.decoder=='rf')&(fits.budget==2000)&
        fits.policy.isin(['area','interior','object','proposal','uncertainty'])&fits.representation.isin(['aef','optical','optical_context']))
    boundary=(fits.scope=='leave_R04')&(fits.seed==101)&(
        ((fits.representation=='aef')&(fits.policy=='area'))|((fits.representation=='optical')&(fits.policy=='object')))
    other=(fits.scope=='within')&(fits.seed==101)&(fits.representation=='aef')&(
        ((fits.decoder=='logit')&(fits.policy=='area'))|(fits.policy=='object_mmu'))
    ids=set(fits[primary|boundary|other].fit_id)
    for fit_id in sorted(ids):(links/fit_id).symlink_to(ROOT/'data/evaluation'/fit_id,target_is_directory=True)
    tick=time.monotonic();cores,objects,_,_=load_evaluations(links)
    scores,regions,blocks=describe(cores,objects);strata=strata_scores(objects)
    conditions=dict(scores=(scores,['fit_id','version','condition','boundary_tolerance_m']),
        **{'regional-scores':(regions,['fit_id','version','condition','boundary_tolerance_m','size_bin','coverage_target','region_id']),
        'bootstrap-blocks':(blocks,['fit_id','version','condition','boundary_tolerance_m','size_bin','core_id']),
        'strata-scores':(strata,['fit_id','stratum','region_id'])})
    counts={}
    for name,(actual,keys) in conditions.items():
        expected=pd.read_csv(reference/(name+'.csv'));expected=expected[expected.fit_id.isin(ids)]
        # CSV normalization gives coverage-target fields the same parse types.
        actual.to_csv(out/(name+'.csv'),index=False,float_format='%.17g')
        actual=pd.read_csv(out/(name+'.csv'))
        pd.testing.assert_frame_equal(actual[expected.columns].sort_values(keys).reset_index(drop=True),
            expected.sort_values(keys).reset_index(drop=True),check_dtype=False,check_exact=False,atol=1e-12,rtol=0)
        counts[name]=len(actual)
    actual=primary_bootstrap(blocks)
    expected=json.loads((reference/'summary.json').read_text())['primary_contrasts']
    compared=[]
    for key in ['H1_interaction','aef_oracle_gain','optical_oracle_gain','aef_proposal_gain','optical_proposal_gain',
                'aef_proposal_vs_uncertainty','optical_proposal_vs_uncertainty']:
        assert actual[key]['status']==expected[key]['status']=='complete'
        assert np.isclose(actual[key]['estimate'],expected[key]['estimate'],rtol=0,atol=1e-12)
        assert np.allclose(actual[key]['conditional_block_bootstrap_95_percent_interval'],
            expected[key]['conditional_block_bootstrap_95_percent_interval'],rtol=0,atol=1e-12)
        compared.append(key)
    result=dict(completed_at_utc=now(),status='PASS',fits=len(ids),rows_compared=counts,
        primary_contrasts_compared=compared,absolute_tolerance=1e-12,elapsed_seconds=time.monotonic()-tick,
        interpretation='Optimized aggregation agrees with frozen earlier outputs on the full original75 fits and selected empty-domain/decoder/MMU cases; self-check, not independent reproduction')
    (out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
