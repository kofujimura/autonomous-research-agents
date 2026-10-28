"""Record the full-text checks performed in this session (bookkeeping only)."""
from records import ROOT,now,append,digest,event

for sid,title,authors,year,url,stem,sections,supports in [
 ('STRAT-PPI2024','Stratified Prediction-Powered Inference for Hybrid Language Model Evaluation',
  'Adam Fisch, Joshua Maynez, R. Alex Hofer, Bhuwan Dhingra, Amir Globerson and William W. Cohen',2024,
  'https://papers.neurips.cc/paper_files/paper/2024/file/c9fcd02e6445c7dfbad6986abee53d0d-Paper-Conference.pdf',
  'stratified-ppi-2024','Full-text sections3–4.3, including assumptions, Theorem2, Propositions1–3 and Examples1–2',
  'Stratification, prediction weighting, and allocation in PPI are established; these i.i.d./asymptotic guarantees do not directly establish small-sample projected-entropy coverage'),
 ('CLUSTER-PPI2026','Cluster-Robust Prediction-Powered Inference','David Broska and Michael Howes',2026,
  'https://arxiv.org/pdf/2610.09601','cluster-ppi-2026',
  'Full-text introduction and sections2–2.4, including independent-cluster/Bernoulli labeling assumptions, Theorem1 and power tuning',
  'Dependence-aware PPI and cluster-level power tuning are established; distinct sampling framework from fixed finite-population SRS used here')]:
    paths=[f'sources/{stem}.{ext}' for ext in ['pdf','txt']]
    downloads=[__import__('json').loads(s) for s in (ROOT/'data/downloads.jsonl').read_text().splitlines()]
    download=next((r for r in downloads if r.get('path')==paths[0]),{})
    append('sources.jsonl',dict(source_id=sid,title=title,authors=authors,year=year,url=url,
           doi_or_version='NeurIPS2024' if year==2024 else 'arXiv:2610.09601v1',
           checked_at_utc=now(),access='full_text_relevant_passages_checked',range_checked=sections,
           supports=supports,paths=paths,sha256={p:digest(ROOT/p) for p in paths},
           obtained_at_utc=download.get('obtained_at_utc'),obtained_time_note='Corrected provenance lookup: data/downloads.jsonl; supersedes preceding bibliographic registration',
           incidental_information='Public scholarly contact details occur in source PDFs; not research data, analyzed or contacted'))
event('prior_work_check','Checked full methods for stratified and cluster-robust PPI; no estimator or sampling-design novelty claimed',
      ['sources/stratified-ppi-2024.pdf','sources/cluster-ppi-2026.pdf','sources.jsonl'])
