"""Register the actual final search scope and unresolved leads, without claims."""
import json
from records import ROOT,now,append,event,digest

for number in [1,2]:
    path=f'sources/final-prior-search-{number}.json';data=json.loads((ROOT/path).read_text())
    append('sources.jsonl',dict(source_id=f'FINAL-SEARCH-{number}',title='Final close-prior search record',url=None,
        checked_at_utc=now(),access='search_results_only',range_checked=data['queries'],paths=[path],sha256=digest(ROOT/path),
        supports='Search-scope record only; not scientific evidence or proof of novelty'))
for sid,title,url,note in [
 ('CROP-SCALE2020-LEAD','The scale dependency of spatial crop species diversity and its relation to temporal diversity','https://doi.org/10.1073/pnas.2011702117','Search/abstract lead; attempted PMC full-page opening returned a browser challenge; no bypass or claim-support citation'),
 ('DIVERSITY-DESIGN-LEAD','Design-Based Inference on Diversity in Biological Populations','https://cab.unime.it/mus/362/1/Design-Based_Inference_on_Diversity_in_Biological_Populations.pdf','Public institutional PDF retrieval failed TLS certificate verification; validation was not disabled; not cited as supporting evidence'),
 ('RESURVEY2026-LEAD','Can we trust vegetation resurveys?','https://doi.org/10.1111/1365-2745.70425','Search-only lead relevant to permanent plots; not cited as full-text evidence'),
 ('RAREFACTION2026-LEAD','Rarefaction profiles for repeated biodiversity surveys: integrating temporal variability and trend along sample-based accumulation curves','https://www.sciencedirect.com/science/article/pii/S1574954126005212','Search-only recent lead; does not establish a method gap and is not used as scientific evidence')]:
    append('sources.jsonl',dict(source_id=sid,title=title,url=url,authors=None,year=None,checked_at_utc=now(),
        access='search_or_abstract_only',range_checked=note,supports=None,paths=['sources/final-prior-search-1.json','sources/final-prior-search-2.json']))
event('final_prior_work_search','Rechecked crop-diversity, entropy-change, design-based and repeated/rotating-sample literature; retained unresolved leads and access failures; no novelty assertion',
      ['sources/final-prior-search-1.json','sources/final-prior-search-2.json','sources.jsonl'])
