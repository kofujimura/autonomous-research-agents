"""Execute the four conditions fixed in the numerical sensitivity plan."""
from gradient_sensitivity import run
for taxonomy in ['broad','fine']:
    for rep in ['tessera','alphaearth']:
        run(f'results/inference/logistic-{taxonomy}-{rep}',f'results/gradient/{taxonomy}-{rep}')
