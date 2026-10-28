"""Apply the already fixed source logistic head as target extracts become ready."""
import argparse,json,shutil
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from records import ROOT,now,digest
from fit_models import load_population

def restore(directory,year=2021):
    with np.load(directory/f'coefficients-{year}.npz') as z:
        model=LogisticRegression();model.classes_=z['classes'];model.coef_=z['coef'];model.intercept_=z['intercept']
        model.n_features_in_=model.coef_.shape[1]
        scale=StandardScaler();scale.mean_=z['mean'];scale.scale_=z['scale'];scale.var_=scale.scale_**2
        scale.n_features_in_=len(scale.mean_);scale.n_samples_seen_=1
    return model,scale

def predict(base_path,manifest_path,destination):
    base=ROOT/base_path;meta=json.loads((base/'fit.json').read_text())
    assert meta['classifier']=='logistic' and not meta['refreshed']
    source=json.loads((ROOT/meta['manifest_path']).read_text())
    assert source['source_only'] and not source['status_counts'].get('incomplete',0)
    m,data=load_population(manifest_path,meta['representation'],meta['taxonomy'])
    assert m[meta['taxonomy']+'_names']==meta['class_names']
    full={r['landscape_id']:r for r in m['landscapes']}
    assert set(r['landscape_id'] for r in source['landscapes'])==set(r['landscape_id'] for r in m['landscapes'] if r['split']!='test')
    for r in source['landscapes']:
        assert full[r['landscape_id']]['status']==r['status']
        if r['status']=='included':assert full[r['landscape_id']]['valid_indices']==r['valid_indices'],'Source population changed after model fitting'
    out=ROOT/destination
    if out.exists():raise FileExistsError('Keep previous fixed-head predictions')
    out.mkdir(parents=True);(out/'predictions').mkdir()
    model,scale=restore(base);k=len(meta['class_names']);files=[];diagnostics=[];crosschecks=[]
    original={r['landscape_id']:r for r in meta['prediction_files']}
    for lid,d in data.items():
        p=np.full((5,len(d['y'][0]),k),np.nan,np.float32)
        for ti,x in d['x'].items():
            good=np.isfinite(x).all(axis=1)
            pp=model.predict_proba(scale.transform(x[good]))
            result=np.zeros((good.sum(),k),np.float32);result[:,model.classes_]=pp.astype(np.float32);p[ti][good]=result
            if not good.all():continue
            truth=d['y'][ti];pred=p[ti].argmax(axis=1)
            diagnostics.append(dict(landscape_id=lid,split=d['record']['split'],year=2021+ti,n=len(truth),
                        correct=int((truth==pred).sum()),accuracy=float((truth==pred).mean()),
                        unsupported_points=int((~np.isin(truth,model.classes_)).sum()),
                        true_class_counts=np.bincount(truth,minlength=k).tolist(),
                        hard_class_counts=np.bincount(pred,minlength=k).tolist(),soft_means=p[ti].mean(axis=0,dtype=np.float64).tolist()))
        if lid in original:
            with np.load(ROOT/original[lid]['path']) as z:
                old=z['probabilities'][0]
                assert np.array_equal(old,p[0]),'Reconstructed source predictions differ'
            crosschecks.append(dict(landscape_id=lid,source_prediction_bitwise_equal=True))
        dest=out/'predictions'/f'{lid}.npz';np.savez_compressed(dest,probabilities=p,labels=d['y'])
        files.append(dict(landscape_id=lid,path=str(dest.relative_to(ROOT)),sha256=digest(dest)))
    shutil.copyfile(base/'coefficients-2021.npz',out/'coefficients-2021.npz')
    shutil.copyfile(base/'source-calibration.npz',out/'source-calibration.npz')
    result=dict(meta);result.update(manifest_path=manifest_path,manifest_sha256=digest(ROOT/manifest_path),
                                   source_fit_path=base_path,source_fit_sha256=digest(base/'fit.json'),
                                   prediction_generation_end_utc=now(),prediction_files=files,diagnostics=diagnostics,
                                   coefficient_reconstruction_crosschecks=crosschecks)
    (out/'fit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),predicted_landscapes=len(files),unchanged_source_crosschecks=len(crosschecks))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-fit',required=True);p.add_argument('--manifest',required=True)
    p.add_argument('--destination',required=True);a=p.parse_args();predict(a.source_fit,a.manifest,a.destination)
