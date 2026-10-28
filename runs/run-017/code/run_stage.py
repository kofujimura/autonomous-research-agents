"""Run committed fitting grids sequentially inside one bounded worker."""
import argparse
import json
from pathlib import Path
import sys
import time
import fit_models
from records import ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--stages',nargs='+',required=True)
    p.add_argument('--config',default='protocol/execution-priorities.json');a=p.parse_args()
    config=json.loads((ROOT/a.config).read_text());by_name={s['name']:s for s in config['stages']}
    tick=time.monotonic()
    for name in a.stages:
        stage=by_name[name]
        for scope in stage['scopes']:
            for budget in stage['budgets']:
                remaining=1680-(time.monotonic()-tick)
                if remaining<180:
                    print('STAGE BOUNDARY: unfinished requested cells remain',flush=True);return
                args=['fit_models.py','--budget',str(budget),'--seeds',*map(str,stage['training_seeds']),
                    '--policies',*stage['policies'],'--representations',*stage['representations'],
                    '--decoders',*stage['decoders'],'--time-budget',str(int(min(1500,remaining-120)))]
                if scope.startswith('leave_'):args+=['--holdout-region',scope.replace('leave_','',1)]
                elif scope!='within':raise ValueError('Unsupported committed scope: '+scope)
                sys.argv=args;fit_models.main()

if __name__=='__main__':main()
