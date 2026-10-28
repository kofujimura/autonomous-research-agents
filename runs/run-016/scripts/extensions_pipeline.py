"""Run the recorded exploratory follow-ups, without changing original analyses."""
import argparse
from sparse_change_analysis import run as sparse
from jackknife_analysis import run as jackknife
from stratified_audits import run as stratified
from power_tuning_analysis import run as power

p=argparse.ArgumentParser();p.add_argument('--representation',choices=['tessera','alphaearth'],required=True)
p.add_argument('--stage',choices=['sparse','jackknife','stratified','power'],required=True);a=p.parse_args()
assert a.stage!='sparse' or a.representation=='tessera','Direct sampling is representation-invariant'
functions=dict(sparse=sparse,jackknife=jackknife,stratified=stratified,power=power)
functions[a.stage](f'results/inference/logistic-broad-{a.representation}',f'results/{a.stage}/{a.representation}')
