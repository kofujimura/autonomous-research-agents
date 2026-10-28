"""Check a submitted inventory without writing to the submitted source copy."""
from pathlib import Path
import argparse,hashlib,json

def check(root,allow_unbundled=False):
 root=Path(root).resolve();scope=json.loads((root/'hash-scope.json').read_text());failures=[];skipped=[];checked=0
 for line in (root/'SHA256SUMS').read_text().splitlines():
  expected,name=line.split('  ',1);p=(root/name).resolve();assert p.is_relative_to(root),'Unsafe inventory path'
  if not p.exists():
   if allow_unbundled and (name in scope['nonbundled_paths'] or any(name.startswith(prefix) for prefix in scope.get('nonbundled_prefixes',{}))):skipped.append(name);continue
   failures.append(dict(path=name,reason='missing'));continue
  h=hashlib.sha256()
  with p.open('rb') as stream:
   for block in iter(lambda:stream.read(1048576),b''):h.update(block)
  checked+=1
  if h.hexdigest()!=expected:failures.append(dict(path=name,reason='hash mismatch'))
 return dict(checked=checked,skipped_nonbundled=skipped,failures=failures,passed=not failures)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--allow-unbundled',action='store_true');p.add_argument('--out',type=Path);a=p.parse_args();r=check(a.root,a.allow_unbundled)
 if a.out:
  assert not a.out.resolve().is_relative_to(a.root.resolve());a.out.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r));raise SystemExit(0 if r['passed'] else 1)
