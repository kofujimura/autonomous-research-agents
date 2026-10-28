"""Small local record utilities. Never print or persist credentials."""
from pathlib import Path
import datetime
import fcntl
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

def append(path, value):
    with (ROOT / path).open('a') as f:
        f.write(json.dumps(value, ensure_ascii=False) + '\n')

def event(kind, summary, paths=(), related=(), **extra):
    with (ROOT / 'events.jsonl').open('a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        rows = [json.loads(x) for x in f.read().splitlines() if x]
        n = max(int(x['event_id'][1:]) for x in rows) + 1 if rows else 1
        value = dict(event_id=f'E{n:04d}', observed_at_utc=now(), type=kind,
                     summary=summary, artifact_paths=list(paths), related_ids=list(related), **extra)
        f.seek(0, 2)
        f.write(json.dumps(value, ensure_ascii=False) + '\n')
        fcntl.flock(f, fcntl.LOCK_UN)
    return value['event_id']

def check_secret():
    key = os.environ.get('FREE_RESEARCH_OPENAI_API_KEY', '').encode()
    if not key:
        return {'key_present_in_environment': False, 'match_in_directory': False}
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.is_symlink():
            continue
        with p.open('rb') as f:
            tail = b''
            while chunk := f.read(1024*1024):
                combined = tail + chunk
                if key in combined:
                    raise RuntimeError('SECRET VALUE FOUND IN RESEARCH DIRECTORY: stop and notify human')
                tail = combined[-max(len(key)-1, 0):]
    return {'key_present_in_environment': True, 'match_in_directory': False}

def commit(event_id, message, exclude=()):
    check = check_secret()
    subprocess.run(['git', 'add', '.', *[':(exclude)'+x for x in exclude]], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(['git', '-c', 'user.name=Autonomous Research', '-c',
                    'user.email=research@localhost', 'commit', '-m', f'{event_id}: {message}'],
                   cwd=ROOT, check=True, capture_output=True)
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    event('git_commit', message, related=[event_id], commit_id=sha, secret_check=check,
          excluded_in_progress_paths=list(exclude))
    return sha

if __name__ == '__main__':
    if sys.argv[1] == 'secret-check':
        print(json.dumps(check_secret()))
    elif sys.argv[1] == 'commit':
        print(commit(sys.argv[2], sys.argv[3]))
