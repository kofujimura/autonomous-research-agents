"""Exact saved-score diagnostics; no outcomes select queries."""
import numpy as np

def diagnose(pred):
 rows=[];required={'candidate_n','candidate_score_range','best_score_tie_n','nontrivial_matchable','confidence','query_id','region','rotation'}
 for method,g in pred.groupby('method',sort=True):
  missing=sorted(required-set(g.columns));missing+=['missing values in '+col for col in sorted(required&set(g.columns)) if g[col].isna().any()]
  if missing:rows.append(dict(method=method,nonempty_queries=len(g),diagnostic_available=False,missing_fields='|'.join(missing)));continue
  constant=(g.candidate_n>1)&(g.candidate_score_range==0);row=dict(method=method,diagnostic_available=True,missing_fields=None,nonempty_queries=len(g),multiple_best_reference_n=int((g.best_score_tie_n>1).sum()),constant_multi_candidate_n=int(constant.sum()),nontrivial_constant_n=int((constant&g.nontrivial_matchable).sum()),zero_half_budget_groups=0,boundary_tie_groups=0,boundary_tie_query_n=0,accepted_boundary_tie_n=0)
  for _,part in g.groupby(['region','rotation'],sort=True):
   ordered=part.sort_values(['confidence','query_id'],ascending=[False,True],kind='stable');k=int(np.floor(len(ordered)*.5))
   if k==0:row['zero_half_budget_groups']+=1;continue
   cutoff=ordered.confidence.iloc[k-1];selected=int((ordered.confidence.iloc[:k]==cutoff).sum());total=int((ordered.confidence==cutoff).sum())
   if total>selected:row['boundary_tie_groups']+=1;row['boundary_tie_query_n']+=total;row['accepted_boundary_tie_n']+=selected
  rows.append(row)
 return rows
