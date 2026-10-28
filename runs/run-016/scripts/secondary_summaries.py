"""Summarize the original preplanned secondary contrasts, without new draws."""
from records import ROOT
from summarize_inference import build

for tax in ['broad','fine']:
    paths=[f'results/inference/logistic-{tax}-{rep}' for rep in ['tessera','alphaearth']]
    if tax=='broad':
        paths += [f'results/inference/forest-broad-{rep}' for rep in ['tessera','alphaearth']]
    build(paths,f'results/tables/secondary-{tax}',primary=False)
