import json,sys,numpy as np,collections
rows=json.load(open(sys.argv[1]))
out={}
for n in [128]:
    P={r['unit']:r['mse'] for r in rows if r['n']==n and r['design']=='paired'}
    I={r['unit']:r['mse'] for r in rows if r['n']==n and r['design']=='independent'}
    T={r['unit']:r['truth']**2 for r in rows if r['n']==n and r['design']=='paired'}
    L=collections.defaultdict(list)
    for u in P: L[u.rsplit('-',2)[0]].append(u)
    land=sorted(L); rng=np.random.default_rng(1)
    def stat(ls):
        us=[u for l in ls for u in L[l]]
        return np.mean([P[u] for u in us])/np.mean([I[u] for u in us]), np.sqrt(np.mean([T[u] for u in us])), np.sqrt(np.mean([P[u] for u in us]))
    bs=np.array([stat(rng.choice(land,len(land),replace=True)) for _ in range(5000)])
    per_unit=np.array([P[u]/I[u] for u in P])
    out[n]=dict(landscapes=len(land),ratio=stat(land)[0],ratio_ci95=np.percentile(bs[:,0],[2.5,97.5]).tolist(),
                nochange_rmse_ci95=np.percentile(bs[:,1],[2.5,97.5]).tolist(),paired_rmse_ci95=np.percentile(bs[:,2],[2.5,97.5]).tolist(),
                per_unit_ratio_min=float(per_unit.min()),per_unit_ratio_median=float(np.median(per_unit)),per_unit_ratio_max=float(per_unit.max()),
                units_ratio_above_1=int((per_unit>1).sum()))
print(json.dumps(out,indent=1)); json.dump(out,open(sys.argv[2],'w'),indent=1)
