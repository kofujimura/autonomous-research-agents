"""Download a public source with native curl TLS and record its provenance."""
from pathlib import Path
import argparse, hashlib, json, subprocess
from records import ROOT, now, append, event

def fetch(sid, url, output, licence='Not yet assessed; not approved as experimental input', timeout=120):
    path = ROOT / output
    path.parent.mkdir(parents=True, exist_ok=True)
    start = now()
    proc = subprocess.run(['curl','--fail','--silent','--show-error','--location',
                           '--max-time',str(timeout),'--output',str(path),url],
                          capture_output=True, text=True, timeout=timeout+10)
    item = dict(source_id=sid, url=url, requested_at_utc=start, obtained_at_utc=now(),
                path=output, licence=licence, licence_checked_at_utc=None,
                range_checked='Downloaded, relevant passages not yet inspected',
                exit_code=proc.returncode, error=proc.stderr.strip() or None,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None,
                bytes=path.stat().st_size if path.exists() else 0, bundled=path.exists())
    append('sources.jsonl', item)
    print(json.dumps(item))
    return proc.returncode

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('source_id');p.add_argument('url');p.add_argument('output')
    p.add_argument('--licence',default='Not yet assessed; not approved as experimental input')
    p.add_argument('--timeout',type=int,default=120)
    a=p.parse_args()
    raise SystemExit(fetch(a.source_id,a.url,a.output,a.licence,a.timeout))
