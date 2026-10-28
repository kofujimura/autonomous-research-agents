from projection_derivative import run
for rep in ['tessera','alphaearth']:
    for name,dest in [(f'forest-broad-{rep}',f'forest-broad-{rep}'),(f'logistic-broad-refreshed-{rep}',f'refreshed-broad-{rep}')]:
        run('results/inference/'+name,'results/projection-derivative/'+dest,plan_path='protocol/plan-v14a-projection-controls.md')
