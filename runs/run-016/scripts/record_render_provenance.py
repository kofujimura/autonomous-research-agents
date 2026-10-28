"""Append a factual correction; do not rewrite the original run record."""
import json,subprocess
from records import ROOT,now,event,append,digest
r=json.loads((ROOT/'experiments/E32-manuscript-render-2/run.json').read_text())
actual='874527d5b0c97c5f905fbd1f04556e5082b36f52'
blob=subprocess.check_output(['git','show',actual+':scripts/render_paper.py'],cwd=ROOT)
assert __import__('hashlib').sha256(blob).hexdigest()==digest(ROOT/'scripts/render_paper.py')
event('code_provenance_correction','Paper-formatting run E32-manuscript-render-2 began before its code commit completed; original run record retained, exact actual code recoverable from subsequent commit. Main statistical experiments unchanged.',
      ['experiments/E32-manuscript-render-2/run.json','scripts/render_paper.py'],retrospective=True,
      originally_recorded_code_commit=r['code_commit_id'],actual_code_snapshot_commit=actual,
      qualification='The actual code was committed after this formatting run; it is not described as precommitted. A fresh formatting run follows, and the runner now checks committed scripts/plans before starting.')
with (ROOT/'protocol/deviations.md').open('a') as f:
    f.write('\n## Manuscript-render code provenance\n\nA paper-formatting run E32-manuscript-render-2 started before its asynchronous code commit finished. Its original recorded code revision is retained; the actual renderer is recoverable from874527d. This is recorded as a post-run code snapshot, not a precommit. Main inference outputs are unchanged. The formatting step is rerun from committed code; scripts/run.py now rejects uncommitted script/plan changes and records script SHA-256 values. See the correction event for tool-observed time.\n')
