"""Check case-level bookkeeping before interpreting reference context tables."""
import json
import numpy as np,pandas as pd
from records import ROOT,now
from audit_inference import sign

source=ROOT/'results/reference-frames';out=ROOT/'results/validation-reference-context'
if out.exists():raise FileExistsError('Keep diagnostics')
out.mkdir(parents=True)
units=[u for u in map(json.loads,(source/'units.jsonl').read_text().splitlines()) if u['frame']=='full_reference' and u['taxonomy']=='broad']
rows=[]
for u in units:
    with np.load(source/u['raw_path']) as z:
        for design in ['paired','independent']:
            pre=f'{design}_128_';direction=z[pre+'direction'];wrong=z[pre+'wrong']
            expected=(direction!=0)&(direction!=sign(u['true_change']))
            assert np.array_equal(expected,wrong)
            s=next(s for s in u['summaries'] if s['design']==design and s['n']==128)
            assert s['wrong_reports']==int(wrong.sum())
            rows.append(dict(unit_id=u['unit_id'],design=design,zero_change=u['zero_change'],true_change=u['true_change'],
                             changed=u['changed_reference_locations'],wrong_reports=int(wrong.sum()),wrong_rate=float(wrong.mean()),
                             coverage=float(z[pre+'covered'].mean())))
frame=pd.DataFrame(rows);frame.to_csv(out/'case-checks.csv',index=False)
summary=[]
for design,g in frame.groupby('design'):
    for subset,sg in [('all',g),('nonzero_change',g[~g.zero_change])]:
        summary.append(dict(design=design,subset=subset,units=len(sg),wrong_reports=int(sg.wrong_reports.sum()),
                            maximum_wrong_rate=float(sg.wrong_rate.max()),above_0_05=int((sg.wrong_rate>.05).sum())))
result=dict(completed_at_utc=now(),status='raw_checks_passed',summary=summary,
            zero_cases=frame[frame.zero_change].to_dict('records'),top_wrong=frame.sort_values('wrong_rate',ascending=False).head(8).to_dict('records'))
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
