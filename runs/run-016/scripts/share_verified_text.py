"""Save storage by sharing exact byte-identical completed self-rerun text outputs."""
import hashlib,json,os,subprocess
from records import ROOT,now,event,digest

def run():
    before=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])*1024
    canonical={};rows=[]
    # Restrict sharing to completed verification scientific text outputs. All values and paths
    # remain unchanged; these frozen outputs are never edited in later revisions.
    for path in sorted((p for p in (ROOT/'results').rglob('*') if p.is_file() and p.suffix in ['.csv','.jsonl','.json'])):
        canonical.setdefault((path.stat().st_size,digest(path)),path)
    for output in sorted((ROOT/'verification-work').glob('output*')):
        report=output/'verification-result.json'
        if not report.exists() or json.loads(report.read_text()).get('status')!='passed':continue
        for target in sorted((p for p in output.rglob('*') if p.is_file() and p.suffix in ['.csv','.jsonl','.json'])):
            key=(target.stat().st_size,digest(target));source=canonical.setdefault(key,target)
            if target.stat().st_ino==source.stat().st_ino:continue
            temporary=target.with_name(target.name+'.byte-identical-hardlink');assert not temporary.exists()
            os.link(source,temporary);os.replace(temporary,target)
            rows.append(dict(source=str(source.relative_to(ROOT)),target=str(target.relative_to(ROOT)),sha256=key[1],bytes=key[0]))
    after=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])*1024
    record=dict(observed_at_utc=now(),before_allocated_bytes=before,after_allocated_bytes=after,files_shared=len(rows),files=rows,
      scope='Only byte-identical CSV/JSONL/JSON in completed passed self-reruns; exact full-file SHA-256 match precedes hardlinking; every path/value retained. No original scientific file content changed.')
    (ROOT/'review/exact-csv-storage-sharing.json').write_text(json.dumps(record,indent=2)+'\n')
    event('verification_text_storage_shared','Share exact byte-identical scientific text files from completed passed self-reruns without changing scientific bytes',['review/exact-csv-storage-sharing.json'],saved_allocated_bytes=before-after)
    print(json.dumps({k:record[k] for k in ['observed_at_utc','before_allocated_bytes','after_allocated_bytes','files_shared']}))

if __name__=='__main__':run()
