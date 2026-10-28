"""Offline deterministic features from saved patches and numerical rasters."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np,rasterio
from scipy.ndimage import uniform_filter,distance_transform_edt
from records import ROOT

def moments(arr,size):
 valid=np.isfinite(arr);weight=uniform_filter(valid.astype(float),size=size,mode='nearest')
 mean=uniform_filter(np.nan_to_num(arr,nan=0),size=size,mode='nearest')/np.maximum(weight,1e-12)
 m2=uniform_filter(np.nan_to_num(arr,nan=0)**2,size=size,mode='nearest')/np.maximum(weight,1e-12)
 mean[weight==0]=np.nan;std=np.sqrt(np.maximum(m2-mean**2,0));std[weight==0]=np.nan
 return mean,std

def hydro(folder,sample_points=None,polygon_index=None):
 selected=json.loads((folder/'selected.geojson').read_text())['features'];values={}
 with rasterio.open(folder/'dem-30m.tif') as src:
  z=src.read(1,masked=True).filled(np.nan).astype(float)
  coords=np.array([[f['properties']['x'],f['properties']['y']] for f in selected]) if sample_points is None else np.asarray(sample_points)
  rr,cc=rasterio.transform.rowcol(src.transform,coords[:,0],coords[:,1]);rc=np.column_stack([rr,cc]).astype(int)
 good=(rc[:,0]>=0)&(rc[:,0]<z.shape[0])&(rc[:,1]>=0)&(rc[:,1]<z.shape[1])
 def sample(ar):
  result=np.full(len(rc),np.nan);result[good]=ar[rc[good,0],rc[good,1]];return result
 def add(name,ar):values[name]=sample(ar)
 zy,zx=np.gradient(z,30);slope=np.hypot(zx,zy)
 for name,arr in [('elevation',z),('slope',slope),('tpi90',z-moments(z,3)[0]),('tpi510',z-moments(z,17)[0])]:
  m,s=moments(arr,3);add(name+'_mean90',m);add(name+'_std90',s)
 water={}
 for name in ['occurrence','recurrence','seasonality']:
  with rasterio.open(folder/f'gsw-{name}-30m.tif') as src:arr=src.read(1).astype(float)
  arr[arr==255]=np.nan;water[name]=arr
  add(name+'_centre',arr);m,s=moments(arr,3);add(name+'_mean90',m);add(name+'_std90',s)
  if name!='seasonality':add(name+'_mean510',moments(arr,17)[0])
 occ=water['occurrence']
 for threshold in [0,75]:
  ar=np.where(np.isfinite(occ),(occ>0 if threshold==0 else occ>=75).astype(float),np.nan)
  for size,metres in [(3,90),(17,510)]:add(f'water_fraction_{threshold}_{metres}',moments(ar,size)[0])
 wet=occ>=75;dist=np.minimum(distance_transform_edt(~wet)*30,2000) if wet.any() else np.full(occ.shape,2000.)
 add('log_distance_occurrence75',np.log1p(dist))
 if (folder/'hand-30m.tif').exists():
  with rasterio.open(folder/'hand-30m.tif') as src:hand=src.read(1).astype(float)
  hand[(hand<0)|~np.isfinite(hand)]=np.nan;hand=np.log1p(hand)
 else:hand=np.full(z.shape,np.nan)
 add('log_hand_centre',hand)
 for size,metres in [(3,90),(17,510)]:
  m,s=moments(hand,size);add(f'log_hand_mean{metres}',m);add(f'log_hand_std{metres}',s)
 areas=np.log([f['properties']['area_m2'] for f in selected]);values['log_area']=areas if polygon_index is None else areas[np.asarray(polygon_index)]
 return list(values),np.column_stack(list(values.values()))

def embedding(path,centre=False,return_norm=False):
 x=np.load(path);raw=x['raw'].astype(np.float32);inside=x['inside']
 if path.name.startswith('aef'):
  valid=inside&(raw!=-128).all(axis=-1);decoded=np.sign(raw)*(raw/127.5)**2
 else:
  valid=inside&np.isfinite(x['scales']);decoded=raw*x['scales'][...,None]
 if centre:
  v=decoded[:,4,:];n=valid[:,4].astype(int);v[~valid[:,4]]=np.nan
 else:
  n=valid.sum(axis=1);v=np.where(valid[:,:,None],decoded,0).sum(axis=1)/np.maximum(n[:,None],1);v[n<5]=np.nan
 norm=np.linalg.norm(v,axis=1);v=v/np.where(norm>0,norm,np.nan)[:,None]
 return (v,n,norm) if return_norm else (v,n)

def derive(root=ROOT,out=None,year=2024,pattern="R??",centre=False,aef_overrides=None):
 root=Path(root);out=Path(out) if out else root/'analysis/features';out.mkdir(parents=True,exist_ok=True)
 rows=[];matrices=[];aef=[];tess=[];aef_norm=[];tess_norm=[];names=None;missing=[]
 for folder in sorted((root/'data/main').glob(pattern)):
  if not (folder/'labels-record.json').exists():missing.append(dict(region=folder.name,reason='labels missing'));continue
  selected=json.loads((folder/'selected.geojson').read_text())['features']
  aef_path=folder/f'aef-{year}.npz'
  if aef_overrides is not None and (Path(aef_overrides)/folder.name/f'aef-{year}.npz').exists():aef_path=Path(aef_overrides)/folder.name/f'aef-{year}.npz'
  required=[folder/'hydro-record.json',aef_path,folder/f'tessera-{year}.npz']
  if not all(p.exists() for p in required):missing.append(dict(region=folder.name,reason='incomplete inputs',missing=[p.name for p in required if not p.exists()]));continue
  nms,h=hydro(folder);assert names is None or names==nms;names=nms
  av,an,avnorm=embedding(aef_path,centre=centre,return_norm=True);tv,tn,tvnorm=embedding(folder/f'tessera-{year}.npz',centre=centre,return_norm=True)
  for f,a,t in zip(selected,an,tn):
   p=f['properties'];rows.append({k:p[k] for k in ['objectid','attribute','vegetation','regime','x','y','lon','lat','area_m2','interior_margin_m','image_year','fold'] }|dict(region=folder.name,aef_valid=int(a),tessera_valid=int(t)))
  matrices.append(h);aef.append(av);tess.append(tv);aef_norm.append(avnorm);tess_norm.append(tvnorm)
 if matrices:
  np.savez_compressed(out/f'features-{year}.npz',hydro=np.concatenate(matrices),aef=np.concatenate(aef),tessera=np.concatenate(tess),aef_norm=np.concatenate(aef_norm),tessera_norm=np.concatenate(tess_norm),hydro_names=np.array(names))
 (out/f'rows-{year}.json').write_text(json.dumps(rows,indent=2)+'\n');(out/f'missing-{year}.json').write_text(json.dumps(missing,indent=2)+'\n')
 print(json.dumps(dict(rows=len(rows),missing=missing,hydro_features=names)),flush=True)
 return rows

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path);p.add_argument('--year',type=int,default=2024);p.add_argument('--pattern',default='R??');p.add_argument('--centre',action='store_true');p.add_argument('--aef-overrides',type=Path);a=p.parse_args();derive(a.root,a.out,a.year,a.pattern,a.centre,a.aef_overrides)
