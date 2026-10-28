"""Small local record helpers. No network and no secret output."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, fcntl

ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')

def append(path, obj):
    with (ROOT / path).open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')
        f.flush()

def event(kind, summary, paths=(), related=(), **extra):
    with (ROOT/'logs/events-allocation.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        lines = [json.loads(x) for x in (ROOT/'events.jsonl').read_text().splitlines() if x]
        eid = 'E%04d' % (1 + max([int(x['event_id'][1:]) for x in lines], default=0))
        append('events.jsonl', dict(event_id=eid, observed_at_utc=now(), type=kind,
               summary=summary, artifact_paths=list(paths), related_ids=list(related), **extra))
    return eid

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def secret_scan():
    value = os.environ.get('FREE_RESEARCH_OPENAI_API_KEY')
    if not value:
        print('Secret scan: variable unset; no value available for comparison.')
        return {'key_is_set':False,'found':None}
    # Pass the exact fixed-string pattern over stdin, never argv or a file.
    # --text covers binary files; hidden/ignored files include Git, caches and
    # the dedicated environment. Like the prior implementation, do not follow
    # symlinks. Only an exit status is exposed, never matching contents.
    checked = subprocess.run(['rg','--fixed-strings','--quiet','--text','--hidden',
                              '--no-ignore','--file','-',str(ROOT)],
                             input=value.encode()+b'\n',stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE)
    if checked.returncode not in (0,1):
        print('Secret scan could not complete; stop before committing.')
        raise SystemExit(71)
    found = checked.returncode==0
    print('Secret scan: FAIL; stop immediately.' if found else 'Secret scan: PASS (value not displayed).')
    if found: raise SystemExit(70)
    return {'key_is_set':True,'found':False}

def commit(message):
    scan = secret_scan()
    eid = event('git_commit_prepared', message, secret_scan=scan)
    subprocess.run(['git','add','--all'],cwd=ROOT,check=True)
    subprocess.run(['git','-c','gc.auto=0','-c','maintenance.auto=false','-c','user.name=Autonomous Research Agent',
                    '-c','user.email=research-agent@localhost','commit','--quiet','-m',eid+' '+message],
                   cwd=ROOT,check=True)
    sha = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    event('git_commit_recorded',message,related=[eid],commit_id=sha)
    print('COMMIT',sha)
    return sha

if __name__ == '__main__':
    if sys.argv[1] == 'commit': commit(' '.join(sys.argv[2:]))
    elif sys.argv[1] == 'scan': secret_scan()
    elif sys.argv[1] == 'event': print(event(sys.argv[2],sys.argv[3],sys.argv[4:]))
