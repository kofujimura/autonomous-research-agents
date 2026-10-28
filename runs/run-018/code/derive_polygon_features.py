"""Build all four plan-v10 conditions on a single outcome-blind common cohort."""
from pathlib import Path
import argparse,hashlib,json,warnings
import numpy as np,pandas as pd,shapely,rasterio
from derive_features import hydro
from collect_embeddings import load
from records import ROOT,now

def mean_vector(decoded,valid):
 if not valid.any():return np.full(decoded.shape[1],np.nan),np.nan
 v=decoded[valid].sum(axis=0).astype(np.float64)/int(valid.sum());norm=float(np.linalg.norm(v));return v/norm if norm>0 else np.full_like(v,np.nan),norm

def derive(root,out,primary_features=None):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False)
 primary_features=Path(primary_features).resolve() if primary_features is not None else root/'analysis/features'
 original=np.load(primary_features/'features-2024.npz');rows=json.loads((primary_features/'rows-2024.json').read_text());index={v['objectid']:i for i,v in enumerate(rows)};names=original['hydro_names'].tolist();n=len(rows)
 values={c:{k:np.full_like(original[k],np.nan,dtype=float) for k in ['hydro','aef','tessera','aef_norm','tessera_norm']} for c in ['A','B','C','D']};valid_count={c:{k:np.zeros(n,int) for k in ['aef','tessera']} for c in values};eligible=np.ones(n,bool);audit=[];exclusions=[];input_hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [primary_features/'features-2024.npz',primary_features/'rows-2024.json',root/'data/main/main-input-manifest.json']}
 for rid in sorted(set(v['region'] for v in rows)):
  folder=root/'data/polygon'/rid;points=np.load(folder/'points.npz');aa=np.load(folder/'aef-2024.npz')['raw'];tt=np.load(folder/'tessera-2024.npz');sc=tt['scales'];raw_t=tt['raw'];xy=points['xy'];offsets=points['offsets'];owners=points['owners'];objectids=points['objectid'];geom_inside=points['original_inside_n'];_,info,fs,_,geoms=load(rid)
  assert np.array_equal(objectids,[f['properties']['objectid'] for f in fs]);assert len(xy)==len(aa)==len(raw_t)==len(sc);assert np.array_equal(owners,np.repeat(np.arange(len(objectids)),np.diff(offsets)))
  aef_patch=root/f'data/corrections/{rid}/aef-2024.npz'
  if not aef_patch.exists():aef_patch=root/f'data/main/{rid}/aef-2024.npz'
  pa=np.load(aef_patch);pt=np.load(root/f'data/main/{rid}/tessera-2024.npz');shared=0;old_a=pa['raw'];old_t=pt['raw'];old_scale=pt['scales'];old_xy=pa['xy'];old_inside=pa['inside']
  input_hashes[str(aef_patch.relative_to(root))]=hashlib.sha256(aef_patch.read_bytes()).hexdigest()
  for k,oid in enumerate(objectids):
   lo,hi=offsets[k:k+2];assert np.all(shapely.covers(geoms[k],shapely.points(xy[lo:hi])));assert len(set(map(tuple,xy[lo:hi])))==hi-lo
   lookup={tuple(p):j for j,p in enumerate(xy[lo:hi],start=int(lo))}
   for j in np.flatnonzero(old_inside[k]):
    key=tuple(old_xy[k,j]);p=lookup.get(key)
    if p is None:continue
    assert np.array_equal(aa[p],old_a[k,j]);assert np.array_equal(raw_t[p],old_t[k,j]);assert np.array_equal(np.asarray(sc[p]),np.asarray(old_scale[k,j]),equal_nan=True);shared+=1
  hnames,hpoints=hydro(root/'data/main'/rid,sample_points=xy,polygon_index=owners);assert hnames==names
  with rasterio.open(root/f'data/main/{rid}/dem-30m.tif') as grid:bounds=grid.bounds;grid_transform=grid.transform;grid_crs=grid.crs;grid_shape=grid.shape
  for layer in ['gsw-occurrence','gsw-recurrence','gsw-seasonality','hand']:
   with rasterio.open(root/f'data/main/{rid}/{layer}-30m.tif') as other:assert other.transform==grid_transform and other.crs==grid_crs and other.shape==grid_shape
  edge=np.minimum.reduce([xy[:,0]-bounds.left,bounds.right-xy[:,0],xy[:,1]-bounds.bottom,bounds.top-xy[:,1]])
  adecode=np.sign(aa.astype(np.float32))*(aa.astype(np.float32)/127.5)**2;tdecode=raw_t.astype(np.float32)*sc[:,None];avalid=(aa!=-128).all(axis=1);tvalid=np.isfinite(sc)
  region_essential_min=1.;per_polygon=[]
  for k,oid in enumerate(objectids):
   i=index[int(oid)];lo,hi=map(int,offsets[k:k+2]);count=hi-lo;small=int(geom_inside[k]);assert count>=small>=5;spans={'B':slice(lo,hi),'C':slice(lo,hi),'D':slice(lo,lo+small)};reasons=[]
   if edge[lo:hi].min()<2030:reasons.append('insufficient2030m_physical_grid_context')
   for key in values['A']:values['A'][key][i]=original[key][i]
   valid_count['A']['aef'][i]=rows[i]['aef_valid'];valid_count['A']['tessera'][i]=rows[i]['tessera_valid']
   for c,sl in spans.items():
    av=avalid[sl];tv=tvalid[sl];v,nn=mean_vector(adecode[sl],av);values[c]['aef'][i]=v;values[c]['aef_norm'][i]=nn;v,nn=mean_vector(tdecode[sl],tv);values[c]['tessera'][i]=v;values[c]['tessera_norm'][i]=nn;valid_count[c]['aef'][i]=int(av.sum());valid_count[c]['tessera'][i]=int(tv.sum());values[c]['hydro'][i]=original['hydro'][i]
    if av.sum()<5 or tv.sum()<5:reasons.append(c+':fewer_than5_valid_vectors')
    if c in ['B','C'] and (av.mean()<.8 or tv.mean()<.8):reasons.append(c+':below80percent_valid_vectors')
   with warnings.catch_warnings():
    warnings.simplefilter('ignore',RuntimeWarning);hm=np.nanmean(hpoints[lo:hi],axis=0)
   hm[names.index('log_area')]=original['hydro'][i,names.index('log_area')];values['C']['hydro'][i]=hm
   fractions={name:float(np.isfinite(hpoints[lo:hi,names.index(name)]).mean()) for name in ['elevation_mean90','occurrence_mean90','recurrence_mean90']};region_essential_min=min(region_essential_min,*fractions.values())
   if min(fractions.values())<.8:reasons.append('C:below80percent_essential_physical_samples')
   if not all(np.isfinite(values[c]['aef'][i]).all() and np.isfinite(values[c]['tessera'][i]).all() and np.isfinite(values[c]['hydro'][i,names.index('elevation_mean90')]) for c in values):reasons.append('nonfinite_essential_condition')
   if reasons:eligible[i]=False;exclusions.append(dict(objectid=int(oid),region=rid,reasons=sorted(set(reasons))))
   per_polygon.append(dict(objectid=int(oid),minimum_physical_grid_edge_distance_m=float(edge[lo:hi].min()),sample_n=count,total_interior_pixels=int(points['total_interior_pixels'][k]),dispersed_small_n=small,aef_valid=int(avalid[lo:hi].sum()),tessera_valid=int(tvalid[lo:hi].sum()),essential_hydro_fractions=fractions,hydro_finite_n=np.isfinite(hpoints[lo:hi]).sum(axis=0).tolist(),eligible=bool(eligible[i])))
  (out/f'{rid}-quality.json').write_text(json.dumps(per_polygon,indent=2)+'\n');audit.append(dict(region=rid,polygon_n=len(fs),sampled_pixels=len(xy),primary_patch_overlap_pixels=shared,raw_values_on_overlap_exactly_equal=True,essential_physical_fraction_min=region_essential_min,common_eligible_n=int(sum(eligible[index[int(v)]] for v in objectids))))
  for p in [folder/'points.npz',folder/'aef-2024.npz',folder/'tessera-2024.npz',root/f'data/main/{rid}/selected.geojson']:input_hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 for c,v in values.items():
  folder=out/c;folder.mkdir();np.savez_compressed(folder/'features-2024.npz',**{k:x[eligible] for k,x in v.items()},hydro_names=original['hydro_names'])
  rr=[dict(row,aef_valid=int(valid_count[c]['aef'][i]),tessera_valid=int(valid_count[c]['tessera'][i])) for i,row in enumerate(rows) if eligible[i]];(folder/'rows-2024.json').write_text(json.dumps(rr,indent=2)+'\n')
 (out/'exclusions.json').write_text(json.dumps(exclusions,indent=2)+'\n');(out/'input-hashes.json').write_text(json.dumps(input_hashes,indent=2)+'\n');record=dict(primary_features_source=str(primary_features),derived_at_utc=now(),original_n=n,common_n=int(eligible.sum()),excluded_n=int((~eligible).sum()),original_cohort_unchanged=bool(eligible.all()),conditions={'A':'Original contiguous3x3 and physical features','B':'Dispersed up to256embedding pixels, original physical features','C':'Dispersed up to256embedding pixels and sample-mean physical features','D':'Dispersed geometric-pixel count equal to original contiguous patch, original physical features'},audits=audit)
 (out/'derivation-record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);p.add_argument('--primary-features',type=Path);a=p.parse_args();derive(a.root,a.out,a.primary_features)
