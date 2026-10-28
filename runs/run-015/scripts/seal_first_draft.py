"""Seal an already verified first draft locally; never publish or call an API."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from record import ROOT, event, now, secret_check


def main():
    verification = json.loads((ROOT / 'review/verification-summary.json').read_text())
    assert verification['status'] == 'passed', 'Final-state verification has not passed'
    assert json.loads((ROOT / 'review/final-source-after-check.json').read_text())['status'] == 'passed'
    for path in (ROOT / 'experiments').glob('*/record.json'):
        assert json.loads(path.read_text())['status'] != 'running', str(path)
    assert subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/tags/submission-1'], cwd=ROOT).returncode != 0
    submission = ROOT / 'review/submission-1'
    assert not submission.exists(), 'Refuse overwriting a submission directory'
    for name in ['README.md', 'VERIFY.md', 'review/self-check.md']:
        assert '**Working' not in (ROOT / name).read_text() and 'WORKING:' not in (ROOT / name).read_text(), name
    assert 'not ready for submission' not in (ROOT / 'paper.md').read_text()
    assert '{{' not in (ROOT / 'paper.md').read_text()
    # The replay source precedes only the final administrative/status updates.
    # Require its scientific code, data and result bytes still to be current.
    critical = ('scripts/', 'data/', 'protocol/', 'results/', 'manuscript/', 'literature/',
                'sources.jsonl', 'api_calls.jsonl', 'requirements-')
    checked = 0
    for line in (ROOT / 'review/final-source-before.SHA256SUMS').read_text().splitlines():
        digest, relative = line.split('  ', 1)
        if relative.startswith(critical):
            assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative
            checked += 1
    scan = secret_check()
    manifest_path = ROOT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['first_draft_submission'] = {'prepared_at_utc': now(), 'tag': 'submission-1',
        'verified_scientific_files_checked': checked, 'verification_report': 'review/verification-summary.json',
        'sealing_commit_id': None,
        'commit_id_location': 'Resolve refs/tags/submission-1 in local Git; the conversation reports the resulting ID. A commit cannot contain its own hash.'}
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    eid = event('first_draft_submission_prepared',
        'Finalize first-draft files and prepare the local sealing commit/tag. Its resulting ID is resolved from submission-1; no self-referential hash is claimed.',
        ['paper.md', 'claims.jsonl', 'VERIFY.md', 'final_report.md', 'review/self-check.md', 'SHA256SUMS', 'review/submission-1'],
        secret_scan=scan, verified_scientific_files_checked=checked, submission_tag='submission-1')
    (ROOT / 'checkpoint.md').write_text(
        '# Checkpoint — free-research-015\n\nPrepared ' + now() + '.\n\n'
        'Resolve local Git tag `submission-1`. If present, the first draft is submitted and this directory is frozen: wait for human REVIEW-1 and make no changes. If absent, sealing is pending; inspect the last tool output/event and finish that operation without starting new research or overwriting a submitted version.\n\n'
        f"Root: {ROOT}. Original start: {manifest['start_time_utc']}. Original first-draft deadline: 2026-10-26T09:33:35Z. Current extended deadline: {manifest['first_draft_deadline_utc']}. Confirmed pause calculations and all conditions remain in manifest.json; no estimated pause extension is claimed. Limits:12research hours,2review-response hours,10GiB inclusive storage,2experiment workers,1800seconds per worker,$20combined API budget. No experiment was running at sealing preflight.\n\n"
        'Main files: paper.md, claims.jsonl, VERIFY.md, final_report.md, review/self-check.md and review/submission-1/. Final offline author replay: review/verification-summary.json and review/final-source-after-check.json. The sealing commit ID is resolved from the tag and reported in the conversation; a commit cannot contain its own hash.\n\n'
        'On receiving REVIEW-1, first obtain UTC time with a tool and start the two-hour review-response period. Save the literal review to review/review-1.md, record peer_review, respond pointwise, plan any new experiments before execution, revise and re-run verification, tally changes and seal/tag final. Do not contact or invoke a reviewer/other AI/sub-agent. No external publication or contact. If the human explicitly cancels the review, record that and make the first draft final.\n\n'
        f"Conversation session ID: {manifest['session_id']}; continuation IDs: {manifest['continuation_session_ids']}. Unknown IDs remain unknown. Preserve this conversation and local Git history. API key value is never printed/saved; scan before each commit/submission. Only the one authorized topic critique has been used; consult api_calls.jsonl and the final tally for its usage-based cost and remaining budget.\n")
    submission.mkdir()
    for name in ['paper.md', 'claims.jsonl', 'VERIFY.md', 'final_report.md']:
        shutil.copy2(ROOT / name, submission / name)
    shutil.copy2(ROOT / 'review/self-check.md', submission / 'self-check.md')
    shutil.copytree(ROOT / 'results/figures', submission / 'results/figures')
    def run(*args):
        subprocess.run([sys.executable, str(ROOT / 'scripts/hashes.py'), *args], cwd=ROOT, check=True)
    run('--root', str(ROOT / 'verification_work'), '--file', str(ROOT / 'review/verification-work-SHA256SUMS'),
        '--scope-file', str(ROOT / 'review/verification-work-hash-scope.json'))
    run('--file', str(ROOT / 'SHA256SUMS'), '--exclude', 'verification_work',
        '--exclude', 'review/submission-1/SHA256SUMS', '--scope-file', str(ROOT / 'hash-scope.json'))
    shutil.copy2(ROOT / 'SHA256SUMS', submission / 'SHA256SUMS')
    run('--file', str(ROOT / 'SHA256SUMS'), '--check')
    allocated = int(subprocess.check_output(['du', '-sk', str(ROOT)], text=True).split()[0]) * 1024
    assert allocated <= manifest['limits']['storage_bytes'], 'Storage limit exceeded'
    final_scan = secret_check()
    subprocess.run(['git', 'add', '--all'], cwd=ROOT, check=True)
    identity = ['git', '-c', 'user.name=Autonomous Research', '-c', 'user.email=research@localhost']
    subprocess.run([*identity, 'commit', '--quiet', '-m', f'{eid}: First draft submission; sealed output hashes'], cwd=ROOT, check=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    subprocess.run([*identity, 'tag', '-a', 'submission-1', '-m', f'First draft; {eid}; {commit}'], cwd=ROOT, check=True)
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()
    # No research-directory file is changed after the sealing commit/tag.
    print(json.dumps({'status': 'first_draft_submitted', 'commit_id': commit, 'tag': 'submission-1',
        'submission_time_utc': now(), 'event_id': eid, 'secret_scan': final_scan,
        'allocated_bytes_at_check': allocated, 'end_state': 'frozen; awaiting human REVIEW-1'}))


if __name__ == '__main__':
    main()
