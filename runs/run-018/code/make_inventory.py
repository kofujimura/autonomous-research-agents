"""Hash research artifacts, including raw inputs and failures; no secret output."""
from pathlib import Path
import argparse,hashlib,json
from records import ROOT,now

EXCLUDED_COMPONENTS={'.git','.venv','.cache','__pycache__','.matplotlib-cache'}

def inventory(root):
 root=Path(root).resolve();scope=dict(generated_at_utc=now(),algorithm='SHA-256',excluded_path_components=sorted(EXCLUDED_COMPONENTS),excluded_basenames=['SHA256SUMS'],nonbundled_paths={'data/pilot/aef_index.csv':'Large public tile-locator index excluded from Git; needed for reacquisition only. All selected raw measurements required for offline analysis are bundled.'},nonbundled_prefixes={'verification-work/':'Fresh author-verification Git archives and regenerated outputs are excluded from Git as duplicated workspaces, but their raw files are hashed here. Copy these optional workspaces from the local submission directory for complete inventory checking. Source commits and verification reports are bundled; all scientific inputs and canonical predictions are bundled separately.'},scope='All other files under the research directory, including raw measurements, failed experiment outputs, verification workspace inputs/outputs, logs, plans, paper, figures and submission snapshots. Hashes establish content consistency, not independence or tamper-proofness.')
 (root/'hash-scope.json').write_text(json.dumps(scope,indent=2)+'\n');entries=[]
 for p in sorted(root.rglob('*')):
  if not p.is_file() or any(c in EXCLUDED_COMPONENTS for c in p.relative_to(root).parts) or p.name=='SHA256SUMS':continue
  h=hashlib.sha256()
  with p.open('rb') as stream:
   for block in iter(lambda:stream.read(1048576),b''):h.update(block)
  entries.append((h.hexdigest(),str(p.relative_to(root))))
 (root/'SHA256SUMS').write_text(''.join(f'{h}  {path}\n' for h,path in entries));print(json.dumps(dict(file_n=len(entries),bytes=sum((root/p).stat().st_size for _,p in entries),output='SHA256SUMS')))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();inventory(a.root)
