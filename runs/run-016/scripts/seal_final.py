"""Seal the reviewed local final; no external publication or contact."""
import json,subprocess
from records import ROOT,now,event,secret_scan,commit
from hash_outputs import run as hash_outputs
from verify_hashes import check

def run():
    assert subprocess.check_output(['git','rev-parse','submission-1'],cwd=ROOT,text=True).strip()=='faf7dce40c1a27313b4ae7fb51554fa5d061393b'
    assert not subprocess.check_output(['git','tag','--list','final'],cwd=ROOT,text=True).strip(),'Final already sealed'
    v=json.loads((ROOT/'review/verification-final.json').read_text())
    assert v['status']=='passed' and v['valid_as_final_submission_check'] and v['mode']=='all'
    snap=json.loads((ROOT/'review/snapshot-final.json').read_text())
    assert all(json.loads(p.read_text())['status']!='running' for p in (ROOT/'experiments').glob('*/run.json'))
    changed=subprocess.check_output(['git','diff','--name-only',snap['source_commit']],cwd=ROOT,text=True).splitlines()
    for path in changed:
        scientific=path.startswith(('scripts/','data/','sources/','protocol/','input_skills/')) or path in ['paper.md','claims.jsonl','manuscript/template.md','input_prompt.md','sources.jsonl','verification-config.json','requirements-verify.txt'] or (path.startswith('results/') and path!='results/study-tallies.json')
        assert not scientific,('Scientific artifact changed since full rerun',path)
    allocation=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])*1024
    assert allocation+24*1024**2<=10*1024**3,'Need final inventory/Git reserve'
    secret_scan()
    response=json.loads((ROOT/'review/response-summary.json').read_text());assert response['verification_status']=='passed'
    event('paper_finalized','Finalize reviewed paper: all nine review points disposed, original first draft preserved; full offline self-rerun passed',
      ['paper.md','claims.jsonl','review/response-1.md','review/verification-final.json'],verified_source_commit=snap['source_commit'])
    (ROOT/'review/storage-final.json').write_text(json.dumps(dict(observed_at_utc=now(),allocated_bytes_from_du_kib=allocation,limit_bytes=10*1024**3,
      qualification='Point observation, not high-water mark; earlier unmeasured Git-packing peak remains disclosed.'),indent=2)+'\n')
    (ROOT/'checkpoint.md').write_text(f'# Checkpoint\n\nFinal reviewed study ready for sealing, tool-observed {now()}. Original submission-1 preserved. Review-response start2026-10-27T02:50:07Z and deadline2026-10-27T04:50:07Z. Full final offline rerun passed, source {snap["source_commit"]}; numerical outputs/paper/claims unchanged since that rerun. No study process remains running. No additional API calls or permissions. USD1.94391 cumulative API cost. Session/continuation identifiers unknown(null).\n\nAfter final tag exists, the study is complete. Inspect tag final and terminal final_submission event for commit/time. No external publication or contact. Final report, verification, review response and scoped hashes are at repository root/review.\n')
    hash_outputs('SHA256SUMS.json');result=check('SHA256SUMS.json')
    (ROOT/'review/hash-verification-final.json').write_text(json.dumps(result,indent=2)+'\n')
    sha=commit('Final reviewed submission with full offline verification and regenerated scoped SHA-256 inventory')
    subprocess.run(['git','tag','final',sha],cwd=ROOT,check=True)
    eid=event('final_submission','Reviewed final submitted locally; study complete with no external publication',
      ['paper.md','claims.jsonl','VERIFY.md','final_report.md','review/response-1.md','SHA256SUMS.json'],commit_id=sha,tag='final',
      verified_source_commit=snap['source_commit'],terminal_receipt_note='This append-only event and final commit receipt are outside the inventory event prefix and their own referenced commit; scientific files unchanged.')
    print(json.dumps(dict(status='Final submitted',commit_id=sha,event_id=eid,submission_time_utc=now(),tag='final',session_id=None,continuation_session_ids=[])))

if __name__=='__main__':run()
