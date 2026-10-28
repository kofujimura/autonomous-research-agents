"""Separate exploratory geographic cohort; never changes the main population."""
import argparse,datetime,json,time
import numpy as np,pandas as pd
from records import ROOT,now,digest,event

ORDER='data/validation-order-v1.json';LEDGER='data/validation-selection-results.jsonl';PLAN='protocol/plan-v13-additional-geography.md'
def write_new(path,data):
    p=ROOT/path
    if p.exists():raise FileExistsError('Preserve prior frozen validation artifacts')
    p.write_text(json.dumps(data,indent=2)+'\n')

def freeze_order():
    prior={r['landscape_id']:r for r in map(json.loads,(ROOT/'data/selection-results.jsonl').read_text().splitlines())}
    used={r['supercell'] for r in prior.values() if r['status']=='accepted'}
    original=json.loads((ROOT/'data/selection-order.json').read_text())
    candidates=[r for r in original['candidates'] if r['split']=='test' and r['landscape_id'] not in prior and r['supercell'] not in used]
    data=dict(fixed_at_utc=now(),plan_path=PLAN,target=10,candidates=candidates,
        available_supercells=len(set(r['supercell'] for r in candidates)),
        main_order_sha256=digest(ROOT/'data/selection-order.json'),main_ledger_sha256=digest(ROOT/'data/selection-results.jsonl'),
        excluded_ids=sorted(prior),excluded_accepted_supercells=sorted(used),outcome_use='No new-candidate entropy/change outcome used')
    write_new(ORDER,data)
    event('additional_cohort_order_fixed','Freeze unused test-supercell metadata order, without new diversity outcomes',[ORDER])
    print(json.dumps(dict(candidates=len(candidates),supercells=data['available_supercells'],target=data['target'])))

def cache_bytes():return sum(p.stat().st_size for p in (ROOT/'data/labels-chunks').rglob('*') if p.is_file())

def acquire(max_seconds):
    assert not (ROOT/'data/validation-cohort-v1.json').exists(),'Cohort already sealed'
    acquisitions=[]
    for path in (ROOT/'experiments').glob('*/run.json'):
        r=json.loads(path.read_text());cmd=r.get('command',[])
        if any(str(v).endswith('validation_geography.py') for v in cmd) and 'acquire' in cmd:acquisitions.append(r)
    assert len(acquisitions)<=2,'Prespecified two acquisition batches exhausted'
    if (ROOT/'data/validation-acquisition-resource-stop.json').exists():
        print('STOP: previous prespecified resource/time stop remains in force');return
    refreshed=all((ROOT/f'results/inference/logistic-broad-refreshed-{r}/analysis.json').exists() for r in ['tessera','alphaearth'])
    assert refreshed or (ROOT/'protocol/refreshed-stop.json').exists(),'Finish or explicitly stop refreshed comparison first'
    from study_tallies import tally
    t=tally();limit=10*1024**3
    if t['storage_unique_inode_bytes']+768*1024**2>limit:
        event('additional_cohort_resource_stop','Insufficient reserved storage headroom for additional labels',[PLAN],unique_bytes=t['storage_unique_inode_bytes'])
        print('STOP: insufficient reserved headroom');return
    baseline=ROOT/'data/validation-resource-baseline.json'
    if not baseline.exists():
        baseline.write_text(json.dumps(dict(observed_at_utc=now(),range_cache_bytes=cache_bytes(),unique_inode_bytes=t['storage_unique_inode_bytes']),indent=2)+'\n')
    starting=json.loads(baseline.read_text())['range_cache_bytes'];cap=128*1024**2
    deadline=datetime.datetime.fromisoformat(json.loads((ROOT/'manifest.json').read_text())['first_draft_deadline_utc'].replace('Z','+00:00'))-datetime.timedelta(hours=2)
    data=json.loads((ROOT/ORDER).read_text());flag={'stop':False}
    import swiss_labels
    ordinary=swiss_labels.read_range
    def guarded(url,start,length,*args,**kwargs):
        if datetime.datetime.now(datetime.timezone.utc)>=deadline or cache_bytes()-starting+length>cap:
            flag['stop']=True
            raise RuntimeError('Additional-reference acquisition stopped at prespecified time/cache-growth reserve')
        return ordinary(url,start,length,*args,**kwargs)
    swiss_labels.read_range=guarded
    remaining=(deadline-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
    if remaining<180:print('STOP: no bounded acquisition time remains');return
    swiss_labels.collect(99,max_seconds=min(max_seconds,int(remaining)),ledger_path=LEDGER,
        output_path='data/validation-landscapes',order_items=data['candidates'],quotas={'train':0,'calibration':0,'test':10},
        distinct_supercells=True,should_stop=lambda:flag['stop'])
    if flag['stop']:
        (ROOT/'data/validation-acquisition-resource-stop.json').write_text(json.dumps(dict(observed_at_utc=now(),
            cache_growth_bytes=cache_bytes()-starting,reason='Prespecified time/cache-growth stop'),indent=2)+'\n')
    event('additional_cohort_acquisition_batch','Completed bounded additional-reference acquisition batch',[LEDGER],
        cache_growth_bytes=cache_bytes()-starting,resource_stop=flag['stop'])

def freeze_cohort():
    records=[json.loads(s) for s in (ROOT/LEDGER).read_text().splitlines()] if (ROOT/LEDGER).exists() else []
    latest={r['landscape_id']:r for r in records};accepted=[r for r in latest.values() if r['status']=='accepted']
    assert len(set(r['supercell'] for r in accepted))==len(accepted)
    tax=json.loads((ROOT/'data/taxonomy.json').read_text());h=pd.read_csv(ROOT/'sources/swisscrop25-crop-classes.csv').dropna(subset=['Crop_Label_lv1','Crop_Label_lv3'])
    parents=dict(h[['Crop_Label_lv1','Crop_Label_lv3']].values);ids=[i for i,name in enumerate(tax['fine']) if parents.get(name)=='Arable Land']
    context=[]
    for r in accepted:
        assert digest(ROOT/r['path'])==r['sha256']
        with np.load(ROOT/r['path']) as z:
            arable=z['support']&np.isin(z['fine_raster'],ids).all(axis=0)
            baseline=z['fine_raster'][0][z['baseline_agricultural']]
            names=np.asarray(tax['fine'],object)[baseline]
            groups=np.asarray([parents.get(name) for name in names],object)
        context.append(dict(landscape_id=r['landscape_id'],stable_arable_pixels=int(arable.sum()),
            baseline_arable_fraction=float((groups=='Arable Land').mean()),baseline_grassland_fraction=float((groups=='Grassland').mean())))
    obj=dict(fixed_at_utc=now(),plan_path=PLAN,order_path=ORDER,order_sha256=digest(ROOT/ORDER),selection_ledger=LEDGER,
        ledger_sha256=digest(ROOT/LEDGER) if (ROOT/LEDGER).exists() else None,landscapes=accepted,context=context,
        accepted_landscapes=len(accepted),eligible_arable_cases=sum(r['stable_arable_pixels']>=1024 for r in context),
        candidate_status_counts={s:sum(r['status']==s for r in latest.values()) for s in ['accepted','ineligible','failed']},
        scope='Additional main-cohort-absent test supercells; first obtained eligible candidate per cell; no national inference or independent reproduction')
    write_new('data/validation-cohort-v1.json',obj)
    event('additional_cohort_fixed','Freeze attained additional-reference cohort before its inference',['data/validation-cohort-v1.json',LEDGER])
    print(json.dumps({k:obj[k] for k in ['accepted_landscapes','eligible_arable_cases','candidate_status_counts']}))

def analyse():
    c=json.loads((ROOT/'data/validation-cohort-v1.json').read_text());n=c['accepted_landscapes']
    if not n:
        print('No additional eligible reference cases; no inference claimed');return
    assert digest(ROOT/LEDGER)==c['ledger_sha256'],'Cohort changed after freeze'
    from reference_frame_analysis import run
    from reference_frame_summaries import run as summarize
    run('data/population-source-v1.json','results/additional-geography',selection_ledger=LEDGER,expected_landscapes=n,plan_path=PLAN)
    summarize('results/additional-geography','results/additional-geography-context')
    if c['eligible_arable_cases']>=5:
        run('data/population-source-v1.json','results/additional-geography-arable',arable_only=True,
            selection_ledger=LEDGER,expected_landscapes=n,plan_path=PLAN)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['freeze-order','acquire','freeze-cohort','analyse']);p.add_argument('--max-seconds',type=int,default=1650);a=p.parse_args()
    if a.stage=='freeze-order':freeze_order()
    elif a.stage=='acquire':acquire(a.max_seconds)
    elif a.stage=='freeze-cohort':freeze_cohort()
    else:analyse()
