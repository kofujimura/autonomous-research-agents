"""Input-only checks and visual alignment; no map performance scores."""
import argparse
import json
import hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from records import ROOT, now

def main():
    p=argparse.ArgumentParser();p.add_argument('--cores',nargs='+',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for cid in a.cores:
        meta_path=ROOT/'data/derived/features'/(cid+'.json');feature_path=meta_path.with_suffix('.npz')
        meta=json.loads(meta_path.read_text())
        feature_sha=hashlib.sha256(feature_path.read_bytes()).hexdigest()
        if feature_sha!=meta['feature_file_sha256']:raise RuntimeError('Feature hash mismatch')
        data=np.load(feature_path)
        aef=data['aef'];optical=data['optical'];valid=data['valid'];y=data['y'];objects=data['objects']
        if not np.all(np.isfinite(aef[valid])) or not np.all(np.isfinite(optical[valid])):
            raise RuntimeError('Nonfinite predictor values in common-valid pixels')
        norms=np.sqrt((aef[valid]**2).sum(axis=-1))
        if not np.all((norms>.95)&(norms<1.05)):raise RuntimeError('Invalid decoded embedding norms')
        if not np.all(y[objects>0]==1):raise RuntimeError('Object labels and wetland labels disagree')
        if np.any(data['positive_interior']&~y.astype(bool)):raise RuntimeError('Positive interior outside reference wetland')
        if np.any(data['negative_interior']&y.astype(bool)):raise RuntimeError('Negative interior inside reference wetland')
        row=dict(core_id=cid,observed_at_utc=now(),embedding_norm_quantiles=np.quantile(norms,[0,.5,1]).tolist() if norms.size else [],
            feature_path=str(feature_path.relative_to(ROOT)),feature_sha256=feature_sha,
            metadata_path=str(meta_path.relative_to(ROOT)),metadata_sha256=hashlib.sha256(meta_path.read_bytes()).hexdigest(),
            valid_pixels=int(valid.sum()),positive_pixels=int(y[valid].sum()),
            reference_scoring_empty=not np.any(valid),
            main_small_patches=sum(o['main_eligible'] and o['size_bin']=='small' for o in meta['objects']),
            zero_pixel_patches=meta['reference_diagnostics']['zero_pixel_objects'],
            all_finite=True,orientation='north-up target; native orientation preserved in source metadata')
        rows.append(row)
        # A readable self-check of geography, not an independent label annotation.
        rgb=optical[...,[12,11,10]]
        rgb=np.clip(rgb/.25,0,1)
        pc=aef[...,:3]
        lo=np.quantile(pc[valid],.02,axis=0) if np.any(valid) else np.zeros(3)
        hi=np.quantile(pc[valid],.98,axis=0) if np.any(valid) else np.ones(3)
        pc=np.clip((pc-lo)/(hi-lo+1e-8),0,1)
        fig,axes=plt.subplots(1,3,figsize=(12,4))
        axes[0].imshow(rgb);axes[0].contour(y,levels=[.5],colors='yellow',linewidths=.4)
        axes[0].set_title('Summer optical RGB + inventory')
        axes[1].imshow(pc);axes[1].contour(y,levels=[.5],colors='white',linewidths=.4)
        axes[1].set_title('Embedding channels 0–2 + inventory')
        axes[2].imshow(np.ma.masked_where(~valid,y),cmap='Blues',vmin=0,vmax=1)
        axes[2].set_title('Common-valid reference target')
        for ax in axes:ax.axis('off')
        fig.suptitle(cid+' input alignment self-check')
        fig.tight_layout();fig.savefig(out/(cid+'-alignment.png'),dpi=140);plt.close(fig)
    (out/'qc.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))

if __name__=='__main__':main()
