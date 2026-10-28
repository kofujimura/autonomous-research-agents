"""Small local record/commit helpers; never print or serialize the API key."""
from pathlib import Path
import argparse, datetime as dt, hashlib, json, os, subprocess, fcntl

ROOT = Path(__file__).resolve().parents[1]

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def append(path, value):
    with (ROOT / path).open('a') as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + '\n')

def event(kind, summary, paths=(), related=(), **extra):
    with (ROOT/'events.jsonl').open('a+') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        stream.seek(0)
        eid=f'E{sum(1 for _ in stream)+1:04d}'
        stream.write(json.dumps(dict(event_id=eid,observed_at_utc=now(),type=kind,
                     summary=summary,artifact_paths=list(paths),related_ids=list(related),**extra))+'\n')
        stream.flush()
        fcntl.flock(stream,fcntl.LOCK_UN)
    return eid

def secret_check():
    key = os.environ.get('FREE_RESEARCH_OPENAI_API_KEY')
    if not key:
        return {'checked_at_utc': now(), 'key_present': False, 'matches': 0}
    needle = key.encode()
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        with path.open('rb') as stream:
            tail = b''
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                if needle in tail + chunk:
                    raise RuntimeError('SECRET_MATCH_FOUND: stop work and notify user')
                tail = (tail + chunk)[-(len(needle)-1):] if len(needle)>1 else b''
    return {'checked_at_utc': now(), 'key_present': True, 'matches': 0}

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()

def commit(summary):
    check = secret_check()
    eid = event('git_commit_prepared', summary, secret_check=check)
    git('add', '--all')
    result = git('-c', 'user.name=Research Agent', '-c', 'user.email=research@localhost',
                 'commit', '-m', f'{eid}: {summary}')
    sha = git('rev-parse', 'HEAD')
    event('git_commit', summary, ['.git'], [eid], commit_id=sha)
    print(json.dumps({'event_id':eid, 'commit_id':sha, 'result':result}))
    return sha

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['commit','check-key','time'])
    parser.add_argument('summary', nargs='?', default='checkpoint')
    args = parser.parse_args()
    if args.action == 'commit':
        commit(args.summary)
    elif args.action == 'check-key':
        print(json.dumps(secret_check()))
    else:
        print(now())
