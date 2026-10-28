"""Explore a standard hard-label auxiliary without changing fitted classifiers."""
import argparse,json,shutil
import numpy as np
from records import ROOT,now,digest
from audit_inference import run
from summarize_inference import build

p=argparse.ArgumentParser();p.add_argument('--representation',choices=['tessera','alphaearth'],required=True);a=p.parse_args()
source=f'results/models/logistic-broad-{a.representation}'
destination=f'results/models/hard-auxiliary-broad-{a.representation}'
base=ROOT/source;out=ROOT/destination
if out.exists():raise FileExistsError('Preserve prior auxiliary comparisons')
out.mkdir(parents=True);(out/'predictions').mkdir()
fit=json.loads((base/'fit.json').read_text());k=len(fit['class_names'])
m=json.loads((ROOT/fit['manifest_path']).read_text());splits={r['landscape_id']:r['split'] for r in m['landscapes']}
files=[];calp=[];caly=[];diagnostics=[]
for entry in fit['prediction_files']:
    assert digest(ROOT/entry['path'])==entry['sha256']
    with np.load(ROOT/entry['path']) as z:p=z['probabilities'];y=z['labels']
    good=np.isfinite(p).all(axis=2);hard=np.full_like(p,np.nan)
    hard[good]=np.eye(k,dtype=np.float32)[p[good].argmax(axis=1)]
    assert np.array_equal(hard[good].argmax(axis=1),p[good].argmax(axis=1))
    path=out/'predictions'/f"{entry['landscape_id']}.npz"
    np.savez_compressed(path,probabilities=hard,labels=y)
    files.append(dict(landscape_id=entry['landscape_id'],path=str(path.relative_to(ROOT)),sha256=digest(path)))
    for ti in range(5):
        if not good[ti].all():continue
        truth=y[ti];pred=hard[ti].argmax(axis=1)
        classes=np.asarray(fit['fit_records'][0]['classes'])
        diagnostics.append(dict(landscape_id=entry['landscape_id'],split=splits[entry['landscape_id']],year=2021+ti,
            n=len(truth),correct=int((truth==pred).sum()),accuracy=float((truth==pred).mean()),
            unsupported_points=int((~np.isin(truth,classes)).sum()),true_class_counts=np.bincount(truth,minlength=k).tolist(),
            hard_class_counts=np.bincount(pred,minlength=k).tolist(),soft_means=hard[ti].mean(axis=0,dtype=np.float64).tolist()))
    if splits[entry['landscape_id']]=='calibration':calp.append(hard[0]);caly.append(y[0])
pc=np.concatenate(calp);yc=np.concatenate(caly);counts=np.bincount(yc,minlength=k)
confusion=np.zeros((k,k))
for c in range(k):
    if counts[c]:confusion[:,c]=pc[yc==c].mean(axis=0,dtype=np.float64)
sv=np.linalg.svd(confusion,compute_uv=False)
np.savez_compressed(out/'source-calibration.npz',soft_confusion=confusion,class_counts=counts,prior=counts/counts.sum(),singular_values=sv)
fit.update(classifier='logistic_hard_auxiliary',prediction_files=files,diagnostics=diagnostics,auxiliary_transform='argmax_onehot',
           source_fit_path=source,source_fit_sha256=digest(base/'fit.json'),transformed_at_utc=now(),exploratory=True,
           calibration=dict(class_counts=counts.tolist(),rank=int(np.linalg.matrix_rank(confusion)),singular_values=sv.tolist()))
(out/'fit.json').write_text(json.dumps(fit,indent=2)+'\n')
analysis=f'results/inference/hard-auxiliary-broad-{a.representation}'
run(destination,'data/audit-draws-main/manifest.json',analysis)
build([analysis],f'results/tables/hard-auxiliary-{a.representation}')
