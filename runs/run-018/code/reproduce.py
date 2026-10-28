"""Offline read-only-source verification. All regenerated artifacts go to --out."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,time
sys.dont_write_bytecode=True
from records import now

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def files(root):return {str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}
def arrays_equal(a,b):
 import numpy as np
 if a.dtype.kind in 'fc' and b.dtype.kind in 'fc':return bool(np.array_equal(a,b,equal_nan=True))
 return bool(np.array_equal(a,b))
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--refit',choices=['none','primary','polygonC'],default='none');p.add_argument('--rotations',type=int,nargs='+',default=[0,1,2,3]);a=p.parse_args();source=a.source.resolve();out=a.out.resolve()
 if out==source or source in out.parents:raise RuntimeError('--out must be outside the submitted source copy')
 if out.exists() and any(out.iterdir()):raise RuntimeError('--out must be new or empty')
 out.mkdir(parents=True,exist_ok=True);os.environ['PYTHONDONTWRITEBYTECODE']='1';os.environ['MPLCONFIGDIR']=str(out/'.matplotlib-cache');started_at_utc=now();start=time.monotonic();before=files(source);checks=[];commands=[]
 # This entry point must be executed from the copied code, never by importing a different checkout.
 assert Path(__file__).resolve().parents[1]==source,'Execute the entry point inside the supplied source copy'
 import numpy as np,pandas as pd
 from derive_features import derive
 from audit_data import audit
 from collect_polygon import points
 from summarize_matching import summarize
 from build_report_data import build
 from make_figures import make
 from render_manuscript import render
 from build_claims import build as build_claims
 from audit_constant_controls import audit as constant_audit
 from audit_polygon_conditions import audit as polygon_audit
 from analysis_paths import paths
 canonical=paths(source)
 shutil.copy2(source/'manifest.json',out/'manifest.json')
 for rel in ['data/corrections/edge-correction-manifest.json','analysis/tile-edge-audit/feature-correction-check.json']:
  dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/rel,dest)
 for change in json.loads((source/'analysis/tile-edge-audit/feature-correction-check.json').read_text()):
  original=np.load(source/'analysis'/change['source']/'features-2024.npz');corrected=np.load(source/'analysis'/change['corrected']/'features-2024.npz')
  for key,expected_rows in change['changed_rows'].items():
   left=original[key];right=corrected[key];same=(left==right)|(np.isnan(left)&np.isnan(right));different=np.flatnonzero(~same.all(axis=tuple(range(1,same.ndim)))).tolist();assert different==expected_rows,('correction changed rows',change['source'],key)
 checks.append(dict(check='reported changed feature rows from preserved initial/corrected arrays',passed=True))
 def compare_npz(original,regenerated,label):
  x=np.load(original);y=np.load(regenerated);assert set(x.files)==set(y.files),(label,'keys')
  result={k:arrays_equal(x[k],y[k]) for k in x.files};checks.append(dict(check=label,arrays=result,passed=all(result.values())));assert all(result.values()),(label,result)
 derived=out/canonical['primary_features'];derive(source,derived,aef_overrides=source/'data/corrections')
 compare_npz(source/canonical['primary_features']/'features-2024.npz',derived/'features-2024.npz','primary features from raw patches and physical grids')
 assert json.loads((source/canonical['primary_features']/'rows-2024.json').read_text())==json.loads((derived/'rows-2024.json').read_text());checks.append(dict(check='primary row metadata',passed=True))
 if (source/'analysis/features-centre-corrected/features-2024.npz').exists():
  centre=out/'analysis/features-centre-corrected';derive(source,centre,centre=True,aef_overrides=source/'data/corrections')
  compare_npz(source/'analysis/features-centre-corrected/features-2024.npz',centre/'features-2024.npz','centre-pixel boundary features from raw patches')
 if (source/canonical['recent_features']/'features-2024.npz').exists():
  recent_derived=out/canonical['recent_features'];derive(source,recent_derived,pattern='S??',aef_overrides=source/'data/corrections')
  compare_npz(source/canonical['recent_features']/'features-2024.npz',recent_derived/'features-2024.npz','recent features from raw patches and physical grids')
 audit(source,out/'input-audit')
 if (source/'data/polygon/points-manifest.json').exists():
  for rid in sorted(p.name for p in (source/'data/polygon').glob('R??') if (p/'points.npz').exists()):
   points(rid,out/'regenerated-polygon-points');compare_npz(source/f'data/polygon/{rid}/points.npz',out/f'regenerated-polygon-points/{rid}/points.npz','polygon pixel selection '+rid)
 if (source/canonical['polygon_features']/'derivation-record.json').exists():
  from derive_polygon_features import derive as polygon_derive
  polygon_derive(source,out/canonical['polygon_features'],source/canonical['primary_features'])
  for c in ['A','B','C','D']:compare_npz(source/canonical['polygon_features']/c/'features-2024.npz',out/canonical['polygon_features']/c/'features-2024.npz','polygon condition '+c)
 if (source/'analysis/year-common/manifest.json').exists():
  from prepare_year_features import prepare as prepare_years
  annual=json.loads(json.dumps(prepare_years(source,out/'analysis/year-common')));archived=json.loads((source/'analysis/year-common/manifest.json').read_text())
  for key in ['common_ids','common_n','excluded_n','reuse_original_2024_fits','year_quality','physical_arrays_identical']:
   assert annual[key]==archived[key],('annual common cohort',key)
  for year in [2024,2023,2021]:
   compare_npz(source/f'analysis/year-common/{year}/features-{year}.npz',out/f'analysis/year-common/{year}/features-{year}.npz','annual common-cohort features '+str(year))
 # Regenerate summaries directly from saved decisions. No source file is written.
 summary_dirs=sorted({p.parent for p in (source/'analysis').rglob('metrics.csv') if p.parent.name.endswith('-summary')})
 for folder in summary_dirs:
  rel=folder.relative_to(source);meta=json.loads((folder/'summary.json').read_text());spec=meta.get('source_predictions')
  if spec:
   inp=Path(spec)
   if inp.is_absolute():
    original_root=Path(json.loads((source/'manifest.json').read_text())['research_directory']);inp=inp.relative_to(original_root)
  elif str(rel)=='analysis/primary-summary':inp=Path('analysis/main')
  elif str(rel)=='analysis/recent-summary':inp=Path('analysis/recent')
  elif str(rel)=='analysis/transfer-summary':inp=Path('analysis/transfer-combined')
  else:inp=rel.parent/rel.name.removesuffix('-summary')
  target=out/rel;summarize(source/inp,target)
  # Regenerated summaries must refer to the copied records in this workspace.
  # Keeping the absolute source-copy path loses them when report generation
  # resolves paths against the original research-directory manifest.
  summary_record=json.loads((target/'summary.json').read_text());summary_record['source_predictions']=str(inp);(target/'summary.json').write_text(json.dumps(summary_record,indent=2)+'\n')
  for r in range(4):
   detail=source/inp/f'r{r}/analysis-record.json'
   if detail.exists():
    dest=out/inp/f'r{r}';dest.mkdir(parents=True,exist_ok=True);shutil.copy2(detail,dest/'analysis-record.json')
  for name in ['metrics.csv','contrasts.csv','pool-counts.csv','fixed-screen-risk.csv']:
   x=pd.read_csv(folder/name);y=pd.read_csv(target/name);assert x.columns.tolist()==y.columns.tolist() and x.shape==y.shape,(str(rel),name,'shape')
   for col in x:
    if pd.api.types.is_numeric_dtype(x[col]):assert np.allclose(x[col],y[col],rtol=0,atol=1e-12,equal_nan=True),(str(rel),name,col)
    else:assert x[col].fillna('<NA>').equals(y[col].fillna('<NA>')),(str(rel),name,col)
  checks.append(dict(check='summary '+str(rel),passed=True))
 # Decoder outputs are observational model measurements; copy to the output workspace for report generation.
 for r in range(4):
  dest=out/canonical['primary_predictions']/f'r{r}';dest.mkdir(parents=True,exist_ok=True);shutil.copy2(source/canonical['primary_predictions']/f'r{r}/decoder-probabilities.npz',dest/'decoder-probabilities.npz');shutil.copy2(source/canonical['primary_predictions']/f'r{r}/predictions.csv',dest/'predictions.csv')
 if (source/'analysis/constant-audit/audit.json').exists():
  constant_audit(source,out/'analysis/constant-audit')
  assert pd.read_csv(source/'analysis/constant-audit/counts.csv').equals(pd.read_csv(out/'analysis/constant-audit/counts.csv'));checks.append(dict(check='constant feature/choice/confidence/screen audit',passed=True))
 if (source/'analysis/constant-corrected-audit/audit.json').exists():
  constant_audit(source,out/'analysis/constant-corrected-audit',corrected=True)
  assert pd.read_csv(source/'analysis/constant-corrected-audit/counts.csv').equals(pd.read_csv(out/'analysis/constant-corrected-audit/counts.csv'));checks.append(dict(check='corrected-input constant feature/choice/confidence/screen audit',passed=True))
 if (source/'analysis/polygon-condition-audit/result.json').exists():
  polygon_audit(source,out/'analysis/polygon-condition-audit');checks.append(dict(check='polygon input/prediction factor isolation',passed=True))
 if (source/'analysis/whitening-svd-audit/result.json').exists():
  from audit_metric_transforms import audit as whitening_audit
  whitening_audit(source,out/'analysis/whitening-svd-audit');checks.append(dict(check='32 training-only whitening vectors by separate author SVD calculation',passed=True))
 if (source/'analysis/year-condition-audit/result.json').exists():
  from audit_year_conditions import audit as year_audit
  year_audit(source,out/'analysis/year-condition-audit');checks.append(dict(check='annual physical-only predictions and role/pair invariance',passed=True))
 pool_path=canonical.get('pool_influence')
 if pool_path and (source/pool_path/'result.json').exists():
  from audit_pool_influence import audit as pool_audit
  pool_audit(source,out/pool_path)
  for name in ['fixed-nontrivial.csv','leave-window-out.csv','window-counts.csv','score-ambiguity.csv']:
   x=pd.read_csv(source/pool_path/name);y=pd.read_csv(out/pool_path/name);assert x.shape==y.shape and x.columns.tolist()==y.columns.tolist()
   for col in x:
    if pd.api.types.is_numeric_dtype(x[col]):assert np.allclose(x[col],y[col],rtol=0,atol=1e-12,equal_nan=True),(name,col)
    else:assert x[col].fillna('<NA>').equals(y[col].fillna('<NA>')),(name,col)
  checks.append(dict(check='conditional common screens and all-window influence diagnostic',passed=True))
 budget_path=canonical.get('budget_allocation')
 if budget_path and (source/budget_path/'result.json').exists():
  from analyse_budget_allocation import analyse as budget_analyse
  budget_analyse(source,out/budget_path)
  for name in ['metrics.csv','contrasts.csv','region-metrics.csv','vegetation-coverage.csv','selected-050.csv']:
   x=pd.read_csv(source/budget_path/name);y=pd.read_csv(out/budget_path/name);assert x.shape==y.shape and x.columns.tolist()==y.columns.tolist()
   for col in x:
    if pd.api.types.is_numeric_dtype(x[col]):assert np.allclose(x[col],y[col],rtol=0,atol=1e-12,equal_nan=True),(name,col)
    else:assert x[col].fillna('<NA>').equals(y[col].fillna('<NA>')),(name,col)
  checks.append(dict(check='screening-budget allocation policies and accepted queries',passed=True))
 if (source/'analysis/input-change-audit/result.json').exists():
  from audit_input_changes import audit as change_audit
  change_audit(source,out/'analysis/input-change-audit')
  for name in ['physical-summary.csv','physical-features.csv','physical-wetlands.csv','embedding-summary.csv','embedding-wetlands.csv']:
   x=pd.read_csv(source/'analysis/input-change-audit'/name);y=pd.read_csv(out/'analysis/input-change-audit'/name);assert x.shape==y.shape and x.columns.tolist()==y.columns.tolist()
   for col in x:
    if pd.api.types.is_numeric_dtype(x[col]):assert np.allclose(x[col],y[col],rtol=0,atol=1e-12,equal_nan=True),(name,col)
    else:assert x[col].fillna('<NA>').equals(y[col].fillna('<NA>')),(name,col)
  checks.append(dict(check='physical and embedding input-change magnitudes',passed=True))
 if (source/'analysis/strong-transfer-audit/result.json').exists():
  from audit_strong_transfer import audit as strong_transfer_audit
  strong_transfer_audit(source,out/'analysis/strong-transfer-audit');checks.append(dict(check='strong transfer pools, shared physical decisions, copied augmentations and whitening',passed=True))
 continuity=source/'analysis/review-model-continuity.json'
 if continuity.exists():
  evidence=json.loads(continuity.read_text());assert evidence['passed']
  for row in evidence['files']:assert digest(source/row['path'])==row['current_sha256']==row['historical_sha256'],row['path']
  checks.append(dict(check='current model and feature hashes agree with retained pre-review refit inputs',passed=True))
 review_path=canonical.get('review_reanalysis')
 if review_path:
  from analyse_review import analyse as review_analyse
  original=json.loads((source/review_path/'result.json').read_text())
  review_analyse(source,out/review_path,original['include_new_seeds'])
  for original_csv in sorted((source/review_path).glob('*.csv')):
   x=pd.read_csv(original_csv);y=pd.read_csv(out/review_path/original_csv.name)
   assert x.shape==y.shape and x.columns.tolist()==y.columns.tolist(),original_csv.name
   for col in x:
    if pd.api.types.is_numeric_dtype(x[col]):assert np.allclose(x[col],y[col],rtol=0,atol=1e-12,equal_nan=True),(original_csv.name,col)
    else:assert x[col].fillna('<NA>').equals(y[col].fillna('<NA>')),(original_csv.name,col)
  checks.append(dict(check='post-review paired uncertainty, seed/null synthesis, window contributions and planned subgroups',passed=True))
 build(out,out/'analysis/report-data');make(out/'analysis/report-data',out/'figures')
 for name in ['paper-template.md','references.md']:shutil.copy2(source/name,out/name)
 if (source/'analysis/verification-status.json').exists():shutil.copy2(source/'analysis/verification-status.json',out/'analysis/verification-status.json')
 render(out,out/'paper.md')
 assert (source/'paper.md').read_text()==(out/'paper.md').read_text(),'Complete regenerated manuscript text differs'
 checks.append(dict(check='complete manuscript text and displayed numerical fields regenerated exactly',passed=True))
 if (source/'claims.jsonl').exists():
  build_claims(out)
  original_claims=[json.loads(line) for line in (source/'claims.jsonl').read_text().splitlines()]
  rebuilt_claims=[json.loads(line) for line in (out/'claims.jsonl').read_text().splitlines()]
  def same_claim_value(x,y):
   if isinstance(x,dict):return isinstance(y,dict) and x.keys()==y.keys() and all(same_claim_value(x[k],y[k]) for k in x)
   if isinstance(x,list):return isinstance(y,list) and len(x)==len(y) and all(same_claim_value(a,b) for a,b in zip(x,y))
   if isinstance(x,(int,float)) and not isinstance(x,bool):return isinstance(y,(int,float)) and bool(np.isclose(x,y,atol=1e-12,rtol=0))
   return x==y
  assert same_claim_value(original_claims,rebuilt_claims),'Generated claim statements or expected evidence differ'
  checks.append(dict(check='main claim statements and expected numerical evidence regenerated',passed=True))
 if a.refit in ['primary','polygonC']:
  refit_inputs=derived if a.refit=='primary' else out/canonical['polygon_features']/'C'
  saved_predictions=source/canonical['primary_predictions'] if a.refit=='primary' else source/'analysis/polygon/C-rf'
  for r in a.rotations:
   assert r in range(4);target=out/f'refit/{a.refit}/r{r}';target.parent.mkdir(parents=True,exist_ok=True);command=[sys.executable,'-B',str(source/'code/analyse_matching.py'),'--inputs',str(refit_inputs),'--rotation',str(r),'--output',str(target)];commands.append(command)
   remaining=1740-(time.monotonic()-start)
   if remaining<60:raise RuntimeError('Insufficient verification time for another fit')
   result=subprocess.run(command,timeout=remaining)
   assert result.returncode==0,('refit',r,result.returncode)
   x=pd.read_csv(saved_predictions/f'r{r}/predictions.csv').sort_values(['query_id','method']).reset_index(drop=True);y=pd.read_csv(target/'predictions.csv').sort_values(['query_id','method']).reset_index(drop=True);assert x.shape==y.shape
   for col in x:
    if pd.api.types.is_float_dtype(x[col]):assert np.allclose(x[col],y[col],atol=1e-12,rtol=0,equal_nan=True),('prediction',r,col)
    else:assert x[col].fillna('<NA>').equals(y[col].fillna('<NA>')),('prediction',r,col)
   compare_npz(saved_predictions/f'r{r}/roles-pairs.npz',target/'roles-pairs.npz',a.refit+' refit roles/pairs '+str(r));checks.append(dict(check=a.refit+' refit predictions '+str(r),passed=True))
 after=files(source);assert before==after,'Submitted source copy changed during verification';checks.append(dict(check='source contents and file list unchanged',passed=True))
 record=dict(start_time_utc=started_at_utc,end_time_utc=now(),elapsed_seconds=time.monotonic()-start,source=str(source),out=str(out),network_used=False,api_calls=0,mode=a.refit,refit_rotations=a.rotations if a.refit in ['primary','polygonC'] else [],scope='All saved-decision summaries/figures and available raw-feature derivations; optional original-primary or polygon-conditionC refit. Other supplementary models are not refitted by this reduced entry point.',checks=checks,commands=commands,passed=True)
 (out/'verification-report.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(checks),elapsed_seconds=record['elapsed_seconds'])))
if __name__=='__main__':main()
