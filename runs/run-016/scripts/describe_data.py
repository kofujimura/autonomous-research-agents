"""Regenerate cohort and model context tables from fixed recorded inputs."""
import argparse,json
from collections import Counter
import numpy as np,pandas as pd
from records import ROOT,now,digest

def describe(manifest_path,models,destination):
    m=json.loads((ROOT/manifest_path).read_text());out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve previous descriptive outputs')
    out.mkdir(parents=True);rows=[]
    for r in m['landscapes']:
        row={k:r.get(k) for k in ['landscape_id','split','status','valid_points','missing_points','baseline_arable_fraction','baseline_grassland_fraction','baseline_agricultural_pixels','stable_agricultural_pixels','supercell']}
        if r['status']=='included':
            row['stable_share_of_2021_agriculture']=r['stable_agricultural_pixels']/r['baseline_agricultural_pixels']
            row['stable_share_of_landscape']=r['stable_agricultural_pixels']/(512**2)
        rows.append(row)
    pd.DataFrame(rows).to_csv(out/'landscape-description.csv',index=False)
    split=[]
    for name in ['train','calibration','test']:
        group=[r for r in rows if r['split']==name and r['status']=='included']
        split.append(dict(split=name,landscapes=len(group),spatial_supercells=len(set(r['supercell'] for r in group)),
                          finite_population_points=sum(r['valid_points'] for r in group),
                          minimum_points=min((r['valid_points'] for r in group),default=0),
                          maximum_points=max((r['valid_points'] for r in group),default=0),
                          source_year_labels=sum(r['valid_points'] for r in group) if name!='test' else 0,
                          median_stable_share_of_2021_agriculture=float(np.median([r['stable_share_of_2021_agriculture'] for r in group])) if group else None))
    pd.DataFrame(split).to_csv(out/'split-description.csv',index=False)
    train=[r for r in m['landscapes'] if r['status']=='included' and r['split']=='train']
    distances=[]
    for r in m['landscapes']:
        if r['status']!='included' or r['split']!='test':continue
        nearest=min(np.hypot(max(abs(r['left']-t['left'])-5120,0),max(abs(r['top']-t['top'])-5120,0)) for t in train)
        distances.append(dict(landscape_id=r['landscape_id'],minimum_test_train_footprint_gap_m=float(nearest)))
    pd.DataFrame(distances).to_csv(out/'spatial-distances.csv',index=False)
    diagnostics=[];convergence=[];model_inputs=[]
    for model_path in models:
        fit=json.loads((ROOT/model_path/'fit.json').read_text())
        model_inputs.append(dict(path=model_path,fit_sha256=digest(ROOT/model_path/'fit.json')))
        tag=f"{fit['classifier']}-{fit['taxonomy']}-{'refreshed' if fit['refreshed'] else 'frozen'}-{fit['representation']}"
        for rec in fit['fit_records']:
            convergence.append(dict(tag=tag,year=rec['year'],training_points=rec['training_points'],
                                    observed_training_classes=len(rec['classes']),convergence_warnings=len(rec['convergence_warnings']),
                                    maximum_iterations_used=max(rec.get('iterations') or [0]),
                                    excluded_training_points=rec.get('excluded_training_points',0)))
        frame=pd.DataFrame(fit['diagnostics'])
        for (split_name,year),g in frame.groupby(['split','year']):
            diagnostics.append(dict(tag=tag,representation=fit['representation'],taxonomy=fit['taxonomy'],classifier=fit['classifier'],refreshed=fit['refreshed'],
                                    split=split_name,year=int(year),landscapes=len(g),points=int(g.n.sum()),correct=int(g.correct.sum()),
                                    pixel_weighted_accuracy=float(g.correct.sum()/g.n.sum()),mean_landscape_accuracy=float(g.accuracy.mean()),
                                    unsupported_points=int(g.unsupported_points.sum()),unsupported_fraction=float(g.unsupported_points.sum()/g.n.sum()),
                                    source_calibration_rank=fit['calibration']['rank'],taxonomy_classes=len(fit['class_names'])))
    pd.DataFrame(diagnostics).to_csv(out/'classification-context.csv',index=False)
    pd.DataFrame(convergence).to_csv(out/'convergence.csv',index=False)
    latest={r['landscape_id']:r for r in map(json.loads,(ROOT/'data/selection-results.jsonl').read_text().splitlines())}
    result=dict(generated_at_utc=now(),manifest_path=manifest_path,manifest_sha256=digest(ROOT/manifest_path),models=model_inputs,
                selected_candidate_statuses=dict(Counter(r['status'] for r in latest.values())),attempted_distinct_candidates=len(latest),
                label_attempt_records=len((ROOT/'data/selection-results.jsonl').read_text().splitlines()),
                broad_taxonomy_groups=len(m['broad_ids']),fine_taxonomy_groups=len(m['fine_ids']),split_descriptions=split,
                minimum_test_train_gap_m=min(r['minimum_test_train_footprint_gap_m'] for r in distances),
                median_test_train_gap_m=float(np.median([r['minimum_test_train_footprint_gap_m'] for r in distances])),
                classification_context=diagnostics,convergence=convergence,
                national_probability_sample=False,farmer_or_household_id_analysis=False)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['generated_at_utc','attempted_distinct_candidates','broad_taxonomy_groups','fine_taxonomy_groups']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--model',action='append',default=[])
    p.add_argument('--destination',required=True);a=p.parse_args();describe(a.manifest,a.model,a.destination)
