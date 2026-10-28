"""Response letter and review tallies from structured decisions and actual records."""
import collections,datetime as dt,json,re
from pathlib import Path
from record import ROOT,now

def run():
    data=json.loads((ROOT/'review/response-points.json').read_text());points=data['points'];m=json.loads((ROOT/'manifest.json').read_text())
    old={r['claim_id']:r for r in map(json.loads,(ROOT/'review/submission-1/claims.jsonl').read_text().splitlines())};new={r['claim_id']:r for r in map(json.loads,(ROOT/'claims.jsonl').read_text().splitlines())}
    keys=['text','status','scope','expected','evidence_paths','source_ids','experiment_ids','exploratory','reader_implication']
    changed=[cid for cid in old if any(old[cid].get(k)!=new[cid].get(k) for k in keys)]
    status_changes=[dict(claim_id=cid,before=old[cid]['status'],after=new[cid]['status']) for cid in old if old[cid]['status']!=new[cid]['status']]
    added=sorted(set(new)-set(old));decisions=dict(collections.Counter(p['decision'] for p in points))
    scientific_experiments=sorted({e for p in points for e in p['experiments_added']})
    tally=dict(observed_at_utc=now(),review_id=data['review_id'],points=len(points),decisions=decisions,claims_modified=changed,claims_added=added,status_changes=status_changes,claims_withdrawn=[x['claim_id'] for x in status_changes if x['after'] in ['withdrawn','unsupported']],scientific_experiments_added=scientific_experiments,self_reruns_added=['end-to-end-self-rerun-4'],new_ai_api_calls=0)
    (ROOT/'review/review-response-summary.json').write_text(json.dumps(tally,indent=2)+'\n')
    paper=(ROOT/'paper.md').read_text();abstract=paper.split('## Abstract\n\n',1)[1].split('\n\n## 1.',1)[0]
    header=f'''# Response to review-014-1

The original review is preserved verbatim in review/review-1.md. It is a review by an AI agent, arranged and reported by the human; the reviewer model/settings and its same-machine rerun are not directly observable by the author. The reported check is not described as independent reproduction. Author-side additions use only saved public data and are explicitly exploratory after review. No other AI was called for the response.

Review-response period began {m['review_received_at_utc']}; deadline {m['review_response_deadline_utc']}. The revised title is **{paper.splitlines()[0].lstrip('# ')}**. The abstract now has {len(abstract.split())} whitespace-separated words, with {len(re.findall(r'\breadouts?\b',paper,re.I))} occurrences of readout terminology in the paper. Primary per-comparison changed-case counts are retained to satisfy the original trial instruction, using a compact defined order rather than the earlier horizon lists.

All {len(points)} points have a decision: {json.dumps(decisions,sort_keys=True)}. Main claim entries modified: {', '.join(changed)}. New entries: {', '.join(added)}. Claim status changes: {len(status_changes)}; withdrawn: {len(tally['claims_withdrawn'])}. Modified scopes preserve supported observed counts while narrowing interpretation; they are not silently recast as new primary hypotheses.

'''
    text=header
    for p in points:
        commits=f"Writing changes: {p.get('change_commit') or p['change_commit_ref']}"
        if p.get('analysis_commit'):commits+=f"; saved-data analysis/code: {p['analysis_commit']}"
        text+=f"## {p['point_id']} — {p['decision']}\n\nReason: {p['reason']}\n\n{p['detail']}\n\nChanges:\n\n"+'\n'.join('- '+x for x in p['changes'])+f"\n\n{commits}.\n\nExperiments added: {', '.join(p['experiments_added']) or 'none; documentation/presentation change'}.\n\n"
    text+='## Verification and preserved records\n\nThe final numerical procedure adds review-diagnostics-r1 to the complete existing entry point; every original metric and all new CSV columns are compared. See review/self-rerun-4.json for the actual candidate, timing, source-integrity result and numerical-module coverage. The first-draft tag/submission snapshot and earlier self-reruns remain unchanged. VERIFY.md explains how to verify the revised and original versions. The response decisions are in review/response-points.json, and tool-counted tallies in review/review-response-summary.json.\n'
    (ROOT/'review/response-1.md').write_text(text)
    final=(ROOT/'final_report.md').read_text();cut='\n## Review response tally\n'
    if cut in final:final=final.split(cut)[0]
    start=dt.datetime.fromisoformat(m['review_received_at_utc'].replace('Z','+00:00'));current=dt.datetime.fromisoformat(tally['observed_at_utc'].replace('Z','+00:00'))
    final+=cut+f"\nReview period: {m['review_received_at_utc']} to this snapshot {tally['observed_at_utc']}, {(current-start).total_seconds():.0f} seconds elapsed, deadline {m['review_response_deadline_utc']}. No confirmed usage-limit stop has occurred in this period. First-draft-to-review waiting time is excluded from both periods.\n\nThe human provided one review by an AI agent. Reviewer-side rerun and settings are reported, not directly observed; same-machine rerunning is not independent reproduction.\n\nPoints: {tally['points']}; decisions: {json.dumps(decisions,sort_keys=True)}. Existing claims modified: {len(changed)} ({', '.join(changed)}); added: {len(added)} ({', '.join(added)}); status changes: {len(status_changes)}; withdrawn: {len(tally['claims_withdrawn'])}. Scientific saved-data experiments added: {len(scientific_experiments)} ({', '.join(scientific_experiments)}); full author self-reruns added: {len(tally['self_reruns_added'])}. New AI API calls:0; combined-period API total remains in the usage section above.\n\nThe revised paper foregrounds absolute reference discrimination and magnitude ranking, documents year/region concentration and reference variation, adds training-target/production-version qualifications, and moves secondary checks to appendices. Source-access limits and reasons for partial adoption remain explicit. See review/response-1.md and review/review-response-summary.json. The final tag identifies the sealed revision; no further review round is planned. Session IDs remain unknown; preserve this conversation and the directory/Git history.\n"
    (ROOT/'final_report.md').write_text(final)
    verify=(ROOT/'VERIFY.md').read_text().replace('check out tag `submission-1`','check out tag `final`')
    marker='## Original first draft and revised package'
    if marker not in verify:verify+='\n'+marker+'\n\nTag `submission-1` and review/submission-1/ preserve the original report. To rerun that original procedure/inventory, check out submission-1 on a separate copy; its copied hash list describes that commit, not the revised root. Tag `final` supplies the updated offline entry point and inventory, including review-diagnostics-r1. The latter is post-review exploratory and uses no new data acquisition. Numerical diagnostics do not require rerunning any AI API.\n'
    (ROOT/'VERIFY.md').write_text(verify)
    print(json.dumps({**{k:v for k,v in tally.items() if k not in ['claims_modified','scientific_experiments_added']},'modified_claim_count':len(changed),'abstract_words':len(abstract.split())},indent=2))

if __name__=='__main__':run()
