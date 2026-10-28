"""Download a small number of ordinary public resources with provenance."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request
from records import ROOT, append, now
import truststore

# Use macOS's trust store while retaining certificate verification.
truststore.inject_into_ssl()

def fetch(url, path, source_id, license_note, purpose, timeout=60):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return {'cached':True, 'path':path, 'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
    request = urllib.request.Request(url, headers={'User-Agent':'FreeResearch017/1.0 (public research; no crawling)'})
    started = now()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read(150*1024*1024+1)
        if len(data)>150*1024*1024:
            raise RuntimeError('Resource exceeds single-resource limit')
        headers = dict(response.headers)
        final_url = response.url
    dest.write_bytes(data)
    result = dict(source_id=source_id, url=url, final_url=final_url, obtained_at_utc=now(),
                  retrieval_started_at_utc=started, path=path, bytes=len(data),
                  sha256=hashlib.sha256(data).hexdigest(), license=license_note,
                  purpose=purpose, range_checked='downloaded; passage review pending',
                  response_headers=headers, bundled=True)
    append('sources.jsonl', result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('url'); p.add_argument('path'); p.add_argument('source_id')
    p.add_argument('--license',default='Terms pending; do not use as experimental data before checking')
    p.add_argument('--purpose',default='Prior-work or feasibility check')
    a=p.parse_args()
    r=fetch(a.url,a.path,a.source_id,a.license,a.purpose)
    print(json.dumps({k:r[k] for k in ['path','sha256'] if k in r}))
