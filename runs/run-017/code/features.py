"""Offline feature/reference construction from bundled inputs (protocol v2)."""
import argparse
import hashlib
import json
from pathlib import Path
import warnings
import numpy as np
from pyproj import Transformer
from rasterio.features import rasterize
from rasterio.transform import from_origin
from scipy.ndimage import gaussian_filter
from shapely import make_valid, STRtree
from shapely.geometry import shape, box, Polygon, MultiPolygon, GeometryCollection, mapping
from shapely.ops import unary_union, transform as geom_transform
from records import ROOT, now

SEASONS=['spring','summer','late']
NAMES=['blue','green','red','nir','rededge1','rededge2','swir16','swir22','ndvi','mndwi']
SL=np.s_[16:272,16:272]

def reflectance_offsets(scene):
    p=scene['properties'];flag=p.get('earthsearch:boa_offset_applied')
    try:baseline=float(p.get('s2:processing_baseline'))
    except (ValueError,TypeError):baseline=None
    scales=np.array([float((scene['assets'][b].get('raster:bands') or [{}])[0].get('scale',.0001))
        for b in NAMES[:8]],dtype=np.float32)
    if flag is True or (baseline is not None and baseline<4):
        offsets=np.zeros(8,dtype=np.float32);rule='already harmonized or pre-baseline-4; no extra offset'
    elif flag is False and baseline is not None and baseline>=4:
        offsets=-1000*scales;rule='explicitly unharmonized baseline>=4; subtract 1000 DN'
    else:raise RuntimeError('Unresolved BOA harmonization state: '+scene['id'])
    return scales,offsets,rule

def optical(directory):
    composites=[];valids=[];radiometry=[]
    for season in SEASONS:
        selected=json.loads((directory/f'scenes-{season}.json').read_text())
        values=[]
        for k,scene in enumerate(selected):
            raw=np.load(directory/f'optical-{season}-{k}.npz')
            scale,offset,rule=reflectance_offsets(scene)
            data=raw['dn']*scale[:,None,None]+offset[:,None,None]
            clear=np.isin(raw['scl'],[2,4,5,6,7])&np.all(raw['dn']>0,axis=0)
            valid_values=data[:,clear]
            radiometry.append(dict(scene_id=scene['id'],rule=rule,declared_offsets=raw['offset'].tolist(),
                effective_offsets=offset.tolist(),scale=scale.tolist(),clear_pixels=int(clear.sum()),
                negative_reflectance_fraction=float(np.mean(valid_values<0)) if valid_values.size else None,
                reflectance_quantiles=np.quantile(valid_values,[.01,.5,.99]).tolist() if valid_values.size else []))
            data[:,~clear]=np.nan;values.append(data)
        if values:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',RuntimeWarning)
                comp=np.nanmedian(np.stack(values),axis=0)
        else:comp=np.full((8,288,288),np.nan,dtype=np.float32)
        composites.append(comp);valids.append(np.all(np.isfinite(comp),axis=0))
    comp=np.stack(composites)
    valid=np.stack(valids)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        mean=np.nanmean(comp,axis=0)
    for j in range(3):comp[j]=np.where(np.isfinite(comp[j]),comp[j],mean)
    indices=[]
    for j in range(3):
        b=comp[j]
        ndvi=np.divide(b[3]-b[2],b[3]+b[2],out=np.zeros_like(b[0]),where=np.abs(b[3]+b[2])>1e-6)
        mndwi=np.divide(b[1]-b[6],b[1]+b[6],out=np.zeros_like(b[0]),where=np.abs(b[1]+b[6])>1e-6)
        indices.append(np.concatenate([b,ndvi[None],mndwi[None]],axis=0))
    predictors=np.concatenate(indices+[(~valid).astype(np.float32)],axis=0).astype(np.float32)
    common=np.sum(valid,axis=0)>=2
    predictors[:,~common]=0
    return predictors,common,radiometry

def polygonal(g):
    if isinstance(g,(Polygon,MultiPolygon)):return g
    if isinstance(g,GeometryCollection):
        parts=[x for x in g.geoms if isinstance(x,(Polygon,MultiPolygon))]
        return unary_union(parts) if parts else Polygon()
    return Polygon()

def reference(directory,core,valid):
    projection=Transformer.from_crs(4326,core['crs'],always_xy=True)
    geometries=[];attrs=[];other=[];repairs=0;nonpolygon=0
    for path in sorted(directory.glob('nwi-batch-*.geojson')):
        for f in json.loads(path.read_text())['features']:
            g=geom_transform(projection.transform,shape(f['geometry']))
            if not g.is_valid:g=make_valid(g);repairs+=1
            g=polygonal(g)
            if g.is_empty:nonpolygon+=1;continue
            if str(f['properties']['ATTRIBUTE']).startswith('P'):
                geometries.append(g);attrs.append(f['properties'])
            else:other.append(g)
    # Connected components include shared boundaries and point contacts.
    parent=list(range(len(geometries)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(i,j):
        a,b=find(i),find(j)
        if a!=b:parent[max(a,b)]=min(a,b)
    if geometries:
        tree=STRtree(geometries)
        pairs=tree.query(geometries,predicate='intersects')
        for i,j in pairs.T:
            if i<j:union(int(i),int(j))
    groups={}
    for i in range(len(geometries)):groups.setdefault(find(i),[]).append(i)
    objects=[]
    for indices in groups.values():
        ids=sorted(int(attrs[i]['OBJECTID']) for i in indices)
        codes=sorted(set(str(attrs[i]['ATTRIBUTE']) for i in indices))
        objects.append(dict(geometry=unary_union([geometries[i] for i in indices]),source_ids=ids,codes=codes))
    objects.sort(key=lambda x:x['source_ids'][0])
    west,south,east,north=core['buffer_bounds'];transform=from_origin(west,north,10,10)
    raster=np.zeros((288,288),dtype=np.int32)
    if objects:raster=rasterize([(o['geometry'],i+1) for i,o in enumerate(objects)],
        out_shape=(288,288),transform=transform,fill=0,dtype='int32')
    othermask=rasterize([(g,1) for g in other],out_shape=(288,288),transform=transform,
        fill=0,dtype='uint8').astype(bool) if other else np.zeros((288,288),dtype=bool)
    palustrine=unary_union(geometries) if geometries else Polygon()
    all_water=unary_union(geometries+other) if geometries or other else Polygon()
    interior=palustrine.buffer(-20)
    pos_interior=rasterize([(interior,1)],out_shape=(288,288),transform=transform,
        fill=0,dtype='uint8').astype(bool) if not interior.is_empty else np.zeros((288,288),dtype=bool)
    water_buffer=all_water.buffer(20)
    outside_buffer=~rasterize([(water_buffer,1)],out_shape=(288,288),transform=transform,
        fill=0,dtype='uint8').astype(bool) if not water_buffer.is_empty else np.ones((288,288),dtype=bool)
    positive=raster>0
    eligible=valid&(~othermask|positive)
    core_box=box(*core['core_bounds'])
    rows=[]
    for i,o in enumerate(objects):
        g=o['geometry'];oid=i+1
        pixel=(raster[SL]==oid);n=int(pixel.sum());nv=int(np.sum(pixel&eligible[SL]))
        contained=bool(core_box.covers(g));area=float(g.area)
        distances=[float(g.distance(q['geometry'])) for j,q in enumerate(objects) if j!=i]
        nearest=min(distances) if distances else 160.0
        rows.append(dict(object_id=oid,core_id=core['core_id'],region_id=core['region_id'],
            source_ids=o['source_ids'],codes=o['codes'],vector_area_m2=area,raster_pixels=n,
            valid_pixels=nv,valid_fraction=nv/n if n else None,wholly_in_core=contained,
            main_eligible=contained and area>=2000 and nv>0,
            size_bin='small' if area<10000 else 'medium' if area<100000 else 'large',
            nearest_other_m=min(nearest,160.0),isolated_50m=nearest>=50,
            interior_pixels=int(np.sum(pixel&pos_interior[SL]&eligible[SL]))))
    diagnostics=dict(source_palustrine_polygons=len(geometries),other_aquatic_polygons=len(other),
        dissolved_components=len(objects),invalid_geometry_repairs=repairs,nonpolygon_geometries=nonpolygon,
        palustrine_pixels=int(np.sum(positive[SL])),other_aquatic_pixels=int(np.sum(othermask[SL])),
        excluded_other_overlap_pixels=int(np.sum((othermask&positive)[SL])),
        fully_contained_objects=sum(x['wholly_in_core'] for x in rows),
        sub_mmu_objects=sum(x['wholly_in_core'] and x['vector_area_m2']<2000 for x in rows),
        zero_pixel_objects=sum(x['wholly_in_core'] and x['raster_pixels']==0 for x in rows),
        zero_valid_pixel_objects=sum(x['wholly_in_core'] and x['valid_pixels']==0 for x in rows))
    return dict(y=positive[SL].astype(np.uint8),valid=eligible[SL],objects=raster[SL],
                positive_interior=pos_interior[SL]&eligible[SL],
                negative_interior=outside_buffer[SL]&eligible[SL]&~positive[SL]),rows,diagnostics

def build(directory,output):
    info=json.loads((directory/'core.json').read_text());core=info['core']
    complete=json.loads((directory/'complete.json').read_text())
    if not complete['quality']['technical_coverage_pass']:
        return dict(core_id=core['core_id'],status='technical_coverage_failure',quality=complete['quality'])
    raw=np.load(directory/'embedding.npz')['values']
    embeddings=np.sign(raw.astype(np.float32))*(raw.astype(np.float32)/127.5)**2
    embed_valid=np.all(raw!=-128,axis=0)
    s2,valid,radiometry=optical(directory);valid&=embed_valid
    refs,objects,diagnostics=reference(directory,core,valid)
    optical_buffer=np.moveaxis(s2,0,-1)
    context_buffer=context_features(optical_buffer,valid)
    values=dict(aef=np.moveaxis(embeddings[:,16:272,16:272],0,-1),
                optical=optical_buffer[SL],optical_context=context_buffer[SL],**refs)
    output.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(output/(core['core_id']+'.npz'),**values)
    reference_output=output.parent/'references';reference_output.mkdir(parents=True,exist_ok=True)
    reference_path=reference_output/(core['core_id']+'.npz')
    np.savez_compressed(reference_path,**refs)
    meta=dict(core=core,project=info['project'],created_at_utc=now(),status='complete',
        objects=objects,reference_diagnostics=diagnostics,radiometry=radiometry,
        quality=complete['quality'],optical_feature_names=[season+'_'+band for season in SEASONS for band in NAMES]
            +[season+'_missing' for season in SEASONS],
        input_complete_sha256=hashlib.sha256((directory/'complete.json').read_bytes()).hexdigest(),
        feature_file_sha256=hashlib.sha256((output/(core['core_id']+'.npz')).read_bytes()).hexdigest(),
        reference_path=str(reference_path.relative_to(ROOT)),
        reference_file_sha256=hashlib.sha256(reference_path.read_bytes()).hexdigest())
    (output/(core['core_id']+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
    return dict(core_id=core['core_id'],status='complete',positive_pixels=int(refs['y'][refs['valid']].sum()),
        common_valid_pixels=int(refs['valid'].sum()),eligible_small_objects=sum(o['main_eligible'] and o['size_bin']=='small' for o in objects),
        diagnostics=diagnostics)

def context_features(optical,valid):
    # Use the retrieval buffer in source construction for the final context version.
    # This helper accepts a complete buffered field when called by the builder.
    result=[optical]
    for sigma in [1.,2.]:
        weight=gaussian_filter(valid.astype(np.float32),sigma,mode='nearest')
        smooth=np.empty(optical.shape[:-1]+(optical.shape[-1]-3,),dtype=optical.dtype)
        for j in range(optical.shape[-1]-3):
            numerator=gaussian_filter(np.where(valid,optical[...,j],0),sigma,mode='nearest')
            smooth[...,j]=np.divide(numerator,weight,out=np.zeros_like(weight),where=weight>1e-8)
        result.append(smooth)
    return np.concatenate(result,axis=-1)

def main():
    p=argparse.ArgumentParser();p.add_argument('--cores',nargs='*');p.add_argument('--out',default='data/derived/features')
    a=p.parse_args();output=ROOT/a.out
    directories=sorted((ROOT/'data/main/cores').iterdir())
    if a.cores:directories=[d for d in directories if d.name in a.cores]
    for directory in directories:
        if not (directory/'complete.json').exists():continue
        result=build(directory,output);print(json.dumps(result),flush=True)

if __name__=='__main__':main()
