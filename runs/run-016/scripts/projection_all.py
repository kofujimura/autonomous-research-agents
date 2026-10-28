from projection_derivative import run
for taxonomy in ['broad','fine']:
    for rep in ['tessera','alphaearth']:
        run(f'results/inference/logistic-{taxonomy}-{rep}',f'results/projection-derivative/{taxonomy}-{rep}')
