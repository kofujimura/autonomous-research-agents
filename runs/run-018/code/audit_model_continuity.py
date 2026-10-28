"""Hash continuity of the previously refitted polygon model and current inputs."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from records import ROOT,now

def audit(root,commit,out):
 root=Path(root)
 files=['code/analyse_matching.py','code/analysis_paths.py','code/records.py',
        'code/derive_features.py','code/derive_polygon_features.py','code/collect_polygon.py',
        'analysis/features-corrected/features-2024.npz','analysis/features-corrected/rows-2024.json',
        'analysis/polygon-features-v3/C/features-2024.npz','analysis/polygon-features-v3/C/rows-2024.json']
 rows=[]
 for rel in files:
  old=subprocess.check_output(['git','-C',str(root),'show',commit+':'+rel]);current=(root/rel).read_bytes()
  rows.append(dict(path=rel,historical_sha256=hashlib.sha256(old).hexdigest(),current_sha256=hashlib.sha256(current).hexdigest(),exact_bytes_equal=old==current))
 result=dict(checked_at_utc=now(),reference_commit=commit,passed=all(r['exact_bytes_equal'] for r in rows),files=rows,scope='Hash continuity with the complete first-draft author verification source. That source links to the older full polygon refit through its separately retained equivalence record; this is not a new polygon model refit.')
 assert result['passed'];Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,files=len(rows),reference_commit=commit)))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--reference-commit',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();audit(a.root,a.reference_commit,a.out)
