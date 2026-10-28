"""Seal the authorized local first draft; never publishes or contacts anyone."""
import json,shutil,subprocess
from pathlib import Path
from records import ROOT,now,event,secret_scan,commit
from hash_outputs import run as hash_outputs
from verify_hashes import check

def run():
    assert not subprocess.check_output(['git','tag','--list','submission-1'],cwd=ROOT,text=True).strip(),'First draft already sealed; wait for REVIEW-1'
    v=json.loads((ROOT/'review/verification-submission-1.json').read_text())
    assert v['status']=='passed' and v['valid_as_final_submission_check'] and v['mode']=='all'
    assert 'Final pre-submission full rerun: passed.' in (ROOT/'review/self-check.md').read_text()
    assert all(json.loads(p.read_text())['status']!='running' for p in (ROOT/'experiments').glob('*/run.json'))
    snapshot=json.loads((ROOT/'review/snapshot-submission-1.json').read_text())
    changed=subprocess.check_output(['git','diff','--name-only',snapshot['source_commit']],cwd=ROOT,text=True).splitlines()
    for path in changed:
        scientific=path.startswith(('scripts/','data/','sources/','protocol/','input_skills/')) or path in ['paper.md','claims.jsonl','manuscript/template.md','input_prompt.md','sources.jsonl','verification-config.json','requirements-verify.txt'] or (path.startswith('results/') and path!='results/study-tallies.json')
        assert not scientific,('Scientific file changed after full verification',path)
    allocated=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])*1024
    assert allocated+64*1024**2<=10*1024**3,'Keep sealing storage reserve'
    secret_scan()
    event('first_draft_prepared','All scientific files unchanged since the passed fresh-copy rerun; prepare local submission-1',['paper.md','claims.jsonl','VERIFY.md','final_report.md','review/self-check.md'],verified_source_commit=snapshot['source_commit'],allocated_storage_bytes=allocated)
    (ROOT/'review/storage-submission-1.json').write_text(json.dumps(dict(observed_at_utc=now(),allocated_bytes_from_du_kib=allocated,
        limit_bytes=10*1024**3,qualification='Point observation including hardlinks once; not a measured high-water mark. Earlier Git packing peak remains unknown.'),indent=2)+'\n')
    dest=ROOT/'review/submission-1';dest.mkdir()
    for name in ['paper.md','claims.jsonl','VERIFY.md','final_report.md']:
        shutil.copyfile(ROOT/name,dest/name)
    shutil.copyfile(ROOT/'review/self-check.md',dest/'self-check.md')
    hash_outputs('SHA256SUMS.json');shutil.copyfile(ROOT/'SHA256SUMS.json',dest/'SHA256SUMS.json')
    result=check('SHA256SUMS.json')
    (ROOT/'review/hash-verification-submission-1.json').write_text(json.dumps(result,indent=2)+'\n')
    sha=commit('First draft submission-1 with passed full rerun and scoped SHA-256 inventory')
    subprocess.run(['git','tag','submission-1',sha],cwd=ROOT,check=True)
    eid=event('first_draft_submission','First draft submitted locally; directory frozen awaiting human REVIEW-1',['review/submission-1','SHA256SUMS.json'],
        commit_id=sha,tag='submission-1',verified_source_commit=snapshot['source_commit'],
        terminal_receipt_note='This append-only event and the last commit receipt are outside the inventory event prefix and are not in their own referenced commit. No scientific artifact is changed.')
    receipt=json.loads((ROOT/'events.jsonl').read_text().splitlines()[-1])
    print(json.dumps(dict(status='First draft submitted',commit_id=sha,tag='submission-1',submission_time_utc=receipt['observed_at_utc'],event_id=eid,
        title=(ROOT/'paper.md').read_text().splitlines()[0].lstrip('# '),verification_path=str(ROOT/'VERIFY.md'),state='Waiting for REVIEW-1; no further directory changes permitted.')))

if __name__=='__main__':run()
