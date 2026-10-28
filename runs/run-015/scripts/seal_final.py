"""Seal the revised local final submission after a verified scientific snapshot."""
import hashlib
import json
import shutil
import subprocess
import sys

from record import ROOT,event,now,secret_check


def main():
    verification=json.loads((ROOT/'review/verification-summary.json').read_text())
    assert verification['status']=='passed'
    assert json.loads((ROOT/'review/revision-source-after-check.json').read_text())['status']=='passed'
    for path in (ROOT/'experiments').glob('*/record.json'):
        assert json.loads(path.read_text())['status']!='running',str(path)
    assert subprocess.run(['git','show-ref','--verify','--quiet','refs/tags/final'],cwd=ROOT).returncode!=0
    assert subprocess.check_output(['git','rev-parse','submission-1^{}'],cwd=ROOT,text=True).strip()=='b2a57df1db623ddc9fb7512cc5778ad2ae96832b'
    assert len(json.loads((ROOT/'review/decisions.json').read_text()))==7
    assert (ROOT/'review/response-1.md').exists()
    critical=('scripts/','data/','protocol/','results/','manuscript/','literature/',
              'sources.jsonl','api_calls.jsonl','requirements-')
    checked=0
    for line in (ROOT/'review/revision-source-before.SHA256SUMS').read_text().splitlines():
        digest,relative=line.split('  ',1)
        if relative.startswith(critical):
            assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,relative
            checked+=1
    # The immutable first-draft copies must still have their submitted bytes.
    old_files=subprocess.check_output(['git','ls-tree','-r','--name-only','submission-1','review/submission-1'],cwd=ROOT,text=True).splitlines()
    for name in old_files:
        old=subprocess.check_output(['git','show','submission-1:'+name],cwd=ROOT)
        assert (ROOT/name).read_bytes()==old,name
    scan=secret_check();stamp=now()
    manifest_path=ROOT/'manifest.json';manifest=json.loads(manifest_path.read_text())
    manifest['final_submission']={'prepared_at_utc':stamp,'tag':'final','review_id':'review-015-1',
        'verification_report':'review/verification-summary.json','verified_scientific_files_checked':checked,
        'commit_id':None,'commit_id_location':'Resolve local tag final; a commit cannot contain its own hash.'}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    eid=event('final_submission_prepared','Finalize revised paper and pointwise review response; prepare local final commit/tag. Resulting ID is resolved from final; no self-referential hash is claimed.',
        ['paper.md','claims.jsonl','VERIFY.md','final_report.md','review/response-1.md','SHA256SUMS'],
        secret_scan=scan,verified_scientific_files_checked=checked,submission_tag='final')
    (ROOT/'checkpoint.md').write_text('# Checkpoint — final submission\n\nPrepared '+stamp+'. Resolve local tag `final`: if present the review response and study are complete; no further research work is pending. If absent, sealing is pending and this script may not have finished; inspect its output before retrying.\n\nRoot: '+str(ROOT)+'. First-draft tag submission-1 is preserved. Original research start/deadlines and confirmed pauses remain in manifest.json. Review response began 2026-10-26T12:54:07Z; unchanged deadline 2026-10-26T14:54:07Z. Resource limits remain 10 GiB including verification copies, two experiment workers, 1800 seconds per run and $20 combined API budget. No experiment is running. Only the authorized topic critique used an API; no new review-response API call or subagent. No external publication/contact.\n\nThe paper and pointwise response are paper.md and review/response-1.md; verification is documented in VERIFY.md and review/verification-summary.json. Main and auxiliary SHA-256 lists cover their stated scopes, including preserved failed/partial raw results. Session ID and continuation session IDs are unknown when not exposed; preserve this conversation and both submitted Git tags.\n')
    submission=ROOT/'review/submission-final';submission.mkdir(exist_ok=False)
    for name in ['paper.md','claims.jsonl','VERIFY.md','final_report.md']:
        shutil.copy2(ROOT/name,submission/name)
    for name in ['self-check.md','response-1.md']:
        shutil.copy2(ROOT/'review'/name,submission/name)
    shutil.copytree(ROOT/'results/figures',submission/'results/figures')
    def run(*args):subprocess.run([sys.executable,str(ROOT/'scripts/hashes.py'),*args],cwd=ROOT,check=True)
    run('--root',str(ROOT/'verification_work'),'--file',str(ROOT/'review/verification-work-SHA256SUMS'),
        '--scope-file',str(ROOT/'review/verification-work-hash-scope.json'))
    run('--file',str(ROOT/'SHA256SUMS'),'--exclude','verification_work',
        '--exclude','review/submission-final/SHA256SUMS','--scope-file',str(ROOT/'hash-scope.json'))
    shutil.copy2(ROOT/'SHA256SUMS',submission/'SHA256SUMS')
    run('--file',str(ROOT/'SHA256SUMS'),'--check')
    allocated=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])*1024
    assert allocated<=manifest['limits']['storage_bytes'],'Storage limit exceeded'
    final_scan=secret_check()
    subprocess.run(['git','add','--all'],cwd=ROOT,check=True)
    identity=['git','-c','user.name=Autonomous Research','-c','user.email=research@localhost']
    subprocess.run([*identity,'commit','--quiet','-m',f'{eid}: Final submission after AI-agent review; sealed output hashes'],cwd=ROOT,check=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    subprocess.run([*identity,'tag','-a','final','-m',f'Final revised submission; {eid}; {commit}'],cwd=ROOT,check=True)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()
    print(json.dumps({'status':'final_submitted','commit_id':commit,'tag':'final','submission_time_utc':now(),
        'event_id':eid,'secret_scan':final_scan,'allocated_bytes_at_check':allocated,'end_state':'complete; no external publication'}))


if __name__=='__main__':main()
