"""Presentation-only regeneration; numerical CSVs and simulations are untouched."""
from records import ROOT,now,digest
from summarize_inference import plots
import pandas as pd,json

updated=[]
for path in sorted((ROOT/'results/tables').iterdir()):
    if not (path/'audit-performance.csv').exists():continue
    csvs=list(path.glob('*.csv'));before={p.name:digest(p) for p in csvs}
    plots(path,pd.read_csv(path/'audit-performance.csv'),pd.read_csv(path/'oracle-diagnostics.csv'),pd.read_csv(path/'point-estimates.csv'))
    assert before=={p.name:digest(p) for p in csvs},'Presentation update changed a numerical table'
    updated.append(str(path.relative_to(ROOT)))
print(json.dumps(dict(completed_at_utc=now(),presentation_only=True,unchanged_numerical_csvs=True,updated=updated)))
